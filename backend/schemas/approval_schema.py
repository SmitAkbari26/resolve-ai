from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    ticket_id: UUID
    approval_type: str
    reason: str = ""
    amount: float | None = None
    requested_by: str = "system"


class ApprovalUpdate(BaseModel):
    approval_type: str | None = None
    reason: str | None = None
    amount: float | None = None
    status: str | None = None
    decided_by: str | None = None
    decision_notes: str | None = None
    decided_at: datetime | None = None


class ApprovalResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    approval_type: str
    reason: str
    amount: float | None
    status: str
    requested_by: str
    decided_by: str | None
    decision_notes: str
    created_at: datetime
    decided_at: datetime | None

    class Config:
        from_attributes = True
