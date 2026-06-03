from sqlalchemy.ext.asyncio import AsyncSession
from repositories.customer_profile_repository import CustomerProfileRepository
from schemas.customer_profile_schema import CustomerProfileCreate, CustomerProfileUpdate


class CustomerProfileService:
    def __init__(self, db: AsyncSession):
        self.repository = CustomerProfileRepository(db)

    async def create_profile(self, payload: CustomerProfileCreate):
        existing_profile = await self.repository.get_profile_by_user_id(payload.user_id)
        if existing_profile:
            raise Exception("Customer profile already exists")
        return await self.repository.create_profile(payload)

    async def get_profiles(self):
        return await self.repository.get_profiles()

    async def get_profile_by_id(self, profile_id: str):
        return await self.repository.get_profile_by_id(profile_id)

    async def update_profile(self, profile_id: str, payload: CustomerProfileUpdate):
        profile = await self.repository.get_profile_by_id(profile_id)
        if not profile:
            return None
        return await self.repository.update_profile(profile, payload)

    async def delete_profile(self, profile_id: str):
        profile = await self.repository.get_profile_by_id(profile_id)
        if not profile:
            return False
        return await self.repository.delete_profile(profile)
