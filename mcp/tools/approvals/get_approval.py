from register import register_tool
from clients.approval_client import ApprovalClient
from tools.approvals.model import (
    ApprovalResponse,
    GetApprovalRequest,
    ListApprovalsRequest,
    ListApprovalsResponse,
)

approval_client = ApprovalClient()


@register_tool(
    name="get_approval",
    description="Get approval details.",
    input_schema=GetApprovalRequest.model_json_schema(),
    output_schema=ApprovalResponse.model_json_schema(),
)
async def get_approval_tool(**kwargs):
    """
    Retrieve approval details using provided parameters.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`GetApprovalRequest` (e.g., ``approval_id``).

    Returns:
        dict: JSON-serializable representation of an
            :class:`ApprovalResponse` containing the approval details.
    """
    request = GetApprovalRequest(**kwargs)
    response = await approval_client.get_approval(str(request.approval_id))
    validated = ApprovalResponse.model_validate(response["data"])
    return validated.model_dump(mode="json")


@register_tool(
    name="list_approvals",
    description="List approvals optionally filtered by status.",
    input_schema=ListApprovalsRequest.model_json_schema(),
    output_schema=ListApprovalsResponse.model_json_schema(),
)
async def list_approvals_tool(**kwargs):
    """
    List approvals optionally filtered by status.

    Args:
        **kwargs: Keyword arguments matching the fields of ListApprovalsRequest (e.g., `status`).

    Returns:
        dict: JSON-serializable dictionary representing a ListApprovalsResponse, containing a list of approvals.
    """
    request = ListApprovalsRequest(**kwargs)
    response = await approval_client.list_approvals(request.status)
    validated = ListApprovalsResponse(
        approvals=[ApprovalResponse.model_validate(item) for item in response["data"]]
    )
    return validated.model_dump(mode="json")
