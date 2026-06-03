from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import TicketHistoryRecord
from schemas.ticket_history_schema import TicketHistoryCreate, TicketHistoryUpdate


class TicketHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_history(self, payload: TicketHistoryCreate):
        history = TicketHistoryRecord(
            ticket_id=payload.ticket_id,
            field_name=payload.field_name,
            old_value=payload.old_value,
            new_value=payload.new_value,
            changed_by=payload.changed_by,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_histories(self):
        result = await self.db.execute(select(TicketHistoryRecord))
        return result.scalars().all()

    async def get_history_by_id(self, history_id: str):
        result = await self.db.execute(
            select(TicketHistoryRecord).where(TicketHistoryRecord.id == history_id)
        )
        return result.scalar_one_or_none()

    async def get_histories_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(TicketHistoryRecord).where(
                TicketHistoryRecord.ticket_id == ticket_id
            )
        )
        return result.scalars().all()

    async def update_history(
        self, history: TicketHistoryRecord, payload: TicketHistoryUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(history, key, value)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def delete_history(self, history: TicketHistoryRecord):
        await self.db.delete(history)
        await self.db.commit()
        return True
