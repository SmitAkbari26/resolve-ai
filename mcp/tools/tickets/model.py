from uuid import UUID

from pydantic import BaseModel, Field
from typing import Any, Optional


class CreateTicketRequest(BaseModel):
    """
    Request model for creating a support ticket.

    Attributes:
        user_id (UUID): Identifier of the user creating the ticket.
        category (str): Category of the ticket (e.g., bug, feature request).
        summary (str): Short summary of the issue.
        priority (str): Priority level of the ticket (e.g., low, medium, high).
        description (str): Detailed description of the issue.
        user_id (Optional[str]): Optional alternative user identifier; defaults to None.
        conversation_id (Optional[str]): Optional identifier linking the ticket to a conversation; defaults to None.
        assigned_agent (Optional[str]): Name of the agent to assign to the ticket; defaults to None.
    """

    user_id: UUID
    category: str
    summary: str
    priority: str
    description: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    assigned_agent: Optional[str] = None


class CreateTicketResponse(BaseModel):
    """
    Response model for ticket creation.

    Attributes:
        id (UUID): Unique identifier of the ticket.
        user_id (Optional[UUID]): Identifier of the user who created the ticket.
        conversation_id (Optional[UUID]): Identifier of the related conversation.
        category (str): Ticket category.
        priority (str): Ticket priority level.
        status (str): Current status of the ticket.
        summary (str): Brief summary of the ticket.
        description (str): Detailed description of the issue.
        severity_score (float): Calculated severity score, defaults to 0.0.
        suggested_action (str): Suggested action for the ticket, defaults to an empty string.
        resolution (str): Resolution details of the ticket.
        assigned_agent (Optional[str]): Agent assigned to handle the ticket.
        metadata_ (dict[str, Any]): Additional metadata for the ticket.
        created_at (str): Timestamp when the ticket was created.
        updated_at (str): Timestamp when the ticket was last updated.
    """

    id: UUID
    user_id: Optional[UUID]
    conversation_id: Optional[UUID] = None
    category: str
    priority: str
    status: str
    summary: str
    description: str
    severity_score: float = 0.0
    suggested_action: str = ""
    resolution: str
    assigned_agent: Optional[str] = None
    metadata_: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class GetTicketRequest(BaseModel):
    """
    Request model for retrieving a ticket.

    Attributes:
        ticket_id (Optional[str]): Identifier of the ticket to retrieve.
        user_id (Optional[str]): Identifier of the user requesting the ticket.
        status (Optional[str]): Desired status filter for the ticket query.
    """

    ticket_id: Optional[str] = ""
    user_id: Optional[str] = ""
    status: Optional[str] = ""


class GetTicketResponse(BaseModel):
    """
    Response model for retrieving a ticket.

    Attributes:
        id (UUID): Unique identifier of the ticket.
        user_id (Optional[UUID]): Identifier of the user who created the ticket, if any.
        conversation_id (Optional[UUID]): Identifier of the related conversation, defaults to None.
        category (str): Category of the ticket.
        priority (str): Priority level of the ticket.
        status (str): Current status of the ticket.
        summary (str): Brief summary of the ticket.
        description (str): Detailed description of the ticket.
        severity_score (float): Calculated severity score, defaults to 0.0.
        suggested_action (str): Suggested action for the ticket, defaults to an empty string.
        resolution (str): Resolution details of the ticket.
        assigned_agent (Optional[str]): Name or identifier of the assigned agent, if any.
        metadata_ (dict[str, Any]): Additional metadata associated with the ticket.
        created_at (str): Timestamp when the ticket was created.
        updated_at (str): Timestamp when the ticket was last updated.
    """

    id: UUID
    user_id: Optional[UUID]
    conversation_id: Optional[UUID] = None
    category: str
    priority: str
    status: str
    summary: str
    description: str
    severity_score: float = 0.0
    suggested_action: str = ""
    resolution: str
    assigned_agent: Optional[str] = None
    metadata_: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class ListTicketsResponse(BaseModel):
    """
    Response model containing a list of ticket details.

    Attributes:
        tickets (list[GetTicketResponse]): Collection of ticket information objects.
    """

    tickets: list[GetTicketResponse]


class UpdateTicketRequest(BaseModel):
    """
    Request model for updating a ticket.

    Attributes:
        ticket_id (str): Unique identifier of the ticket to be updated.
        status (str): New status of the ticket (e.g., "open", "closed").
        priority (str): Updated priority level (e.g., "low", "high").
        resolution (Optional[str]): Resolution details if the ticket is resolved.
        assigned_agent (Optional[str]): Identifier of the agent assigned to the ticket.
        category (Optional[str]): Category classification for the ticket.
        severity_score (Optional[float]): Numeric severity rating of the issue.
        summary (Optional[str]): Brief summary of the ticket changes.
        description (Optional[str]): Detailed description of the update.
        suggested_action (Optional[str]): Recommended action to address the ticket.
        metadata_ (dict[str, Any] | None): Additional arbitrary metadata associated with the update.
    """

    ticket_id: str
    status: str
    priority: str
    resolution: Optional[str] = None
    assigned_agent: Optional[str] = None
    category: Optional[str] = None
    severity_score: Optional[float] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    suggested_action: Optional[str] = None
    metadata_: dict[str, Any] | None = None
