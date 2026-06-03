"""
Resolve AI - Ticket Agent
Creates or updates support tickets through the MCP runtime.
"""

import json

import httpx

from agents.base_agent import BaseAgent
from config import API_HOST, API_PORT, API_PREFIX
from prompts.ticket_prompt import build_ticket_prompt
from utils.logger import get_logger
from utils.ticket_messages import format_ticket_created_reply

logger = get_logger(__name__)


def _parse_tool_payload(result: dict) -> dict:
    """Normalize MCP tool call responses into a flat ticket dict."""
    if not isinstance(result, dict):
        return {}

    # JSON-RPC wrapper
    if "result" in result and isinstance(result["result"], dict):
        inner = result["result"]
        if "content" in inner:
            return _parse_tool_payload(inner)
        if inner.get("id") or inner.get("ticket_id"):
            return inner
        if "data" in inner and isinstance(inner["data"], dict):
            return inner["data"]

    content = result.get("content", [])
    if content and isinstance(content, list):
        first = content[0]
        if isinstance(first, dict):
            if first.get("type") == "json":
                return first.get("data", {}) or {}
            if first.get("type") == "text":
                try:
                    return json.loads(first.get("text", "")) or {}
                except json.JSONDecodeError:
                    return {}

    if result.get("id") or result.get("ticket_id"):
        return result

    return {}


class TicketAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    async def process(self, state: dict) -> dict:
        if "runtime_events" not in state:
            state["runtime_events"] = []
        if "tool_calls" not in state:
            state["tool_calls"] = []

        action = state.get("recommended_action", "create_ticket")
        if state.get("ticket_id") and action == "create_ticket":
            action = "update_ticket"

        if action in ("none", "auto_resolve", "escalate"):
            return state

        state["runtime_events"].append(
            {"type": "ticket_agent_started", "action": action}
        )

        try:
            # Bypass LLM step: execute tool directly to save 20-30s of response time
            if action == "create_ticket":
                await self._create_ticket_direct(state)
                if not state.get("ticket_id"):
                    await self._create_ticket_via_http(state)
            elif action == "update_ticket" and state.get("ticket_id"):
                await self._update_ticket_direct(state)
        except Exception as e:
            logger.error(f"Ticket agent processing failed: {e}")
            state["runtime_events"].append(
                {"type": "ticket_agent_failed", "error": str(e)}
            )

        if state.get("ticket_id"):
            state["recommended_action"] = "none"
        elif action in ("create_ticket", "update_ticket"):
            logger.error(
                f"Ticket agent finished without ticket_id (action={action})"
            )

        return state

    async def _create_ticket_direct(self, state: dict) -> None:
        category = str(state.get("detected_category", "general")).lower()
        if category not in (
            "authentication",
            "billing",
            "technical",
            "refund",
            "general",
            "account",
        ):
            category = "general"

        priority = str(
            state.get("severity") or state.get("urgency") or "medium"
        ).lower()
        if priority not in ("low", "medium", "high", "critical"):
            priority = "medium"

        args = {
            "category": category,
            "priority": priority,
            "summary": (state.get("query_summary") or state.get("user_query", ""))[
                :200
            ],
            "description": state.get("user_query", ""),
            "user_id": state.get("user_id") or None,
            "conversation_id": state.get("conversation_id") or None,
        }

        try:
            result = await self.mcp.execute_tool("create_ticket", args)
            if "error" in str(result).lower():
                logger.error(f"Direct create_ticket failed: {result}")
                state["runtime_events"].append(
                    {"type": "ticket_direct_create_failed", "error": str(result)}
                )
                return

            payload = _parse_tool_payload({"result": result.get("result", result)})
            ticket_id = payload.get("id") or payload.get("ticket_id")
            if not ticket_id:
                logger.error(f"Direct create_ticket missing id: {result}")
                return

            state["ticket_id"] = str(ticket_id)
            state["ticket"] = payload
            state["ai_response"] = format_ticket_created_reply(payload)
            state["runtime_events"].append(
                {
                    "type": "ticket_processed_direct",
                    "ticket_id": ticket_id,
                    "action": "create_ticket",
                }
            )
            logger.info(f"Ticket created directly: {ticket_id}")
        except Exception as e:
            logger.exception(f"Direct ticket creation failed: {e}")

    async def _create_ticket_via_http(self, state: dict) -> None:
        """Fallback when MCP subprocess is unavailable."""
        category = str(state.get("detected_category", "general")).lower()
        if category not in (
            "authentication",
            "billing",
            "technical",
            "refund",
            "general",
            "account",
        ):
            category = "general"

        priority = str(
            state.get("severity") or state.get("urgency") or "medium"
        ).lower()
        if priority not in ("low", "medium", "high", "critical"):
            priority = "medium"

        user_id = state.get("user_id")
        if not user_id:
            logger.error("Cannot create ticket via HTTP — missing user_id")
            return

        payload = {
            "user_id": user_id,
            "conversation_id": state.get("conversation_id"),
            "category": category,
            "priority": priority,
            "summary": (state.get("query_summary") or state.get("user_query", ""))[
                :200
            ],
            "description": state.get("user_query", ""),
        }

        host = API_HOST if API_HOST not in ("0.0.0.0", "") else "127.0.0.1"
        url = f"http://{host}:{API_PORT}{API_PREFIX}/tickets"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            ticket_id = data.get("id")
            if not ticket_id:
                logger.error(f"HTTP create_ticket missing id: {data}")
                return

            state["ticket_id"] = str(ticket_id)
            state["ticket"] = data
            state["ai_response"] = format_ticket_created_reply(data)
            state["runtime_events"].append(
                {
                    "type": "ticket_processed_http",
                    "ticket_id": str(ticket_id),
                    "action": "create_ticket",
                }
            )
            logger.info(f"Ticket created via HTTP API: {ticket_id}")
        except Exception as e:
            logger.exception(f"HTTP ticket creation failed: {e}")
            state["runtime_events"].append(
                {"type": "ticket_http_create_failed", "error": str(e)}
            )

    async def _update_ticket_direct(self, state: dict) -> None:
        ticket_id = state.get("ticket_id")
        if not ticket_id:
            return

        priority = str(
            state.get("severity") or state.get("urgency") or "medium"
        ).lower()
        if priority not in ("low", "medium", "high", "critical"):
            priority = "medium"

        status = "pending_approval" if state.get("requires_approval") else "in_progress"

        args = {
            "ticket_id": str(ticket_id),
            "status": status,
            "priority": priority,
            "description": state.get("user_query", ""),
            "resolution": state.get("ai_response", ""),
        }

        try:
            result = await self.mcp.execute_tool("update_ticket", args)
            payload = _parse_tool_payload({"result": result.get("result", result)})
            if payload:
                state["ticket"] = payload
            state["runtime_events"].append(
                {
                    "type": "ticket_updated_direct",
                    "ticket_id": ticket_id,
                }
            )
            logger.info(f"Ticket updated directly: {ticket_id}")
        except Exception as e:
            logger.exception(f"Direct ticket update failed: {e}")
