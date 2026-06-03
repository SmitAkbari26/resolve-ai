from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import WorkflowStepRecord
from schemas.workflow_step_schema import WorkflowStepCreate, WorkflowStepUpdate


class WorkflowStepRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow_step(self, payload: WorkflowStepCreate):
        workflow_step = WorkflowStepRecord(
            workflow_execution_id=payload.workflow_execution_id,
            step_name=payload.step_name,
            agent_id=payload.agent_id,
            status=payload.status,
            input_payload=payload.input_payload,
            output_payload=payload.output_payload,
        )
        self.db.add(workflow_step)
        await self.db.commit()
        await self.db.refresh(workflow_step)
        return workflow_step

    async def get_workflow_steps(self):
        result = await self.db.execute(select(WorkflowStepRecord))
        return result.scalars().all()

    async def get_workflow_step_by_id(self, workflow_step_id: str):
        result = await self.db.execute(
            select(WorkflowStepRecord).where(WorkflowStepRecord.id == workflow_step_id)
        )
        return result.scalar_one_or_none()

    async def get_steps_by_workflow_id(self, workflow_execution_id: str):
        result = await self.db.execute(
            select(WorkflowStepRecord).where(
                WorkflowStepRecord.workflow_execution_id == workflow_execution_id
            )
        )
        return result.scalars().all()

    async def get_steps_by_status(self, status: str):
        result = await self.db.execute(
            select(WorkflowStepRecord).where(WorkflowStepRecord.status == status)
        )
        return result.scalars().all()

    async def update_workflow_step(
        self, workflow_step: WorkflowStepRecord, payload: WorkflowStepUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(workflow_step, key, value)
        await self.db.commit()
        await self.db.refresh(workflow_step)
        return workflow_step

    async def delete_workflow_step(self, workflow_step: WorkflowStepRecord):
        await self.db.delete(workflow_step)
        await self.db.commit()
        return True
