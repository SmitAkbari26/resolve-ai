from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from repositories.user_repository import UserRepository
from core.security import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def create_user(self, payload: UserCreate):
        return await self.repository.create_user(payload)

    async def get_users(self):
        return await self.repository.get_users()

    async def get_user_by_id(self, user_id: str):
        return await self.repository.get_user_by_id(user_id)

    async def update_user(self, user_id: str, payload: UserUpdate):
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            return None
        return await self.repository.update_user(user, payload)

    async def delete_user(self, user_id: str):
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            return False
        return await self.repository.delete_user(user)

    async def login_user(self, payload: UserLogin):

        user = await self.repository.get_user_by_email(payload.email)

        if not user:
            return None

        valid_password = verify_password(payload.password, user.password_hash)

        if not valid_password:
            return None

        token = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": user.role}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "user_id": str(user.id),
            "email": user.email,
        }
