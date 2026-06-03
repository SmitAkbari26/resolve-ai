from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation_message_repository import ConversationMessageRepository
from schemas.conversation_message_schema import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
)


class ConversationMessageService:
    def __init__(self, db: AsyncSession):
        self.repository = ConversationMessageRepository(db)

    async def create_message(self, payload: ConversationMessageCreate):
        return await self.repository.create_message(payload)

    async def get_messages(self):
        return await self.repository.get_messages()

    async def get_message_by_id(self, message_id: str):
        return await self.repository.get_message_by_id(message_id)

    async def get_messages_by_conversation_id(self, conversation_id: str):
        return await self.repository.get_messages_by_conversation_id(conversation_id)

    async def update_message(self, message_id: str, payload: ConversationMessageUpdate):
        message = await self.repository.get_message_by_id(message_id)
        if not message:
            return None
        return await self.repository.update_message(message, payload)

    async def delete_message(self, message_id: str):
        message = await self.repository.get_message_by_id(message_id)
        if not message:
            return False
        return await self.repository.delete_message(message)
