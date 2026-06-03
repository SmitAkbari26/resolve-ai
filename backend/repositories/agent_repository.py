from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import AgentRecord
from schemas.agent_schema import AgentCreate, AgentUpdate


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, payload: AgentCreate):
        agent = AgentRecord(
            name=payload.name,
            agent_type=payload.agent_type,
            description=payload.description,
            model_name=payload.model_name,
            status=payload.status,
        )
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agents(self):
        result = await self.db.execute(select(AgentRecord))
        return result.scalars().all()

    async def get_agent_by_id(self, agent_id: str):
        result = await self.db.execute(
            select(AgentRecord).where(AgentRecord.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_agents_by_type(self, agent_type: str):
        result = await self.db.execute(
            select(AgentRecord).where(AgentRecord.agent_type == agent_type)
        )
        return result.scalars().all()

    async def get_agents_by_status(self, status: str):
        result = await self.db.execute(
            select(AgentRecord).where(AgentRecord.status == status)
        )
        return result.scalars().all()

    async def update_agent(self, agent: AgentRecord, payload: AgentUpdate):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def delete_agent(self, agent: AgentRecord):
        await self.db.delete(agent)
        await self.db.commit()
        return True
