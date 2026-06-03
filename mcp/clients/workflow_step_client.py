from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class WorkflowStepClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="workflow-steps")

    async def create_workflow_step(
        self,
        workflow_execution_id: str,
        step_name: str,
        agent_id: str | None = None,
        status: str = "pending",
        input_payload: dict = {},
        output_payload: dict = {},
    ):
        payload = {
            "workflow_execution_id": workflow_execution_id,
            "step_name": step_name,
            "agent_id": agent_id,
            "status": status,
            "input_payload": input_payload,
            "output_payload": output_payload,
        }
        return await self.post(payload=payload)

    async def get_workflow_step(self, workflow_step_id: str):
        return await self.get(path=f"/{workflow_step_id}")

    async def list_workflow_steps(self, workflow_execution_id: str):
        return await self.get(path=f"/workflow/{workflow_execution_id}")

    async def list_steps_by_status(self, status: str):
        return await self.get(path=f"/status/{status}")

    async def update_workflow_step(
        self,
        workflow_step_id: str,
        status: str | None = None,
        output_payload: dict | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        error_message: str | None = None,
    ):
        payload = {}
        if status is not None:
            payload["status"] = status
        if output_payload is not None:
            payload["output_payload"] = output_payload
        if started_at is not None:
            payload["started_at"] = started_at
        if completed_at is not None:
            payload["completed_at"] = completed_at
        if error_message is not None:
            payload["error_message"] = error_message
        return await self.put(path=f"/{workflow_step_id}", payload=payload)

    async def delete_workflow_step(self, workflow_step_id: str):
        return await self.delete(path=f"/{workflow_step_id}")
