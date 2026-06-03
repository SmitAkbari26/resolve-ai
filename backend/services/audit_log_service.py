from sqlalchemy.ext.asyncio import AsyncSession
from repositories.audit_log_repository import AuditLogRepository
from schemas.audit_log_schema import AuditLogCreate, AuditLogUpdate


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.repository = AuditLogRepository(db)

    async def create_audit_log(self, payload: AuditLogCreate):
        return await self.repository.create_audit_log(payload)

    async def get_audit_logs(self):
        return await self.repository.get_audit_logs()

    async def get_audit_log_by_id(self, audit_log_id: int):
        return await self.repository.get_audit_log_by_id(audit_log_id)

    async def get_audit_logs_by_entity_type(self, entity_type: str):
        return await self.repository.get_audit_logs_by_entity_type(entity_type)

    async def get_audit_logs_by_entity_id(self, entity_id: str):
        return await self.repository.get_audit_logs_by_entity_id(entity_id)

    async def update_audit_log(self, audit_log_id: int, payload: AuditLogUpdate):
        audit_log = await self.repository.get_audit_log_by_id(audit_log_id)
        if not audit_log:
            return None
        return await self.repository.update_audit_log(audit_log, payload)

    async def delete_audit_log(self, audit_log_id: int):
        audit_log = await self.repository.get_audit_log_by_id(audit_log_id)
        if not audit_log:
            return False
        return await self.repository.delete_audit_log(audit_log)
