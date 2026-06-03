from schemas.widget_validation_schema import ValidateWidgetResponse
from db.schemas import WidgetDomain
from repositories.widget_domain_repository import (
    WidgetDomainRepository,
)
from schemas.widget_domain_schema import (
    CreateWidgetDomainRequest,
)


class WidgetDomainService:

    def __init__(self, db):
        self.repo = WidgetDomainRepository(db)

    async def create_domain(
        self,
        request: CreateWidgetDomainRequest,
    ):
        existing = await self.repo.get_by_domain(
            request.tenant_id,
            request.domain,
        )

        if existing:
            raise ValueError("Domain already exists")

        entity = WidgetDomain(
            tenant_id=request.tenant_id,
            domain=request.domain.lower(),
        )

        return await self.repo.create(entity)

    async def get_domains(
        self,
        tenant_id,
    ):
        return await self.repo.get_by_tenant_id(tenant_id)

    async def validate_widget(
        self,
        api_key: str,
        domain: str,
    ):
        result = await self.repo.validate_domain(
            api_key,
            domain,
        )

        if not result:
            return ValidateWidgetResponse(
                valid=False,
                message="Domain not allowed",
            )

        tenant, config = result

        return ValidateWidgetResponse(
            valid=True,
            tenant_id=tenant.id,
            company_name=config.company_name,
        )

    async def delete_domain(
        self,
        domain_id,
    ):
        entity = await self.repo.get_by_id(domain_id)

        if not entity:
            raise ValueError("Domain not found")

        await self.repo.delete(entity)
