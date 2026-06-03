from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class EscalationClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="escalations")

    async def create_escalation(
        self,
        ticket_id: str,
        reason: str,
        escalation_level: int = 1,
        escalated_to: str | None = None,
        status: str = "active",
    ):
        payload = {
            "ticket_id": ticket_id,
            "reason": reason,
            "escalation_level": escalation_level,
            "escalated_to": escalated_to,
            "status": status,
        }
        return await self.post(payload=payload)

    async def get_escalation(self, escalation_id: str):
        return await self.get(path=f"/{escalation_id}")

    async def list_escalations(self, status: Optional[str] = None):
        if status:
            return await self.get(path=f"/status/{status}")
        return await self.get()

    async def get_ticket_escalations(self, ticket_id: str):
        return await self.get(path=f"/ticket/{ticket_id}")

    async def update_escalation(
        self,
        escalation_id: str,
        escalation_level: int | None = None,
        escalated_to: str | None = None,
        status: str | None = None,
        resolved_at: str | None = None,
    ):
        payload = {}
        if escalation_level is not None:
            payload["escalation_level"] = escalation_level
        if escalated_to is not None:
            payload["escalated_to"] = escalated_to
        if status is not None:
            payload["status"] = status
        if resolved_at is not None:
            payload["resolved_at"] = resolved_at
        return await self.put(path=f"/{escalation_id}", payload=payload)

    async def delete_escalation(self, escalation_id: str):
        return await self.delete(path=f"/{escalation_id}")
