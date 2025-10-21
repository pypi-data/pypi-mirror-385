from __future__ import annotations

"""Manage lifecycle of background and digit popup hotkeys."""

from typing import Any, Callable, Dict, Optional

from .digit_popup import DigitHotkeyExtension
from .. import background_hotkey


class HotkeyListener:
    """Coordinate registration of global and digit popup hotkeys."""

    def __init__(
        self,
        service: Optional[Any],
        spawn_popup: Callable[[str], None],
        focus_main: Callable[[], None],
    ) -> None:
        self._service = service
        self._spawn_popup = spawn_popup
        self._focus_main = focus_main
        self._digits: Optional[DigitHotkeyExtension] = None
        if service is not None and getattr(service, "available", True):
            self._digits = DigitHotkeyExtension(service, spawn_popup=spawn_popup, focus_main=focus_main)
        self._active = False
        self._conflicts: Dict[str, str] = {}

    @property
    def active(self) -> bool:
        return self._active

    @property
    def conflicts(self) -> Dict[str, str]:
        return dict(self._conflicts)

    def start(self, settings: Optional[dict] = None) -> bool:
        self._conflicts = {}
        if not self._service or not getattr(self._service, "available", True):
            return False
        settings = settings or {}
        try:
            ok = background_hotkey.ensure_registered(settings, self._service)
        except Exception as exc:
            self._conflicts["background_hotkey"] = str(exc)
            return False
        if not ok:
            self._conflicts["background_hotkey"] = "registration failed"
            return False
        if self._digits:
            conflicts = self._digits.register()
            if conflicts:
                self._conflicts.update(conflicts)
        self._active = True
        return True

    def stop(self) -> None:
        if not self._service or not getattr(self._service, "available", True):
            return
        try:
            background_hotkey.unregister(self._service)
        except Exception:
            pass
        if self._digits:
            try:
                self._digits.unregister()
            except Exception:
                pass
        self._active = False


__all__ = ["HotkeyListener"]
