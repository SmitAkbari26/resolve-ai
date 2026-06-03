from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.customer_profile_service import CustomerProfileService
from schemas.customer_profile_schema import (
    CustomerProfileCreate,
    CustomerProfileUpdate,
    CustomerProfileResponse,
)

router = APIRouter(prefix="/customer-profiles", tags=["Customer Profiles"])


@router.post("", response_model=CustomerProfileResponse)
async def create_profile_api(
    payload: CustomerProfileCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = CustomerProfileService(db)
        return await service.create_profile(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[CustomerProfileResponse])
async def get_profiles_api(db: AsyncSession = Depends(get_db)):
    service = CustomerProfileService(db)
    return await service.get_profiles()


@router.get("/{profile_id}", response_model=CustomerProfileResponse)
async def get_profile_api(profile_id: str, db: AsyncSession = Depends(get_db)):
    service = CustomerProfileService(db)
    profile = await service.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return profile


@router.put("/{profile_id}", response_model=CustomerProfileResponse)
async def update_profile_api(
    profile_id: str, payload: CustomerProfileUpdate, db: AsyncSession = Depends(get_db)
):
    service = CustomerProfileService(db)
    profile = await service.update_profile(profile_id, payload)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return profile


@router.delete("/{profile_id}")
async def delete_profile_api(profile_id: str, db: AsyncSession = Depends(get_db)):
    service = CustomerProfileService(db)
    deleted = await service.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer profile not found")
    return {"message": "Customer profile deleted successfully"}
