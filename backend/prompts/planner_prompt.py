import json


def build_planner_prompt(state: dict) -> str:

    user_query = state.get("user_query", "")
    category = state.get("detected_category", "general")
    sentiment = state.get("detected_sentiment", "neutral")
    urgency = state.get("urgency", "medium")
    entities = state.get("extracted_entities", [])
    query_summary = state.get("query_summary", user_query[:200])
    ticket_id = state.get("ticket_id", None)
    ticket = state.get("ticket", {})

    existing_ticket_note = ""
    if ticket_id:
        existing_ticket_note = f"""
⚠️  EXISTING TICKET DETECTED: {ticket_id}
Ticket Details: {json.dumps(ticket, indent=2)[:500]}

RULES WHEN TICKET EXISTS:
- Do NOT plan ticket_agent with create intent — only update is allowed
- If the user is just asking about the ticket, use decision_agent to inform them, then notification_agent
- NEVER run ticket_agent alone without decision_agent
"""

    available_agents = [
        {
            "name": "decision_agent",
            "purpose": "Classifies severity, decides resolution strategy, generates the customer-facing response. ALWAYS the first agent.",
        },
        {
            "name": "ticket_agent",
            "purpose": "Creates a new ticket OR updates an existing one via MCP tools. Only when a ticket action is actually needed.",
        },
        {
            "name": "approval_agent",
            "purpose": "Triggers human approval workflow for sensitive actions (refunds, account changes, critical issues).",
        },
        {
            "name": "notification_agent",
            "purpose": "Sends email/Slack notifications to customer and internal team. Runs at end of workflow.",
        },
    ]

    return f"""You are the Planner Agent in Resolve AI.

The ConversationAgent has analyzed the query and determined a full workflow is required.
Your job is to select the MINIMAL set of agents needed — do not over-plan.

{existing_ticket_note}

════════════════════════════════════════
PRE-ANALYZED CONTEXT
════════════════════════════════════════

Query: {user_query}
Category: {category}
Sentiment: {sentiment}
Urgency: {urgency}
Entities: {json.dumps(entities, indent=2)}
Summary: {query_summary}
Existing Ticket ID: {ticket_id or "None"}

════════════════════════════════════════
AVAILABLE AGENTS
════════════════════════════════════════

{json.dumps(available_agents, indent=2)}

════════════════════════════════════════
PLANNING RULES — READ CAREFULLY
════════════════════════════════════════

1. decision_agent MUST always be the FIRST agent in any plan.

2. Include ticket_agent ONLY when:
   - A brand new ticket needs to be created (no existing ticket, user reported an actual new issue)
   - An existing ticket needs to be updated with new information

3. Include approval_agent ONLY when:
   - Refund, payment, or billing action is needed with high/critical severity
   - Account security changes are needed
   - Critical severity issue detected

4. Include notification_agent ONLY when:
   - A ticket was created or updated (user and team need to know)
   - An escalation occurred

5. If ONLY a decision/informational response is needed (e.g., ticket exists, user needs update):
   - Plan: ["decision_agent"] ONLY — do NOT add ticket_agent or notification_agent

6. MINIMUM VIABLE PLAN — fewer agents = faster response:
   - Pure informational: ["decision_agent"]
   - New issue: ["decision_agent", "ticket_agent", "notification_agent"]
   - Approval needed: ["decision_agent", "ticket_agent", "approval_agent", "notification_agent"]
   - Existing ticket update: ["decision_agent", "ticket_agent", "notification_agent"]

════════════════════════════════════════
OUTPUT FORMAT — Return ONLY valid JSON
════════════════════════════════════════

WORKFLOW PLAN:
{{
  "plan": ["decision_agent", "ticket_agent", "notification_agent"],
  "reasoning": "Why these specific agents were chosen"
}}

DIRECT RESPONSE (if planner itself can fully answer without any agents):
{{
  "ai_response": "Direct answer to customer",
  "plan": [],
  "reasoning": "Why no workflow is needed"
}}

Return ONLY valid JSON. No markdown. No extra text.
"""
