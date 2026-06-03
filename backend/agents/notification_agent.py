"""
Resolve AI - Notification Agent
Sends customer and support team notifications via MCP.
Also persists notification records to the DB via MCP tool.

Uses real user_email from state (populated during conversation setup).
Falls back gracefully if email is unavailable.
"""

from agents.base_agent import BaseAgent
from prompts.notification_prompt import build_notification_prompt
from config import SLACK_WEBHOOK_URL
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    async def process(self, state: dict) -> dict:
        # Skip slow LLM+tools when notifications aren't configured or not needed
        if state.get("skip_notifications"):
            state["notifications"] = []
            return state

        ticket_id = state.get("ticket_id", "N/A")
        ai_response = state.get("ai_response", "")
        category = state.get("detected_category", "general")
        severity = state.get("severity", "medium")
        user_id = state.get("user_id", "")
        conversation_id = state.get("conversation_id", "")
        user_email = state.get("user_email", "")

        if "runtime_events" not in state:
            state["runtime_events"] = []

        if "tool_calls" not in state:
            state["tool_calls"] = []

        notifications_sent = []

        if not ticket_id or ticket_id == "N/A":
            logger.info("Notification skipped — no ticket in state")
            state["notifications"] = []
            return state

        if not user_email and not SLACK_WEBHOOK_URL:
            logger.info("Notification skipped — no email or Slack configured")
            state["notifications"] = []
            return state

        state["runtime_events"].append(
            {
                "type": "notification_started",
                "ticket_id": ticket_id,
            }
        )

        try:
            # 1. Send support email if ticket was created/escalated
            if ticket_id and ticket_id != "N/A":
                from agents.templates.support_email_template import build_support_email_template
                support_email_body = build_support_email_template(
                    category=category,
                    severity=severity,
                    user_id=user_id,
                    ticket_id=ticket_id,
                    query_summary=state.get("query_summary", "No summary available."),
                    ai_response=ai_response,
                )
                
                email_args = {
                    "to": "support-team@resolveai.com",
                    "subject": f"[{severity.upper()}] Ticket {ticket_id} — {category}",
                    "body": support_email_body
                }
                
                try:
                    result = await self.mcp.execute_tool("send_email", email_args)
                    if result and "error" not in str(result).lower():
                        notifications_sent.append("email_support_team")
                        logger.info("Support email sent successfully")
                except Exception as ex:
                    logger.error(f"Failed to send support email: {ex}")

            # 2. Create notification record in DB
            if user_id and ai_response:
                import uuid
                ticket_uuid = None
                if ticket_id and ticket_id != "N/A":
                    try:
                        ticket_uuid = str(uuid.UUID(ticket_id))
                    except ValueError:
                        pass
                
                noti_args = {
                    "user_id": str(user_id),
                    "notification_type": "ticket_update",
                    "channel": "email",
                    "subject": "Update on your support request",
                    "message": ai_response,
                    "status": "pending"
                }
                if ticket_uuid:
                    noti_args["ticket_id"] = ticket_uuid
                    
                try:
                    result = await self.mcp.execute_tool("create_notification", noti_args)
                    if result and "error" not in str(result).lower():
                        notifications_sent.append("db_notification_record")
                        logger.info("Notification DB record created successfully")
                except Exception as ex:
                    logger.error(f"Failed to create notification record: {ex}")

        except Exception as e:
            logger.exception(f"Notification agent exception: {e}")

        # Store results
        state["notifications"] = notifications_sent
        state["runtime_events"].append(
            {
                "type": "notification_completed",
                "notifications_sent": notifications_sent,
            }
        )

        logger.info(f"Notifications sent: {notifications_sent}")
        return state
