from register import register_tool
from clients.workflow_execution_client import WorkflowExecutionClient

workflow_client = WorkflowExecutionClient()


@register_tool(
    name="create_workflow_execution",
    description="Create workflow execution.",
    input_schema={
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "workflow_type": {"type": "string"},
            "current_step": {"type": "string"},
            "status": {"type": "string"},
            "created_by": {"type": "string"},
        },
        "required": ["ticket_id", "workflow_type"],
    },
    output_schema={"type": "object"},
)
async def create_workflow_execution_tool(**kwargs):
    return await workflow_client.create_workflow(
        ticket_id=kwargs.get("ticket_id"),
        workflow_type=kwargs.get("workflow_type"),
        current_step=kwargs.get("current_step"),
        status=kwargs.get("status", "pending"),
        created_by=kwargs.get("created_by"),
    )


@register_tool(
    name="get_workflow_execution",
    description="Get workflow execution.",
    input_schema={
        "type": "object",
        "properties": {"workflow_id": {"type": "string"}},
        "required": ["workflow_id"],
    },
    output_schema={"type": "object"},
)
async def get_workflow_execution_tool(**kwargs):
    return await workflow_client.get_workflow(workflow_id=kwargs.get("workflow_id"))


@register_tool(
    name="list_workflow_executions",
    description="List workflow executions.",
    input_schema={"type": "object", "properties": {"status": {"type": "string"}}},
    output_schema={"type": "object"},
)
async def list_workflow_executions_tool(**kwargs):
    return await workflow_client.list_workflows(status=kwargs.get("status"))


@register_tool(
    name="get_ticket_workflows",
    description="Get workflows for a ticket.",
    input_schema={
        "type": "object",
        "properties": {"ticket_id": {"type": "string"}},
        "required": ["ticket_id"],
    },
    output_schema={"type": "object"},
)
async def get_ticket_workflows_tool(**kwargs):
    return await workflow_client.get_ticket_workflows(ticket_id=kwargs.get("ticket_id"))


@register_tool(
    name="update_workflow_execution",
    description="Update workflow execution.",
    input_schema={
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string"},
            "current_step": {"type": "string"},
            "status": {"type": "string"},
            "completed_at": {"type": "string"},
            "failed_reason": {"type": "string"},
        },
        "required": ["workflow_id"],
    },
    output_schema={"type": "object"},
)
async def update_workflow_execution_tool(**kwargs):
    return await workflow_client.update_workflow(
        workflow_id=kwargs.get("workflow_id"),
        current_step=kwargs.get("current_step"),
        status=kwargs.get("status"),
        completed_at=kwargs.get("completed_at"),
        failed_reason=kwargs.get("failed_reason"),
    )


@register_tool(
    name="delete_workflow_execution",
    description="Delete workflow execution.",
    input_schema={
        "type": "object",
        "properties": {"workflow_id": {"type": "string"}},
        "required": ["workflow_id"],
    },
    output_schema={"type": "object"},
)
async def delete_workflow_execution_tool(**kwargs):
    return await workflow_client.delete_workflow(workflow_id=kwargs.get("workflow_id"))
