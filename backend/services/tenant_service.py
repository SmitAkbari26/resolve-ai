import secrets

from db.schemas import Tenant

from repositories.tenant_repository import (
    TenantRepository,
)


class TenantService:

    def __init__(self, db):
        self.repo = TenantRepository(db)

    async def create_tenant(
        self,
        request,
    ):
        existing = await self.repo.get_by_slug(request.slug)

        if existing:
            raise ValueError("Tenant slug already exists")

        tenant = Tenant(
            name=request.name,
            slug=request.slug,
            api_key=(f"rw_live_{secrets.token_hex(16)}"),
        )

        return await self.repo.create(tenant)

    async def get_all_tenants(
        self,
    ):
        return await self.repo.get_all()

    async def get_tenant(
        self,
        tenant_id,
    ):
        return await self.repo.get_by_id(tenant_id)
