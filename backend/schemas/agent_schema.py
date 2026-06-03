from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    agent_type: str
    description: str = ""
    model_name: str | None = None
    status: str = "active"


class AgentUpdate(BaseModel):
    name: str | None = None
    agent_type: str | None = None
    description: str | None = None
    model_name: str | None = None
    status: str | None = None


class AgentResponse(BaseModel):
    id: UUID
    name: str
    agent_type: str
    description: str
    model_name: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
