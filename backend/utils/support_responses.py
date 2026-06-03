"""Deterministic customer-facing responses for common support intents (plain text)."""

from __future__ import annotations


CAPABILITIES_RESPONSE = """I'm Resolve AI, your support assistant.

I can help with:

- Account & login — sign-in issues, password reset, MFA/SSO
- Orders & billing — payments, refunds, invoices
- Technical issues — errors, bugs, something not working
- Product guidance — how to use a product you purchased (general tips; not medical advice)
- Tickets — open or check status of a support request

Tell me what you need and I'll guide you step-by-step."""


def login_troubleshooting_response() -> str:
    return (
        "Sorry you're having trouble signing in. Let's go step by step:\n\n"
        "1. Confirm your email/username and password (passwords are case-sensitive).\n"
        "2. Check Caps Lock and keyboard layout.\n"
        "3. Clear browser cache/cookies, or try Incognito/Private mode.\n"
        "4. Try another browser or device to rule out a local issue.\n"
        "5. Use Forgot password to reset if you're unsure of the password.\n"
        "6. If you use SSO (Google/Microsoft), sign in with that button instead of email/password.\n\n"
        "If it still fails, reply with the exact error message on screen (or a screenshot description) "
        "and whether you use SSO or email/password — I can help further or open a support ticket."
    )


def thanks_response() -> str:
    return (
        "You're welcome! If you need anything else, just ask. "
        "I'm here to help."
    )


def build_conversation_summary(history: list[dict]) -> str:
    """Summarize chat from memory without requiring JSON from the LLM gate."""
    if not history:
        return "We haven't discussed anything yet — feel free to describe what you need help with."

    user_points: list[str] = []
    assistant_points: list[str] = []

    for msg in history[-12:]:
        role = msg.get("role", "")
        content = (msg.get("content") or "").strip()
        if not content or len(content) < 3:
            continue
        if role == "user":
            user_points.append(content)
        elif role == "assistant":
            assistant_points.append(content)

    lines = ["Here's a summary of our conversation so far:\n"]

    if user_points:
        lines.append("What you asked about:")
        for i, point in enumerate(user_points[-5:], 1):
            short = point if len(point) <= 120 else point[:117] + "..."
            lines.append(f"{i}. {short}")

    if assistant_points:
        lines.append("\nWhat we covered:")
        last = assistant_points[-1]
        short = last if len(last) <= 200 else last[:197] + "..."
        lines.append(f"- {short}")

    lines.append(
        "\nIf you want to go deeper on any topic, tell me which point and I'll expand."
    )
    return "\n".join(lines)


def fallback_response(
    query_intent: str,
    user_query: str,
    history: list[dict] | None = None,
) -> str:
    """Context-aware fallback when LLM JSON parsing fails."""
    history = history or []

    if query_intent == "capabilities":
        return CAPABILITIES_RESPONSE
    if query_intent == "login_help":
        return login_troubleshooting_response()
    if query_intent == "conversation_summary":
        return build_conversation_summary(history)
    if query_intent == "thanks":
        return thanks_response()
    if query_intent == "name":
        return "My name is Resolve AI, your enterprise support assistant."

    if query_intent in ("informational", "general", "auth_guidance"):
        return (
            "I'm here to help. Could you tell me a bit more about what you need — "
            "for example account/login, billing, a technical error, or product usage?"
        )

    return (
        "I want to make sure I help correctly. "
        "Could you describe the issue you're facing (or what you'd like to do)?"
    )
