from sqlalchemy.ext.asyncio import AsyncSession
from repositories.ticket_history_repository import TicketHistoryRepository
from schemas.ticket_history_schema import TicketHistoryCreate, TicketHistoryUpdate


class TicketHistoryService:
    def __init__(self, db: AsyncSession):
        self.repository = TicketHistoryRepository(db)

    async def create_history(self, payload: TicketHistoryCreate):
        return await self.repository.create_history(payload)

    async def get_histories(self):
        return await self.repository.get_histories()

    async def get_history_by_id(self, history_id: str):
        return await self.repository.get_history_by_id(history_id)

    async def get_histories_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_histories_by_ticket_id(ticket_id)

    async def update_history(self, history_id: str, payload: TicketHistoryUpdate):
        history = await self.repository.get_history_by_id(history_id)
        if not history:
            return None
        return await self.repository.update_history(history, payload)

    async def delete_history(self, history_id: str):
        history = await self.repository.get_history_by_id(history_id)
        if not history:
            return False
        return await self.repository.delete_history(history)
