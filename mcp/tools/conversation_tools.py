from register import register_tool
from clients.conversation_client import ConversationClient

conversation_client = ConversationClient()


@register_tool(
    name="create_conversation",
    description="Create a new conversation.",
    input_schema={
        "type": "object",
        "properties": {"user_id": {"type": "string"}, "channel": {"type": "string"}},
        "required": ["user_id"],
    },
    output_schema={"type": "object"},
)
async def create_conversation_tool(**kwargs):

    return await conversation_client.create_conversation(
        user_id=kwargs.get("user_id"), channel=kwargs.get("channel", "web_chat")
    )


@register_tool(
    name="get_conversation",
    description="Get conversation details.",
    input_schema={
        "type": "object",
        "properties": {"conversation_id": {"type": "string"}},
        "required": ["conversation_id"],
    },
    output_schema={"type": "object"},
)
async def get_conversation_tool(**kwargs):
    return await conversation_client.get_conversation(
        conversation_id=kwargs.get("conversation_id")
    )


@register_tool(
    name="list_conversations",
    description="List all conversations.",
    input_schema={"type": "object", "properties": {"status": {"type": "string"}}},
    output_schema={"type": "object"},
)
async def list_conversations_tool(**kwargs):
    return await conversation_client.list_conversations(status=kwargs.get("status"))
