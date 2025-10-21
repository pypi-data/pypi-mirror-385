"""Context-aware Escape key handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable


Predicate = Callable[[], bool]
Callback = Callable[[], Any]


@dataclass
class _Action:
    callback: Callback
    predicate: Predicate
    priority: int


class EscapeHandler:
    """Dispatch Escape presses according to a priority list."""

    def __init__(self, root: Any | None = None) -> None:
        self._actions: Dict[str, _Action] = {}
        self._root = root
        if root is not None:
            try:
                root.bind_all("<Escape>", self._on_escape, add="+")
            except Exception:
                pass

    def register(
        self,
        name: str,
        callback: Callback,
        *,
        predicate: Predicate | None = None,
        priority: int = 100,
    ) -> None:
        """Register an Escape action under *name* replacing any previous entry."""

        pred = predicate or (lambda: True)
        self._actions[name] = _Action(callback=callback, predicate=pred, priority=priority)

    def unregister(self, name: str) -> None:
        self._actions.pop(name, None)

    def clear(self, names: Iterable[str]) -> None:
        for name in names:
            self.unregister(name)

    def handle_escape(self, _event=None):
        """Execute the highest-priority action whose predicate passes."""

        ordered = sorted(self._actions.items(), key=lambda kv: kv[1].priority)
        for _name, action in ordered:
            try:
                if not action.predicate():
                    continue
            except Exception:
                continue
            try:
                result = action.callback()
            except Exception:
                return "break"
            if result is None:
                return "break"
            return result
        return None

    # Tk binding -------------------------------------------------------
    def _on_escape(self, event):
        result = self.handle_escape(event)
        if result is None:
            return "break"
        return result


__all__ = ["EscapeHandler"]
