from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.approval_service import ApprovalService
from schemas.approval_schema import ApprovalCreate, ApprovalUpdate, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("", response_model=ApprovalResponse)
async def create_approval_api(
    payload: ApprovalCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = ApprovalService(db)
        return await service.create_approval(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[ApprovalResponse])
async def get_approvals_api(db: AsyncSession = Depends(get_db)):
    service = ApprovalService(db)
    return await service.get_approvals()


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval_api(approval_id: str, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(db)
    approval = await service.get_approval_by_id(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.get("/ticket/{ticket_id}", response_model=list[ApprovalResponse])
async def get_ticket_approvals_api(ticket_id: str, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(db)
    return await service.get_approvals_by_ticket_id(ticket_id)


@router.get("/status/{status}", response_model=list[ApprovalResponse])
async def get_status_approvals_api(status: str, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(db)
    return await service.get_approvals_by_status(status)


@router.put("/{approval_id}", response_model=ApprovalResponse)
async def update_approval_api(
    approval_id: str, payload: ApprovalUpdate, db: AsyncSession = Depends(get_db)
):
    service = ApprovalService(db)
    approval = await service.update_approval(approval_id, payload)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.delete("/{approval_id}")
async def delete_approval_api(approval_id: str, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(db)
    deleted = await service.delete_approval(approval_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Approval not found")
    return {"message": "Approval deleted successfully"}
