from uuid import UUID
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from schemas.widget_validation_schema import (
    ValidateWidgetRequest,
    ValidateWidgetResponse,
)
from db.database import get_db
from services.widget_domain_service import (
    WidgetDomainService,
)

from schemas.widget_domain_schema import (
    CreateWidgetDomainRequest,
    WidgetDomainResponse,
)

router = APIRouter(
    prefix="/widget-domains",
    tags=["Widget Domains"],
)


@router.post(
    "",
    response_model=WidgetDomainResponse,
)
async def create_domain(
    request: CreateWidgetDomainRequest,
    db=Depends(get_db),
):
    try:
        service = WidgetDomainService(db)

        return await service.create_domain(request)

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )


@router.get(
    "/{tenant_id}",
    response_model=list[WidgetDomainResponse],
)
async def get_domains(
    tenant_id: UUID,
    db=Depends(get_db),
):
    service = WidgetDomainService(db)

    return await service.get_domains(tenant_id)


@router.post(
    "/validate",
    response_model=ValidateWidgetResponse,
)
async def validate_widget(
    request: ValidateWidgetRequest,
    db=Depends(get_db),
):
    service = WidgetDomainService(db)

    return await service.validate_widget(
        request.api_key,
        request.domain,
    )


@router.delete("/{domain_id}")
async def delete_domain(
    domain_id: UUID,
    db=Depends(get_db),
):
    try:
        service = WidgetDomainService(db)

        await service.delete_domain(domain_id)

        return {"success": True, "message": "Domain deleted successfully"}

    except ValueError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )
