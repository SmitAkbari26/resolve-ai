from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import TicketAttachmentRecord
from schemas.ticket_attachment_schema import (
    TicketAttachmentCreate,
    TicketAttachmentUpdate,
)


class TicketAttachmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_attachment(self, payload: TicketAttachmentCreate):
        attachment = TicketAttachmentRecord(
            ticket_id=payload.ticket_id,
            file_name=payload.file_name,
            file_path=payload.file_path,
            file_type=payload.file_type,
            uploaded_by=payload.uploaded_by,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def get_attachments(self):
        result = await self.db.execute(select(TicketAttachmentRecord))
        return result.scalars().all()

    async def get_attachment_by_id(self, attachment_id: str):
        result = await self.db.execute(
            select(TicketAttachmentRecord).where(
                TicketAttachmentRecord.id == attachment_id
            )
        )
        return result.scalar_one_or_none()

    async def get_attachments_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(TicketAttachmentRecord).where(
                TicketAttachmentRecord.ticket_id == ticket_id
            )
        )
        return result.scalars().all()

    async def update_attachment(
        self, attachment: TicketAttachmentRecord, payload: TicketAttachmentUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attachment, key, value)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def delete_attachment(self, attachment: TicketAttachmentRecord):
        await self.db.delete(attachment)
        await self.db.commit()
        return True
