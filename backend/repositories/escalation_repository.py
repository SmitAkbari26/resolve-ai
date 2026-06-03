from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import EscalationRecord
from schemas.escalation_schema import EscalationCreate, EscalationUpdate


class EscalationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_escalation(self, payload: EscalationCreate):
        escalation = EscalationRecord(
            ticket_id=payload.ticket_id,
            escalation_level=payload.escalation_level,
            reason=payload.reason,
            escalated_to=payload.escalated_to,
            status=payload.status,
        )
        self.db.add(escalation)
        await self.db.commit()
        await self.db.refresh(escalation)
        return escalation

    async def get_escalations(self):
        result = await self.db.execute(select(EscalationRecord))
        return result.scalars().all()

    async def get_escalation_by_id(self, escalation_id: str):
        result = await self.db.execute(
            select(EscalationRecord).where(EscalationRecord.id == escalation_id)
        )
        return result.scalar_one_or_none()

    async def get_escalations_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(EscalationRecord).where(EscalationRecord.ticket_id == ticket_id)
        )
        return result.scalars().all()

    async def get_escalations_by_status(self, status: str):
        result = await self.db.execute(
            select(EscalationRecord).where(EscalationRecord.status == status)
        )
        return result.scalars().all()

    async def update_escalation(
        self, escalation: EscalationRecord, payload: EscalationUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(escalation, key, value)
        await self.db.commit()
        await self.db.refresh(escalation)
        return escalation

    async def delete_escalation(self, escalation: EscalationRecord):
        await self.db.delete(escalation)
        await self.db.commit()
        return True
