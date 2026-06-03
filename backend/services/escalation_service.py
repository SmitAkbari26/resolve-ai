from sqlalchemy.ext.asyncio import AsyncSession
from repositories.escalation_repository import EscalationRepository
from schemas.escalation_schema import EscalationCreate, EscalationUpdate


class EscalationService:
    def __init__(self, db: AsyncSession):
        self.repository = EscalationRepository(db)

    async def create_escalation(self, payload: EscalationCreate):
        return await self.repository.create_escalation(payload)

    async def get_escalations(self):
        return await self.repository.get_escalations()

    async def get_escalation_by_id(self, escalation_id: str):
        return await self.repository.get_escalation_by_id(escalation_id)

    async def get_escalations_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_escalations_by_ticket_id(ticket_id)

    async def get_escalations_by_status(self, status: str):
        return await self.repository.get_escalations_by_status(status)

    async def update_escalation(self, escalation_id: str, payload: EscalationUpdate):
        escalation = await self.repository.get_escalation_by_id(escalation_id)
        if not escalation:
            return None
        return await self.repository.update_escalation(escalation, payload)

    async def delete_escalation(self, escalation_id: str):
        escalation = await self.repository.get_escalation_by_id(escalation_id)
        if not escalation:
            return False
        return await self.repository.delete_escalation(escalation)
