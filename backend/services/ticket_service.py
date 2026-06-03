from sqlalchemy.ext.asyncio import AsyncSession
from repositories.ticket_repository import TicketRepository
from schemas.ticket_schema import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, db: AsyncSession):
        self.repository = TicketRepository(db)

    async def create_ticket(self, payload: TicketCreate):
        return await self.repository.create_ticket(payload)

    async def get_tickets(self):
        return await self.repository.get_tickets()

    async def get_ticket_by_id(self, ticket_id: str):
        return await self.repository.get_ticket_by_id(ticket_id)

    async def get_ticket_by_conversation_id(self, conversation_id: str):
        return await self.repository.get_ticket_by_conversation_id(conversation_id)

    async def get_tickets_by_user_id(self, user_id: str):
        return await self.repository.get_tickets_by_user_id(user_id)

    async def get_tickets_by_status(self, status: str):
        return await self.repository.get_tickets_by_status(status)

    async def update_ticket(self, ticket_id: str, payload: TicketUpdate):
        ticket = await self.repository.get_ticket_by_id(ticket_id)
        if not ticket:
            return None
        return await self.repository.update_ticket(ticket, payload)

    async def delete_ticket(self, ticket_id: str):
        ticket = await self.repository.get_ticket_by_id(ticket_id)
        if not ticket:
            return False
        return await self.repository.delete_ticket(ticket)
