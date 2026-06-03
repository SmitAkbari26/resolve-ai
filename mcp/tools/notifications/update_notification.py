from register import register_tool
from clients.notification_client import NotificationClient
from tools.notifications.model import NotificationResponse, UpdateNotificationRequest

notification_client = NotificationClient()


@register_tool(
    name="update_notification",
    description="Update notification details.",
    input_schema=UpdateNotificationRequest.model_json_schema(),
    output_schema=NotificationResponse.model_json_schema(),
)
async def update_notification_tool(**kwargs):
    """
    Update notification details using provided keyword arguments.

    Args:
        **kwargs (dict): Fields required to construct an UpdateNotificationRequest, typically including
            notification_id and other updatable attributes.

    Returns:
        dict: JSON-serializable representation of the updated NotificationResponse.
    """
    request = UpdateNotificationRequest(**kwargs)
    response = await notification_client.update_notification(
        str(request.notification_id), request.model_dump()
    )
    validated = NotificationResponse.model_validate(response["data"])
    return validated.model_dump(mode="json")
