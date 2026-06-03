from email.message import EmailMessage
import aiosmtplib
from config import SMTP_FROM_EMAIL, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME
from register import register_tool
from clients.notification_client import NotificationClient
from tools.notifications.model import SendEmailRequest, SendEmailResponse

notification_client = NotificationClient()


@register_tool(
    name="send_email",
    description="Send a real email notification.",
    input_schema=SendEmailRequest.model_json_schema(),
    output_schema=SendEmailResponse.model_json_schema(),
)
async def send_email_tool(**kwargs):
    """
    Send an email using SMTP based on provided request data.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`SendEmailRequest` (e.g., ``to``, ``subject``, ``body``).

    Returns:
        dict: JSON-serializable dictionary representation of
            :class:`SendEmailResponse` indicating success and a confirmation message.
    """
    request = SendEmailRequest(**kwargs)
    message = EmailMessage()
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = request.to
    message["Subject"] = request.subject

    message.add_alternative(request.body, subtype="html")
    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
    return SendEmailResponse(
        success=True, message=f"Email sent successfully to {request.to}"
    ).model_dump(mode="json")
