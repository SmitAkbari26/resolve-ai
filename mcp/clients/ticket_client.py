from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL
from tools.tickets.model import CreateTicketRequest, UpdateTicketRequest


class TicketClient(BaseClient):
    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="tickets")

    async def create_ticket(self, payload: CreateTicketRequest):
        return await self.post(payload=payload)

    async def get_ticket(self, ticket_id: str):
        return await self.get(path=f"/{ticket_id}")

    async def list_tickets(self, status: Optional[str] = None):
        params = {}
        if status:
            params["status"] = status
        return await self.get(params=params)

    async def update_ticket(self, ticket_id: str, payload: UpdateTicketRequest):
        payload = {k: v for k, v in payload.items() if v is not None and v is not ticket_id}
        return await self.post(path=f"/{ticket_id}", payload=payload)
