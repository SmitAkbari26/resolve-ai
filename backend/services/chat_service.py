"""
Resolve AI - Chat Service

The single orchestrating service for the end-to-end chat flow:

  Frontend sends message
        │
        ▼
  1. Ensure conversation record exists in DB   (conversations)
  2. Persist user message to DB               (conversation_messages)
  3. Execute multi-agent workflow             (workflow_executions, workflow_steps)
      └─ ConversationAgent → PlannerAgent
          └─ Plan: retrieval → decision → ticket → approval → notification
              └─ TicketAgent  → DB ticket record  (tickets)
              └─ ApprovalAgent→ DB approval record (approvals)
              └─ NotificationAgent → DB record     (notifications)
  4. Update conversation sentiment in DB      (conversations)
  5. Persist AI response message to DB        (conversation_messages)
  6. Write audit log entry                    (audit_logs)
  7. Return structured response to frontend
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from services.conversation_service import ConversationService
from services.conversation_message_service import ConversationMessageService
from services.workflow_service import WorkflowService
from services.audit_log_service import AuditLogService

from schemas.conversation_schema import ConversationCreate, ConversationUpdate
from schemas.conversation_message_schema import ConversationMessageCreate
from schemas.audit_log_schema import AuditLogCreate

from db.memory_store import get_conversation_memory, store_conversation_memory, append_message
from utils.logger import get_logger
from utils.text_sanitize import plain_chat_text, sanitize_dict_strings, sanitize_text

logger = get_logger(__name__)


class ChatService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self._conversation_svc = ConversationService(db)
        self._message_svc = ConversationMessageService(db)
        self._workflow_svc = WorkflowService(db)
        self._audit_svc = AuditLogService(db)

    # ─────────────────────────────────────────────────────
    # PRIMARY ENTRY POINT
    # ─────────────────────────────────────────────────────

    async def handle_message(
        self,
        user_id: str,
        user_email: str,
        user_message: str,
        conversation_id: str | None = None,
        stream_callback = None,
        api_key: str | None = None,
    ) -> dict:
        """
        Full end-to-end chat handler.
        """

        # Resolve tenant_id and company_name from api_key
        tenant_id = None
        company_name = "our company"
        if api_key:
            from repositories.tenant_repository import TenantRepository
            try:
                tenant_repo = TenantRepository(self.db)
                tenant = await tenant_repo.get_by_api_key(api_key)
                if tenant:
                    tenant_id = str(tenant.id)
                    from services.widget_configuration_service import WidgetConfigurationService
                    from uuid import UUID
                    widget_svc = WidgetConfigurationService(self.db)
                    widget_conf = await widget_svc.get_configuration(UUID(tenant_id))
                    if widget_conf and widget_conf.company_name:
                        company_name = widget_conf.company_name
            except Exception as e:
                logger.warning(f"Could not resolve tenant or company name by API key: {e}")

        # =================================================
        # STEP 1 — Ensure Conversation Record in DB
        # =================================================

        conversation_id = await self._ensure_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_email=user_email,
        )

        logger.info(
            f"Chat | User={user_id} | "
            f"ConversationID={conversation_id} | Tenant={tenant_id}"
        )

        try:
            redis_history = get_conversation_memory(conversation_id)
            if not redis_history:
                db_messages = await self._message_svc.get_messages_by_conversation_id(conversation_id)
                if db_messages:
                    messages_to_store = [
                        {"role": msg.role, "content": msg.message}
                        for msg in db_messages
                    ]
                    store_conversation_memory(conversation_id, messages_to_store)
                    logger.info(f"Warmed up conversation memory in Redis from DB for conversation {conversation_id}")
        except Exception as memory_err:
            logger.warning(f"Failed to warm up conversation memory: {memory_err}")

        # =================================================
        # STEP 2 — Persist User Message → conversation_messages
        # =================================================

        await self._save_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            metadata={"source": "frontend_chat"},
        )

        # Check if there is an existing ticket for this conversation to prevent duplicate creations
        from services.ticket_service import TicketService
        ticket_id = ""
        try:
            ticket_svc = TicketService(self.db)
            existing_ticket = await ticket_svc.get_ticket_by_conversation_id(
                conversation_id
            )
            if existing_ticket:
                ticket_id = str(existing_ticket.id)
        except Exception as e:
            logger.warning(f"Failed to query existing ticket for conversation: {e}")

        workflow_result = await self._workflow_svc.execute_workflow(
            user_query=user_message,
            conversation_id=conversation_id,
            user_id=user_id,
            user_email=user_email,
            ticket_id=ticket_id,
            stream_callback=stream_callback,
            tenant_id=tenant_id,
            company_name=company_name,
        )

        # The DB session was closed during workflow execution to prevent deadlocks.
        # Re-open a fresh session from the factory for the remaining DB operations.
        from db.database import async_session_factory
        new_db = async_session_factory()
        self.db = new_db
        self._conversation_svc.db = new_db
        self._message_svc.db = new_db
        self._workflow_svc.db = new_db
        self._audit_svc.db = new_db



        # If a ticket was created this turn, reload it for the next user message
        if workflow_result.get("ticket_id") and not ticket_id:
            try:
                ticket_svc = TicketService(self.db)
                fresh = await ticket_svc.get_ticket_by_id(
                    workflow_result["ticket_id"]
                )
                if fresh:
                    workflow_result["ticket"] = {
                        "id": str(fresh.id),
                        "category": fresh.category,
                        "priority": fresh.priority,
                        "status": fresh.status,
                        "summary": fresh.summary,
                        "description": fresh.description,
                    }
            except Exception as e:
                logger.warning(f"Could not reload created ticket: {e}")

        # =================================================
        # STEP 4 — Update Conversation Sentiment in DB
        # =================================================

        detected_sentiment = workflow_result.get("detected_sentiment", "neutral")
        await self._update_conversation_sentiment(
            conversation_id=conversation_id,
            sentiment=detected_sentiment,
        )

        # =================================================
        # STEP 5 — Persist AI Response → conversation_messages
        # =================================================

        ai_response = workflow_result.get("ai_response", "")
        workflow_status = workflow_result.get("status", "completed")

        # Paused workflows: the response is the approval-pending message
        if not ai_response and workflow_status == "paused":
            ai_response = (
                "Your request is being reviewed by our team. "
                "You will be notified once a decision is made."
            )

        ai_response = plain_chat_text(ai_response)

        if ai_response:
            await self._save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response,
                metadata={
                    "workflow_id":   workflow_result.get("workflow_id"),
                    "status":        workflow_status,
                    "ticket_id":     workflow_result.get("ticket_id"),
                    "approval_id":   workflow_result.get("approval_id"),
                    "severity":      workflow_result.get("severity"),
                    "agent_count":   len(workflow_result.get("agent_trace", [])),
                },
            )
            try:
                append_message(conversation_id, "assistant", ai_response)
                logger.info(f"Appended assistant response to Redis memory for {conversation_id}")
            except Exception as e:
                logger.warning(f"Memory append failed for assistant: {e}")

        # =================================================
        # STEP 6 — Write Audit Log → audit_logs
        # =================================================

        await self._write_audit_log(
            entity_type="conversation",
            entity_id=conversation_id,
            action="chat_workflow_executed",
            agent_name="ChatService",
            details={
                "workflow_id":      workflow_result.get("workflow_id"),
                "workflow_status":  workflow_status,
                "plan":             workflow_result.get("plan", []),
                "category":         workflow_result.get("detected_category"),
                "sentiment":        detected_sentiment,
                "urgency":          workflow_result.get("urgency"),
                "severity":         workflow_result.get("severity"),
                "ticket_id":        workflow_result.get("ticket_id"),
                "approval_id":      workflow_result.get("approval_id"),
                "requires_approval":workflow_result.get("requires_approval"),
                "agent_count":      len(workflow_result.get("agent_trace", [])),
            },
        )

        # =================================================
        # STEP 7 — Build Frontend Response
        # =================================================

        return {
            "conversation_id":    conversation_id,
            "workflow_id":        workflow_result.get("workflow_id"),
            "status":             workflow_status,
            "ai_response":        ai_response,
            "ticket_id":          workflow_result.get("ticket_id"),
            "approval_id":        workflow_result.get("approval_id"),
            "requires_approval":  workflow_result.get("requires_approval", False),
            "approval_reason":    workflow_result.get("approval_reason", ""),
            "detected_category":  workflow_result.get("detected_category"),
            "detected_sentiment": detected_sentiment,
            "urgency":            workflow_result.get("urgency"),
            "severity":           workflow_result.get("severity"),
            "plan":               workflow_result.get("plan", []),
            "agent_trace":        workflow_result.get("agent_trace", []),
            "runtime_events":     workflow_result.get("runtime_events", []),
            "tool_calls":         workflow_result.get("tool_calls", []),
        }

    # ─────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────

    async def _ensure_conversation(
        self,
        user_id: str,
        conversation_id: str | None,
        tenant_id: str | None = None,
        user_email: str | None = None,
    ) -> str:
        """
        Returns the conversation_id.
        Creates a new ConversationRecord in DB if none provided.
        """
        try:
            from uuid import UUID
            from db.schemas import UserRecord
            from sqlalchemy import select
            from core.security import hash_password
            
            user_uuid = UUID(user_id)
            
            # 1. Ensure user exists first
            result = await self.db.execute(
                select(UserRecord).where(UserRecord.id == user_uuid)
            )
            user = result.scalar_one_or_none()
            if not user:
                email = user_email or f"{user_id}@guest.resolve.ai"
                # Check if email is already taken
                email_result = await self.db.execute(
                    select(UserRecord).where(UserRecord.email == email)
                )
                existing_email_user = email_result.scalar_one_or_none()
                if existing_email_user:
                    # Link to existing user if email matches
                    user_uuid = existing_email_user.id
                    user_id = str(user_uuid)
                else:
                    name = email.split("@")[0] if "@" in email else "Guest"
                    new_user = UserRecord(
                        id=user_uuid,
                        name=name,
                        email=email,
                        role="customer",
                        password_hash=hash_password("guest_secret_pass_123!"),
                    )
                    self.db.add(new_user)
                    await self.db.commit()
                    logger.info(f"Auto-created guest user record for user_id {user_id} with email {email}")
        except Exception as ue:
            logger.warning(f"Failed to verify or auto-create user {user_id}: {ue}")
            try:
                await self.db.rollback()
            except Exception:
                pass

        if conversation_id:
            # Verify it exists; if not, create it
            existing = await self._conversation_svc.get_conversation_by_id(
                conversation_id
            )
            if existing:
                return str(existing.id)

        # Create a fresh conversation record
        try:
            from uuid import UUID
            new_conv = await self._conversation_svc.create_conversation(
                ConversationCreate(
                    user_id=user_uuid,
                    tenant_id=UUID(tenant_id) if tenant_id else None,
                    channel="web_chat",
                    sentiment="neutral",
                    status="active",
                )
            )
            logger.info(f"New conversation created: {new_conv.id}")
            return str(new_conv.id)
        except Exception as e:
            logger.error(f"Conversation creation failed: {e}")
            # Return the provided conversation_id as last resort
            return conversation_id or ""


    async def _save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        """Persist a single message to conversation_messages table."""
        if not conversation_id or not content:
            return
        content = sanitize_text(content)
        safe_metadata = sanitize_dict_strings(metadata or {})
        try:
            await self._message_svc.create_message(
                ConversationMessageCreate(
                    conversation_id=UUID(conversation_id),
                    role=role,
                    message=content,
                    metadata_=safe_metadata,
                )
            )
        except Exception as e:
            logger.warning(f"Message DB write failed ({role}): {e}")
            try:
                await self.db.rollback()
            except Exception as rb_err:
                logger.warning(f"Session rollback after message failure: {rb_err}")

    async def _update_conversation_sentiment(
        self,
        conversation_id: str,
        sentiment: str,
    ) -> None:
        """Update the conversation's detected sentiment in DB."""
        try:
            await self._conversation_svc.update_conversation(
                conversation_id,
                ConversationUpdate(sentiment=sentiment),
            )
        except Exception as e:
            logger.warning(f"Conversation sentiment update failed: {e}")
            try:
                await self.db.rollback()
            except Exception:
                pass

    async def _write_audit_log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        agent_name: str,
        details: dict,
    ) -> None:
        """Write an entry to the audit_logs table."""
        try:
            await self._audit_svc.create_audit_log(
                AuditLogCreate(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    agent_name=agent_name,
                    details=details,
                )
            )
        except Exception as e:
            logger.warning(f"Audit log write failed: {e}")
            try:
                await self.db.rollback()
            except Exception:
                pass
