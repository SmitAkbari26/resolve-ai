from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    agent_name: str | None = None
    details: dict[str, Any] = {}


class AuditLogUpdate(BaseModel):
    entity_type: str | None = None
    entity_id: str | None = None
    action: str | None = None
    agent_name: str | None = None
    details: dict[str, Any] | None = None


class AuditLogResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    action: str
    agent_name: str | None
    details: dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
