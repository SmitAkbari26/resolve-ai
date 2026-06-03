from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import WorkflowExecutionRecord
from schemas.workflow_execution_schema import (
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
)


class WorkflowExecutionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(self, payload: WorkflowExecutionCreate):
        workflow = WorkflowExecutionRecord(
            ticket_id=payload.ticket_id,
            workflow_type=payload.workflow_type,
            current_step=payload.current_step,
            status=payload.status,
            created_by=payload.created_by,
        )
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def get_workflows(self):
        result = await self.db.execute(select(WorkflowExecutionRecord))
        return result.scalars().all()

    async def get_workflow_by_id(self, workflow_id: str):
        result = await self.db.execute(
            select(WorkflowExecutionRecord).where(
                WorkflowExecutionRecord.id == workflow_id
            )
        )
        return result.scalar_one_or_none()

    async def get_workflows_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(WorkflowExecutionRecord).where(
                WorkflowExecutionRecord.ticket_id == ticket_id
            )
        )
        return result.scalars().all()

    async def get_workflows_by_status(self, status: str):
        result = await self.db.execute(
            select(WorkflowExecutionRecord).where(
                WorkflowExecutionRecord.status == status
            )
        )
        return result.scalars().all()

    async def update_workflow(
        self, workflow: WorkflowExecutionRecord, payload: WorkflowExecutionUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(workflow, key, value)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow: WorkflowExecutionRecord):
        await self.db.delete(workflow)
        await self.db.commit()
        return True
