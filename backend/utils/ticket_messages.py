"""Customer-facing ticket messages using only real ticket data (plain text)."""

from __future__ import annotations


def _ticket_id_display(ticket: dict) -> str:
    tid = ticket.get("id") or ticket.get("ticket_id") or ""
    return str(tid)


def format_ticket_status_reply(ticket: dict, user_query: str) -> str:
    """Build a response from DB ticket fields — never invent IDs."""
    tid = _ticket_id_display(ticket)
    if not tid:
        return (
            "I don't see an active support ticket linked to this conversation yet. "
            "If you'd like, describe the issue again and I can create one for you."
        )

    category = ticket.get("category", "general")
    status = ticket.get("status", "open")
    priority = ticket.get("priority", "medium")
    summary = ticket.get("summary") or "Support request"

    q = user_query.lower()
    asks_timing = any(
        p in q
        for p in (
            "how long",
            "how much time",
            "approx",
            "approximately",
            "eta",
            "processing time",
            "time to solve",
            "when will",
        )
    )

    if asks_timing:
        return (
            f"Your ticket {tid} is currently {status} "
            f"(category: {category}, priority: {priority}).\n\n"
            f"For {category} issues, we typically resolve within 24–48 hours. "
            f"You'll be notified when there's an update."
        )

    return (
        f"Here are the details for your support ticket:\n\n"
        f"- Ticket ID: {tid}\n"
        f"- Category: {category}\n"
        f"- Status: {status}\n"
        f"- Priority: {priority}\n"
        f"- Summary: {summary}\n\n"
        f"Typical resolution time is 24–48 hours. "
        f"Reply here if you have more details to add."
    )


def format_ticket_created_reply(ticket: dict) -> str:
    tid = _ticket_id_display(ticket)
    return (
        f"I've created a support ticket for you.\n\n"
        f"- Ticket ID: {tid}\n"
        f"- Category: {ticket.get('category', 'general')}\n"
        f"- Status: {ticket.get('status', 'open')}\n"
        f"- Priority: {ticket.get('priority', 'medium')}\n\n"
        f"Our team will follow up shortly. Typical resolution: 24–48 hours."
    )
