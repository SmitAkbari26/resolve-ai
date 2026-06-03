from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.ticket_attachment_service import TicketAttachmentService
from schemas.ticket_attachment_schema import (
    TicketAttachmentCreate,
    TicketAttachmentUpdate,
    TicketAttachmentResponse,
)

router = APIRouter(prefix="/ticket-attachments", tags=["Ticket Attachments"])


@router.post("", response_model=TicketAttachmentResponse)
async def create_attachment_api(
    payload: TicketAttachmentCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = TicketAttachmentService(db)
        return await service.create_attachment(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[TicketAttachmentResponse])
async def get_attachments_api(db: AsyncSession = Depends(get_db)):
    service = TicketAttachmentService(db)
    return await service.get_attachments()


@router.get("/{attachment_id}", response_model=TicketAttachmentResponse)
async def get_attachment_api(attachment_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketAttachmentService(db)
    attachment = await service.get_attachment_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.get("/ticket/{ticket_id}", response_model=list[TicketAttachmentResponse])
async def get_ticket_attachments_api(
    ticket_id: str, db: AsyncSession = Depends(get_db)
):
    service = TicketAttachmentService(db)
    return await service.get_attachments_by_ticket_id(ticket_id)


@router.put("/{attachment_id}", response_model=TicketAttachmentResponse)
async def update_attachment_api(
    attachment_id: str,
    payload: TicketAttachmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = TicketAttachmentService(db)
    attachment = await service.update_attachment(attachment_id, payload)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.delete("/{attachment_id}")
async def delete_attachment_api(attachment_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketAttachmentService(db)
    deleted = await service.delete_attachment(attachment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"message": "Attachment deleted successfully"}
