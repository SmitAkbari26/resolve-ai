from register import register_tool
from clients.approval_client import ApprovalClient
from tools.approvals.model import (
    ApprovalResponse,
    GetTicketApprovalsRequest,
    ListApprovalsResponse,
)

approval_client = ApprovalClient()


@register_tool(
    name="get_ticket_approvals",
    description="Get approvals for a ticket.",
    input_schema=GetTicketApprovalsRequest.model_json_schema(),
    output_schema=ListApprovalsResponse.model_json_schema(),
)
async def get_ticket_approvals_tool(**kwargs):
    """
    Retrieve approvals for a specific ticket.

    Args:
        **kwargs: Arbitrary keyword arguments that match the fields of
            :class:`GetTicketApprovalsRequest` (e.g., ``ticket_id``).

    Returns:
        dict: JSON-serializable representation of a
            :class:`ListApprovalsResponse` containing the list of approvals.
    """
    request = GetTicketApprovalsRequest(**kwargs)

    response = await approval_client.get_ticket_approvals(str(request.ticket_id))

    validated = ListApprovalsResponse(
        approvals=[ApprovalResponse.model_validate(item) for item in response["data"]]
    )

    return validated.model_dump(mode="json")
