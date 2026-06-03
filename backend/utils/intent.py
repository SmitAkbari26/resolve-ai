"""Intent detection — Hybrid two-tier system.

Tier 1 (sync, < 1 ms):
    Handles pure greetings and short thank-you messages via fast set/substring
    lookup.  Also keeps a minimal context-question check used to skip RAG
    before the LLM call.

Tier 2 (LLM, ~0 extra ms — Option B):
    Full intent classification is embedded in the existing CONVERSATION_PROMPT
    JSON response as the ``"intent"`` field.  conversation_agent.py reads that
    field after the LLM call and updates ``state["query_intent"]`` accordingly.
    See: prompts/conversation_prompt.py

The old 200-line keyword pattern approach has been replaced.  All phrasing
variations, product-specific terms, and edge-case language are now handled
naturally by the LLM.
"""

from __future__ import annotations

# ── Tier 1 data ───────────────────────────────────────────────────────────────

_GREETINGS: frozenset[str] = frozenset({
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "greetings", "whats up", "howdy", "hola", "yo", "sup", "good day",
})

_THANKS_PATTERNS: tuple[str, ...] = (
    "thank you",
    "thanks",
    "thank u",
    "thx",
    "appreciate",
    "grateful",
    "nice thanks",
)

# Minimal subset — only what's needed for the pre-LLM RAG / short-circuit
# decision.  Full intent classification is done by the LLM (Tier 2).
_CONTEXT_PATTERNS: tuple[str, ...] = (
    "what did you",
    "what have you",
    "you said",
    "you mentioned",
    "earlier you",
    "as we discussed",
    "ticket information",
    "ticket status",
    "status of my ticket",
    "update on my ticket",
    "ticket id",
    "ticket number",
)

# ── Internal helper ───────────────────────────────────────────────────────────


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    q = text.strip().lower()
    return any(p in q for p in patterns)


# ── Tier 1 helpers (public) ───────────────────────────────────────────────────


def is_greeting(query: str) -> bool:
    """True for short, pure greeting tokens (exact set lookup)."""
    clean = (
        query.strip()
        .lower()
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
    )
    return clean in _GREETINGS


def is_thanks(query: str) -> bool:
    """True for short thank-you messages (≤ 8 words)."""
    q = query.strip().lower()
    if len(q.split()) > 8:
        return False
    return _contains_any(q, _THANKS_PATTERNS)


def is_context_question(query: str, has_history: bool, has_ticket: bool) -> bool:
    """
    Lightweight pre-LLM check: is the user asking about something already
    discussed or about an existing ticket?  Used only for the RAG skip
    decision; the LLM provides the authoritative intent label afterwards.
    """
    if not (has_history or has_ticket):
        return False
    return _contains_any(query, _CONTEXT_PATTERNS)


# ── Tier 1 classifier ─────────────────────────────────────────────────────────


def classify_query_intent_tier1(query: str) -> str | None:
    """
    Fast synchronous Tier-1 classification.

    Returns an intent label for the clearest, cheapest-to-detect cases:
      ``"greeting"`` or ``"thanks"``.

    Returns ``None`` for everything else — the LLM (Tier 2) determines the
    correct intent via the ``"intent"`` field in the CONVERSATION_PROMPT
    JSON response.
    """
    if is_greeting(query):
        return "greeting"
    if is_thanks(query):
        return "thanks"
    return None


# ── Backward-compat shim ──────────────────────────────────────────────────────


def classify_query_intent(
    query: str,
    *,
    has_history: bool = False,
    has_ticket: bool = False,
) -> str:
    """
    Synchronous intent classifier (backward-compat).

    Returns the Tier-1 intent when confident; otherwise ``"general"`` as a
    safe placeholder.  **conversation_agent.py replaces this value with the
    LLM-returned ``"intent"`` field** after the main LLM call, so the
    ``"general"`` default is only ever used for the pre-LLM RAG decision.
    """
    return classify_query_intent_tier1(query) or "general"
