import json
from datetime import datetime
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.llm_json import extract_json_object, pick_str, pick_bool

logger = get_logger(__name__)

RESOLVE_AGENT_PROMPT = """You are Resolve AI, an agentic customer support specialist.
Resolve the customer inquiry using the tools provided.

Query: {user_query}
User ID: {user_id}
Conversation ID: {conversation_id}
Category: {category} | Sentiment: {sentiment} | Urgency: {urgency}
KB Context: {context_text}
History: {history_text}
Ticket: {existing_ticket}

Available Support Agents for Assignment:
{available_agents_text}

RULES:
1. Use tools to search KB, create/update tickets, create approvals, send notifications as needed.
2. For critical/high-severity issues: create ticket + create approval.
3. For informational queries with existing ticket: check status, respond directly.
4. Do NOT fabricate IDs — use real IDs returned by tools.
5. When creating or updating a ticket, ALWAYS assign one of the available support agents above
   based on the ticket category and severity. Pick the best match from the list.
   If no agents are listed, leave assigned_agent as null.

After executing tools, return JSON:
{{"ai_response":"empathetic reply to user","recommended_action":"create_ticket|update_ticket|escalate|auto_resolve","requires_approval":false,"approval_reason":"","severity":"low|medium|high|critical","resolution_notes":"details","assigned_agent":"agent name or null"}}
"""

class ResolveAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "resolve_agent"

    @property
    def description(self) -> str:
        return "Resolves customer support inquiries by executing tools in a loop."

    async def process(self, state: dict) -> dict:
        user_query = state.get("user_query", "").strip()
        category = state.get("detected_category", "general")
        sentiment = state.get("detected_sentiment", "neutral")
        urgency = state.get("urgency", "medium")
        context_text = state.get("context_text", "No context available.")
        history_text = state.get("history_text", "No previous conversation.")
        
        ticket_obj = state.get("ticket") or {}
        existing_ticket = (
            json.dumps(ticket_obj, indent=2) if ticket_obj else "No existing ticket."
        )

        # Format available agents for the prompt
        available_agents = state.get("available_agents", [])
        if available_agents:
            available_agents_text = "\n".join(
                f"- {a['name']} (type: {a['agent_type']}, {a['description'] or 'General support'})"
                for a in available_agents
            )
        else:
            available_agents_text = "No agents currently registered in the system."

        prompt = RESOLVE_AGENT_PROMPT.format(
            user_query=user_query,
            user_id=state.get("user_id", ""),
            conversation_id=state.get("conversation_id", ""),
            category=category,
            sentiment=sentiment,
            urgency=urgency,
            context_text=context_text[:1500],
            history_text=history_text,
            existing_ticket=existing_ticket,
            available_agents_text=available_agents_text,
        )

        if "runtime_events" not in state:
            state["runtime_events"] = []
        if "tool_calls" not in state:
            state["tool_calls"] = []

        state["runtime_events"].append({
            "type": "resolve_agent_started",
            "timestamp": datetime.utcnow().isoformat(),
        })

        allowed_tools = [
            "create_ticket",
            "update_ticket",
            "get_ticket",
            "get_tickets_by_conversation",
            "create_approval",
            "get_approval",
            "update_approval",
            "get_approvals_by_ticket",
            "create_notification",
            "send_email",
            "get_user_notifications",
            "create_escalation",
            "get_escalation",
            "get_ticket_escalations",
            "update_escalation",
            "get_knowledge_document",
            "list_knowledge_documents",
        ]

        try:
            logger.info("ResolveAgent | Sending prompt to LLM with tools enabled")
            response = await self.invoke_llm(
                prompt,
                state=state,
                tools_enabled=True,
                allowed_tool_names=allowed_tools,
                json_mode=False,
                max_turns=5
            )

            result_content = response.get("content") or "{}"
            result = extract_json_object(result_content)

            # Store the tool calls executed during LLM loop in state
            executed_tool_calls = response.get("tool_calls", [])
            state["tool_calls"].extend(executed_tool_calls)

            # Parse results and update state dynamically based on executed tools
            for tc in executed_tool_calls:
                tool_name = tc.get("tool")
                tool_res = tc.get("result")
                # Normalize tool_res to extract payload
                if isinstance(tool_res, dict):
                    # Unwrap JSON-RPC if present
                    inner = tool_res.get("result", tool_res)
                    if isinstance(inner, dict) and "data" in inner:
                        inner = inner["data"]
                    
                    if tool_name == "create_ticket":
                        ticket_id = inner.get("id") or inner.get("ticket_id")
                        if ticket_id:
                            state["ticket_id"] = str(ticket_id)
                            state["ticket"] = inner
                            logger.info(f"ResolveAgent | Ticket created: {ticket_id}")
                    elif tool_name == "update_ticket":
                        ticket_id = inner.get("id") or inner.get("ticket_id") or state.get("ticket_id")
                        if ticket_id:
                            state["ticket_id"] = str(ticket_id)
                            state["ticket"] = inner
                            logger.info(f"ResolveAgent | Ticket updated: {ticket_id}")
                    elif tool_name == "create_approval":
                        approval_id = inner.get("id") or inner.get("approval_id")
                        if approval_id:
                            state["approval_id"] = str(approval_id)
                            state["approval_status"] = "pending"
                            state["requires_approval"] = True
                            state["status"] = "paused"
                            logger.info(f"ResolveAgent | Approval request created: {approval_id}")

            state["severity"] = pick_str(result, "severity", default="medium")
            state["recommended_action"] = pick_str(result, "recommended_action", default="auto_resolve")

            # Capture assigned_agent from LLM result and sync to state
            llm_assigned_agent = pick_str(result, "assigned_agent", default="")
            if llm_assigned_agent:
                state["assigned_agent"] = llm_assigned_agent
                # If we have a ticket in state, reflect the assignment
                if state.get("ticket") and isinstance(state["ticket"], dict):
                    state["ticket"]["assigned_agent"] = llm_assigned_agent

            # If a tool call or the LLM output indicates requires_approval, set paused status
            if pick_bool(result, "requires_approval", default=False) or state.get("requires_approval"):
                state["requires_approval"] = True
                state["status"] = "paused"
                state["approval_reason"] = pick_str(result, "approval_reason", default="")
            
            state["ai_response"] = pick_str(result, "ai_response", default="")
            state["resolution_notes"] = pick_str(result, "resolution_notes", default="")

        except Exception as e:
            logger.exception(f"ResolveAgent processing failed: {e}")
            state["status"] = "failed"
            state["error"] = str(e)

        state["runtime_events"].append({
            "type": "resolve_agent_completed",
            "timestamp": datetime.utcnow().isoformat(),
        })

        return state
