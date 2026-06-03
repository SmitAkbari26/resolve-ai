from register import register_tool
from clients.conversation_message_client import ConversationMessageClient

message_client = ConversationMessageClient()


@register_tool(
    name="create_conversation_message",
    description="Create a conversation message.",
    input_schema={
        "type": "object",
        "properties": {
            "conversation_id": {"type": "string"},
            "role": {"type": "string"},
            "message": {"type": "string"},
            "metadata_": {"type": "object"},
        },
        "required": ["conversation_id", "role", "message"],
    },
    output_schema={"type": "object"},
)
async def create_conversation_message_tool(**kwargs):
    return await message_client.create_message(
        conversation_id=kwargs.get("conversation_id"),
        role=kwargs.get("role"),
        message=kwargs.get("message"),
        metadata_=kwargs.get("metadata_", {}),
    )


@register_tool(
    name="get_conversation_message",
    description="Get conversation message details.",
    input_schema={
        "type": "object",
        "properties": {"message_id": {"type": "string"}},
        "required": ["message_id"],
    },
    output_schema={"type": "object"},
)
async def get_conversation_message_tool(**kwargs):
    return await message_client.get_message(message_id=kwargs.get("message_id"))


@register_tool(
    name="list_conversation_messages",
    description="List all messages of a conversation.",
    input_schema={
        "type": "object",
        "properties": {"conversation_id": {"type": "string"}},
        "required": ["conversation_id"],
    },
    output_schema={"type": "object"},
)
async def list_conversation_messages_tool(**kwargs):
    return await message_client.list_messages(
        conversation_id=kwargs.get("conversation_id")
    )
