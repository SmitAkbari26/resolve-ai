from uuid import UUID
from typing import Any
from datetime import datetime
from pydantic import BaseModel


class ConversationMessageCreate(BaseModel):
    conversation_id: UUID
    role: str
    message: str
    metadata_: dict[str, Any] = {}


class ConversationMessageUpdate(BaseModel):
    role: str | None = None
    message: str | None = None
    metadata_: dict[str, Any] | None = None


class ConversationMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    message: str
    metadata_: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
