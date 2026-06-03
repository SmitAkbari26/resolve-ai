"""
Resolve AI - Chat Router

The PRIMARY endpoint the frontend calls for all chat interactions.

POST /api/v1/chat/message
    → Runs full multi-agent workflow
    → Returns AI response + full trace

POST /api/v1/chat/resume/{workflow_id}
    → Resumes a paused workflow after human approval
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import uuid
from datetime import datetime, date

from db.database import get_db, async_session_factory
from services.chat_service import ChatService
from services.workflow_service import WorkflowService
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# ─── Request / Response Models ─────────────────────────────

class ChatMessageRequest(BaseModel):
    user_id: str
    user_email: str = ""
    message: str
    conversation_id: str | None = None   # None = start new conversation


class ChatMessageResponse(BaseModel):
    conversation_id: str
    workflow_id: str | None
    status: str                           # completed | paused | failed
    ai_response: str
    ticket_id: str | None = None
    approval_id: str | None = None
    requires_approval: bool = False
    approval_reason: str = ""
    detected_category: str | None = None
    detected_sentiment: str | None = None
    urgency: str | None = None
    severity: str | None = None
    plan: list[str] = []
    agent_trace: list[dict] = []
    runtime_events: list[dict] = []
    tool_calls: list[dict] = []


class ChatResumeRequest(BaseModel):
    approval_decision: str   # "approved" | "rejected"
    decided_by: str = "system"


# ─── Endpoints ─────────────────────────────────────────────

@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Main chat endpoint — called by the frontend for every user message.

    Flow:
      1. Creates / retrieves conversation in DB
      2. Saves user message to DB
      3. Runs multi-agent workflow:
           ConversationAgent → PlannerAgent → [retrieval → decision →
           ticket → approval → notification] (dynamically planned)
      4. Updates conversation sentiment in DB
      5. Saves AI response to DB
      6. Writes audit log
      7. Returns structured response

    If the workflow is paused (requires human approval), status="paused"
    and the caller should display the approval message to the user, then
    use POST /chat/resume/{workflow_id} after approval is granted.
    """
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    try:
        service = ChatService(db)
        result = await service.handle_message(
            user_id=payload.user_id,
            user_email=payload.user_email,
            user_message=payload.message.strip(),
            conversation_id=payload.conversation_id,
        )
        return result

    except Exception as ex:
        logger.error(f"Chat endpoint error: {ex}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/resume/{workflow_id}", response_model=ChatMessageResponse)
async def chat_resume(
    workflow_id: str,
    payload: ChatResumeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a paused workflow after a human approval decision.

    Call this endpoint AFTER the approver has reviewed the request.
    The workflow continues from the point it was paused (typically
    after ApprovalAgent, continuing into NotificationAgent).
    """
    if payload.approval_decision not in ("approved", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="approval_decision must be 'approved' or 'rejected'",
        )

    try:
        service = WorkflowService(db)
        result = await service.resume_workflow(
            workflow_id=workflow_id,
            approval_decision=payload.approval_decision,
            decided_by=payload.decided_by,
        )

        if result.get("status") == "failed":
            error = result.get("error", "")
            if "not found" in error or "expired" in error:
                raise HTTPException(status_code=404, detail=error)

        # Wrap into ChatMessageResponse shape
        return {
            "conversation_id": result.get("conversation_id", ""),
            "workflow_id":     result.get("workflow_id"),
            "status":          result.get("status", "completed"),
            "ai_response":     result.get("ai_response", ""),
            "ticket_id":       result.get("ticket_id"),
            "approval_id":     result.get("approval_id"),
            "requires_approval": result.get("requires_approval", False),
            "approval_reason": result.get("approval_reason", ""),
            "detected_category": result.get("detected_category"),
            "detected_sentiment": result.get("detected_sentiment"),
            "urgency":         result.get("urgency"),
            "severity":        result.get("severity"),
            "plan":            result.get("plan", []),
            "agent_trace":     result.get("agent_trace", []),
            "runtime_events":  result.get("runtime_events", []),
            "tool_calls":      result.get("tool_calls", []),
        }

    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Chat resume error: {ex}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/history/{conversation_id}")
async def chat_history(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Return all messages for a conversation (for the frontend chat window).
    Returns both user and assistant messages in chronological order.
    """
    from services.conversation_message_service import ConversationMessageService
    try:
        svc = ConversationMessageService(db)
        messages = await svc.get_messages_by_conversation_id(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id":         str(msg.id),
                    "role":       msg.role,
                    "content":    msg.message,
                    "metadata":   msg.metadata_,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket chat connection accepted")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            user_id = payload.get("user_id")
            user_email = payload.get("user_email", "")
            message = payload.get("message")
            conversation_id = payload.get("conversation_id")

            if not user_id or not message:
                await websocket.send_json({"error": "user_id and message are required"})
                continue

            async with async_session_factory() as db:
                try:
                    async def stream_callback(chunk: str):
                        try:
                            await websocket.send_text(json.dumps({
                                "type": "chunk",
                                "delta": chunk
                            }))
                        except Exception as send_ex:
                            logger.warning(f"Failed to send stream chunk: {send_ex}")

                    service = ChatService(db)
                    result = await service.handle_message(
                        user_id=user_id,
                        user_email=user_email,
                        user_message=message.strip(),
                        conversation_id=conversation_id,
                        stream_callback=stream_callback,
                    )
                    await db.commit()
                    # Use custom encoder to handle UUID, datetime, etc.
                    import uuid
                    from datetime import date

                    def _default_encoder(obj):
                        if isinstance(obj, uuid.UUID):
                            return str(obj)
                        if isinstance(obj, (datetime, date)):
                            return obj.isoformat()
                        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

                    await websocket.send_text(json.dumps(result, default=_default_encoder))
                except Exception as db_ex:
                    await db.rollback()
                    logger.error(f"Error handling WebSocket message: {db_ex}", exc_info=True)
                    await websocket.send_text(json.dumps({"error": str(db_ex)}))

    except WebSocketDisconnect:
        logger.info("WebSocket chat connection closed by client")
    except Exception as ex:
        logger.error(f"WebSocket unhandled error: {ex}", exc_info=True)
