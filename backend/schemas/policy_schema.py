from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class PolicyCreate(BaseModel):
    title: str
    category: str
    content: str
    active: bool = True
    version: int = 1


class PolicyUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None
    active: bool | None = None
    version: int | None = None


class PolicyResponse(BaseModel):
    id: UUID
    title: str
    category: str
    content: str
    active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
