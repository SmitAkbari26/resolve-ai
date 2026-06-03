import json
from typing import Any

from config import REDIS_URL
from utils.logger import get_logger

logger = get_logger(__name__)

_redis_client = None


def _get_redis():
    """Lazy-initialize the Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            _redis_client.ping()
            logger.info("Redis memory store connected")
        except Exception as e:
            logger.warning(f"Redis connection failed (using in-memory fallback): {e}")
            _redis_client = InMemoryFallback()
    return _redis_client


class InMemoryFallback:
    """Simple dict-based fallback when Redis is unavailable."""

    def __init__(self):
        self._store: dict[str, str] = {}
        self._ttls: dict[str, float] = {}
        logger.info("Using in-memory fallback for Redis")

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._store

    def keys(self, pattern: str = "*") -> list[str]:
        import fnmatch
        return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    def ping(self) -> bool:
        return True


# ─── Conversation Memory ─────────────────────────────────

def store_conversation_memory(conversation_id: str, messages: list[dict], ttl: int = 3600):
    """Store conversation messages in Redis with TTL."""
    client = _get_redis()
    key = f"conversation:{conversation_id}:messages"
    client.set(key, json.dumps(messages), ex=ttl)


def get_conversation_memory(conversation_id: str) -> list[dict]:
    """Retrieve conversation messages from Redis."""
    client = _get_redis()
    key = f"conversation:{conversation_id}:messages"
    data = client.get(key)
    return json.loads(data) if data else []


def append_message(conversation_id: str, role: str, content: str, ttl: int = 3600):
    """Append a single message to conversation memory."""
    messages = get_conversation_memory(conversation_id)
    messages.append({"role": role, "content": content})
    store_conversation_memory(conversation_id, messages, ttl)


# ─── Conversation Summary ────────────────────────────────

def store_conversation_summary(conversation_id: str, summary: str, ttl: int = 7200):
    """Store a rolling conversation summary (compressed context)."""
    client = _get_redis()
    key = f"conversation:{conversation_id}:summary"
    client.set(key, summary, ex=ttl)


def get_conversation_summary(conversation_id: str) -> str | None:
    """Retrieve the rolling conversation summary."""
    client = _get_redis()
    key = f"conversation:{conversation_id}:summary"
    return client.get(key)


# ─── User Session ────────────────────────────────────────

def store_session(user_id: str, data: dict, ttl: int = 7200):
    """Store user session data."""
    client = _get_redis()
    key = f"session:{user_id}"
    client.set(key, json.dumps(data), ex=ttl)


def get_session(user_id: str) -> dict:
    """Retrieve user session data."""
    client = _get_redis()
    key = f"session:{user_id}"
    data = client.get(key)
    return json.loads(data) if data else {}


# ─── Short-term State (Workflow) ─────────────────────────

def store_workflow_state(workflow_id: str, state: dict, ttl: int = 1800):
    """Store workflow execution state."""
    client = _get_redis()
    key = f"workflow:{workflow_id}:state"
    client.set(key, json.dumps(state), ex=ttl)


def get_workflow_state(workflow_id: str) -> dict:
    """Retrieve workflow execution state."""
    client = _get_redis()
    key = f"workflow:{workflow_id}:state"
    data = client.get(key)
    return json.loads(data) if data else {}


# ─── Generic Cache ───────────────────────────────────────

def cache_set(key: str, value: Any, ttl: int = 600):
    """Set a cache value with TTL."""
    client = _get_redis()
    client.set(f"cache:{key}", json.dumps(value), ex=ttl)


def cache_get(key: str) -> Any | None:
    """Get a cached value."""
    client = _get_redis()
    data = client.get(f"cache:{key}")
    return json.loads(data) if data else None
