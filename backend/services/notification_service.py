from sqlalchemy.ext.asyncio import AsyncSession
from repositories.notification_repository import NotificationRepository
from schemas.notification_schema import NotificationCreate, NotificationUpdate


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repository = NotificationRepository(db)

    async def create_notification(self, payload: NotificationCreate):
        return await self.repository.create_notification(payload)

    async def get_notifications(self):
        return await self.repository.get_notifications()

    async def get_notification_by_id(self, notification_id: str):
        return await self.repository.get_notification_by_id(notification_id)

    async def get_notifications_by_user_id(self, user_id: str):
        return await self.repository.get_notifications_by_user_id(user_id)

    async def get_notifications_by_status(self, status: str):
        return await self.repository.get_notifications_by_status(status)

    async def update_notification(
        self, notification_id: str, payload: NotificationUpdate
    ):
        notification = await self.repository.get_notification_by_id(notification_id)
        if not notification:
            return None
        return await self.repository.update_notification(notification, payload)

    async def delete_notification(self, notification_id: str):
        notification = await self.repository.get_notification_by_id(notification_id)
        if not notification:
            return False
        return await self.repository.delete_notification(notification)
