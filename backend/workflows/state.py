from typing import TypedDict, Optional, Any


class SupportWorkflowState(TypedDict, total=False):

    workflow_id: str
    workflow_db_id: str
    conversation_id: str
    user_id: str
    user_email: str

    user_query: str

    detected_category: str
    detected_sentiment: str
    extracted_entities: list[str]
    urgency: str
    query_summary: str
    short_circuit: bool

    plan: list[str]
    current_agent_index: int
    reasoning: str

    retrieved_context: list[dict]
    context_text: str
    retrieval_count: int

    severity: str
    severity_score: float
    recommended_action: str
    requires_approval: bool
    approval_reason: str
    ai_response: str
    resolution_notes: str
    decision_reasoning: str

    ticket_id: Optional[str]
    ticket_status: Optional[str]

    approval_id: Optional[str]
    approval_decision: Optional[str]
    approval_status: Optional[str]

    notifications: list[str]

    tool_calls: list[dict]
    agent_trace: list[dict]
    runtime_events: list[dict]

    status: str
    workflow_status: str
    error: Optional[str]

    metadata: dict[str, Any]

    tenant_id: Optional[str]
    company_name: Optional[str]

