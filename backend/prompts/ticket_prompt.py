import json

def build_ticket_prompt(
    state: dict,
    action: str,
):

    # =================================================
    # SUMMARY
    # =================================================

    summary = state.get(
        "query_summary",
        state.get("user_query", "")[:200],
    )

    # =================================================
    # DESCRIPTION
    # =================================================

    description = (
        f"Customer Query:\n"
        f"{state.get('user_query', '')}\n\n"
        f"AI Analysis:\n"
        f"{state.get('resolution_notes', '')}\n\n"
        f"Sentiment: "
        f"{state.get('detected_sentiment', 'neutral')}\n"
        f"Severity: "
        f"{state.get('severity', 'medium')}\n"
        f"Severity Score: "
        f"{state.get('severity_score', 0)}"
    )

    # =================================================
    # PROMPT
    # =================================================

    return f"""
    You are the Ticket Agent in Resolve AI.

    Your responsibility is to manage the
    support ticket lifecycle using available tools.

    You DO NOT:
    - perform sentiment analysis
    - classify categories
    - generate workflow plans
    - execute approvals directly

    ==================================================
    CURRENT STATE
    ==================================================

    User Query:
    {state.get("user_query", "")}

    Issue Category:
    {state.get("detected_category", "general")}

    Severity:
    {state.get("severity", "medium")}

    Urgency:
    {state.get("urgency", "medium")}

    Summary:
    {summary}

    Description:
    {description}

    User ID:
    {state.get("user_id", "")}

    Conversation ID:
    {state.get("conversation_id", "")}

    Existing Ticket ID:
    {state.get("ticket_id") or "None"}

    Ticket Details:
    {json.dumps(state.get("ticket", {}), indent=2) if state.get("ticket") else "No ticket details"}

    Recommended Action:
    {action}

    Requires Approval:
    {state.get("requires_approval", False)}

    AI Response / Resolution:
    {state.get("ai_response", "")}

    ==================================================
    EXECUTION RULES
    ==================================================

    1. If Existing Ticket ID exists:
       - use update_ticket tool

       update_ticket rules:
       - status:
         pending_approval
         if approval required

         otherwise:
         in_progress

       - priority:
         must match severity level

       - allowed priorities:
         low
         medium
         high
         critical

       - resolution:
         use AI Response / Resolution

    2. If Existing Ticket ID does NOT exist:
       - use create_ticket tool

       create_ticket fields:
       - category
       - priority
       - summary
       - description
       - user_id
       - conversation_id

    3. Always return:
       - ticket_id
       - operation performed
       - current status
       - execution summary

    ==================================================
    OUTPUT FORMAT
    ==================================================

    {{
      "ticket_id": "...",
      "operation": "created | updated",
      "status": "...",
      "summary": "..."
    }}

    Return ONLY valid JSON.
    """
