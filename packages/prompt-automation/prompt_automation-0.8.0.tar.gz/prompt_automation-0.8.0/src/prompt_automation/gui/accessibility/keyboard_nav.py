"""Focus navigation utilities for keyboard accessibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List

try:  # Optional visual helpers
    from ..visual_feedback import indicators as _visual
except Exception:  # pragma: no cover - defensive fallback
    _visual = None  # type: ignore[assignment]


_SHIFT_MASK = 0x0001


def _call(widget: Any, name: str, *args, default=None):
    try:
        method = getattr(widget, name)
    except Exception:
        return default
    try:
        return method(*args)
    except Exception:
        return default


def _is_disabled(widget: Any) -> bool:
    try:
        state = widget.cget("state")  # type: ignore[attr-defined]
    except Exception:
        state = None
    if isinstance(state, str):
        return state.lower() in {"disabled", "disable"}
    return False


def _takes_focus(widget: Any) -> bool:
    try:
        tf = widget.cget("takefocus")  # type: ignore[attr-defined]
    except Exception:
        tf = None
    if tf in {None, "", "1", 1, True}:
        return True
    return False


@dataclass
class FocusNavigator:
    """Cycle focus between registered widgets when Tab is pressed."""

    root: Any
    highlight: bool = True
    order: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        try:
            self.root.bind_all("<KeyPress-Tab>", self._on_tab, add="+")
        except Exception:
            pass
        self._highlighted: set[Any] = set()

    # Registration -----------------------------------------------------
    def register(self, widget: Any) -> None:
        """Add *widget* to the focus cycle if it can receive focus."""

        if not self._should_include(widget):
            return
        if widget not in self.order:
            self.order.append(widget)
        if self.highlight and widget not in self._highlighted:
            self._apply_highlight(widget)
            self._highlighted.add(widget)

    def reset(self, widgets: Iterable[Any]) -> None:
        """Replace the cycle order with *widgets* filtering out ineligible ones."""

        self.order = []
        for widget in widgets:
            self.register(widget)

    # Event handling ---------------------------------------------------
    def _on_tab(self, event) -> str | None:
        return self.handle_tab(event)

    def handle_tab(self, event) -> str | None:
        """Advance focus forward/backward depending on the event state."""

        if not self.order:
            return None

        forward = not bool(getattr(event, "state", 0) & _SHIFT_MASK)
        widgets = [w for w in self.order if self._is_focusable(w)]
        if not widgets:
            return None

        current = _call(self.root, "focus_get")
        try:
            idx = widgets.index(current)
        except Exception:
            idx = -1

        if forward:
            idx = (idx + 1) % len(widgets)
        else:
            idx = (idx - 1) % len(widgets)

        target = widgets[idx]
        _call(target, "focus_set")
        return "break"

    # Helpers ----------------------------------------------------------
    def _should_include(self, widget: Any) -> bool:
        return widget is not None and _takes_focus(widget)

    def _is_focusable(self, widget: Any) -> bool:
        if widget is None:
            return False
        if _is_disabled(widget):
            return False
        visible = _call(widget, "winfo_viewable", default=True)
        return bool(visible)

    def _apply_highlight(self, widget: Any) -> None:
        if not self.highlight or widget is None:
            return
        helper = getattr(_visual, "configure_focus_highlight", None)
        if helper is None:
            return
        try:
            helper(widget)
        except Exception:
            pass


__all__ = ["FocusNavigator"]
