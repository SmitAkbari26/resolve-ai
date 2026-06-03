from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.ticket_comment_service import TicketCommentService
from schemas.ticket_comment_schema import (
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
)

router = APIRouter(prefix="/ticket-comments", tags=["Ticket Comments"])


@router.post("", response_model=TicketCommentResponse)
async def create_comment_api(
    payload: TicketCommentCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = TicketCommentService(db)
        return await service.create_comment(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[TicketCommentResponse])
async def get_comments_api(db: AsyncSession = Depends(get_db)):
    service = TicketCommentService(db)
    return await service.get_comments()


@router.get("/{comment_id}", response_model=TicketCommentResponse)
async def get_comment_api(comment_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketCommentService(db)
    comment = await service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/ticket/{ticket_id}", response_model=list[TicketCommentResponse])
async def get_ticket_comments_api(ticket_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketCommentService(db)
    return await service.get_comments_by_ticket_id(ticket_id)


@router.get("/user/{user_id}", response_model=list[TicketCommentResponse])
async def get_user_comments_api(user_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketCommentService(db)
    return await service.get_comments_by_user_id(user_id)


@router.put("/{comment_id}", response_model=TicketCommentResponse)
async def update_comment_api(
    comment_id: str, payload: TicketCommentUpdate, db: AsyncSession = Depends(get_db)
):
    service = TicketCommentService(db)
    comment = await service.update_comment(comment_id, payload)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}")
async def delete_comment_api(comment_id: str, db: AsyncSession = Depends(get_db)):
    service = TicketCommentService(db)
    deleted = await service.delete_comment(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}
