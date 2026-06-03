from clients.ticket_client import TicketClient
from register import register_tool
from tools.tickets.model import GetTicketRequest, GetTicketResponse, ListTicketsResponse

ticket_client = TicketClient()


@register_tool(
    name="get_ticket",
    description="Retrieve ticket details using ticket ID.",
    input_schema=GetTicketRequest.model_json_schema(),
    output_schema=GetTicketResponse.model_json_schema(),
)
async def get_ticket_tool(**kwargs):
    """
    Retrieve ticket details using ticket ID.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`GetTicketRequest`. Must include ``ticket_id``.

    Returns:
        dict: JSON-serializable dictionary representing a
            :class:`GetTicketResponse` instance.
    """

    request = GetTicketRequest(**kwargs).model_dump()
    response = await ticket_client.get_ticket(request["ticket_id"])
    validated = GetTicketResponse(**response["data"])
    return validated.model_dump(mode="json")


@register_tool(
    name="list_tickets",
    description="List support tickets optionally filtered by status.",
    input_schema=GetTicketRequest.model_json_schema(),
    output_schema=GetTicketResponse.model_json_schema(),
)
async def list_tickets_tool(**kwargs):
    """
    List support tickets optionally filtered by status.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of GetTicketRequest.

    Returns:
        dict: JSON-serializable dictionary representation of ListTicketsResponse containing the retrieved tickets.
    """

    request = GetTicketRequest(**kwargs).model_dump()
    response = await ticket_client.list_tickets(request["status"])
    validated = ListTicketsResponse(
        tickets=[GetTicketResponse(**ticket) for ticket in response["data"]]
    )
    return validated.model_dump(mode="json")
