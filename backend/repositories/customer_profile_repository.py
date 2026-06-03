from sqlalchemy import select
from db.schemas import CustomerProfileRecord
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.customer_profile_schema import CustomerProfileCreate, CustomerProfileUpdate


class CustomerProfileRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(self, payload: CustomerProfileCreate):
        profile = CustomerProfileRecord(
            user_id=payload.user_id,
            phone=payload.phone,
            company=payload.company,
            subscription_plan=payload.subscription_plan,
            preferred_language=payload.preferred_language,
            timezone=payload.timezone,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_profiles(self):
        result = await self.db.execute(select(CustomerProfileRecord))
        return result.scalars().all()

    async def get_profile_by_id(self, profile_id: str):
        result = await self.db.execute(
            select(CustomerProfileRecord).where(CustomerProfileRecord.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(CustomerProfileRecord).where(
                CustomerProfileRecord.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self, profile: CustomerProfileRecord, payload: CustomerProfileUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete_profile(self, profile: CustomerProfileRecord):
        await self.db.delete(profile)
        await self.db.commit()
        return True