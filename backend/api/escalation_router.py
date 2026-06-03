from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.escalation_service import EscalationService
from schemas.escalation_schema import (
    EscalationCreate,
    EscalationUpdate,
    EscalationResponse,
)

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.post("", response_model=EscalationResponse)
async def create_escalation_api(
    payload: EscalationCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = EscalationService(db)
        return await service.create_escalation(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[EscalationResponse])
async def get_escalations_api(db: AsyncSession = Depends(get_db)):
    service = EscalationService(db)
    return await service.get_escalations()


@router.get("/ticket/{ticket_id}", response_model=list[EscalationResponse])
async def get_ticket_escalations_api(
    ticket_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = EscalationService(db)
    return await service.get_escalations_by_ticket_id(str(ticket_id))


@router.get("/status/{status}", response_model=list[EscalationResponse])
async def get_status_escalations_api(status: str, db: AsyncSession = Depends(get_db)):
    service = EscalationService(db)
    return await service.get_escalations_by_status(status)


@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation_api(escalation_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EscalationService(db)
    escalation = await service.get_escalation_by_id(str(escalation_id))
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return escalation


@router.put("/{escalation_id}", response_model=EscalationResponse)
async def update_escalation_api(
    escalation_id: UUID, payload: EscalationUpdate, db: AsyncSession = Depends(get_db)
):
    service = EscalationService(db)
    escalation = await service.update_escalation(str(escalation_id), payload)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return escalation


@router.delete("/{escalation_id}")
async def delete_escalation_api(escalation_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EscalationService(db)
    deleted = await service.delete_escalation(str(escalation_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return {"message": "Escalation deleted successfully"}
