from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ValidateWidgetRequest(BaseModel):
    api_key: str
    domain: str


class ValidateWidgetResponse(BaseModel):
    valid: bool
    tenant_id: Optional[UUID] = None
    company_name: Optional[str] = None
    message: Optional[str] = None
