from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CustomerProfileCreate(BaseModel):
    user_id: UUID
    phone: str | None = None
    company: str | None = None
    subscription_plan: str | None = None
    preferred_language: str = "en"
    timezone: str = "UTC"

class CustomerProfileUpdate(BaseModel):
    phone: str | None = None
    company: str | None = None
    subscription_plan: str | None = None
    preferred_language: str | None = None
    timezone: str | None = None

class CustomerProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    phone: str | None
    company: str | None
    subscription_plan: str | None
    preferred_language: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True