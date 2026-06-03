from register import register_tool
from clients.workflow_step_client import WorkflowStepClient

workflow_step_client = WorkflowStepClient()


@register_tool(
    name="create_workflow_step",
    description="Create workflow step.",
    input_schema={
        "type": "object",
        "properties": {
            "workflow_execution_id": {"type": "string"},
            "step_name": {"type": "string"},
            "agent_id": {"type": "string"},
            "status": {"type": "string"},
            "input_payload": {"type": "object"},
            "output_payload": {"type": "object"},
        },
        "required": ["workflow_execution_id", "step_name"],
    },
    output_schema={"type": "object"},
)
async def create_workflow_step_tool(**kwargs):
    return await workflow_step_client.create_workflow_step(
        workflow_execution_id=kwargs.get("workflow_execution_id"),
        step_name=kwargs.get("step_name"),
        agent_id=kwargs.get("agent_id"),
        status=kwargs.get("status", "pending"),
        input_payload=kwargs.get("input_payload", {}),
        output_payload=kwargs.get("output_payload", {}),
    )


@register_tool(
    name="get_workflow_step",
    description="Get workflow step.",
    input_schema={
        "type": "object",
        "properties": {"workflow_step_id": {"type": "string"}},
        "required": ["workflow_step_id"],
    },
    output_schema={"type": "object"},
)
async def get_workflow_step_tool(**kwargs):
    return await workflow_step_client.get_workflow_step(
        workflow_step_id=kwargs.get("workflow_step_id")
    )


@register_tool(
    name="list_workflow_steps",
    description="List workflow steps.",
    input_schema={
        "type": "object",
        "properties": {"workflow_execution_id": {"type": "string"}},
        "required": ["workflow_execution_id"],
    },
    output_schema={"type": "object"},
)
async def list_workflow_steps_tool(**kwargs):
    return await workflow_step_client.list_workflow_steps(
        workflow_execution_id=kwargs.get("workflow_execution_id")
    )


@register_tool(
    name="list_workflow_steps_by_status",
    description="List workflow steps by status.",
    input_schema={
        "type": "object",
        "properties": {"status": {"type": "string"}},
        "required": ["status"],
    },
    output_schema={"type": "object"},
)
async def list_workflow_steps_by_status_tool(**kwargs):
    return await workflow_step_client.list_steps_by_status(status=kwargs.get("status"))


@register_tool(
    name="update_workflow_step",
    description="Update workflow step.",
    input_schema={
        "type": "object",
        "properties": {
            "workflow_step_id": {"type": "string"},
            "status": {"type": "string"},
            "output_payload": {"type": "object"},
            "started_at": {"type": "string"},
            "completed_at": {"type": "string"},
            "error_message": {"type": "string"},
        },
        "required": ["workflow_step_id"],
    },
    output_schema={"type": "object"},
)
async def update_workflow_step_tool(**kwargs):
    return await workflow_step_client.update_workflow_step(
        workflow_step_id=kwargs.get("workflow_step_id"),
        status=kwargs.get("status"),
        output_payload=kwargs.get("output_payload"),
        started_at=kwargs.get("started_at"),
        completed_at=kwargs.get("completed_at"),
        error_message=kwargs.get("error_message"),
    )


@register_tool(
    name="delete_workflow_step",
    description="Delete workflow step.",
    input_schema={
        "type": "object",
        "properties": {"workflow_step_id": {"type": "string"}},
        "required": ["workflow_step_id"],
    },
    output_schema={"type": "object"},
)
async def delete_workflow_step_tool(**kwargs):
    return await workflow_step_client.delete_workflow_step(
        workflow_step_id=kwargs.get("workflow_step_id")
    )
