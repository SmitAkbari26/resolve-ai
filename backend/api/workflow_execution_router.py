"""
Resolve AI - Workflow Execution Router

CRUD endpoints for WorkflowExecution records PLUS the critical
POST /{workflow_id}/resume endpoint for post-approval continuation.
"""

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.workflow_service import WorkflowService
from services.workflow_execution_service import WorkflowExecutionService
from schemas.workflow_execution_schema import (
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
    WorkflowExecutionResponse,
)

router = APIRouter(prefix="/workflow-executions", tags=["Workflow Executions"])


# ─── Request schema for the resume endpoint ────────────────

class WorkflowResumeRequest(BaseModel):
    approval_decision: str     # "approved" | "rejected"
    decided_by: str = "system"


# ─── Chat / Trigger endpoint ───────────────────────────────

class WorkflowRunRequest(BaseModel):
    user_query: str
    conversation_id: str
    user_id: str = ""
    user_email: str = ""
    ticket_id: str = ""


@router.post("/run")
async def run_workflow_api(
    payload: WorkflowRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a fresh workflow for a customer query.
    Returns the final state including ai_response, plan, status.
    """
    try:
        service = WorkflowService(db)
        result = await service.execute_workflow(
            user_query=payload.user_query,
            conversation_id=payload.conversation_id,
            user_id=payload.user_id,
            user_email=payload.user_email,
            ticket_id=payload.ticket_id,
        )
        return result
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# ─── Resume a paused workflow ──────────────────────────────

@router.post("/{workflow_id}/resume")
async def resume_workflow_api(
    workflow_id: str,
    payload: WorkflowResumeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a paused workflow after a human approval decision.

    workflow_id:  The in-memory WRK-XXXXXXXX identifier returned
                  when the workflow was first paused.
    """
    if payload.approval_decision not in ("approved", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="approval_decision must be 'approved' or 'rejected'",
        )

    try:
        service = WorkflowService(db)
        result = await service.resume_workflow(
            workflow_id=workflow_id,
            approval_decision=payload.approval_decision,
            decided_by=payload.decided_by,
        )

        if result.get("status") == "failed" and "not found" in result.get(
            "error", ""
        ):
            raise HTTPException(
                status_code=404,
                detail=result.get("error"),
            )

        return result
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# ─── Standard CRUD endpoints ───────────────────────────────

@router.post("", response_model=WorkflowExecutionResponse)
async def create_workflow_api(
    payload: WorkflowExecutionCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = WorkflowExecutionService(db)
        return await service.create_workflow(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[WorkflowExecutionResponse])
async def get_workflows_api(db: AsyncSession = Depends(get_db)):
    service = WorkflowExecutionService(db)
    return await service.get_workflows()


@router.get("/{workflow_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_api(
    workflow_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowExecutionService(db)
    workflow = await service.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail="Workflow execution not found"
        )
    return workflow


@router.get(
    "/ticket/{ticket_id}", response_model=list[WorkflowExecutionResponse]
)
async def get_ticket_workflows_api(
    ticket_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowExecutionService(db)
    return await service.get_workflows_by_ticket_id(ticket_id)


@router.get(
    "/status/{status}", response_model=list[WorkflowExecutionResponse]
)
async def get_status_workflows_api(
    status: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowExecutionService(db)
    return await service.get_workflows_by_status(status)


@router.put("/{workflow_id}", response_model=WorkflowExecutionResponse)
async def update_workflow_api(
    workflow_id: str,
    payload: WorkflowExecutionUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowExecutionService(db)
    workflow = await service.update_workflow(workflow_id, payload)
    if not workflow:
        raise HTTPException(
            status_code=404, detail="Workflow execution not found"
        )
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow_api(
    workflow_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowExecutionService(db)
    deleted = await service.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Workflow execution not found"
        )
    return {"message": "Workflow execution deleted successfully"}
