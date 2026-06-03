"""
Resolve AI - Decision Agent
Analyzes customer issue severity,
resolution strategy,
approval requirements,
and workflow actions.
"""

import json
import re
from prompts.decision_prompt import DECISION_PROMPT
from agents.base_agent import BaseAgent
from utils.llm_json import extract_json_object, pick_str
from utils.intent import classify_query_intent
from utils.ticket_messages import format_ticket_status_reply

from config import (
    MAX_AUTO_RESOLVE_SEVERITY,
)

from utils.helpers import (
    severity_to_int,
)

from utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


class DecisionAgent(BaseAgent):

    async def process(self, state: dict) -> dict:

        # =================================================
        # INPUTS
        # =================================================

        user_query = state.get(
            "user_query",
            "",
        )

        category = state.get(
            "detected_category",
            "general",
        )

        sentiment = state.get(
            "detected_sentiment",
            "neutral",
        )

        context_text = state.get(
            "context_text",
            "No context available.",
        )

        entities = state.get(
            "extracted_entities",
            [],
        )

        # =================================================
        # INITIALIZE
        # =================================================

        if "runtime_events" not in state:

            state["runtime_events"] = []

        # =================================================
        # RUNTIME EVENT
        # =================================================

        state["runtime_events"].append(
            {
                "type": "decision_started",
                "category": category,
            }
        )

        history_text = state.get("history_text", "No previous conversation.")
        ticket_obj = state.get("ticket") or {}
        existing_ticket = (
            json.dumps(ticket_obj, indent=2) if ticket_obj else "No existing ticket."
        )

        query_intent = state.get("query_intent") or classify_query_intent(
            user_query,
            has_history=bool(history_text and "No previous" not in history_text),
            has_ticket=bool(state.get("ticket_id") or ticket_obj),
        )

        # Fast path: ticket already exists and user asks for status/ETA/details
        if state.get("ticket_id") and query_intent == "informational":
            state["severity"] = "medium"
            state["severity_score"] = 0.5
            state["recommended_action"] = "auto_resolve"
            state["requires_approval"] = False
            state["ai_response"] = format_ticket_status_reply(ticket_obj, user_query)
            state["status"] = "completed"
            state["runtime_events"].append(
                {
                    "type": "decision_completed_fast",
                    "recommended_action": "auto_resolve",
                }
            )
            logger.info("Decision | Fast informational response from existing ticket")
            return state

        prompt = DECISION_PROMPT.format(
            user_query=user_query,
            category=category,
            sentiment=sentiment,
            entities=json.dumps(entities),
            context_text=context_text[:4000],
            history_text=history_text,
            existing_ticket=existing_ticket,
        )

        # =================================================
        # LLM EXECUTION
        # =================================================

        try:

            response_data = await self.invoke_llm(prompt, state=state, json_mode=True)
            decision = extract_json_object(response_data.get("content", ""))
            if not decision:
                raise ValueError("LLM returned invalid JSON")

        except Exception as e:

            logger.warning(f"Decision parsing failed: {e}")

            if state.get("ticket_id"):
                decision = {
                    "confidence_score": 0.5,
                    "severity": "medium",
                    "severity_score": 0.5,
                    "can_auto_resolve": True,
                    "recommended_action": "auto_resolve",
                    "requires_approval": False,
                    "approval_reason": "",
                    "ai_response": format_ticket_status_reply(
                        ticket_obj, user_query
                    ),
                    "resolution_notes": "Fallback: existing ticket informational.",
                    "reasoning": "Decision parsing failure.",
                }
            else:
                decision = {
                    "confidence_score": 0.5,
                    "severity": "medium",
                    "severity_score": 0.5,
                    "can_auto_resolve": False,
                    "recommended_action": "create_ticket",
                    "requires_approval": False,
                    "approval_reason": "",
                    "ai_response": (
                        "I'll open a support ticket so our team can investigate."
                    ),
                    "resolution_notes": "Fallback decision logic.",
                    "reasoning": "Decision parsing failure.",
                }

        # =================================================
        # BUSINESS RULES
        # =================================================

        severity = pick_str(decision, "severity", default="medium").lower()

        severity_score = decision.get(
            "severity_score",
            0.5,
        )

        # Determine action: create new ticket or update existing one
        recommended_action = pick_str(
            decision, "recommended_action", default="create_ticket"
        ).lower()
        if state.get("ticket_id") and recommended_action == "create_ticket":
            recommended_action = "auto_resolve" if query_intent == "informational" else "update_ticket"

        requires_approval = decision.get(
            "requires_approval",
            False,
        )

        # =============================================
        # AUTO RESOLVE LIMITS
        # =============================================

        if severity_to_int(severity) > severity_to_int(MAX_AUTO_RESOLVE_SEVERITY):
            if state.get("ticket_id"):
                recommended_action = "update_ticket"
            else:
                recommended_action = "create_ticket"

        # =============================================
        # CRITICAL ISSUES
        # =============================================

        if severity == "critical":
            if state.get("ticket_id"):
                recommended_action = "update_ticket"
            else:
                recommended_action = "escalate"
            requires_approval = True

        # =============================================
        # REFUND APPROVALS
        # =============================================

        if category in (
            "refund",
            "payment",
            "billing",
        ):

            if severity in (
                "high",
                "critical",
            ):

                requires_approval = True

        # =================================================
        # STORE IN STATE
        # =================================================

        state["severity"] = severity

        state["severity_score"] = severity_score

        # Confidence score from LLM
        try:
            confidence_score = float(decision.get("confidence_score", 0.9))
        except (TypeError, ValueError):
            confidence_score = 0.9
        state["confidence_score"] = confidence_score

        state["recommended_action"] = recommended_action

        state["requires_approval"] = requires_approval

        state["approval_reason"] = decision.get(
            "approval_reason",
            "",
        )

        # Get the AI response — the LLM outputs "ai_response" not "message"
        ai_response = (
            decision.get("ai_response")
            or decision.get("message")
            or decision.get("response_to_customer")
            or decision.get("response")
            or ""
        )
        if not ai_response.strip():
            if state.get("ticket_id"):
                ai_response = format_ticket_status_reply(ticket_obj, user_query)
            elif recommended_action == "create_ticket":
                ai_response = (
                    "I'll open a support ticket so our team can investigate."
                )
            else:
                ai_response = "Thanks — I'm processing your request now."

        # Never expose fabricated ticket IDs (e.g. TCK-20231001-001)
        if "TCK-" in ai_response and not state.get("ticket_id"):
            ai_response = (
                "I'm preparing your support ticket now. "
                "You'll receive the real ticket ID in my next message."
            )

        state["ai_response"] = ai_response

        state["resolution_notes"] = decision.get(
            "resolution_notes",
            "",
        )

        state["decision_reasoning"] = decision.get(
            "reasoning",
            "",
        )

        # =================================================
        # AUTO COMPLETE
        # =================================================

        if recommended_action == "auto_resolve":

            state["status"] = "completed"

        # =================================================
        # RUNTIME EVENT
        # =================================================

        state["runtime_events"].append(
            {
                "type": "decision_completed",
                "severity": severity,
                "recommended_action": (recommended_action),
                "requires_approval": (requires_approval),
            }
        )

        logger.info(
            f"Decision | Severity={severity} | Action={recommended_action} | "
            f"Approval={requires_approval} | Confidence={confidence_score:.2f}"
        )

        return state
