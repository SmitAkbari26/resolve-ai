from sqlalchemy.ext.asyncio import AsyncSession
from repositories.ticket_attachment_repository import TicketAttachmentRepository
from schemas.ticket_attachment_schema import (
    TicketAttachmentCreate,
    TicketAttachmentUpdate,
)


class TicketAttachmentService:
    def __init__(self, db: AsyncSession):
        self.repository = TicketAttachmentRepository(db)

    async def create_attachment(self, payload: TicketAttachmentCreate):
        return await self.repository.create_attachment(payload)

    async def get_attachments(self):
        return await self.repository.get_attachments()

    async def get_attachment_by_id(self, attachment_id: str):
        return await self.repository.get_attachment_by_id(attachment_id)

    async def get_attachments_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_attachments_by_ticket_id(ticket_id)

    async def update_attachment(
        self, attachment_id: str, payload: TicketAttachmentUpdate
    ):
        attachment = await self.repository.get_attachment_by_id(attachment_id)
        if not attachment:
            return None
        return await self.repository.update_attachment(attachment, payload)

    async def delete_attachment(self, attachment_id: str):
        attachment = await self.repository.get_attachment_by_id(attachment_id)
        if not attachment:
            return False
        return await self.repository.delete_attachment(attachment)
