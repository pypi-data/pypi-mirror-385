"""State persistence helpers for recovering selector progress."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Set

from .. import config as _config
from ..gui.single_window import geometry as _geometry


def _canon(rel: str) -> str:
    """Normalize a relative path into a forward-slash string without empties."""

    parts = [p for p in Path(str(rel)).parts if p]
    return "/".join(parts)


def _canon_root(rel: str | Path) -> str:
    """Return a canonical absolute path for prompts root comparison."""

    try:
        return str(Path(rel).expanduser().resolve())
    except Exception:
        try:
            return str(Path(rel).expanduser())
        except Exception:
            return str(rel)


@dataclass
class SelectorState:
    cwd_rel: str = ""
    query: str = ""
    expanded: Set[str] = field(default_factory=set)


class SelectorStateStore:
    """Persist selector UI state scoped to the active prompts root."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path) if path is not None else _geometry.SETTINGS_PATH

    def load(self) -> SelectorState:
        payload = self._read()
        state_data = payload.get("selector_state") if isinstance(payload, dict) else {}
        expanded_raw = None
        root_saved = ""
        if isinstance(state_data, dict):
            cwd = str(state_data.get("cwd", "") or "")
            query = str(state_data.get("query", "") or "")
            expanded_raw = state_data.get("expanded")
            root_val = state_data.get("root")
            if isinstance(root_val, (str, Path)):
                root_saved = _canon_root(root_val)
        else:
            cwd = ""
            query = ""

        if expanded_raw is None:
            expanded_raw = payload.get("selector_expanded") if isinstance(payload, dict) else None

        expanded: Set[str] = set()
        if isinstance(expanded_raw, (list, tuple, set)):
            for item in expanded_raw:
                if isinstance(item, (str, int)):
                    expanded.add(_canon(str(item)))

        current_root = _canon_root(_config.PROMPTS_DIR)
        if root_saved and root_saved != current_root:
            # A previously persisted state belongs to another prompts root, so
            # ignore it to prevent cross-project folder expansions from leaking.
            return SelectorState()

        return SelectorState(cwd_rel=_canon(cwd), query=query, expanded=expanded)

    def save(self, state: SelectorState) -> None:
        payload = self._read()
        if not isinstance(payload, dict):
            payload = {}
        payload["selector_state"] = {
            "cwd": _canon(state.cwd_rel),
            "query": state.query,
            "expanded": sorted({_canon(rel) for rel in state.expanded if rel}),
            "root": _canon_root(_config.PROMPTS_DIR),
        }
        # Maintain backwards compatibility with legacy expanded format
        payload["selector_expanded"] = payload["selector_state"]["expanded"]
        self._write(payload)

    def update(
        self,
        *,
        cwd_rel: str | None = None,
        query: str | None = None,
        expanded: Iterable[str] | None = None,
    ) -> SelectorState:
        current = self.load()
        if cwd_rel is not None:
            current.cwd_rel = _canon(cwd_rel)
        if query is not None:
            current.query = query
        if expanded is not None:
            current.expanded = {_canon(rel) for rel in expanded if rel}
        self.save(current)
        return current

    def clear(self) -> None:
        payload = self._read()
        if not isinstance(payload, dict):
            return
        payload.pop("selector_state", None)
        payload.pop("selector_expanded", None)
        self._write(payload)

    # Internal ---------------------------------------------------------
    def _read(self):
        try:
            if self._path.exists():
                return json.loads(self._path.read_text()) or {}
        except Exception:
            return {}
        return {}

    def _write(self, payload: dict) -> None:
        try:
            self._path.write_text(json.dumps(payload, indent=2))
        except Exception:
            pass


__all__ = ["SelectorState", "SelectorStateStore"]
