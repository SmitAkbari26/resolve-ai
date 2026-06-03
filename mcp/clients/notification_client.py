from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class NotificationClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="notifications")

    async def create_notification(self, payload: dict):
        return await self.post(payload=payload)

    async def get_notification(self, notification_id: str):
        return await self.get(path=f"/{notification_id}")

    async def list_notifications(self, status: Optional[str] = None):
        if status:
            return await self.get(path=f"/status/{status}")
        return await self.get()

    async def get_user_notifications(self, user_id: str):
        return await self.get(path=f"/user/{user_id}")

    async def update_notification(self, notification_id: str, payload: dict):
        payload = {
            k: v for k, v in payload.items() if k != "notification_id" and v is not None
        }

        return await self.put(path=f"/{notification_id}", payload=payload)
