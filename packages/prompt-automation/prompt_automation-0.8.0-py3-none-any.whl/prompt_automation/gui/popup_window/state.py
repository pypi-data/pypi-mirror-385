"""Transient state persistence for popup windows."""

from __future__ import annotations

import atexit
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from ...config import HOME_DIR


_CACHE_DIR = HOME_DIR / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_STATE_PATH = _CACHE_DIR / "popup-windows.json"


@dataclass
class PopupWindowSnapshot:
    """Serializable snapshot of popup window geometry/state."""

    geometry: str
    state: Optional[str]
    screen: Tuple[int, int]


class PopupWindowStateCache:
    """Lightweight geometry cache cleared when the app exits."""

    def __init__(
        self,
        *,
        path: Optional[Path] = None,
        autodelete: bool = True,
    ) -> None:
        self._path = path or _STATE_PATH
        self._autodelete = autodelete
        self._data: Dict[str, Dict[str, str]] = self._load()
        if autodelete:
            atexit.register(self._cleanup)

    @staticmethod
    def _screen_key(width: int, height: int) -> str:
        return f"{int(width)}x{int(height)}"

    def _load(self) -> Dict[str, Dict[str, str]]:
        try:
            if self._path.exists():
                payload = json.loads(self._path.read_text())
                screens = payload.get("screens")
                if isinstance(screens, dict):
                    cleaned: Dict[str, Dict[str, str]] = {}
                    for key, entry in screens.items():
                        if not isinstance(entry, dict):
                            continue
                        geometry = entry.get("geometry")
                        if not isinstance(geometry, str) or "x" not in geometry:
                            continue
                        state = entry.get("state")
                        if isinstance(state, str) and state.strip():
                            cleaned[key] = {
                                "geometry": geometry,
                                "state": state.strip(),
                            }
                        else:
                            cleaned[key] = {"geometry": geometry}
                    return cleaned
        except Exception:
            pass
        return {}

    def _flush(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps({"screens": self._data}, indent=2))
        except Exception:
            pass

    def restore(self, width: int, height: int) -> Optional[PopupWindowSnapshot]:
        key = self._screen_key(width, height)
        entry = self._data.get(key)
        if not entry:
            return None
        geometry = entry.get("geometry")
        if not isinstance(geometry, str) or "x" not in geometry:
            return None
        state = entry.get("state")
        if not isinstance(state, str):
            state = None
        else:
            state = state.strip() or None
        return PopupWindowSnapshot(geometry=geometry, state=state, screen=(width, height))

    def remember(self, width: int, height: int, geometry: Optional[str], state: Optional[str]) -> None:
        if not geometry or "x" not in geometry:
            return
        key = self._screen_key(width, height)
        record: Dict[str, str] = {"geometry": geometry}
        if isinstance(state, str):
            state = state.strip()
            if state:
                record["state"] = state
        self._data[key] = record
        self._flush()

    def clear(self) -> None:
        self._data.clear()
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def _cleanup(self) -> None:
        if not self._autodelete:
            return
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            pass


__all__ = [
    "PopupWindowSnapshot",
    "PopupWindowStateCache",
    "_STATE_PATH",
]
