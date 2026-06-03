from agents.templates.support_email_template import (
    build_support_email_template,
)


def build_notification_prompt(
    state: dict,
    ticket_id: str,
    category: str,
    severity: str,
    user_id: str,
    conversation_id: str,
    user_email: str,
    ai_response: str,
):

    support_email_body = build_support_email_template(
        category=category,
        severity=severity,
        user_id=user_id,
        ticket_id=ticket_id,
        query_summary=state.get("query_summary", "No summary available."),
        ai_response=ai_response,
    )

    return f"""
    You are the Notification Agent in Resolve AI.

    Your job is to:
    - send alerts
    - notify support teams
    - create notification records
    - update communication channels

    Current State:
    - Ticket ID: {ticket_id}
    - Category: {category}
    - Severity: {severity}
    - User ID: {user_id}
    - Conversation ID: {conversation_id}
    - User Email: {user_email}
    - Recommended Action: {state.get("recommended_action", "")}
    - AI Response: {ai_response}
    - Customer Query Summary: {state.get("query_summary", "")}

    Requirements:

    1. If Recommended Action is:
       - create_ticket
       - escalate

       Then:

       - Call `send_email`
       - to: support-team@resolveai.com
       - subject:
         [{severity.upper()}]
         Ticket {ticket_id}
         — {category}

       - body:
        Use the EXACT raw HTML provided below.
        Do NOT summarize it.
        Do NOT truncate it.
        Do NOT rewrite it.
        Do NOT wrap it in additional quotes.

        EMAIL_HTML_BODY_START

        {support_email_body}

        EMAIL_HTML_BODY_END

    2. If User ID exists and AI Response exists:

       - Call `create_notification`

       Parameters:
       - user_id: {user_id}
       - ticket_id: {ticket_id if ticket_id != 'N/A' else None}
       - notification_type: ticket_update
       - channel: email
       - subject: Update on your support request
       - message: {ai_response}
       - status: pending

    Return execution summary after tool completion.

    IMPORTANT TOOL RULES:

    - When calling send_email:
    - use the FULL HTML exactly as provided
    - preserve all HTML tags/styles
    - do NOT escape HTML
    - do NOT shorten the HTML
    - do NOT replace body with placeholders
    - do NOT return "<html>...[full HTML content]..."
    """
