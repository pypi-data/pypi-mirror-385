"""Implementation helpers for note management MCP tools."""
from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple

from ..observability import hooks as obs_hooks
from . import note_schemas, vault_paths


class NoteToolError(ValueError):
    """Raised when a note tool request fails validation."""


class NoteCommandError(NoteToolError):
    """Raised when an exec command is not allowlisted."""


NOTES_READ_NAME = "pa.notes.read"
NOTES_SEARCH_NAME = "pa.notes.search"
NOTES_UPSERT_NAME = "pa.notes.upsert"
NOTES_EXEC_NAME = "pa.notes.exec_command"


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered in {"1", "true", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _require_vault(arguments: Dict[str, Any]) -> str:
    vault = arguments.get("vault")
    if not isinstance(vault, dict):
        raise NoteToolError("vault metadata required")
    reference = vault.get("reference_file")
    if not isinstance(reference, str) or not reference.strip():
        raise NoteToolError("vault.reference_file missing")
    return reference


def _sanitize_relative_path(value: str) -> str:
    cleaned = value.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.lstrip("/")
    if not cleaned:
        raise NoteToolError("path must not be empty")
    return cleaned


def _resolve_context(arguments: Dict[str, Any], *, platform: vault_paths.VaultPlatform | None = None) -> vault_paths.VaultContext:
    reference = _require_vault(arguments)
    return vault_paths.resolve_vault_context(reference, platform=platform)


def _record_metric(event: str, *, trace_id: str | None, context: vault_paths.VaultContext, extra: Dict[str, Any]) -> None:
    payload: Dict[str, Any] = {
        "trace_id": trace_id or "",
        "vault_root": context.vault_root.as_posix(),
    }
    payload.update(extra)
    try:
        obs_hooks.global_state.emit_metric(event, payload)
    except Exception:  # pragma: no cover - defensive telemetry
        pass


def _read_file(path: Path, encoding: str) -> str:
    return path.read_text(encoding=encoding)


def _write_file(path: Path, content: str, encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def _diff(before: str, after: str, *, path: str) -> str:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(before_lines, after_lines, fromfile=f"a/{path}", tofile=f"b/{path}")
    )


def _extract_trace(arguments: Dict[str, Any]) -> str | None:
    value = arguments.get("trace_id")
    if isinstance(value, str):
        return value
    return None


def _relative_for(context: vault_paths.VaultContext, target: Path) -> str:
    return context.relative_path(target)


def read_note(arguments: Dict[str, Any], *, platform: vault_paths.VaultPlatform | None = None) -> Dict[str, Any]:
    context = _resolve_context(arguments, platform=platform)
    path_value = arguments.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise NoteToolError("path is required")
    rel_path = _sanitize_relative_path(path_value)
    encoding = arguments.get("encoding") or "utf-8"
    target = context.ensure_within_vault(rel_path)
    content = _read_file(target, encoding)
    result = {
        "path": rel_path,
        "content": content,
        "vault_root": context.vault_root.as_posix(),
        "absolute_path": target.as_posix(),
        "windows_path": vault_paths.wsl_to_windows(target, platform=platform),
    }
    _record_metric("notes.read", trace_id=_extract_trace(arguments), context=context, extra={"path": rel_path})
    return result


def search_notes(arguments: Dict[str, Any], *, platform: vault_paths.VaultPlatform | None = None) -> Dict[str, Any]:
    context = _resolve_context(arguments, platform=platform)
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise NoteToolError("query is required")
    query_lower = query.lower()
    max_results = arguments.get("max_results") or 25
    try:
        max_results_int = max(1, min(int(max_results), 200))
    except Exception:
        max_results_int = 25
    matches: List[Dict[str, Any]] = []
    for candidate in context.vault_root.rglob("*.md"):
        name = candidate.name.lower()
        if query_lower not in name:
            try:
                text = candidate.read_text(encoding="utf-8")
            except Exception:
                continue
            if query_lower not in text.lower():
                continue
        rel = _relative_for(context, candidate)
        matches.append({
            "path": rel,
            "absolute_path": candidate.as_posix(),
        })
        if len(matches) >= max_results_int:
            break
    _record_metric(
        "notes.search",
        trace_id=_extract_trace(arguments),
        context=context,
        extra={"query": query, "result_count": len(matches)},
    )
    return {"query": query, "matches": matches}


def upsert_note(arguments: Dict[str, Any], *, platform: vault_paths.VaultPlatform | None = None) -> Dict[str, Any]:
    context = _resolve_context(arguments, platform=platform)
    path_value = arguments.get("path")
    content = arguments.get("content")
    if not isinstance(path_value, str) or not path_value.strip():
        raise NoteToolError("path is required")
    if not isinstance(content, str):
        raise NoteToolError("content must be a string")
    rel_path = _sanitize_relative_path(path_value)
    encoding = arguments.get("encoding") or "utf-8"
    target = context.ensure_within_vault(rel_path)
    dry_run = _coerce_bool(arguments.get("dry_run"))
    before = ""
    if target.exists():
        before = _read_file(target, encoding)
    diff_text = _diff(before, content, path=rel_path)
    if dry_run:
        _record_metric(
            "notes.upsert",
            trace_id=_extract_trace(arguments),
            context=context,
            extra={"path": rel_path, "dry_run": True},
        )
        return {
            "path": rel_path,
            "diff": diff_text,
            "dry_run": True,
        }
    _write_file(target, content, encoding)
    _record_metric(
        "notes.upsert",
        trace_id=_extract_trace(arguments),
        context=context,
        extra={"path": rel_path, "dry_run": False},
    )
    return {
        "path": rel_path,
        "absolute_path": target.as_posix(),
        "windows_path": vault_paths.wsl_to_windows(target, platform=platform),
        "diff": diff_text,
    }


def _exec_open(
    context: vault_paths.VaultContext,
    arguments: Dict[str, Any],
    platform: vault_paths.VaultPlatform | None,
) -> Dict[str, Any]:
    path_value = arguments.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise NoteCommandError("path is required for open")
    rel_path = _sanitize_relative_path(path_value)
    target = context.ensure_within_vault(rel_path)
    return {
        "action": "open",
        "path": rel_path,
        "absolute_path": target.as_posix(),
        "windows_path": vault_paths.wsl_to_windows(target, platform=platform),
    }


def _exec_reveal(
    context: vault_paths.VaultContext,
    arguments: Dict[str, Any],
    platform: vault_paths.VaultPlatform | None,
) -> Dict[str, Any]:
    path_value = arguments.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise NoteCommandError("path is required for reveal")
    rel_path = _sanitize_relative_path(path_value)
    target = context.ensure_within_vault(rel_path)
    return {
        "action": "reveal",
        "path": rel_path,
        "directory": target.parent.as_posix(),
        "windows_path": vault_paths.wsl_to_windows(target.parent, platform=platform),
    }


def _exec_index(
    context: vault_paths.VaultContext,
    arguments: Dict[str, Any],
    platform: vault_paths.VaultPlatform | None,
) -> Dict[str, Any]:
    notes: List[str] = []
    for candidate in context.vault_root.rglob("*.md"):
        notes.append(_relative_for(context, candidate))
        if len(notes) >= 200:
            break
    return {
        "action": "index",
        "paths": notes,
    }


ExecHandler = Callable[[vault_paths.VaultContext, Dict[str, Any], vault_paths.VaultPlatform | None], Dict[str, Any]]


_EXEC_HANDLERS: Dict[str, ExecHandler] = {
    "open": _exec_open,
    "reveal": _exec_reveal,
    "index": _exec_index,
}


def exec_command(arguments: Dict[str, Any], *, platform: vault_paths.VaultPlatform | None = None) -> Dict[str, Any]:
    context = _resolve_context(arguments, platform=platform)
    action = arguments.get("action")
    if not isinstance(action, str) or not action.strip():
        raise NoteCommandError("action is required")
    normalized = action.strip().lower()
    if normalized not in _EXEC_HANDLERS:
        raise NoteCommandError(f"action '{action}' not allowlisted")

    handler = _EXEC_HANDLERS[normalized]
    result = handler(context, arguments, platform)
    _record_metric(
        "notes.exec",
        trace_id=_extract_trace(arguments),
        context=context,
        extra={"action": normalized},
    )
    return result


TOOL_REGISTRY: Dict[str, Tuple[Callable[..., Dict[str, Any]], Dict[str, Any], str]] = {
    NOTES_READ_NAME: (read_note, note_schemas.NOTES_READ_SCHEMA, "Read a note within the resolved vault"),
    NOTES_SEARCH_NAME: (search_notes, note_schemas.NOTES_SEARCH_SCHEMA, "Search markdown notes within the vault"),
    NOTES_UPSERT_NAME: (upsert_note, note_schemas.NOTES_UPSERT_SCHEMA, "Create or update a vault note"),
    NOTES_EXEC_NAME: (exec_command, note_schemas.NOTES_EXEC_SCHEMA, "Execute an allowlisted note command"),
}


def iter_tool_descriptors() -> Iterable[Dict[str, Any]]:
    for name, (_, schema, description) in TOOL_REGISTRY.items():
        yield {"name": name, "description": description, "input_schema": schema}


__all__ = [
    "NOTES_EXEC_NAME",
    "NOTES_READ_NAME",
    "NOTES_SEARCH_NAME",
    "NOTES_UPSERT_NAME",
    "NoteCommandError",
    "NoteToolError",
    "TOOL_REGISTRY",
    "exec_command",
    "iter_tool_descriptors",
    "read_note",
    "search_notes",
    "upsert_note",
]
