from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.notification_service import NotificationService
from schemas.notification_schema import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("", response_model=NotificationResponse)
async def create_notification_api(
    payload: NotificationCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = NotificationService(db)
        return await service.create_notification(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("", response_model=list[NotificationResponse])
async def get_notifications_api(db: AsyncSession = Depends(get_db)):
    service = NotificationService(db)
    return await service.get_notifications()

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification_api(
    notification_id: str, db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    notification = await service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("/user/{user_id}", response_model=list[NotificationResponse])
async def get_user_notifications_api(user_id: str, db: AsyncSession = Depends(get_db)):
    service = NotificationService(db)
    return await service.get_notifications_by_user_id(user_id)

@router.get("/status/{status}", response_model=list[NotificationResponse])
async def get_status_notifications_api(status: str, db: AsyncSession = Depends(get_db)):
    service = NotificationService(db)
    return await service.get_notifications_by_status(status)

@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification_api(
    notification_id: str,
    payload: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = NotificationService(db)
    notification = await service.update_notification(notification_id, payload)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.delete("/{notification_id}")
async def delete_notification_api(
    notification_id: str, db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    deleted = await service.delete_notification(notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}