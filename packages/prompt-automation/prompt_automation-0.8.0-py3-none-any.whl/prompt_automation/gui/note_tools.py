from __future__ import annotations

"""GUI helpers for interacting with MCP note tooling."""

import json
from typing import Any, Dict

from ..errorlog import get_logger
from ..mcp import notes_integration
from ..variables import storage

NoteDisplay = notes_integration.NoteDisplay

_log = get_logger(__name__)


def _prompt_optional(label: str, *, initial: str | None = None, parent=None) -> str | None:
    import tkinter.simpledialog as simpledialog

    value = simpledialog.askstring("Notes", label, initialvalue=initial or "", parent=parent)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _prompt_reference_file(parent=None) -> str | None:
    default = storage.get_global_reference_file() or ""
    return _prompt_optional("Reference file", initial=default, parent=parent)


def _prompt_note_path(parent=None, *, title: str = "Note path") -> str | None:
    return _prompt_optional(title, parent=parent)


def _prompt_query(parent=None) -> str | None:
    return _prompt_optional("Search query", parent=parent)


def _prompt_max_results(parent=None) -> int | None:
    raw = _prompt_optional("Max results (1-200)", parent=parent, initial="25")
    if raw is None:
        return None
    try:
        value = max(1, min(int(raw), 200))
    except ValueError:
        value = 25
    return value


def _prompt_note_content(parent=None, *, initial: str | None = None) -> str | None:
    import tkinter as tk
    from tkinter import scrolledtext

    root = parent or tk._default_root  # type: ignore[attr-defined]
    win = tk.Toplevel(root)
    win.title("Note content")
    win.geometry("720x520")
    text = scrolledtext.ScrolledText(win, wrap="word")
    text.pack(fill="both", expand=True)
    if initial:
        text.insert("1.0", initial)

    result: Dict[str, str | None] = {"value": None}

    def _submit() -> None:
        try:
            result["value"] = text.get("1.0", "end-1c")
        except Exception:
            result["value"] = None
        win.destroy()

    def _cancel() -> None:
        result["value"] = None
        win.destroy()

    button_frame = tk.Frame(win)
    button_frame.pack(fill="x")
    tk.Button(button_frame, text="OK", command=_submit).pack(side="left", padx=6, pady=6)
    tk.Button(button_frame, text="Cancel", command=_cancel).pack(side="right", padx=6, pady=6)
    win.transient(root)
    win.grab_set()
    win.wait_window()
    return result["value"]


def _prompt_bool(message: str, *, parent=None, default: bool = False) -> bool:
    from tkinter import messagebox

    return messagebox.askyesno("Notes", message, parent=parent, default="yes" if default else "no")


def _present_error(message: str, *, parent=None) -> None:
    from tkinter import messagebox

    messagebox.showerror("Notes", message, parent=parent)


def _present_result(display: NoteDisplay, *, parent=None) -> None:
    import tkinter as tk
    from tkinter import scrolledtext

    root = parent or tk._default_root  # type: ignore[attr-defined]
    win = tk.Toplevel(root)
    win.title(display.title)
    win.geometry("720x520")

    text = scrolledtext.ScrolledText(win, wrap="word")
    text.pack(fill="both", expand=True)

    lines: list[str] = [display.title, ""]
    for heading, body in display.sections:
        if not body:
            continue
        lines.append(f"{heading}:")
        lines.append(body)
        lines.append("")
    if not display.sections:
        lines.append("(no additional details)")
    text.insert("1.0", "\n".join(lines))
    text.configure(state="disabled")

    tk.Button(win, text="Close", command=win.destroy).pack(pady=6)


def _build_common_arguments(
    reference_file: str,
    *,
    trace_id: str | None,
    idempotency_key: str | None,
    dry_run: bool,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "vault": notes_integration.build_vault_payload(reference_file),
    }
    if trace_id:
        payload["trace_id"] = trace_id
    if idempotency_key:
        payload["idempotency_key"] = idempotency_key
    if dry_run:
        payload["dry_run"] = True
    return payload


def _execute(command: str, arguments: Dict[str, Any], *, parent=None) -> None:
    try:
        result = notes_integration.call_note_tool(command, arguments)
    except Exception as exc:  # pragma: no cover - defensive
        _log.error("notes_command_failed command=%s error=%s", command, exc)
        _present_error(f"Failed to execute notes command: {exc}", parent=parent)
        return
    display = notes_integration.format_note_result(command, result, arguments=arguments)
    _present_result(display, parent=parent)


def read_note(parent=None) -> None:
    reference = _prompt_reference_file(parent)
    if not reference:
        return
    path = _prompt_note_path(parent)
    if not path:
        return
    encoding = _prompt_optional("Encoding (optional)", parent=parent)
    trace_id = _prompt_optional("Trace ID", parent=parent)
    idempotency_key = _prompt_optional("Idempotency key", parent=parent)

    arguments = _build_common_arguments(reference, trace_id=trace_id, idempotency_key=idempotency_key, dry_run=False)
    arguments["path"] = path
    if encoding:
        arguments["encoding"] = encoding
    _execute("read", arguments, parent=parent)


def search_notes(parent=None) -> None:
    reference = _prompt_reference_file(parent)
    if not reference:
        return
    query = _prompt_query(parent)
    if not query:
        return
    max_results = _prompt_max_results(parent)
    trace_id = _prompt_optional("Trace ID", parent=parent)
    idempotency_key = _prompt_optional("Idempotency key", parent=parent)

    arguments = _build_common_arguments(reference, trace_id=trace_id, idempotency_key=idempotency_key, dry_run=False)
    arguments["query"] = query
    if max_results is not None:
        arguments["max_results"] = max_results
    _execute("search", arguments, parent=parent)


def upsert_note(parent=None) -> None:
    reference = _prompt_reference_file(parent)
    if not reference:
        return
    path = _prompt_note_path(parent)
    if not path:
        return
    content = _prompt_note_content(parent)
    if content is None:
        return
    dry_run = _prompt_bool("Preview changes without writing?", parent=parent, default=True)
    trace_id = _prompt_optional("Trace ID", parent=parent)
    idempotency_key = _prompt_optional("Idempotency key", parent=parent)

    arguments = _build_common_arguments(reference, trace_id=trace_id, idempotency_key=idempotency_key, dry_run=dry_run)
    arguments["path"] = path
    arguments["content"] = content
    _execute("upsert", arguments, parent=parent)


def exec_note_command(parent=None) -> None:
    reference = _prompt_reference_file(parent)
    if not reference:
        return
    action = _prompt_optional("Action (open, reveal, index)", parent=parent)
    if not action:
        return
    normalized = action.strip().lower()
    trace_id = _prompt_optional("Trace ID", parent=parent)
    idempotency_key = _prompt_optional("Idempotency key", parent=parent)
    dry_run = False
    arguments = _build_common_arguments(reference, trace_id=trace_id, idempotency_key=idempotency_key, dry_run=dry_run)
    arguments["action"] = normalized
    if normalized in {"open", "reveal"}:
        path = _prompt_note_path(parent, title="Note path")
        if not path:
            return
        arguments["path"] = path
    if normalized == "index":
        dry_run_choice = _prompt_bool("Preview index without changes?", parent=parent)
        if dry_run_choice:
            arguments["dry_run"] = True
    extra = _prompt_optional("Additional JSON arguments (optional)", parent=parent)
    if extra:
        try:
            parsed = json.loads(extra)
        except json.JSONDecodeError as exc:
            _present_error(f"Invalid JSON: {exc}", parent=parent)
            return
        if not isinstance(parsed, dict):
            _present_error("Arguments must be a JSON object", parent=parent)
            return
        arguments["arguments"] = parsed
    _execute("exec", arguments, parent=parent)


__all__ = [
    "NoteDisplay",
    "exec_note_command",
    "read_note",
    "search_notes",
    "upsert_note",
]
