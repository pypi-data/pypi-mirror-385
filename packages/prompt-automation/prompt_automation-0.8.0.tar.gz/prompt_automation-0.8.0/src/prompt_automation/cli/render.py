"""Template rendering helpers for the CLI."""
from __future__ import annotations

import signal
import threading
from contextlib import contextmanager
from typing import Any

from ..menus import provide_mcp_project_cancellation, render_template
from ..mcp.server import ProjectExecutionCancelled
from ..gui.file_append import _append_to_files


@contextmanager
def _install_sigint_handler(cancel: threading.Event) -> None:
    previous = signal.getsignal(signal.SIGINT)

    def _handler(signum, frame):  # type: ignore[override]
        cancel.set()
        if previous in (signal.SIG_IGN,):
            return
        if previous in (None, signal.SIG_DFL, signal.default_int_handler):
            raise KeyboardInterrupt
        if callable(previous):
            previous(signum, frame)

    signal.signal(signal.SIGINT, _handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, previous)


def render_template_cli(tmpl: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """Enhanced CLI template rendering with better prompts."""
    print(f"\nRendering template: {tmpl.get('title', 'Unknown')}")
    print(f"Style: {tmpl.get('style', 'Unknown')}")

    if tmpl.get("placeholders"):
        print(f"\nThis template requires {len(tmpl['placeholders'])} input(s):")
        for ph in tmpl["placeholders"]:
            label = ph.get("label", ph["name"])
            ptype = ph.get("type", "text")
            options = ph.get("options", [])
            multiline = ph.get("multiline", False)

            type_info = ptype
            if multiline:
                type_info += ", multiline"
            if options:
                type_info += f", options: {', '.join(options)}"

            print(f"  - {label} ({type_info})")

        if input("\nProceed with input collection? [Y/n]: ").lower() in {"n", "no"}:
            return None

    cancel_event = threading.Event()
    try:
        with provide_mcp_project_cancellation(cancel_event.is_set):
            with _install_sigint_handler(cancel_event):
                return render_template(tmpl, return_vars=True)
    except KeyboardInterrupt:
        cancel_event.set()
        raise
    except ProjectExecutionCancelled as exc:
        cancel_event.set()
        raise KeyboardInterrupt from exc


__all__ = ["render_template_cli", "_append_to_files"]

