from register import register_tool
from clients.notification_client import NotificationClient
from tools.notifications.model import (
    GetNotificationRequest,
    ListNotificationsRequest,
    ListNotificationsResponse,
    NotificationResponse,
)

notification_client = NotificationClient()


@register_tool(
    name="get_notification",
    description="Get notification details.",
    input_schema=GetNotificationRequest.model_json_schema(),
    output_schema=NotificationResponse.model_json_schema(),
)
async def get_notification_tool(**kwargs):
    """
    Retrieve notification details using provided parameters.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`GetNotificationRequest` (e.g., ``notification_id``).

    Returns:
        dict: JSON-serializable representation of a
            :class:`NotificationResponse` containing the notification data.
    """
    request = GetNotificationRequest(**kwargs)
    response = await notification_client.get_notification(str(request.notification_id))
    validated = NotificationResponse.model_validate(response["data"])
    return validated.model_dump(mode="json")


@register_tool(
    name="list_notifications",
    description="List notifications optionally filtered by status.",
    input_schema=ListNotificationsRequest.model_json_schema(),
    output_schema=ListNotificationsResponse.model_json_schema(),
)
async def list_notifications_tool(**kwargs):
    """
    List notifications optionally filtered by status.

    Args:
        **kwargs (dict): Keyword arguments matching the fields of
            :class:`ListNotificationsRequest` (e.g., ``status``).

    Returns:
        dict: JSON‑serializable dictionary representing a
            :class:`ListNotificationsResponse` containing the list of
            notifications.
    """
    request = ListNotificationsRequest(**kwargs)
    response = await notification_client.list_notifications(request.status)
    validated = ListNotificationsResponse(
        notifications=[
            NotificationResponse.model_validate(item) for item in response["data"]
        ]
    )
    return validated.model_dump(mode="json")
