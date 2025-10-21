from __future__ import annotations

"""Shared helpers for Obsidian note MCP tooling."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .. import config as _config
from .. import features
from ..variables import storage

KILL_SWITCH_PLACEHOLDER = "obsidian_notes_tools_enabled"


def _coerce_optional_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on", "enabled"}:
            return True
        if lowered in {"0", "false", "no", "off", "disabled"}:
            return False
    return None


def _load_global_placeholders(prompts_dir: Path | None = None) -> Mapping[str, Any]:
    directory = prompts_dir or _config.PROMPTS_DIR
    path = directory / "globals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    placeholders = data.get("global_placeholders")
    if isinstance(placeholders, Mapping):
        return placeholders
    return {}


def _load_override_placeholders(overrides: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
    if overrides is None:
        try:
            overrides = storage._load_overrides()
        except Exception:
            overrides = {}
    mapping = overrides.get("global_placeholders") if isinstance(overrides, Mapping) else {}
    return mapping if isinstance(mapping, Mapping) else {}


def is_notes_kill_switch_enabled(*, prompts_dir: Path | None = None, overrides: Mapping[str, Any] | None = None) -> bool:
    """Return ``True`` when the global kill switch allows exposing note tooling."""

    enabled: bool = True

    global_placeholders = _load_global_placeholders(prompts_dir)
    global_value = _coerce_optional_bool(global_placeholders.get(KILL_SWITCH_PLACEHOLDER))
    if global_value is not None:
        enabled = global_value

    override_placeholders = _load_override_placeholders(overrides)
    override_value = _coerce_optional_bool(override_placeholders.get(KILL_SWITCH_PLACEHOLDER))
    if override_value is not None:
        enabled = override_value

    return enabled


def is_notes_feature_enabled() -> bool:
    """Return ``True`` when note tooling should be exposed across surfaces."""

    return features.is_mcp_notes_enabled() and is_notes_kill_switch_enabled()


def build_vault_payload(
    reference_file: str,
    *,
    display_path: str | None = None,
    vault_root: str | None = None,
) -> Dict[str, str]:
    payload: Dict[str, str] = {"reference_file": reference_file}
    if display_path:
        payload["display_path"] = display_path
    if vault_root:
        payload["vault_root"] = vault_root
    return payload


def _note_tool_mapping() -> Dict[str, Any]:
    from .server import note_tools

    return {
        "read": note_tools.read_note,
        "search": note_tools.search_notes,
        "upsert": note_tools.upsert_note,
        "exec": note_tools.exec_command,
    }


def call_note_tool(command: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke a note tool using the local MCP implementation."""

    mapping = _note_tool_mapping()
    if command not in mapping:
        raise ValueError(f"unknown notes command: {command}")
    handler = mapping[command]
    return handler(arguments)


@dataclass(slots=True)
class NoteDisplay:
    """Normalized representation of a note tool response for UI/CLI surfaces."""

    title: str
    sections: list[tuple[str, str]] = field(default_factory=list)
    dry_run: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)


def _paths_section(result: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    lines: list[str] = []
    absolute = result.get("absolute_path")
    windows = result.get("windows_path")
    vault_root = result.get("vault_root")
    if absolute:
        lines.append(f"Absolute: {absolute}")
    if windows:
        lines.append(f"Windows: {windows}")
    if vault_root:
        lines.append(f"Vault root: {vault_root}")
    if lines:
        yield ("Paths", "\n".join(lines))


def _ensure_content_section(content: str | None) -> Iterable[tuple[str, str]]:
    if content is not None:
        return [("Content", content)]
    return []


def _format_diff(diff_text: str | None) -> Iterable[tuple[str, str]]:
    if diff_text is None:
        return []
    normalized = diff_text.rstrip()
    if not normalized:
        normalized = "(no diff)"
    return [("Diff", normalized)]


def format_note_result(
    command: str,
    result: Mapping[str, Any],
    *,
    arguments: Mapping[str, Any] | None = None,
) -> NoteDisplay:
    """Build a :class:`NoteDisplay` representing ``result``."""

    args = arguments or {}
    sections: list[tuple[str, str]] = []
    title = command
    dry_run = bool(result.get("dry_run"))

    if command == "read":
        path = result.get("path") or args.get("path") or "(unknown)"
        title = f"Read note {path}"
        sections.extend(_paths_section(result))
        content = result.get("content") if isinstance(result.get("content"), str) else None
        sections.extend(_ensure_content_section(content))
    elif command == "search":
        query = result.get("query") or args.get("query") or ""
        title = f'Search results for "{query}"'
        matches = result.get("matches")
        if isinstance(matches, Iterable):
            lines: list[str] = []
            for idx, match in enumerate(matches, start=1):
                if not isinstance(match, Mapping):
                    continue
                rel_path = match.get("path") or "(unknown)"
                line = f"{idx}. {rel_path}"
                absolute = match.get("absolute_path")
                if absolute and absolute != rel_path:
                    line += f" — {absolute}"
                lines.append(line)
            if not lines:
                lines.append("(no matches)")
            sections.append(("Matches", "\n".join(lines)))
        else:
            sections.append(("Matches", "(no matches)"))
    elif command == "upsert":
        path = result.get("path") or args.get("path") or "(unknown)"
        title = f"{'Preview' if dry_run else 'Upserted'} note {path}"
        info_lines: list[str] = []
        if dry_run:
            info_lines.append("Dry run: no files were written.")
        sections.extend(_paths_section(result))
        if info_lines:
            sections.append(("Result", "\n".join(info_lines)))
        sections.extend(_format_diff(result.get("diff") if isinstance(result.get("diff"), str) else None))
    elif command == "exec":
        action = (result.get("action") or args.get("action") or "").strip() or "(unknown)"
        title = f"Executed note action '{action}'"
        if action in {"open", "reveal"}:
            sections.extend(_paths_section(result))
            key = "path" if action == "open" else "directory"
            location = result.get(key)
            if location:
                sections.append(("Location", str(location)))
        elif action == "index":
            paths = result.get("paths")
            if isinstance(paths, Iterable):
                lines = [str(p) for p in paths]
                if not lines:
                    lines.append("(no notes indexed)")
                sections.append(("Paths", "\n".join(lines)))
        else:
            sections.extend(_paths_section(result))
    else:
        title = f"Result for {command}"

    return NoteDisplay(title=title, sections=sections, dry_run=dry_run, raw=dict(result))


__all__ = [
    "KILL_SWITCH_PLACEHOLDER",
    "NoteDisplay",
    "build_vault_payload",
    "call_note_tool",
    "format_note_result",
    "is_notes_feature_enabled",
    "is_notes_kill_switch_enabled",
]
