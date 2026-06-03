"""Helpers for parsing and normalizing LLM JSON outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def _normalize_key(key: str) -> str:
    return re.sub(r"[\s\-]+", "_", str(key).strip().lower())


def normalize_dict_keys(data: Any) -> Any:
    """Recursively lowercase/normalize dict keys from LLM output."""
    if isinstance(data, dict):
        return {_normalize_key(k): normalize_dict_keys(v) for k, v in data.items()}
    if isinstance(data, list):
        return [normalize_dict_keys(item) for item in data]
    return data


def extract_json_object(text: str) -> dict | None:
    """Extract and parse the first JSON object from model text."""
    if not text:
        return None

    cleaned = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL,
    ).strip()

    if not cleaned:
        return None

    # Direct parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return normalize_dict_keys(parsed)
    except json.JSONDecodeError:
        pass

    # Brace slice
    if "{" in cleaned and "}" in cleaned:
        snippet = cleaned[cleaned.find("{") : cleaned.rfind("}") + 1]
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, dict):
                return normalize_dict_keys(parsed)
        except json.JSONDecodeError:
            return None

    return None


def pick_str(data: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return default


def pick_bool(data: dict, *keys: str, default: bool = False) -> bool:
    for key in keys:
        if key not in data:
            continue
        val = data[key]
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return bool(val)
        if isinstance(val, str):
            return val.strip().lower() in ("true", "1", "yes", "y")
    return default
