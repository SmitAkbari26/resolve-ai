from register import register_tool
from clients.notification_client import NotificationClient
from tools.notifications.model import (
    GetUserNotificationsRequest,
    ListNotificationsResponse,
    NotificationResponse,
)

notification_client = NotificationClient()


@register_tool(
    name="get_user_notifications",
    description="Get notifications for a user.",
    input_schema=GetUserNotificationsRequest.model_json_schema(),
    output_schema=ListNotificationsResponse.model_json_schema(),
)
async def get_user_notifications_tool(**kwargs):
    """
    Retrieve notifications for a user.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`GetUserNotificationsRequest` (e.g., ``user_id``).

    Returns:
        dict: JSON-serializable representation of a
            :class:`ListNotificationsResponse` containing the user's notifications.
    """
    request = GetUserNotificationsRequest(**kwargs)
    response = await notification_client.get_user_notifications(str(request.user_id))
    validated = ListNotificationsResponse(
        notifications=[
            NotificationResponse.model_validate(item) for item in response["data"]
        ]
    )
    return validated.model_dump(mode="json")
