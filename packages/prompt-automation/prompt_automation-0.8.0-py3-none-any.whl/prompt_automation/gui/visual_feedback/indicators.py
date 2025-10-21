"""Visual cues shared across GUI components."""

from __future__ import annotations

from typing import Any


def folder_indicator(expanded: bool) -> str:
    """Return the unicode triangle used for folders."""

    return "▼️" if expanded else "▶️"


def format_folder_label(name: str, depth: int, expanded: bool) -> str:
    """Return a listbox label with indentation and expansion indicator."""

    indent = "  " * max(depth, 0)
    display = name or "/"
    return f"{indent}{folder_indicator(expanded)} {display}/"


def configure_focus_highlight(
    widget: Any,
    *,
    focus_color: str = "#4A90E2",
    normal_color: str = "#b9c6d8",
    thickness: int = 2,
) -> None:
    """Enhance the widget's native focus ring using Tk attributes."""

    try:
        widget.configure(
            highlightthickness=thickness,
            highlightbackground=normal_color,
            highlightcolor=normal_color,
        )
    except Exception:
        return

    def _focus_in(_event=None):
        try:
            widget.configure(highlightbackground=focus_color, highlightcolor=focus_color)
        except Exception:
            pass

    def _focus_out(_event=None):
        try:
            widget.configure(highlightbackground=normal_color, highlightcolor=normal_color)
        except Exception:
            pass

    try:
        widget.bind("<FocusIn>", _focus_in, add="+")
        widget.bind("<FocusOut>", _focus_out, add="+")
    except Exception:
        pass


__all__ = ["folder_indicator", "format_folder_label", "configure_focus_highlight"]
