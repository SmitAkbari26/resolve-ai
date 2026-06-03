from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation_repository import ConversationRepository
from schemas.conversation_schema import ConversationCreate, ConversationUpdate

class ConversationService:
    def __init__(self, db: AsyncSession):
        self.repository = ConversationRepository(db)

    async def create_conversation(self, payload: ConversationCreate):
        return await self.repository.create_conversation(payload)
    
    async def get_conversations(self):
        return await self.repository.get_conversations()

    async def get_conversation_by_id(self, conversation_id: str):
        return await self.repository.get_conversation_by_id(conversation_id)

    async def get_conversations_by_user_id(self, user_id: str):
        return await self.repository.get_conversations_by_user_id(user_id)

    async def update_conversation(
        self, conversation_id: str, payload: ConversationUpdate
    ):
        conversation = await self.repository.get_conversation_by_id(conversation_id)
        if not conversation:
            return None
        return await self.repository.update_conversation(conversation, payload)

    async def delete_conversation(self, conversation_id: str):
        conversation = await self.repository.get_conversation_by_id(conversation_id)
        if not conversation:
            return False
        return await self.repository.delete_conversation(conversation)