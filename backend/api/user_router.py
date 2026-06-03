from db.database import get_db
from services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.user_schema import UserCreate, UserLogin, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
async def create_user_api(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        service = UserService(db)
        return await service.create_user(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[UserResponse])
async def get_users_api(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_api(user_id: str, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_api(
    user_id: str, payload: UserUpdate, db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    user = await service.update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
async def delete_user_api(user_id: str, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    result = await service.login_user(payload)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result
