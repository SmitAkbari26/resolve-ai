from models.handler_model import SendError, SendErrorMessage


def create_error_message(id, code, message):
    """
    Create a SendError message object.

    Args:
        id (Any): Identifier for the error instance.
        code (int): Error code to include in the message.
        message (str): Human‑readable error description.

    Returns:
        SendError: Constructed SendError object containing the provided error details.
    """
    send_error_message = SendError(
        id=id,
        error=SendErrorMessage(code=code, message=message),
    )

    return send_error_message
