from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class TicketAttachmentCreate(BaseModel):
    ticket_id: UUID
    file_name: str
    file_path: str
    file_type: str | None = None
    uploaded_by: str | None = None


class TicketAttachmentUpdate(BaseModel):
    file_name: str | None = None
    file_path: str | None = None
    file_type: str | None = None
    uploaded_by: str | None = None


class TicketAttachmentResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    file_name: str
    file_path: str
    file_type: str | None
    uploaded_by: str | None
    created_at: datetime

    class Config:
        from_attributes = True
