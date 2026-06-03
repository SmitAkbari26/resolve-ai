from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class WorkflowExecutionClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="workflow-executions")

    async def create_workflow(
        self,
        ticket_id: str,
        workflow_type: str,
        current_step: str | None = None,
        status: str = "pending",
        created_by: str | None = None,
    ):
        payload = {
            "ticket_id": ticket_id,
            "workflow_type": workflow_type,
            "current_step": current_step,
            "status": status,
            "created_by": created_by,
        }
        return await self.post(payload=payload)

    async def get_workflow(self, workflow_id: str):
        return await self.get(path=f"/{workflow_id}")

    async def list_workflows(self, status: Optional[str] = None):
        if status:
            return await self.get(path=f"/status/{status}")
        return await self.get()

    async def get_ticket_workflows(self, ticket_id: str):
        return await self.get(path=f"/ticket/{ticket_id}")

    async def update_workflow(
        self,
        workflow_id: str,
        current_step: str | None = None,
        status: str | None = None,
        completed_at: str | None = None,
        failed_reason: str | None = None,
    ):
        payload = {}
        if current_step is not None:
            payload["current_step"] = current_step
        if status is not None:
            payload["status"] = status
        if completed_at is not None:
            payload["completed_at"] = completed_at
        if failed_reason is not None:
            payload["failed_reason"] = failed_reason
        return await self.put(path=f"/{workflow_id}", payload=payload)

    async def delete_workflow(self, workflow_id: str):
        return await self.delete(path=f"/{workflow_id}")
