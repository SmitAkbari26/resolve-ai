from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from db.database import get_db
from core.security import require_role

from services.tenant_service import (
    TenantService,
)

from schemas.tenant_schema import (
    CreateTenantRequest,
    TenantResponse,
)

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


@router.post(
    "",
    response_model=TenantResponse,
)
async def create_tenant(
    request: CreateTenantRequest,
    db=Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    try:
        service = TenantService(db)

        return await service.create_tenant(request)

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )


@router.get(
    "",
    response_model=list[TenantResponse],
)
async def get_tenants(
    db=Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = TenantService(db)

    return await service.get_all_tenants()


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
)
async def get_tenant(
    tenant_id: UUID,
    db=Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = TenantService(db)

    tenant = await service.get_tenant(tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )

    return tenant
