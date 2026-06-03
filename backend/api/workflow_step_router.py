from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.workflow_step_service import WorkflowStepService
from schemas.workflow_step_schema import (
    WorkflowStepCreate,
    WorkflowStepUpdate,
    WorkflowStepResponse,
)

router = APIRouter(prefix="/workflow-steps", tags=["Workflow Steps"])


@router.post("", response_model=WorkflowStepResponse)
async def create_workflow_step_api(
    payload: WorkflowStepCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = WorkflowStepService(db)
        return await service.create_workflow_step(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[WorkflowStepResponse])
async def get_workflow_steps_api(db: AsyncSession = Depends(get_db)):
    service = WorkflowStepService(db)
    return await service.get_workflow_steps()


@router.get("/{workflow_step_id}", response_model=WorkflowStepResponse)
async def get_workflow_step_api(
    workflow_step_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowStepService(db)
    workflow_step = await service.get_workflow_step_by_id(workflow_step_id)
    if not workflow_step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    return workflow_step


@router.get(
    "/workflow/{workflow_execution_id}", response_model=list[WorkflowStepResponse]
)
async def get_steps_by_workflow_api(
    workflow_execution_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowStepService(db)
    return await service.get_steps_by_workflow_id(workflow_execution_id)


@router.get("/status/{status}", response_model=list[WorkflowStepResponse])
async def get_steps_by_status_api(status: str, db: AsyncSession = Depends(get_db)):
    service = WorkflowStepService(db)
    return await service.get_steps_by_status(status)


@router.put("/{workflow_step_id}", response_model=WorkflowStepResponse)
async def update_workflow_step_api(
    workflow_step_id: str,
    payload: WorkflowStepUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowStepService(db)
    workflow_step = await service.update_workflow_step(workflow_step_id, payload)
    if not workflow_step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    return workflow_step


@router.delete("/{workflow_step_id}")
async def delete_workflow_step_api(
    workflow_step_id: str, db: AsyncSession = Depends(get_db)
):
    service = WorkflowStepService(db)
    deleted = await service.delete_workflow_step(workflow_step_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    return {"message": "Workflow step deleted successfully"}
