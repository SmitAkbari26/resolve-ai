from models.handler_model import SendResponse


def create_response(id, result):
    """
    Create a SendResponse object with the given identifier and result.

    Args:
        id (Any): Identifier for the response.
        result (Any): Result data to include in the response.

    Returns:
        SendResponse: The constructed response object.
    """
    send_response = SendResponse(id=id, result=result)

    return send_response
