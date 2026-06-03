from agents.conversation_agent import ConversationAgent
from agents.resolve_agent import ResolveAgent

AGENT_REGISTRY = {
    "conversation_agent": ConversationAgent,
    "resolve_agent": ResolveAgent,
}
