from uuid import UUID
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class WorkflowStepCreate(BaseModel):
    workflow_execution_id: UUID
    step_name: str
    agent_id: UUID | None = None
    status: str = "pending"
    input_payload: dict[str, Any] = {}
    output_payload: dict[str, Any] = {}


class WorkflowStepUpdate(BaseModel):
    step_name: str | None = None
    agent_id: UUID | None = None
    status: str | None = None
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class WorkflowStepResponse(BaseModel):
    id: UUID
    workflow_execution_id: UUID
    step_name: str
    agent_id: UUID | None
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    class Config:
        from_attributes = True
