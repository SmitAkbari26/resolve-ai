from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class WorkflowExecutionCreate(BaseModel):
    ticket_id: UUID | None = None   # Optional — ticket may not exist yet at workflow start
    workflow_type: str
    current_step: str | None = None
    status: str = "pending"
    created_by: str | None = None


class WorkflowExecutionUpdate(BaseModel):
    ticket_id: UUID | None = None
    workflow_type: str | None = None
    current_step: str | None = None
    status: str | None = None
    completed_at: datetime | None = None
    failed_reason: str | None = None
    created_by: str | None = None


class WorkflowExecutionResponse(BaseModel):
    id: UUID
    ticket_id: UUID | None        # Optional — may be null before TicketAgent runs
    workflow_type: str
    current_step: str | None
    status: str
    started_at: datetime
    completed_at: datetime | None
    failed_reason: str | None
    created_by: str | None

    class Config:
        from_attributes = True
