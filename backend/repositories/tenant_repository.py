from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.schemas import Tenant


class TenantRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant: Tenant,
    ):
        self.db.add(tenant)
        await self.db.flush()
        await self.db.refresh(tenant)
        return tenant

    async def get_all(self):
        result = await self.db.execute(select(Tenant).order_by(Tenant.name))
        return result.scalars().all()

    async def get_by_id(
        self,
        tenant_id: UUID,
    ):
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ):
        result = await self.db.execute(select(Tenant).where(Tenant.slug == slug))
        return result.scalar_one_or_none()
