from register import register_tool
from clients.approval_client import ApprovalClient
from tools.approvals.model import (
    ApprovalResponse,
    UpdateApprovalRequest,
)

approval_client = ApprovalClient()


@register_tool(
    name="update_approval",
    description="Update approval status or decision.",
    input_schema=UpdateApprovalRequest.model_json_schema(),
    output_schema=ApprovalResponse.model_json_schema(),
)
async def update_approval_tool(**kwargs):
    """
    Update approval status or decision using provided parameters.

    Args:
        **kwargs: Arbitrary keyword arguments matching the fields of
            :class:`UpdateApprovalRequest` (e.g., approval_id, decision, etc.).

    Returns:
        dict: JSON-serializable dictionary representing the validated
            :class:`ApprovalResponse`.
    """
    request = UpdateApprovalRequest(**kwargs)

    response = await approval_client.update_approval(
        str(request.approval_id), request.model_dump()
    )

    validated = ApprovalResponse.model_validate(response["data"])

    return validated.model_dump(mode="json")
