from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.ticket_history_service import TicketHistoryService
from schemas.ticket_history_schema import (
    TicketHistoryCreate,
    TicketHistoryUpdate,
    TicketHistoryResponse,
)

router = APIRouter(prefix="/ticket-history", tags=["Ticket History"])


@router.post("", response_model=TicketHistoryResponse)
async def create_history_api(
    payload: TicketHistoryCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = TicketHistoryService(db)
        return await service.create_history(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[TicketHistoryResponse])
async def get_histories_api(db: AsyncSession = Depends(get_db)):
    service = TicketHistoryService(db)
    return await service.get_histories()


@router.get("/{history_id}", response_model=TicketHistoryResponse)
async def get_history_api(history_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketHistoryService(db)
    history = await service.get_history_by_id(history_id)
    if not history:
        raise HTTPException(status_code=404, detail="Ticket history not found")
    return history


@router.get("/ticket/{ticket_id}", response_model=list[TicketHistoryResponse])
async def get_ticket_histories_api(ticket_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketHistoryService(db)
    return await service.get_histories_by_ticket_id(ticket_id)


@router.put("/{history_id}", response_model=TicketHistoryResponse)
async def update_history_api(
    history_id: str, payload: TicketHistoryUpdate, db: AsyncSession = Depends(get_db)
):
    service = TicketHistoryService(db)
    history = await service.update_history(history_id, payload)
    if not history:
        raise HTTPException(status_code=404, detail="Ticket history not found")
    return history


@router.delete("/{history_id}")
async def delete_history_api(history_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketHistoryService(db)
    deleted = await service.delete_history(history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket history not found")
    return {"message": "Ticket history deleted successfully"}
