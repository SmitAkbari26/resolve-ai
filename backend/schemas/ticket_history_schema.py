from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TicketHistoryCreate(BaseModel):
    ticket_id: UUID
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by: str | None = None


class TicketHistoryUpdate(BaseModel):
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    changed_by: str | None = None


class TicketHistoryResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_by: str | None
    changed_at: datetime

    class Config:
        from_attributes = True
