from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class ConversationClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="conversations")

    async def create_conversation(self, user_id: str, channel: str = "web_chat"):
        payload = {"user_id": user_id, "channel": channel}
        return await self.post(payload=payload)

    async def get_conversation(self, conversation_id: str):
        return await self.get(path=f"/{conversation_id}")

    async def list_conversations(self, status: Optional[str] = None):
        params = {}
        if status:
            params["status"] = status
        return await self.get(params=params)
