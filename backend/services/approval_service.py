from sqlalchemy.ext.asyncio import AsyncSession
from repositories.approval_repository import ApprovalRepository
from schemas.approval_schema import ApprovalCreate, ApprovalUpdate


class ApprovalService:

    def __init__(self, db: AsyncSession):
        self.repository = ApprovalRepository(db)

    async def create_approval(self, payload: ApprovalCreate):
        return await self.repository.create_approval(payload)

    async def get_approvals(self):
        return await self.repository.get_approvals()

    async def get_approval_by_id(self, approval_id: str):
        return await self.repository.get_approval_by_id(approval_id)

    async def get_approvals_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_approvals_by_ticket_id(ticket_id)

    async def get_approvals_by_status(self, status: str):
        return await self.repository.get_approvals_by_status(status)

    async def update_approval(self, approval_id: str, payload: ApprovalUpdate):
        approval = await self.repository.get_approval_by_id(approval_id)
        if not approval:
            return None
        return await self.repository.update_approval(approval, payload)

    async def delete_approval(self, approval_id: str):
        approval = await self.repository.get_approval_by_id(approval_id)
        if not approval:
            return False
        return await self.repository.delete_approval(approval)
