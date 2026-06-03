from typing import Optional
from config import BASE_URL
from clients.base_client import BaseClient


class ApprovalClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="approvals")

    async def create_approval(self, payload: dict):
        return await self.post(payload=payload)

    async def get_approval(self, approval_id: str):
        return await self.get(path=f"/{approval_id}")

    async def list_approvals(self, status: Optional[str] = None):
        if status:
            return await self.get(path=f"/status/{status}")
        return await self.get()

    async def get_ticket_approvals(self, ticket_id: str):
        return await self.get(path=f"/ticket/{ticket_id}")

    async def update_approval(self, approval_id: str, payload: dict):
        payload = {
            k: v for k, v in payload.items() if k != "approval_id" and v is not None
        }

        return await self.put(path=f"/{approval_id}", payload=payload)
