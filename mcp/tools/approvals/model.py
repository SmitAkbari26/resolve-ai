from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class CreateApprovalRequest(BaseModel):
    """
    Create an approval request model.

    Attributes:
        ticket_id (str): Identifier of the related ticket.
        approval_type (str): Type of approval being requested.
        reason (str): Optional justification for the request; defaults to an empty string.
        amount (Optional[float]): Optional monetary amount associated with the request; defaults to None.
        requested_by (str): Identifier of the requester; defaults to "system".
    """

    ticket_id: str
    approval_type: str
    reason: str = ""
    amount: Optional[float] = None
    requested_by: str = "system"


class ApprovalResponse(BaseModel):
    """
    Represents an approval response record.

    Attributes:
        id (UUID): Unique identifier of the response.
        ticket_id (str): Identifier of the related ticket.
        approval_type (str): Type of approval requested.
        reason (str): Reason for the approval request.
        amount (Optional[float]): Monetary amount involved, if applicable.
        status (str): Current status of the approval (e.g., pending, approved, rejected).
        requested_by (str): User who requested the approval.
        decided_by (Optional[str]): User who made the decision, if any.
        decision_notes (str): Additional notes regarding the decision.
        created_at (str): Timestamp when the response was created.
        decided_at (Optional[str]): Timestamp when the decision was made, if applicable.
    """

    id: UUID
    ticket_id: str
    approval_type: str
    reason: str
    amount: Optional[float] = None
    status: str
    requested_by: str
    decided_by: Optional[str] = None
    decision_notes: str = ""
    created_at: str
    decided_at: Optional[str] = None


class GetApprovalRequest(BaseModel):
    """
    Represents a request to retrieve an approval.

    Attributes:
        approval_id (str): Identifier of the approval to be fetched.
    """

    approval_id: str


class ListApprovalsRequest(BaseModel):
    """
    Request model for listing approvals.

    Attributes:
        status (Optional[str]): Optional filter to retrieve approvals with the specified status.
    """

    status: Optional[str] = None


class GetTicketApprovalsRequest(BaseModel):
    """
    Request model for retrieving ticket approvals.

    Attributes:
        ticket_id (str): Identifier of the ticket.
    """

    ticket_id: str


class UpdateApprovalRequest(BaseModel):
    """
    UpdateApprovalRequest model representing an approval decision.

    Attributes:
        approval_id (str): Identifier of the approval request.
        status (Optional[str]): Current status of the approval (e.g., approved, rejected).
        decided_by (Optional[str]): Identifier of the user who made the decision.
        decision_notes (Optional[str]): Additional notes regarding the decision.
    """

    approval_id: str
    status: Optional[str] = None
    decided_by: Optional[str] = None
    decision_notes: Optional[str] = None


class ListApprovalsResponse(BaseModel):
    """
    Response model containing a list of approval details.

    Attributes:
        approvals (list[ApprovalResponse]): Collection of approval response objects.
    """

    approvals: list[ApprovalResponse]
