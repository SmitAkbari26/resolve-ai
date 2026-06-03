from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.conversation_service import ConversationService
from schemas.conversation_schema import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation_api(
    payload: ConversationCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = ConversationService(db)
        return await service.create_conversation(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[ConversationResponse])
async def get_conversations_api(db: AsyncSession = Depends(get_db)):
    service = ConversationService(db)
    return await service.get_conversations()


@router.get("/user/{user_id}", response_model=list[ConversationResponse])
async def get_user_conversations_api(user_id: UUID, db: AsyncSession = Depends(get_db)):
    service = ConversationService(db)
    return await service.get_conversations_by_user_id(str(user_id))


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_api(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    conversation = await service.get_conversation_by_id(str(conversation_id))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation_api(
    conversation_id: UUID,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ConversationService(db)
    conversation = await service.update_conversation(str(conversation_id), payload)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation_api(
    conversation_id: UUID, db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    deleted = await service.delete_conversation(str(conversation_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}
