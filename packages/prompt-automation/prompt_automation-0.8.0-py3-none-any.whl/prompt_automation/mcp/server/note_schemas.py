"""JSON schema definitions for note management tools."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


_BASE_PROPERTIES: Dict[str, Any] = {
    "dry_run": {"type": "boolean", "default": False},
    "trace_id": {"type": "string"},
    "idempotency_key": {"type": "string"},
    "vault": {
        "type": "object",
        "properties": {
            "reference_file": {"type": "string"},
            "display_path": {"type": "string"},
            "vault_root": {"type": "string"},
        },
        "required": ["reference_file"],
        "additionalProperties": False,
    },
}


def _extend(extra: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    schema = {"type": "object", "properties": deepcopy(_BASE_PROPERTIES)}
    schema["properties"].update(deepcopy(extra))
    schema["required"] = sorted(set(["vault", *required]))
    schema["additionalProperties"] = False
    return schema


NOTES_READ_SCHEMA: Dict[str, Any] = _extend(
    {
        "path": {"type": "string", "description": "Vault-relative note path"},
        "encoding": {"type": "string", "default": "utf-8"},
    },
    required=["path"],
)

NOTES_SEARCH_SCHEMA: Dict[str, Any] = _extend(
    {
        "query": {"type": "string", "description": "Substring to match against note names and content"},
        "max_results": {"type": "integer", "minimum": 1, "maximum": 200, "default": 25},
    },
    required=["query"],
)

NOTES_UPSERT_SCHEMA: Dict[str, Any] = _extend(
    {
        "path": {"type": "string", "description": "Vault-relative path for the note"},
        "content": {"type": "string", "description": "Markdown body to write"},
        "encoding": {"type": "string", "default": "utf-8"},
    },
    required=["path", "content"],
)

_EXEC_ACTIONS = sorted({"open", "reveal", "index"})

NOTES_EXEC_SCHEMA: Dict[str, Any] = _extend(
    {
        "action": {"type": "string", "enum": _EXEC_ACTIONS},
        "path": {"type": "string"},
        "arguments": {"type": "object"},
    },
    required=["action"],
)


__all__ = [
    "NOTES_READ_SCHEMA",
    "NOTES_SEARCH_SCHEMA",
    "NOTES_UPSERT_SCHEMA",
    "NOTES_EXEC_SCHEMA",
]
