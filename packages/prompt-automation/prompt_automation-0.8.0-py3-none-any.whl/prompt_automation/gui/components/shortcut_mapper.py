from __future__ import annotations

"""Display component for digit → template shortcut mappings."""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Dict, List


@dataclass
class ShortcutRow:
    digit: str
    title: str
    rel: str
    path: str
    label: str


class ShortcutMapperModel:
    """Format shortcut mapping data for UI consumption."""

    def __init__(self, mapping: Dict[str, str], resolver: Callable[[str], Dict[str, Any]]):
        self._resolver = resolver
        self._mapping: Dict[str, str] = {}
        self.rows: List[Dict[str, str]] = []
        self.update(mapping)

    def update(self, mapping: Dict[str, str]) -> None:
        self._mapping = {str(k): str(v) for k, v in mapping.items() if str(k).isdigit()}
        self.rows = [self._row_for_digit(str(d)) for d in range(10)]

    def _row_for_digit(self, digit: str) -> Dict[str, str]:
        rel = self._mapping.get(digit)
        if not rel:
            return {
                "digit": digit,
                "title": "Unassigned",
                "rel": "",
                "path": "",
                "label": f"{digit}: Unassigned",
            }
        meta = self._safe_resolve(rel)
        title = str(meta.get("title") or meta.get("name") or rel)
        display_path = str(meta.get("path") or rel)
        label = f"{digit}: {title} — {display_path}"
        return {
            "digit": digit,
            "title": title,
            "rel": rel,
            "path": display_path,
            "label": label,
        }

    def _safe_resolve(self, rel: str) -> Dict[str, Any]:
        try:
            data = self._resolver(rel)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {"title": rel, "path": rel}


def build_shortcut_mapper(parent: Any, model: ShortcutMapperModel, on_activate: Callable[[str], None] | None = None):  # pragma: no cover - Tk runtime
    """Render shortcut rows into ``parent``.

    Falls back to a headless stub when tkinter widgets are unavailable (e.g.
    during unit tests or CLI usage).
    """
    try:
        import tkinter as tk
    except Exception:  # pragma: no cover - defensive
        tk = None  # type: ignore[assignment]

    if tk is None or not hasattr(parent, "tk"):
        stub = _build_stub(model)
        return SimpleNamespace(widget=None, update=stub.update, model=model, rows=lambda: model.rows)

    frame = tk.Frame(parent)
    frame.grid_columnconfigure(1, weight=1)
    labels: Dict[str, Any] = {}

    def _render() -> None:
        for digit, lbl in labels.items():
            row = model.rows[int(digit)]
            text = row["label"]
            try:
                lbl.configure(text=text)
            except Exception:
                pass

    for idx, row in enumerate(model.rows):
        digit = row["digit"]
        btn = tk.Button(
            frame,
            text=digit,
            width=2,
            command=(lambda d=digit: on_activate(d) if on_activate else None),
            takefocus=0,
        )
        btn.grid(row=idx, column=0, padx=(4, 4), pady=(1, 1))
        lbl = tk.Label(frame, text=row["label"], anchor="w")
        lbl.grid(row=idx, column=1, sticky="we", pady=(1, 1))
        labels[digit] = lbl

    def update_view(new_mapping: Dict[str, str]) -> None:
        model.update(new_mapping)
        _render()

    _render()

    return SimpleNamespace(widget=frame, update=update_view, model=model, rows=lambda: model.rows)


def _build_stub(model: ShortcutMapperModel):
    """Return a minimal stub exposing ``rows`` and ``update``."""
    class _Stub:
        def __init__(self, mdl: ShortcutMapperModel):
            self.model = mdl

        @property
        def rows(self) -> List[Dict[str, str]]:
            return self.model.rows

        def update(self, mapping: Dict[str, str]) -> None:
            self.model.update(mapping)

    return _Stub(model)


__all__ = ["ShortcutMapperModel", "build_shortcut_mapper", "ShortcutRow"]
