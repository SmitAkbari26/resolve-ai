import uuid
from datetime import datetime, timezone


def generate_id(prefix: str = "") -> str:
    short_uuid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{short_uuid}" if prefix else short_uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def truncate(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def severity_to_int(severity: str) -> int:
    mapping = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return mapping.get(severity.lower(), 0)
