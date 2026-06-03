from sqlalchemy.ext.asyncio import AsyncSession
from repositories.policy_repository import PolicyRepository
from schemas.policy_schema import PolicyCreate, PolicyUpdate


class PolicyService:
    def __init__(self, db: AsyncSession):

        self.repository = PolicyRepository(db)

    async def create_policy(self, payload: PolicyCreate):
        return await self.repository.create_policy(payload)

    async def get_policies(self):
        return await self.repository.get_policies()

    async def get_policy_by_id(self, policy_id: str):
        return await self.repository.get_policy_by_id(policy_id)

    async def get_policies_by_category(self, category: str):
        return await self.repository.get_policies_by_category(category)

    async def get_active_policies(self):
        return await self.repository.get_active_policies()

    async def update_policy(self, policy_id: str, payload: PolicyUpdate):
        policy = await self.repository.get_policy_by_id(policy_id)
        if not policy:
            return None
        return await self.repository.update_policy(policy, payload)

    async def delete_policy(self, policy_id: str):
        policy = await self.repository.get_policy_by_id(policy_id)
        if not policy:
            return False
        return await self.repository.delete_policy(policy)
