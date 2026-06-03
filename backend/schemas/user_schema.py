from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr
from sqlalchemy import Enum


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "customer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str


class UserRole(str, Enum):
    customer = "customer"
    agent = "agent"
    manager = "manager"
    admin = "admin"
