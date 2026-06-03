from register import register_tool
from clients.approval_client import ApprovalClient
from tools.approvals.model import CreateApprovalRequest, ApprovalResponse

approval_client = ApprovalClient()


@register_tool(
    name="create_approval",
    description="Create a new approval request.",
    input_schema=CreateApprovalRequest.model_json_schema(),
    output_schema=ApprovalResponse.model_json_schema(),
)
async def create_approval_tool(**kwargs):
    """
    Create a new approval request.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of ``CreateApprovalRequest``.

    Returns:
        dict: JSON-serializable representation of the created ``ApprovalResponse``.
    """
    request = CreateApprovalRequest(**kwargs)
    response = await approval_client.create_approval(request.model_dump())
    validated = ApprovalResponse.model_validate(response["data"])
    return validated.model_dump(mode="json")
