from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ConversationCreate(BaseModel):
    user_id: UUID
    channel: str = "web_chat"
    sentiment: str = "neutral"
    status: str = "active"

class ConversationUpdate(BaseModel):
    channel: str | None = None
    sentiment: str | None = None
    status: str | None = None

class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    channel: str
    sentiment: str
    status: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
