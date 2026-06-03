from sqlalchemy import select
from db.schemas import TicketCommentRecord
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.ticket_comment_schema import TicketCommentCreate, TicketCommentUpdate


class TicketCommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, payload: TicketCommentCreate):
        comment = TicketCommentRecord(
            ticket_id=payload.ticket_id,
            user_id=payload.user_id,
            comment=payload.comment,
            is_internal=payload.is_internal,
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_comments(self):
        result = await self.db.execute(select(TicketCommentRecord))
        return result.scalars().all()

    async def get_comment_by_id(self, comment_id: str):
        result = await self.db.execute(
            select(TicketCommentRecord).where(TicketCommentRecord.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def get_comments_by_ticket_id(self, ticket_id: str):
        result = await self.db.execute(
            select(TicketCommentRecord).where(
                TicketCommentRecord.ticket_id == ticket_id
            )
        )
        return result.scalars().all()

    async def get_comments_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(TicketCommentRecord).where(TicketCommentRecord.user_id == user_id)
        )
        return result.scalars().all()

    async def update_comment(
        self, comment: TicketCommentRecord, payload: TicketCommentUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment, key, value)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete_comment(self, comment: TicketCommentRecord):
        await self.db.delete(comment)
        await self.db.commit()
        return True
