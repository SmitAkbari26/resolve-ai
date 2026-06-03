from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.audit_log_service import AuditLogService
from schemas.audit_log_schema import AuditLogCreate, AuditLogUpdate, AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.post("", response_model=AuditLogResponse)
async def create_audit_log_api(
    payload: AuditLogCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = AuditLogService(db)
        return await service.create_audit_log(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[AuditLogResponse])
async def get_audit_logs_api(db: AsyncSession = Depends(get_db)):
    service = AuditLogService(db)
    return await service.get_audit_logs()


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log_api(audit_log_id: int, db: AsyncSession = Depends(get_db)):
    service = AuditLogService(db)
    audit_log = await service.get_audit_log_by_id(audit_log_id)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log


@router.get("/entity-type/{entity_type}", response_model=list[AuditLogResponse])
async def get_audit_logs_by_entity_type_api(
    entity_type: str, db: AsyncSession = Depends(get_db)
):
    service = AuditLogService(db)
    return await service.get_audit_logs_by_entity_type(entity_type)


@router.get("/entity-id/{entity_id}", response_model=list[AuditLogResponse])
async def get_audit_logs_by_entity_id_api(
    entity_id: str, db: AsyncSession = Depends(get_db)
):
    service = AuditLogService(db)
    return await service.get_audit_logs_by_entity_id(entity_id)


@router.put("/{audit_log_id}", response_model=AuditLogResponse)
async def update_audit_log_api(
    audit_log_id: int, payload: AuditLogUpdate, db: AsyncSession = Depends(get_db)
):
    service = AuditLogService(db)
    audit_log = await service.update_audit_log(audit_log_id, payload)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log


@router.delete("/{audit_log_id}")
async def delete_audit_log_api(audit_log_id: int, db: AsyncSession = Depends(get_db)):
    service = AuditLogService(db)
    deleted = await service.delete_audit_log(audit_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return {"message": "Audit log deleted successfully"}
