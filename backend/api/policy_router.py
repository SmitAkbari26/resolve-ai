from uuid import UUID

from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.policy_service import PolicyService
from schemas.policy_schema import PolicyCreate, PolicyUpdate, PolicyResponse
from core.security import require_role

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.post("", response_model=PolicyResponse)
async def create_policy_api(
    payload: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    try:
        service = PolicyService(db)
        return await service.create_policy(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[PolicyResponse])
async def get_policies_api(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager"])),
):
    service = PolicyService(db)
    return await service.get_policies()


@router.get("/category/{category}", response_model=list[PolicyResponse])
async def get_policies_by_category_api(
    category: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager"])),
):
    service = PolicyService(db)
    return await service.get_policies_by_category(category)


@router.get("/active/list", response_model=list[PolicyResponse])
async def get_active_policies_api(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager"])),
):
    service = PolicyService(db)
    return await service.get_active_policies()


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy_api(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager"])),
):
    service = PolicyService(db)
    policy = await service.get_policy_by_id(str(policy_id))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy_api(
    policy_id: UUID,
    payload: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = PolicyService(db)
    policy = await service.update_policy(str(policy_id), payload)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.delete("/{policy_id}")
async def delete_policy_api(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = PolicyService(db)
    deleted = await service.delete_policy(str(policy_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}

