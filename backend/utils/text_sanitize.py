"""Sanitize text for PostgreSQL UTF-8 and safe display."""

from __future__ import annotations

import re


# C0 controls except tab, newline, carriage return
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(text: str | None) -> str:
    """
    Remove null bytes and other characters PostgreSQL rejects in UTF-8 text.
    """
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Drop NUL (common PDF extraction artifact: "Work\x00ow")
    text = text.replace("\x00", "")

    # Remove other problematic control characters
    text = _CONTROL_CHARS_RE.sub("", text)

    # Ensure valid UTF-8 for asyncpg
    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    return text.strip()


def plain_chat_text(text: str | None) -> str:
    """
    Prepare text for the web chat UI (plain text, no markdown).
    Strips **bold** and normalizes line breaks for readability.
    """
    text = sanitize_text(text)
    if not text:
        return ""
    # **bold** → bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    # *italic* → italic
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    return format_readable_chat(text)


def format_readable_chat(text: str) -> str:
    """
    Turn run-on assistant text into readable paragraphs and lists.
    Handles LLM output like: "...step by step: 1. First 2. Second..."
    """
    if not text:
        return ""

    # Numbered steps: break before " 2. ", " 3. ", etc.
    text = re.sub(r"(?<!\n)\s+(\d+\.\s)", r"\n\1", text)

    # Bullet lines: " - Item" on its own line
    text = re.sub(r"(?<=[.!?:])\s+-\s+", r"\n\n- ", text)
    text = re.sub(r"(?<!\n)\s+-\s+(?=[A-Za-z])", r"\n- ", text)

    # Label before a list (e.g. "I can help with:\n-")
    text = re.sub(r":\s*-\s+", ":\n\n- ", text)

    # Space after colons that start a step block
    text = re.sub(r":\s+(\d+\.\s)", r":\n\n\1", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def sanitize_dict_strings(data: dict) -> dict:
    """Recursively sanitize string values in a dict (e.g. message metadata)."""
    out = {}
    for key, value in data.items():
        if isinstance(value, str):
            out[key] = sanitize_text(value)
        elif isinstance(value, dict):
            out[key] = sanitize_dict_strings(value)
        elif isinstance(value, list):
            out[key] = [
                sanitize_text(v) if isinstance(v, str) else v for v in value
            ]
        else:
            out[key] = value
    return out
