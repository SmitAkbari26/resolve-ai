from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import ConversationMessageRecord
from schemas.conversation_message_schema import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
)


class ConversationMessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, payload: ConversationMessageCreate):
        message = ConversationMessageRecord(
            conversation_id=payload.conversation_id,
            role=payload.role,
            message=payload.message,
            metadata_=payload.metadata_,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages(self):
        result = await self.db.execute(select(ConversationMessageRecord))
        return result.scalars().all()

    async def get_message_by_id(self, message_id: str):
        result = await self.db.execute(
            select(ConversationMessageRecord).where(
                ConversationMessageRecord.id == message_id
            )
        )
        return result.scalar_one_or_none()

    async def get_messages_by_conversation_id(self, conversation_id: str):
        result = await self.db.execute(
            select(ConversationMessageRecord).where(
                ConversationMessageRecord.conversation_id == conversation_id
            )
        )
        return result.scalars().all()

    async def update_message(
        self, message: ConversationMessageRecord, payload: ConversationMessageUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(message, key, value)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def delete_message(self, message: ConversationMessageRecord):
        await self.db.delete(message)
        await self.db.commit()
        return True
