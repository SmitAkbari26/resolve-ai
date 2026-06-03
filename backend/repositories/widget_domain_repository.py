from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas import Tenant, WidgetConfiguration, WidgetDomain


class WidgetDomainRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        entity: WidgetDomain,
    ):
        self.db.add(entity)

        await self.db.flush()

        await self.db.refresh(entity)

        return entity

    async def get_by_tenant_id(
        self,
        tenant_id: UUID,
    ):
        result = await self.db.execute(
            select(WidgetDomain)
            .where(WidgetDomain.tenant_id == tenant_id)
            .order_by(WidgetDomain.created_at.desc())
        )

        return result.scalars().all()

    async def get_by_domain(
        self,
        tenant_id: UUID,
        domain: str,
    ):
        result = await self.db.execute(
            select(WidgetDomain).where(
                WidgetDomain.tenant_id == tenant_id,
                WidgetDomain.domain == domain,
            )
        )

        return result.scalar_one_or_none()

    async def validate_domain(
        self,
        api_key: str,
        domain: str,
    ):
        result = await self.db.execute(
            select(
                Tenant,
                WidgetConfiguration,
            )
            .join(
                WidgetConfiguration,
                Tenant.id == WidgetConfiguration.tenant_id,
            )
            .join(
                WidgetDomain,
                Tenant.id == WidgetDomain.tenant_id,
            )
            .where(
                Tenant.api_key == api_key,
                Tenant.is_active.is_(True),
                WidgetConfiguration.is_active.is_(True),
                WidgetDomain.domain == domain.lower(),
                WidgetDomain.is_active.is_(True),
            )
        )

        return result.first()

    async def get_by_id(
        self,
        domain_id,
    ):
        result = await self.db.execute(
            select(WidgetDomain).where(WidgetDomain.id == domain_id)
        )

        return result.scalar_one_or_none()

    async def delete(
        self,
        entity: WidgetDomain,
    ):
        await self.db.delete(entity)
