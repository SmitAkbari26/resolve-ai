from sqlalchemy.ext.asyncio import AsyncSession
from repositories.ticket_comment_repository import TicketCommentRepository
from schemas.ticket_comment_schema import TicketCommentCreate, TicketCommentUpdate


class TicketCommentService:
    def __init__(self, db: AsyncSession):
        self.repository = TicketCommentRepository(db)

    async def create_comment(self, payload: TicketCommentCreate):
        return await self.repository.create_comment(payload)

    async def get_comments(self):
        return await self.repository.get_comments()

    async def get_comment_by_id(self, comment_id: str):
        return await self.repository.get_comment_by_id(comment_id)

    async def get_comments_by_ticket_id(self, ticket_id: str):
        return await self.repository.get_comments_by_ticket_id(ticket_id)

    async def get_comments_by_user_id(self, user_id: str):
        return await self.repository.get_comments_by_user_id(user_id)

    async def update_comment(self, comment_id: str, payload: TicketCommentUpdate):
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            return None
        return await self.repository.update_comment(comment, payload)

    async def delete_comment(self, comment_id: str):
        comment = await self.repository.get_comment_by_id(comment_id)
        if not comment:
            return False
        return await self.repository.delete_comment(comment)
