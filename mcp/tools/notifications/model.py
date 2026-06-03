from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class CreateNotificationRequest(BaseModel):
    """
    CreateNotificationRequest model.

    Attributes:
        user_id (str): Identifier of the user to receive the notification.
        notification_type (str): Type/category of the notification.
        message (str): Content of the notification message.
        ticket_id (Optional[UUID]): Associated ticket identifier, if applicable.
        channel (str): Delivery channel for the notification (default "email").
        subject (Optional[str]): Subject line for the notification, if applicable.
        status (str): Current status of the notification (default "pending").
    """

    user_id: str
    notification_type: str
    message: str
    ticket_id: Optional[UUID] = None
    channel: str = "email"
    subject: Optional[str] = None
    status: str = "pending"


class NotificationResponse(BaseModel):
    """
    Response model for notifications.

    Attributes:
        id (UUID): Unique identifier of the notification response.
        user_id (UUID): Identifier of the user associated with the notification.
        ticket_id (Optional[UUID]): Identifier of the related ticket, if applicable.
        notification_type (str): Type of the notification (e.g., alert, reminder).
        channel (str): Communication channel used (e.g., email, SMS).
        subject (Optional[str]): Subject line of the notification, if applicable.
        message (str): Content of the notification message.
        status (str): Current status of the notification (e.g., sent, failed).
        sent_at (Optional[str]): Timestamp when the notification was sent, if sent.
        created_at (str): Timestamp when the notification response was created.
    """

    id: UUID
    user_id: UUID
    ticket_id: Optional[UUID] = None
    notification_type: str
    channel: str
    subject: Optional[str] = None
    message: str
    status: str
    sent_at: Optional[str] = None
    created_at: str


class GetNotificationRequest(BaseModel):
    """
    Request model for retrieving a notification.

    Attributes:
        notification_id (str): Identifier of the notification to retrieve.
    """

    notification_id: str


class ListNotificationsRequest(BaseModel):
    """
    Request model for listing notifications.

    Attributes:
        status (Optional[str]): Filter notifications by status. If None, no status filtering is applied.
    """

    status: Optional[str] = None


class GetUserNotificationsRequest(BaseModel):
    """
    Request model for retrieving notifications for a specific user.

    Attributes:
        user_id (str): Identifier of the user whose notifications are being requested.
    """

    user_id: str


class UpdateNotificationRequest(BaseModel):
    """
    UpdateNotificationRequest model.

    Attributes:
        notification_id (str): Unique identifier of the notification.
        status (Optional[str]): Current status of the notification (e.g., 'sent', 'failed').
        sent_at (Optional[str]): ISO‑8601 timestamp when the notification was sent.
        subject (Optional[str]): Subject line of the notification message.
        message (Optional[str]): Body content of the notification.
    """

    notification_id: str
    status: Optional[str] = None
    sent_at: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None


class ListNotificationsResponse(BaseModel):
    """
    Response model containing a list of notifications.

    Attributes:
        notifications (list[NotificationResponse]): Collection of notification details.
    """

    notifications: list[NotificationResponse]


class SendEmailRequest(BaseModel):
    """
    SendEmailRequest model representing an email to be sent.

    Attributes:
        to (str): Recipient email address.
        subject (str): Subject line of the email.
        body (str): Content of the email message.
    """

    to: str
    subject: str
    body: str


class SendEmailResponse(BaseModel):
    """
    Response model for sending an email.

    Attributes:
        success (bool): Indicates whether the email was sent successfully.
        message (Optional[str]): Optional success message providing additional information.
        error (Optional[str]): Optional error message describing why the email could not be sent.
    """

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
