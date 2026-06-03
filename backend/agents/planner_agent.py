"""
Resolve AI - Planner Agent

Reads pre-analyzed state from ConversationAgent and decides:
  1. Whether the AI can directly answer (simple queries)
  2. Which agents to run and in what order (complex workflows)

Planner does NOT re-analyze sentiment/category/entities.
Those are already populated by ConversationAgent.
"""

import json
import re
from agents.base_agent import BaseAgent
from prompts.planner_prompt import build_planner_prompt
from utils.logger import get_logger
from utils.llm_json import extract_json_object
from utils.ticket_messages import format_ticket_status_reply

logger = get_logger(__name__)


class PlannerAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    async def process(self, state: dict) -> dict:

        category = state.get("detected_category", "general")
        urgency = state.get("urgency", "medium")
        query_intent = state.get("query_intent", "general")

        # Rule-based fast plan — skip LLM for common follow-ups
        if query_intent == "informational" and state.get("ticket_id"):
            ticket = state.get("ticket") or {}
            state["plan"] = ["decision_agent"]
            state["reasoning"] = "Existing ticket — informational update only"
            state["status"] = "running"
            state["current_agent_index"] = 0
            state["ai_response"] = format_ticket_status_reply(
                ticket, state.get("user_query", "")
            )
            if "runtime_events" not in state:
                state["runtime_events"] = []
            state["runtime_events"].append(
                {
                    "type": "planner_completed",
                    "plan": state["plan"],
                    "category": category,
                    "urgency": urgency,
                    "direct_response": False,
                    "fast_path": True,
                }
            )
            logger.info(f"Planner | Fast path | Plan={state['plan']}")
            return state

        if state.get("ticket_id") and query_intent not in ("operational",):
            state["plan"] = ["decision_agent"]
            state["reasoning"] = "Ticket exists — avoid duplicate ticket creation"
            state["status"] = "running"
            state["current_agent_index"] = 0
            if "runtime_events" not in state:
                state["runtime_events"] = []
            state["runtime_events"].append(
                {
                    "type": "planner_completed",
                    "plan": state["plan"],
                    "category": category,
                    "urgency": urgency,
                    "fast_path": True,
                }
            )
            logger.info(f"Planner | Ticket exists | Plan={state['plan']}")
            return state

        prompt = build_planner_prompt(state=state)

        # =================================================
        # LLM EXECUTION
        # =================================================

        try:

            response_data = await self.invoke_llm(prompt, json_mode=True)
            result = extract_json_object(response_data.get("content", ""))
            if not result:
                raise ValueError("LLM returned invalid JSON")

        except Exception as e:

            logger.warning(f"Planner LLM failed: {e}")

            # Sensible fallback based on pre-analyzed urgency
            if urgency in ("high", "critical") or category in (
                "refund",
                "billing",
                "payment",
                "technical",
                "account",
            ):
                result = {
                    "plan": [
                        "decision_agent",
                        "ticket_agent",
                        "notification_agent",
                    ],
                    "reasoning": "Fallback: high-urgency workflow",
                }
            else:
                result = {
                    "plan": [
                        "decision_agent",
                        "ticket_agent",
                    ],
                    "reasoning": "Fallback: decision then ticket",
                }

        # =================================================
        # VALIDATE PLAN
        # =================================================

        valid_agents = {
            "decision_agent",
            "ticket_agent",
            "approval_agent",
            "notification_agent",
        }

        raw_plan = result.get("plan", [])

        if not isinstance(raw_plan, list):
            raw_plan = []

        validated_plan = [a for a in raw_plan if a in valid_agents]
        if validated_plan and "decision_agent" not in validated_plan:
            validated_plan.insert(0, "decision_agent")

        # Trim plan for speed
        if state.get("ticket_id"):
            validated_plan = [
                a
                for a in validated_plan
                if a not in ("ticket_agent", "notification_agent")
            ] or ["decision_agent"]
        elif not state.get("user_email"):
            validated_plan = [a for a in validated_plan if a != "notification_agent"]

        # New issue: always include ticket_agent after decision
        if not state.get("ticket_id") and "decision_agent" in validated_plan:
            if "ticket_agent" not in validated_plan:
                idx = validated_plan.index("decision_agent")
                validated_plan.insert(idx + 1, "ticket_agent")

        state["plan"] = validated_plan
        state["reasoning"] = result.get("reasoning", "")
        state["current_agent_index"] = 0

        # =================================================
        # DIRECT RESPONSE
        # =================================================

        ai_response = result.get("ai_response", "")

        if isinstance(ai_response, str) and ai_response.strip():
            state["ai_response"] = ai_response
            state["status"] = "completed"
            state["plan"] = []

        elif not validated_plan:
            state["status"] = "completed"

        else:
            state["status"] = "running"

        # =================================================
        # RUNTIME EVENT
        # =================================================

        if "runtime_events" not in state:
            state["runtime_events"] = []

        state["runtime_events"].append(
            {
                "type": "planner_completed",
                "plan": validated_plan,
                "category": category,
                "urgency": urgency,
                "direct_response": bool(
                    isinstance(ai_response, str) and ai_response.strip()
                ),
            }
        )

        logger.info(
            f"Planner | "
            f"Category={category} | "
            f"Urgency={urgency} | "
            f"Plan={validated_plan}"
        )

        return state
