from sqlalchemy import select
from db.schemas import ConversationRecord
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.conversation_schema import ConversationCreate, ConversationUpdate

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, payload: ConversationCreate):
        conversation = ConversationRecord(
            user_id=payload.user_id,
            channel=payload.channel,
            sentiment=payload.sentiment,
            status=payload.status,
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversations(self):
        result = await self.db.execute(select(ConversationRecord))
        return result.scalars().all()

    async def get_conversation_by_id(self, conversation_id: str):
        result = await self.db.execute(
            select(ConversationRecord).where(ConversationRecord.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_conversations_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(ConversationRecord).where(ConversationRecord.user_id == user_id)
        )
        return result.scalars().all()

    async def update_conversation(
        self, conversation: ConversationRecord, payload: ConversationUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(conversation, key, value)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def delete_conversation(self, conversation: ConversationRecord):
        await self.db.delete(conversation)
        await self.db.commit()
        return True