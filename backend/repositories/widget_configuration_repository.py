from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import Tenant, WidgetConfiguration


class WidgetConfigurationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_tenant_id(
        self,
        tenant_id: UUID,
    ):
        result = await self.db.execute(
            select(WidgetConfiguration).where(
                WidgetConfiguration.tenant_id == tenant_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        entity: WidgetConfiguration,
    ):
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)

        return entity

    async def update(
        self,
        entity: WidgetConfiguration,
    ):
        await self.db.flush()
        await self.db.refresh(entity)

        return entity

    async def get_by_api_key(
        self,
        api_key: str,
    ):
        result = await self.db.execute(
            select(WidgetConfiguration)
            .join(
                Tenant,
                WidgetConfiguration.tenant_id == Tenant.id,
            )
            .where(
                Tenant.api_key == api_key,
                Tenant.is_active.is_(True),
                WidgetConfiguration.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()
