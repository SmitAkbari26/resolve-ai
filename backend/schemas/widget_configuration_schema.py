from pydantic import BaseModel, Field
from uuid import UUID

class WidgetConfigurationRequest(BaseModel):
    primary_color: str = Field(default="#8b5cf6")
    position: str = Field(default="right")
    company_name: str
    welcome_message: str
    width: int = 430
    height: int = 720
    border_radius: int = 32
    launcher_size: int = 64
    show_badge: bool = True
    fullscreen_mobile: bool = True
    auto_open: bool = False
    auto_open_delay: int = 2000


class WidgetConfigurationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    primary_color: str
    position: str
    company_name: str
    welcome_message: str
    width: int
    height: int
    border_radius: int
    launcher_size: int
    show_badge: bool
    fullscreen_mobile: bool
    auto_open: bool
    auto_open_delay: int

    class Config:
        from_attributes = True
