from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.conversation_message_service import ConversationMessageService
from schemas.conversation_message_schema import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
    ConversationMessageResponse,
)

router = APIRouter(prefix="/conversation-messages", tags=["Conversation Messages"])


@router.post("", response_model=ConversationMessageResponse)
async def create_message_api(
    payload: ConversationMessageCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = ConversationMessageService(db)
        return await service.create_message(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[ConversationMessageResponse])
async def get_messages_api(db: AsyncSession = Depends(get_db)):
    service = ConversationMessageService(db)
    return await service.get_messages()


@router.get(
    "/conversation/{conversation_id}",
    response_model=list[ConversationMessageResponse],
)
async def get_conversation_messages_api(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = ConversationMessageService(db)
    return await service.get_messages_by_conversation_id(str(conversation_id))


@router.get("/{message_id}", response_model=ConversationMessageResponse)
async def get_message_api(message_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ConversationMessageService(db)
    message = await service.get_message_by_id(str(message_id))
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.put("/{message_id}", response_model=ConversationMessageResponse)
async def update_message_api(
    message_id: UUID,
    payload: ConversationMessageUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ConversationMessageService(db)
    message = await service.update_message(str(message_id), payload)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.delete("/{message_id}")
async def delete_message_api(message_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ConversationMessageService(db)
    deleted = await service.delete_message(str(message_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}
