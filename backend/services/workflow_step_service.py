from sqlalchemy.ext.asyncio import AsyncSession
from repositories.workflow_step_repository import WorkflowStepRepository
from schemas.workflow_step_schema import WorkflowStepCreate, WorkflowStepUpdate


class WorkflowStepService:

    def __init__(self, db: AsyncSession):
        self.repository = WorkflowStepRepository(db)

    async def create_workflow_step(self, payload: WorkflowStepCreate):
        return await self.repository.create_workflow_step(payload)

    async def get_workflow_steps(self):
        return await self.repository.get_workflow_steps()

    async def get_workflow_step_by_id(self, workflow_step_id: str):
        return await self.repository.get_workflow_step_by_id(workflow_step_id)

    async def get_steps_by_workflow_id(self, workflow_execution_id: str):
        return await self.repository.get_steps_by_workflow_id(workflow_execution_id)

    async def get_steps_by_status(self, status: str):
        return await self.repository.get_steps_by_status(status)

    async def update_workflow_step(
        self, workflow_step_id: str, payload: WorkflowStepUpdate
    ):
        workflow_step = await self.repository.get_workflow_step_by_id(workflow_step_id)
        if not workflow_step:
            return None
        return await self.repository.update_workflow_step(workflow_step, payload)

    async def delete_workflow_step(self, workflow_step_id: str):
        workflow_step = await self.repository.get_workflow_step_by_id(workflow_step_id)
        if not workflow_step:
            return False
        return await self.repository.delete_workflow_step(workflow_step)
