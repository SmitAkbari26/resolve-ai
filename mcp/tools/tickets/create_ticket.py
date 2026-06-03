from clients.ticket_client import TicketClient
from register import register_tool
from tools.tickets.model import CreateTicketRequest, CreateTicketResponse

ticket_client = TicketClient()


@register_tool(
    name="create_ticket",
    description="Create a new customer support ticket.",
    input_schema=CreateTicketRequest.model_json_schema(),
    output_schema=CreateTicketResponse.model_json_schema(),
)
async def create_ticket_tool(**kwargs):
    """
    Create a new customer support ticket.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of ``CreateTicketRequest``.

    Returns:
        dict: JSON-serializable dictionary representing the created ticket, conforming to ``CreateTicketResponse`` schema.
    """

    request = CreateTicketRequest(**kwargs)

    response = await ticket_client.create_ticket(request.model_dump())
    validated = CreateTicketResponse(**response["data"])
    return validated.model_dump(mode="json")
