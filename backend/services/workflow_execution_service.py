from sqlalchemy.ext.asyncio import AsyncSession
from repositories.workflow_execution_repository import WorkflowExecutionRepository
from schemas.workflow_execution_schema import (
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
)


class WorkflowExecutionService:

    def __init__(self, db: AsyncSession):
        self.repository = WorkflowExecutionRepository(db)

    async def create_workflow(self, payload: WorkflowExecutionCreate):
        return await self.repository.create_workflow(payload)

    async def get_workflows(self):
        return await self.repository.get_workflows()

    async def get_workflow_by_id(self, workflow_id: str):
        return await self.repository.get_workflow_by_id(workflow_id)

    async def get_workflows_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_workflows_by_ticket_id(ticket_id)

    async def get_workflows_by_status(self, status: str):
        return await self.repository.get_workflows_by_status(status)

    async def update_workflow(self, workflow_id: str, payload: WorkflowExecutionUpdate):
        workflow = await self.repository.get_workflow_by_id(workflow_id)
        if not workflow:
            return None
        return await self.repository.update_workflow(workflow, payload)

    async def delete_workflow(self, workflow_id: str):
        workflow = await self.repository.get_workflow_by_id(workflow_id)
        if not workflow:
            return False
        return await self.repository.delete_workflow(workflow)
