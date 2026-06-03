from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class EscalationCreate(BaseModel):
    ticket_id: UUID
    escalation_level: int = 1
    reason: str
    escalated_to: str | None = None
    status: str = "active"


class EscalationUpdate(BaseModel):
    escalation_level: int | None = None
    reason: str | None = None
    escalated_to: str | None = None
    status: str | None = None
    resolved_at: datetime | None = None


class EscalationResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    escalation_level: int
    reason: str
    escalated_to: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True
