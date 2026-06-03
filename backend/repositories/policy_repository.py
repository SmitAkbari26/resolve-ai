from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import PolicyRecord
from schemas.policy_schema import PolicyCreate, PolicyUpdate


class PolicyRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_policy(self, payload: PolicyCreate):
        policy = PolicyRecord(
            title=payload.title,
            category=payload.category,
            content=payload.content,
            active=payload.active,
            version=payload.version,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def get_policies(self):
        result = await self.db.execute(select(PolicyRecord))
        return result.scalars().all()

    async def get_policy_by_id(self, policy_id: str):
        result = await self.db.execute(
            select(PolicyRecord).where(PolicyRecord.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def get_policies_by_category(self, category: str):
        result = await self.db.execute(
            select(PolicyRecord).where(PolicyRecord.category == category)
        )
        return result.scalars().all()

    async def get_active_policies(self):
        result = await self.db.execute(
            select(PolicyRecord).where(PolicyRecord.active == True)
        )
        return result.scalars().all()

    async def update_policy(self, policy: PolicyRecord, payload: PolicyUpdate):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def delete_policy(self, policy: PolicyRecord):
        await self.db.delete(policy)
        await self.db.commit()
        return True
