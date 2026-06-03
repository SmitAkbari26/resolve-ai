from clients.ticket_client import TicketClient
from tools.tickets.model import UpdateTicketRequest, GetTicketResponse
from register import register_tool

ticket_client = TicketClient()


@register_tool(
    name="update_ticket",
    description="Update an existing support ticket.",
    input_schema=UpdateTicketRequest.model_json_schema(),
    output_schema=GetTicketResponse.model_json_schema(),
)
async def update_ticket_tool(**kwargs):
    """
    Update an existing support ticket.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of ``UpdateTicketRequest``. These are used to construct the request payload.

    Returns:
        dict: JSON-serializable dictionary representing the validated ``GetTicketResponse``.
    """

    request = UpdateTicketRequest(**kwargs).model_dump()
    response = await ticket_client.update_ticket(request["ticket_id"], request)
    validated = GetTicketResponse(**response["data"])
    return validated.model_dump(mode="json")
