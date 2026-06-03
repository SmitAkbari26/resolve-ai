from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class UpdateTenantRequest(BaseModel):
    name: str
    slug: str
    is_active: bool


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    api_key: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}
