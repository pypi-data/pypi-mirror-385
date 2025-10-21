from __future__ import annotations

"""Ctrl+digit hotkey extension for spawning popup windows."""

from typing import Callable, Dict, List


class DigitHotkeyExtension:
    """Register Ctrl+0-9 shortcuts with a hotkey service."""

    def __init__(
        self,
        service: "HotkeyService",
        spawn_popup: Callable[[str], None],
        focus_main: Callable[[], None],
    ) -> None:
        self._service = service
        self._spawn_popup = spawn_popup
        self._focus_main = focus_main
        self._registered: Dict[str, str] = {}
        self._conflicts: Dict[str, str] = {}

    def register(self) -> Dict[str, str]:
        for digit in map(str, range(10)):
            combo = f"Ctrl+{digit}"
            hotkey_id = f"prompt_automation.popup.{digit}"
            if digit == "0":
                callback = self._focus_main
            else:
                callback = lambda d=digit: self._spawn_popup(d)
            try:
                self._service.register_hotkey(hotkey_id, combo, callback)
            except Exception as exc:
                self._conflicts[hotkey_id] = str(exc)
                continue
            self._registered[hotkey_id] = combo
        return dict(self._conflicts)

    def unregister(self) -> None:
        for hotkey_id in list(self._registered.keys()):
            self._service.unregister_hotkey(hotkey_id)
        self._registered.clear()
        self._conflicts.clear()


class HotkeyService:
    """Protocol-like interface for hotkey services (typing aid)."""

    def register_hotkey(self, hotkey_id: str, combo: str, callback):  # pragma: no cover - interface
        raise NotImplementedError

    def unregister_hotkey(self, hotkey_id: str):  # pragma: no cover - interface
        raise NotImplementedError


__all__ = ["DigitHotkeyExtension", "HotkeyService"]

