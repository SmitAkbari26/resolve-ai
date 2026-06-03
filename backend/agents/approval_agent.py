"""
Resolve AI - Approval Agent
Handles human approval workflows, workflow pausing,
approval persistence to PostgreSQL via MCP,
and approval lifecycle management.
"""

from agents.base_agent import BaseAgent
from prompts.approval_prompt import APPROVAL_PROMPT
from utils.helpers import generate_id
from utils.logger import get_logger

logger = get_logger(__name__)


class ApprovalAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    async def process(self, state: dict) -> dict:
        if "runtime_events" not in state:
            state["runtime_events"] = []

        if "tool_calls" not in state:
            state["tool_calls"] = []

        requires_approval = state.get("requires_approval", False)
        if not requires_approval:
            logger.info("Approval not required — skipping")
            state["runtime_events"].append({"type": "approval_skipped"})
            return state

        state["runtime_events"].append({"type": "approval_started"})

        try:
            approval_type = self._determine_approval_type(state)
            approval_reason = state.get("approval_reason", "Requires human review")

            args = {
                "ticket_id": state.get("ticket_id", ""),
                "approval_type": approval_type,
                "reason": approval_reason,
            }

            approval_id = None
            mcp_success = False

            try:
                result = await self.mcp.execute_tool("create_approval", args)
                if result and "error" not in str(result).lower():
                    mcp_success = True
                    if isinstance(result, dict):
                        inner = result.get("result", result)
                        content = inner.get("content", [])
                        if content and isinstance(content, list):
                            first = content[0]
                            if isinstance(first, dict) and first.get("type") == "json":
                                payload = first.get("data", {})
                                if isinstance(payload, dict):
                                    approval_id = payload.get("id") or payload.get("approval_id")
            except Exception as tool_ex:
                logger.error(f"Direct create_approval tool call failed: {tool_ex}")

            # Fallback to a generated ID if MCP didn't return one
            if not approval_id:
                approval_id = generate_id("APR")
                logger.warning(
                    f"MCP did not return approval ID — using generated: {approval_id}"
                )

            # Pause workflow
            state["approval_id"] = approval_id
            state["status"] = "paused"
            state["ai_response"] = (
                f"Your request requires human approval.\n\n"
                f"Approval ID: {approval_id}\n\n"
                f"Our team will review your request shortly. "
                f"You will be notified once a decision is made."
            )

            state["runtime_events"].append(
                {
                    "type": "approval_created",
                    "approval_id": approval_id,
                    "approval_type": approval_type,
                    "mcp_success": mcp_success,
                }
            )

            logger.info(
                f"Workflow paused | Approval={approval_id} | Type={approval_type} | MCP={'OK' if mcp_success else 'FALLBACK'}"
            )

        except Exception as e:
            logger.error(f"Approval agent failed: {e}")
            state["runtime_events"].append(
                {
                    "type": "approval_failed",
                    "error": str(e),
                }
            )
            state["status"] = "failed"
            state["error"] = str(e)

        return state

    def _determine_approval_type(self, state: dict) -> str:

        category = state.get("detected_category", "").lower()
        severity = state.get("severity", "medium")

        if category in ("refund", "payment", "billing"):
            return "refund_approval"

        if severity == "critical":
            return "critical_escalation"

        if category in ("account", "security"):
            return "account_action_approval"

        return "general_approval"
