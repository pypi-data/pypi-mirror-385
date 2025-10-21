from __future__ import annotations

"""Cross-platform global shortcut service abstraction."""

import threading
from typing import Callable, Dict, Optional

from ..errorlog import get_logger

Callback = Callable[[], None]


def _normalize_combo(combo: str) -> str:
    parts = []
    for segment in combo.replace("-", "+").split("+"):
        token = segment.strip()
        if not token:
            continue
        token = token.lower()
        replacements = {
            "control": "ctrl",
            "ctl": "ctrl",
            "cmd": "command",
            "option": "alt",
        }
        token = replacements.get(token, token)
        parts.append(token)
    return "+".join(parts)


class _BaseBackend:
    name = "noop"

    def __init__(self) -> None:
        self._handlers: Dict[str, Callback] = {}

    def register(self, hotkey_id: str, combo: str, callback: Callback) -> None:
        self._handlers[hotkey_id] = callback

    def unregister(self, hotkey_id: str) -> None:
        self._handlers.pop(hotkey_id, None)

    def stop(self) -> None:
        self._handlers.clear()

    def trigger(self, hotkey_id: str) -> None:
        callback = self._handlers.get(hotkey_id)
        if callback:
            callback()

    @property
    def available(self) -> bool:
        return False


class _KeyboardBackend(_BaseBackend):
    name = "keyboard"

    def __init__(self) -> None:
        import keyboard  # type: ignore

        super().__init__()
        self._keyboard = keyboard
        self._listener_handles: Dict[str, int] = {}

    def register(self, hotkey_id: str, combo: str, callback: Callback) -> None:
        normalized = _normalize_combo(combo)
        self.unregister(hotkey_id)
        handle = self._keyboard.add_hotkey(normalized, callback, suppress=False, trigger_on_release=False)
        self._listener_handles[hotkey_id] = handle
        self._handlers[hotkey_id] = callback

    def unregister(self, hotkey_id: str) -> None:
        handle = self._listener_handles.pop(hotkey_id, None)
        if handle is not None:
            try:
                self._keyboard.remove_hotkey(handle)
            except Exception:
                pass
        self._handlers.pop(hotkey_id, None)

    def stop(self) -> None:
        for handle in list(self._listener_handles.values()):
            try:
                self._keyboard.remove_hotkey(handle)
            except Exception:
                pass
        self._listener_handles.clear()
        super().stop()

    @property
    def available(self) -> bool:
        return True


class GlobalShortcutService:
    """Facade exposing a consistent API regardless of backend availability."""

    def __init__(self) -> None:
        self._log = get_logger("prompt_automation.global_shortcut_service")
        self._lock = threading.RLock()
        self._backend = self._init_backend()

    def _init_backend(self) -> _BaseBackend:
        backend: Optional[_BaseBackend] = None
        for backend_factory in (_KeyboardBackend,):
            try:
                candidate = backend_factory()
            except Exception as exc:
                try:
                    self._log.debug("global_shortcut_backend_init_failed backend=%s error=%s", backend_factory.__name__, exc)
                except Exception:
                    pass
                continue
            if candidate.available:
                backend = candidate
                break
        if backend is None:
            backend = _BaseBackend()
            try:
                self._log.warning("global_shortcut_backend_unavailable")
            except Exception:
                pass
        else:
            try:
                self._log.info("global_shortcut_backend_active name=%s", backend.name)
            except Exception:
                pass
        return backend

    def register_hotkey(self, hotkey_id: str, combo: str, callback: Callback) -> None:
        with self._lock:
            try:
                self._backend.register(hotkey_id, combo, callback)
            except Exception as exc:
                try:
                    self._log.error("global_shortcut_register_failed id=%s combo=%s error=%s", hotkey_id, combo, exc)
                except Exception:
                    pass
                raise

    def unregister_hotkey(self, hotkey_id: str) -> None:
        with self._lock:
            try:
                self._backend.unregister(hotkey_id)
            except Exception as exc:
                try:
                    self._log.error("global_shortcut_unregister_failed id=%s error=%s", hotkey_id, exc)
                except Exception:
                    pass
                raise

    def stop(self) -> None:
        with self._lock:
            try:
                self._backend.stop()
            except Exception as exc:
                try:
                    self._log.error("global_shortcut_stop_failed error=%s", exc)
                except Exception:
                    pass

    def trigger(self, hotkey_id: str) -> None:
        with self._lock:
            self._backend.trigger(hotkey_id)

    @property
    def available(self) -> bool:
        return self._backend.available


service = GlobalShortcutService()

__all__ = ["service", "GlobalShortcutService"]
