from sqlalchemy.ext.asyncio import AsyncSession
from repositories.agent_repository import AgentRepository
from schemas.agent_schema import AgentCreate, AgentUpdate


class AgentService:

    def __init__(self, db: AsyncSession):
        self.repository = AgentRepository(db)

    async def create_agent(self, payload: AgentCreate):
        return await self.repository.create_agent(payload)

    async def get_agents(self):
        return await self.repository.get_agents()

    async def get_agent_by_id(self, agent_id: str):
        return await self.repository.get_agent_by_id(agent_id)

    async def get_agents_by_type(self, agent_type: str):
        return await self.repository.get_agents_by_type(agent_type)

    async def get_agents_by_status(self, status: str):
        return await self.repository.get_agents_by_status(status)

    async def update_agent(self, agent_id: str, payload: AgentUpdate):
        agent = await self.repository.get_agent_by_id(agent_id)
        if not agent:
            return None
        return await self.repository.update_agent(agent, payload)

    async def delete_agent(self, agent_id: str):
        agent = await self.repository.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.repository.delete_agent(agent)
