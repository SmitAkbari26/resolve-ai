from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import NotificationRecord
from schemas.notification_schema import NotificationCreate, NotificationUpdate


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, payload: NotificationCreate):
        notification = NotificationRecord(
            user_id=payload.user_id,
            ticket_id=payload.ticket_id,
            notification_type=payload.notification_type,
            channel=payload.channel,
            subject=payload.subject,
            message=payload.message,
            status=payload.status,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notifications(self):
        result = await self.db.execute(select(NotificationRecord))
        return result.scalars().all()

    async def get_notification_by_id(self, notification_id: str):
        result = await self.db.execute(
            select(NotificationRecord).where(NotificationRecord.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_notifications_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(NotificationRecord).where(NotificationRecord.user_id == user_id)
        )
        return result.scalars().all()

    async def get_notifications_by_status(self, status: str):
        result = await self.db.execute(
            select(NotificationRecord).where(NotificationRecord.status == status)
        )
        return result.scalars().all()

    async def update_notification(
        self, notification: NotificationRecord, payload: NotificationUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(notification, key, value)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete_notification(self, notification: NotificationRecord):
        await self.db.delete(notification)
        await self.db.commit()
        return True
