from sqlalchemy import select
from core.security import hash_password
from db.schemas import UserRecord
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, payload: UserCreate):
        try:
            user = UserRecord(
                name=payload.name,
                email=payload.email,
                password_hash=hash_password(payload.password),
                role=payload.role,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except Exception as ex:
            await self.db.rollback()
            print("ERROR:", str(ex))
            raise ex

    async def get_users(self):
        result = await self.db.execute(select(UserRecord))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: str):
        result = await self.db.execute(
            select(UserRecord).where(UserRecord.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(
            select(UserRecord).where(UserRecord.email == email)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user: UserRecord, payload: UserUpdate):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: UserRecord):
        await self.db.delete(user)
        await self.db.commit()
        return True
