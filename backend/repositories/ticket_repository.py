from sqlalchemy import select
from db.schemas import TicketRecord
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.ticket_schema import TicketCreate, TicketUpdate


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ticket(self, payload: TicketCreate):
        ticket = TicketRecord(
            user_id=payload.user_id,
            conversation_id=payload.conversation_id,
            category=payload.category,
            priority=payload.priority,
            severity_score=payload.severity_score,
            summary=payload.summary,
            description=payload.description,
            suggested_action=payload.suggested_action,
            assigned_agent=payload.assigned_agent,
            metadata_=payload.metadata_,
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_tickets(self):
        result = await self.db.execute(select(TicketRecord))
        return result.scalars().all()

    async def get_ticket_by_id(self, ticket_id: str):
        result = await self.db.execute(
            select(TicketRecord).where(TicketRecord.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_ticket_by_conversation_id(self, conversation_id: str):
        from uuid import UUID
        try:
            conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
        except ValueError:
            return None
        result = await self.db.execute(
            select(TicketRecord).where(TicketRecord.conversation_id == conv_uuid)
        )
        return result.scalar_one_or_none()

    async def get_tickets_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(TicketRecord).where(TicketRecord.user_id == user_id)
        )
        return result.scalars().all()

    async def get_tickets_by_status(self, status: str):
        result = await self.db.execute(
            select(TicketRecord).where(TicketRecord.status == status)
        )
        return result.scalars().all()

    async def update_ticket(self, ticket: TicketRecord, payload: TicketUpdate):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def delete_ticket(self, ticket: TicketRecord):
        await self.db.delete(ticket)
        await self.db.commit()
        return True
