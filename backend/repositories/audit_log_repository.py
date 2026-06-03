from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import AuditLogRecord
from schemas.audit_log_schema import AuditLogCreate, AuditLogUpdate


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(self, payload: AuditLogCreate):
        audit_log = AuditLogRecord(
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            action=payload.action,
            agent_name=payload.agent_name,
            details=payload.details,
        )
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_audit_logs(self):
        result = await self.db.execute(select(AuditLogRecord))
        return result.scalars().all()

    async def get_audit_log_by_id(self, audit_log_id: int):
        result = await self.db.execute(
            select(AuditLogRecord).where(AuditLogRecord.id == audit_log_id)
        )
        return result.scalar_one_or_none()

    async def get_audit_logs_by_entity_type(self, entity_type: str):
        result = await self.db.execute(
            select(AuditLogRecord).where(AuditLogRecord.entity_type == entity_type)
        )
        return result.scalars().all()

    async def get_audit_logs_by_entity_id(self, entity_id: str):
        result = await self.db.execute(
            select(AuditLogRecord).where(AuditLogRecord.entity_id == entity_id)
        )
        return result.scalars().all()

    async def update_audit_log(
        self, audit_log: AuditLogRecord, payload: AuditLogUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(audit_log, key, value)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def delete_audit_log(self, audit_log: AuditLogRecord):
        await self.db.delete(audit_log)
        await self.db.commit()
        return True
