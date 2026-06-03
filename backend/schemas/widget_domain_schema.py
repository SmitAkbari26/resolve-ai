from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CreateWidgetDomainRequest(BaseModel):
    tenant_id: UUID
    domain: str


class WidgetDomainResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    domain: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
