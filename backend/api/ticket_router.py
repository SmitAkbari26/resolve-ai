from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from services.ticket_service import TicketService
from schemas.ticket_schema import TicketCreate, TicketUpdate, TicketResponse
from core.security import get_current_user, require_role

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
async def create_ticket_api(
    payload: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        service = TicketService(db)
        if current_user["role"] == "customer":
            # Customers can only create tickets for themselves
            payload.user_id = UUID(current_user["id"])
        return await service.create_ticket(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[TicketResponse])
async def get_tickets_api(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    if current_user["role"] == "customer":
        return await service.get_tickets_by_user_id(current_user["id"])
    return await service.get_tickets()


@router.get("/user/{user_id}", response_model=list[TicketResponse])
async def get_user_tickets_api(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] == "customer" and str(user_id) != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tickets",
        )
    service = TicketService(db)
    return await service.get_tickets_by_user_id(str(user_id))


@router.get("/status/{status}", response_model=list[TicketResponse])
async def get_status_tickets_api(
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    service = TicketService(db)
    return await service.get_tickets_by_status(status)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_api(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = await service.get_ticket_by_id(str(ticket_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if current_user["role"] == "customer" and str(ticket.user_id) != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this ticket",
        )
    return ticket


@router.post("/{ticket_id}", response_model=TicketResponse)
async def update_ticket_api(
    ticket_id: UUID,
    payload: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = await service.get_ticket_by_id(str(ticket_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user["role"] == "customer":
        if str(ticket.user_id) != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this ticket",
            )
        # Customers can only update comments, not status/agents
        payload.assigned_agent = None
        payload.status = None

    updated_ticket = await service.update_ticket(str(ticket_id), payload)
    return updated_ticket


@router.delete("/{ticket_id}")
async def delete_ticket_api(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    service = TicketService(db)
    deleted = await service.delete_ticket(str(ticket_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket deleted successfully"}

