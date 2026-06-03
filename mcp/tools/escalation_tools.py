from register import register_tool
from clients.escalation_client import EscalationClient

escalation_client = EscalationClient()


@register_tool(
    name="create_escalation",
    description="Create a new ticket escalation.",
    input_schema={
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string", "description": "Ticket ID"},
            "reason": {"type": "string", "description": "Escalation reason"},
            "escalation_level": {"type": "integer", "description": "Escalation level"},
            "escalated_to": {
                "type": "string",
                "description": "Escalated person or team",
            },
            "status": {"type": "string", "description": "Escalation status"},
        },
        "required": ["ticket_id", "reason"],
    },
    output_schema={"type": "object"},
)
async def create_escalation_tool(**kwargs):
    return await escalation_client.create_escalation(
        ticket_id=kwargs.get("ticket_id"),
        reason=kwargs.get("reason"),
        escalation_level=kwargs.get("escalation_level", 1),
        escalated_to=kwargs.get("escalated_to"),
        status=kwargs.get("status", "active"),
    )


@register_tool(
    name="get_escalation",
    description="Get escalation details.",
    input_schema={
        "type": "object",
        "properties": {
            "escalation_id": {"type": "string", "description": "Escalation ID"}
        },
        "required": ["escalation_id"],
    },
    output_schema={"type": "object"},
)
async def get_escalation_tool(**kwargs):
    return await escalation_client.get_escalation(
        escalation_id=kwargs.get("escalation_id")
    )


@register_tool(
    name="list_escalations",
    description="List escalations optionally filtered by status.",
    input_schema={
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Escalation status"}
        },
    },
    output_schema={"type": "object"},
)
async def list_escalations_tool(**kwargs):
    return await escalation_client.list_escalations(status=kwargs.get("status"))


@register_tool(
    name="get_ticket_escalations",
    description="Get escalations of a ticket.",
    input_schema={
        "type": "object",
        "properties": {"ticket_id": {"type": "string", "description": "Ticket ID"}},
        "required": ["ticket_id"],
    },
    output_schema={"type": "object"},
)
async def get_ticket_escalations_tool(**kwargs):
    return await escalation_client.get_ticket_escalations(
        ticket_id=kwargs.get("ticket_id")
    )


@register_tool(
    name="update_escalation",
    description="Update escalation details.",
    input_schema={
        "type": "object",
        "properties": {
            "escalation_id": {"type": "string", "description": "Escalation ID"},
            "escalation_level": {"type": "integer", "description": "Escalation level"},
            "escalated_to": {
                "type": "string",
                "description": "Escalated person or team",
            },
            "status": {"type": "string", "description": "Escalation status"},
            "resolved_at": {
                "type": "string",
                "description": "Escalation resolved timestamp",
            },
        },
        "required": ["escalation_id"],
    },
    output_schema={"type": "object"},
)
async def update_escalation_tool(**kwargs):
    return await escalation_client.update_escalation(
        escalation_id=kwargs.get("escalation_id"),
        escalation_level=kwargs.get("escalation_level"),
        escalated_to=kwargs.get("escalated_to"),
        status=kwargs.get("status"),
        resolved_at=kwargs.get("resolved_at"),
    )


@register_tool(
    name="delete_escalation",
    description="Delete escalation.",
    input_schema={
        "type": "object",
        "properties": {
            "escalation_id": {"type": "string", "description": "Escalation ID"}
        },
        "required": ["escalation_id"],
    },
    output_schema={"type": "object"},
)
async def delete_escalation_tool(**kwargs):
    return await escalation_client.delete_escalation(
        escalation_id=kwargs.get("escalation_id")
    )
