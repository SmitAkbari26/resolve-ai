from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: UUID
    ticket_id: UUID | None = None
    notification_type: str
    channel: str = "email"
    subject: str | None = None
    message: str
    status: str = "pending"


class NotificationUpdate(BaseModel):
    notification_type: str | None = None
    channel: str | None = None
    subject: str | None = None
    message: str | None = None
    status: str | None = None
    sent_at: datetime | None = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    ticket_id: UUID | None
    notification_type: str
    channel: str
    subject: str | None
    message: str
    status: str
    sent_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
