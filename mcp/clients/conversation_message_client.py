from clients.base_client import BaseClient
from config import BASE_URL


class ConversationMessageClient(BaseClient):
    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="conversation-messages")

    async def create_message(
        self, conversation_id: str, role: str, message: str, metadata_: dict = {}
    ):
        payload = {
            "conversation_id": conversation_id,
            "role": role,
            "message": message,
            "metadata_": metadata_,
        }
        return await self.post(payload=payload)

    async def get_message(self, message_id: str):
        return await self.get(path=f"/{message_id}")

    async def list_messages(self, conversation_id: str):
        return await self.get(path=f"/conversation/{conversation_id}")
