from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class TicketCommentCreate(BaseModel):
    ticket_id: UUID
    user_id: UUID
    comment: str
    is_internal: bool = False


class TicketCommentUpdate(BaseModel):
    comment: str | None = None
    is_internal: bool | None = None


class TicketCommentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    user_id: UUID
    comment: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True
