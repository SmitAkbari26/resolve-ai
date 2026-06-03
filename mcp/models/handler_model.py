from pydantic import BaseModel


class SendResponse(BaseModel):
    """
    Response model for sending data.

    Attributes:
        id (int): Unique identifier of the response.
        result (dict): Dictionary containing the result payload.
    """

    id: int
    result: dict


class SendErrorMessage(BaseModel):
    """
    Represents an error message to be sent.

    Attributes:
        code (int): Error code.
        message (str): Human-readable error description.
    """

    code: int
    message: str


class SendError(BaseModel):
    """
    Represents an error that occurred while sending a message.

    Attributes:
        id (int): Unique identifier for the error instance.
        error (SendErrorMessage): Detailed information about the send error.
    """

    id: int
    error: SendErrorMessage
