from uuid import UUID
from typing import Any
from datetime import datetime
from pydantic import BaseModel


class TicketCreate(BaseModel):
    user_id: UUID
    conversation_id: UUID | None = None
    category: str
    priority: str = "medium"
    summary: str
    description: str = ""
    severity_score: float = 0.0
    suggested_action: str = ""
    assigned_agent: str | None = None
    metadata_: dict[str, Any] = {}


class TicketUpdate(BaseModel):
    category: str | None = None
    priority: str | None = None
    status: str | None = None
    severity_score: float | None = None
    summary: str | None = None
    description: str | None = None
    resolution: str | None = None
    suggested_action: str | None = None
    assigned_agent: str | None = None
    metadata_: dict[str, Any] | None = None


class TicketResponse(BaseModel):
    id: UUID
    user_id: UUID
    conversation_id: UUID | None
    category: str
    priority: str
    status: str
    severity_score: float
    summary: str
    description: str
    resolution: str
    suggested_action: str
    assigned_agent: str | None
    metadata_: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
