from register import register_tool
from clients.notification_client import NotificationClient
from tools.notifications.model import CreateNotificationRequest, NotificationResponse

notification_client = NotificationClient()


@register_tool(
    name="create_notification",
    description="Create a notification.",
    input_schema=CreateNotificationRequest.model_json_schema(),
    output_schema=NotificationResponse.model_json_schema(),
)
async def create_notification_tool(**kwargs):
    """
    Create a notification using the provided request data.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`CreateNotificationRequest`. These are used to construct the
            request object.

    Returns:
        dict: JSON-serializable dictionary representation of a
            :class:`NotificationResponse` instance returned by the notification
            service.
    """
    request = CreateNotificationRequest(**kwargs)
    response = await notification_client.create_notification(request.model_dump())
    validated = NotificationResponse.model_validate(response["data"])
    return validated.model_dump(mode="json")
