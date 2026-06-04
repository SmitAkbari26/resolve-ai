import json
from datetime import datetime

from agents.base_agent import BaseAgent
from db.memory_store import (
    get_conversation_memory,
    append_message,
    get_conversation_summary,
    store_conversation_summary,
)
from rag.pipeline import RAGPipeline
from utils.logger import get_logger
from utils.llm_json import extract_json_object, pick_bool, pick_str
from utils.intent import (
    classify_query_intent_tier1,
    is_context_question,
    is_greeting,
)
from utils.support_responses import (
    CAPABILITIES_RESPONSE,
    build_conversation_summary,
    fallback_response,
    login_troubleshooting_response,
    thanks_response,
)
from utils.text_sanitize import plain_chat_text
from utils.ticket_messages import format_ticket_status_reply
from prompts.conversation_prompt import CONVERSATION_PROMPT

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────
# Intent classification helpers — avoids LLM call for trivials
# ─────────────────────────────────────────────────────────────

_NO_RAG_INTENTS = frozenset(
    {
        "greeting",
        "name",
        "thanks",
        "capabilities",
        "conversation_summary",
        "login_help",
        "auth_guidance",
    }
)


def needs_rag(query: str, is_greet: bool, is_ctx: bool, query_intent: str) -> bool:
    """Determine if RAG retrieval is worthwhile for this query."""
    if query_intent == "product_guidance":
        return True
    elif is_greet or is_ctx or query_intent in _NO_RAG_INTENTS:
        return False
    else:
        return len(query.split()) >= 6


def build_history_text(history: list[dict], summary: str | None) -> str:
    """
    Build a compact history string.
    If there's a stored summary + recent messages, use that.
    Otherwise use raw recent messages.
    """
    if not history:
        return "No previous conversation."

    # Always include last 6 raw messages for recency
    recent_messages = history[-6:]
    recent_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" for msg in recent_messages
    )

    if summary and len(history) > 6:
        return f"[SUMMARY OF EARLIER CONVERSATION]\n{summary}\n\n[RECENT MESSAGES]\n{recent_text}"

    return f"[CONVERSATION]\n{recent_text}"


class ConversationAgent(BaseAgent):

    def __init__(self, mcp_client=None):
        super().__init__(mcp_client)
        self.rag = RAGPipeline()

    @property
    def name(self) -> str:
        return "conversation_agent"

    @property
    def description(self) -> str:
        return (
            "Understands customer query, "
            "maintains conversation context & memory, "
            "detects sentiment, extracts entities, "
            "and decides whether to answer directly or run a workflow."
        )

    async def process(self, state: dict) -> dict:

        user_query = state.get("user_query", "").strip()
        conversation_id = state.get("conversation_id", "")
        detected_category = state.get("detected_category", "general")
        urgency = state.get("urgency", "medium")

        if "runtime_events" not in state:
            state["runtime_events"] = []

        # ─── Load conversation memory ──────────────────────────────
        history = get_conversation_memory(conversation_id)
        summary = get_conversation_summary(conversation_id)
        history_text = build_history_text(history, summary)
        state["history_text"] = history_text

        # ─── Existing ticket context ───────────────────────────────
        existing_ticket = state.get("ticket", {})
        existing_ticket_text = (
            json.dumps(existing_ticket, indent=2)
            if existing_ticket
            else "No existing ticket."
        )

        # ─── Persist user message ──────────────────────────────────
        try:
            append_message(conversation_id, "user", user_query)
        except Exception as e:
            logger.warning(f"Memory append failed: {e}")

        state["runtime_events"].append(
            {
                "type": "conversation_agent_started",
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # ─── Smart tier routing ────────────────────────────────────
        is_greet = is_greeting(user_query)
        has_history = bool(history)
        has_ticket = bool(existing_ticket) or bool(state.get("ticket_id"))
        is_ctx = is_context_question(user_query, has_history, has_ticket)

        # Tier-1 fast-path: "greeting" or "thanks" decided instantly; everything
        # else is "general" as a safe placeholder.  The LLM (Tier 2) will
        # return the authoritative "intent" label in its JSON response below.
        tier1_intent = classify_query_intent_tier1(user_query)
        query_intent = tier1_intent or "general"
        state["query_intent"] = query_intent
        should_rag = needs_rag(user_query, is_greet, is_ctx, query_intent)
        q_lower = user_query.lower()

        def _finish_short_circuit(ai_response: str, event_type: str) -> dict:
            state["short_circuit"] = True
            state["workflow_status"] = "completed"
            state["status"] = "completed"
            state["ai_response"] = plain_chat_text(ai_response)
            state["runtime_events"].append(
                {"type": event_type, "timestamp": datetime.utcnow().isoformat()}
            )
            state["runtime_events"].append(
                {
                    "type": "conversation_agent_completed",
                    "sentiment": state.get("detected_sentiment", "neutral"),
                    "category": state.get("detected_category", "general"),
                    "urgency": state.get("urgency", "medium"),
                    "entity_count": len(state.get("extracted_entities", [])),
                    "short_circuit": True,
                    "rag_used": False,
                    "query_intent": query_intent,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return state

        # ─── Fast-path: simple greetings (skip LLM) ─────────────────
        if is_greet:
            state["detected_sentiment"] = "positive"
            state["detected_category"] = "general"
            state["urgency"] = "low"
            state["extracted_entities"] = []
            state["query_summary"] = user_query[:200]
            return _finish_short_circuit(
                "Hello! How can I assist you today?",
                "conversation_agent_short_circuit_greeting",
            )

        # Ticket status — answer from real DB ticket data (no LLM needed)
        if query_intent == "informational" and existing_ticket:
            state["detected_category"] = existing_ticket.get("category", "general")
            return _finish_short_circuit(
                format_ticket_status_reply(existing_ticket, user_query),
                "conversation_agent_short_circuit_ticket_info",
            )

        # ─── RAG retrieval (conditional) ───────────────────────────
        tenant_id = state.get("tenant_id")
        try:
            if should_rag:
                retrieval_result = await self.rag.retrieve_context(
                    query=user_query,
                    category=detected_category,
                    top_k=3,
                    tenant_id=tenant_id,
                )
                retrieved_context = [
                    {
                        "content": ctx.get("content", ""),
                        "source": ctx.get("source", ""),
                        "type": ctx.get("type", ""),
                        "relevance_score": ctx.get("relevance_score", 0),
                    }
                    for ctx in retrieval_result.all_context
                ]
                context_text = retrieval_result.context_text
                retrieval_count = len(retrieved_context)
            else:
                retrieved_context = []
                context_text = (
                    "Skipped — answerable from conversation history or ticket context."
                )
                retrieval_count = 0

        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            retrieved_context = []
            context_text = "RAG unavailable."
            retrieval_count = 0

        state["retrieved_context"] = retrieved_context
        state["context_text"] = context_text
        state["retrieval_count"] = retrieval_count

        logger.info(
            f"ConversationAgent | RAG={'yes' if should_rag else 'skipped'} | "
            f"Retrieved={retrieval_count} | Greeting={is_greet} | ContextQ={is_ctx}"
        )

        # ─── Build and run LLM prompt ─────────────────────────────
        try:
            prompt = CONVERSATION_PROMPT.format(
                user_query=user_query,
                detected_category=detected_category,
                urgency=urgency,
                history_text=history_text,
                existing_ticket=existing_ticket_text,
                retrieval_result=context_text,
                company_name=state.get("company_name", "our company"),
            )


            logger.info("ConversationAgent | Sending prompt to LLM")
            sc_response = await self.invoke_llm(prompt, state=state, json_mode=True)

            if not sc_response:
                raise ValueError("LLM returned empty response")

            sc_clean = sc_response.get("content") or ""
            result = extract_json_object(sc_clean)
            if not result:
                raise ValueError("No valid JSON in response")

            # ─── Populate state ────────────────────────────────────
            state["detected_sentiment"] = pick_str(
                result, "sentiment", default="neutral"
            )
            state["detected_category"] = pick_str(
                result, "category", default=detected_category
            )
            state["extracted_entities"] = result.get("entities") or []
            if not isinstance(state["extracted_entities"], list):
                state["extracted_entities"] = []
            state["urgency"] = pick_str(result, "urgency", default=urgency)
            state["query_summary"] = pick_str(
                result, "summary", default=user_query[:200]
            )

            # ─── Tier-2 intent (LLM-determined) ────────────────────
            # Override the Tier-1 placeholder with the LLM's authoritative
            # intent label.  Falls back to the Tier-1 result so greetings /
            # thanks are never accidentally overwritten with "general".
            query_intent = pick_str(result, "intent", default=tier1_intent or "general")
            state["query_intent"] = query_intent
            logger.info(f"ConversationAgent | Intent (LLM Tier-2): {query_intent}")

            # ─── Confidence score ───────────────────────────────────
            try:
                confidence_score = float(result.get("confidence_score", 0.9))
            except (TypeError, ValueError):
                confidence_score = 0.9
            state["confidence_score"] = confidence_score

            state["ai_response"] = plain_chat_text(
                pick_str(result, "answer", "message", "response", default="")
            )

            # ─── Routing: trust LLM short_circuit unless confidence is too low ──
            llm_short_circuit = pick_bool(result, "short_circuit", default=True)

            # If LLM confidence is < 0.65, escalate even if LLM said short_circuit=true
            if llm_short_circuit and confidence_score < 0.65:
                logger.info(
                    f"ConversationAgent | Low confidence ({confidence_score:.2f}) — "
                    f"escalating to workflow despite short_circuit=true"
                )
                llm_short_circuit = False
                state["ai_response"] = ""

            # Force short_circuit on intents that never need a workflow
            # query_intent is now LLM-determined — use it instead of keyword check
            if existing_ticket and query_intent != "login_help":
                llm_short_circuit = True

            state["short_circuit"] = llm_short_circuit

            if not state["ai_response"]:
                if state["short_circuit"] and existing_ticket:
                    state["ai_response"] = plain_chat_text(
                        format_ticket_status_reply(existing_ticket, user_query)
                    )
                elif state["short_circuit"]:
                    state["ai_response"] = plain_chat_text(
                        fallback_response(query_intent, user_query, history)
                    )
                else:
                    state["ai_response"] = ""

            if state["short_circuit"]:
                state["workflow_status"] = "completed"
                logger.info(
                    f"ConversationAgent | Short-circuit triggered | "
                    f"Confidence={confidence_score:.2f} | Reason: {result.get('reasoning')}"
                )
            else:
                logger.info(
                    f"ConversationAgent | Action required — passing to planner | "
                    f"Confidence={confidence_score:.2f}"
                )

            # ─── Rolling summary (every 10 user messages) ──────────
            user_message_count = sum(1 for m in history if m.get("role") == "user")
            if user_message_count > 0 and user_message_count % 10 == 0:
                await self._update_conversation_summary(
                    conversation_id, history, existing_ticket_text
                )

        except Exception as e:
            logger.exception(f"ConversationAgent processing failed: {e}")
            # Avoid cascading into ticket/escalation flows due to parsing issues.
            state["short_circuit"] = True
            state["workflow_status"] = "completed"
            state["detected_sentiment"] = state.get("detected_sentiment", "neutral")
            state["detected_category"] = state.get("detected_category", "general")
            state["urgency"] = state.get("urgency", urgency)
            state["short_circuit"] = True
            state["ai_response"] = plain_chat_text(
                fallback_response(query_intent, user_query, history)
            )

        state["runtime_events"].append(
            {
                "type": "conversation_agent_completed",
                "sentiment": state.get("detected_sentiment", "neutral"),
                "category": state.get("detected_category", "general"),
                "urgency": state.get("urgency", "medium"),
                "entity_count": len(state.get("extracted_entities", [])),
                "short_circuit": state.get("short_circuit", False),
                "rag_used": should_rag,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return state

    async def _update_conversation_summary(
        self,
        conversation_id: str,
        history: list[dict],
        ticket_context: str,
    ) -> None:
        """Generate and store a rolling summary of the conversation."""
        try:
            history_text = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in history[-20:]
            )
            summary_prompt = f"""Summarize the following customer support conversation in 3-5 sentences.
            Focus on: the main issue, what was discussed, and any ticket/resolution details.
            Be concise and factual.

            Ticket Context: {ticket_context}

            Conversation:
            {history_text}

            Summary:"""
            response = await self.invoke_llm(summary_prompt)
            summary_text = response.get("content", "").strip()
            if summary_text:
                store_conversation_summary(conversation_id, summary_text)
                logger.info(
                    f"ConversationAgent | Updated rolling summary for {conversation_id}"
                )
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
