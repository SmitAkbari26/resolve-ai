from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from db.database import get_db
from services.widget_configuration_service import (
    WidgetConfigurationService,
)
from schemas.widget_configuration_schema import (
    WidgetConfigurationRequest,
    WidgetConfigurationResponse,
)

router = APIRouter(
    prefix="/widget-configurations",
    tags=["Widget Configurations"],
)


@router.get(
    "/{tenant_id}",
    response_model=WidgetConfigurationResponse,
)
async def get_widget_configuration(
    tenant_id: UUID,
    db=Depends(get_db),
):
    service = WidgetConfigurationService(db)

    return await service.get_configuration(tenant_id)


@router.post(
    "/{tenant_id}",
    response_model=WidgetConfigurationResponse,
)
async def save_widget_configuration(
    tenant_id: UUID,
    request: WidgetConfigurationRequest,
    db=Depends(get_db),
):
    service = WidgetConfigurationService(db)

    return await service.save_configuration(
        tenant_id,
        request,
    )


@router.get(
    "/by-api-key/{api_key}",
    response_model=WidgetConfigurationResponse,
)
async def get_widget_configuration_by_api_key(
    api_key: str,
    db=Depends(get_db),
):
    try:
        service = WidgetConfigurationService(db)

        return await service.get_configuration_by_api_key(api_key)

    except ValueError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex),
        )
