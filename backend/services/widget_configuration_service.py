from uuid import UUID

from db.schemas import WidgetConfiguration

from repositories.widget_configuration_repository import (
    WidgetConfigurationRepository,
)

from schemas.widget_configuration_schema import (
    WidgetConfigurationRequest,
)


class WidgetConfigurationService:

    def __init__(self, db):
        self.repo = WidgetConfigurationRepository(db)

    async def get_configuration(
        self,
        tenant_id: UUID,
    ):
        return await self.repo.get_by_tenant_id(tenant_id)

    async def save_configuration(
        self,
        tenant_id: UUID,
        request: WidgetConfigurationRequest,
    ):
        existing = await self.repo.get_by_tenant_id(tenant_id)

        if existing:
            existing.primary_color = request.primary_color
            existing.position = request.position
            existing.company_name = request.company_name
            existing.welcome_message = request.welcome_message
            existing.width = request.width
            existing.height = request.height
            existing.border_radius = request.border_radius
            existing.launcher_size = request.launcher_size
            existing.show_badge = request.show_badge
            existing.fullscreen_mobile = request.fullscreen_mobile
            existing.auto_open = request.auto_open
            existing.auto_open_delay = request.auto_open_delay

            return await self.repo.update(existing)

        entity = WidgetConfiguration(
            tenant_id=tenant_id,
            primary_color=request.primary_color,
            position=request.position,
            company_name=request.company_name,
            welcome_message=request.welcome_message,
            width=request.width,
            height=request.height,
            border_radius=request.border_radius,
            launcher_size=request.launcher_size,
            show_badge=request.show_badge,
            fullscreen_mobile=request.fullscreen_mobile,
            auto_open=request.auto_open,
            auto_open_delay=request.auto_open_delay,
        )

        return await self.repo.create(entity)

    async def get_configuration_by_api_key(
        self,
        api_key: str,
    ):
        configuration = await self.repo.get_by_api_key(api_key)

        if not configuration:
            raise ValueError("Widget configuration not found")

        return configuration
