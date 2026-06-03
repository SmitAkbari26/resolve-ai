from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import ApprovalRecord
from schemas.approval_schema import ApprovalCreate, ApprovalUpdate


class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_approval(self, payload: ApprovalCreate):
        approval = ApprovalRecord(
            ticket_id=payload.ticket_id,
            approval_type=payload.approval_type,
            reason=payload.reason,
            amount=payload.amount,
            requested_by=payload.requested_by,
        )
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_approvals(self):
        result = await self.db.execute(select(ApprovalRecord))
        return result.scalars().all()

    async def get_approval_by_id(self, approval_id: str):
        result = await self.db.execute(
            select(ApprovalRecord).where(ApprovalRecord.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def get_approvals_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(ApprovalRecord).where(ApprovalRecord.ticket_id == ticket_id)
        )
        return result.scalars().all()

    async def get_approvals_by_status(self, status: str):
        result = await self.db.execute(
            select(ApprovalRecord).where(ApprovalRecord.status == status)
        )
        return result.scalars().all()

    async def update_approval(self, approval: ApprovalRecord, payload: ApprovalUpdate):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(approval, key, value)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def delete_approval(self, approval: ApprovalRecord):
        await self.db.delete(approval)
        await self.db.commit()
        return True
