from __future__ import annotations

import tkinter as tk

from .constants import INFO_CLOSE_SAVE
from ..variables import storage
from ..features import is_mcp_enabled, is_mcp_observability_enabled
from ..errorlog import get_logger

_log = get_logger(__name__)


def _refresh_hotkey() -> None:
    """Refresh background hotkey registration best-effort."""
    try:  # pragma: no cover - relies on optional service
        from ..cli.controller import PromptCLI

        PromptCLI()._maybe_register_background_hotkey()
    except Exception as e:  # pragma: no cover - defensive
        try:
            _log.error("hotkey_refresh_failed error=%s", e)
        except Exception:
            pass


def open_settings_panel(root) -> None:  # pragma: no cover - GUI heavy
    """Open settings panel window."""
    win = tk.Toplevel(root)
    win.title("Settings")
    win.resizable(False, False)
    frame = tk.Frame(win, padx=12, pady=8)
    frame.pack(fill="both", expand=True)

    # Store variables as window attributes to prevent garbage collection
    bg_var = tk.BooleanVar(value=storage.get_background_hotkey_enabled())
    esp_var = tk.BooleanVar(value=storage.get_espanso_enabled())
    use_mcp_server_var = tk.BooleanVar(value=storage.get_use_mcp_server())
    
    # Keep variables alive by storing them on the window
    win._bg_var = bg_var
    win._esp_var = esp_var
    win._use_mcp_server_var = use_mcp_server_var

    debug_mode_labels = [
        ("Off", "off"),
        ("CLI only", "cli"),
        ("CLI + Observability", "observability"),
    ]
    _label_to_value = {label: value for label, value in debug_mode_labels}
    _value_to_label = {value: label for label, value in debug_mode_labels}
    persisted_mode = storage.get_mcp_debug_mode()
    if is_mcp_observability_enabled():
        effective_mode = "observability"
    elif is_mcp_enabled():
        effective_mode = "cli"
    else:
        effective_mode = persisted_mode
    debug_mode_var = tk.StringVar(value=_value_to_label.get(effective_mode, "Off"))

    def _toggle_bg() -> None:
        try:
            new_value = bg_var.get()
            _log.info("toggle_background_hotkey value=%s", new_value)
            storage.set_background_hotkey_enabled(new_value)
            _refresh_hotkey()
            _log.info("toggle_background_hotkey_success new_value=%s", new_value)
        except Exception as e:
            _log.error("toggle_background_hotkey_failed error=%s", e)

    def _toggle_esp() -> None:
        try:
            new_value = esp_var.get()
            _log.info("toggle_espanso value=%s", new_value)
            storage.set_espanso_enabled(new_value)
            _refresh_hotkey()
            _log.info("toggle_espanso_success new_value=%s", new_value)
        except Exception as e:
            _log.error("toggle_espanso_failed error=%s", e)

    def _toggle_use_mcp_server() -> None:
        try:
            new_value = use_mcp_server_var.get()
            _log.info("toggle_use_mcp_server value=%s", new_value)
            storage.set_use_mcp_server(new_value)
            _log.info("toggle_use_mcp_server_success new_value=%s", new_value)
        except Exception as e:
            _log.error("toggle_use_mcp_server_failed error=%s", e)

    def _set_debug_mode(selected_label: str) -> None:
        mode_value = _label_to_value.get(selected_label, "off")
        try:
            storage.set_mcp_debug_mode(mode_value)
        except Exception as e:
            _log.error("set_mcp_debug_mode_failed error=%s", e)
            debug_mode_var.set(_value_to_label.get(storage.get_mcp_debug_mode(), "Off"))

    tk.Checkbutton(
        frame,
        text="Enable background activation hotkey",
        variable=bg_var,
        command=_toggle_bg,
        anchor="w",
        justify="left",
    ).pack(anchor="w")
    tk.Checkbutton(
        frame,
        text="Enable Espanso integration",
        variable=esp_var,
        command=_toggle_esp,
        anchor="w",
        justify="left",
    ).pack(anchor="w", pady=(4, 0))
    tk.Checkbutton(
        frame,
        text="Use MCP server integration",
        variable=use_mcp_server_var,
        command=_toggle_use_mcp_server,
        anchor="w",
        justify="left",
    ).pack(anchor="w", pady=(4, 0))

    tk.Label(
        frame,
        text="Setup help: see docs/MCP_INTEGRATION.md",
        justify="left",
        anchor="w",
    ).pack(anchor="w", padx=(20, 0))

    tk.Label(frame, text="MCP Debug Mode").pack(anchor="w", pady=(12, 0))
    tk.OptionMenu(
        frame,
        debug_mode_var,
        *[label for label, _ in debug_mode_labels],
        command=_set_debug_mode,
    ).pack(anchor="w", pady=(2, 0))

    def _open_manual_packaging():  # pragma: no cover - GUI heavy
        try:
            from .manual_packaging_dialog import open_manual_packaging_dialog

            open_manual_packaging_dialog(win)
        except Exception as exc:
            _log.error("manual_packaging_dialog_failed error=%s", exc)

    tk.Button(frame, text="Manual packaging...", command=_open_manual_packaging).pack(anchor="w", pady=(10, 0))

    tk.Button(frame, text=INFO_CLOSE_SAVE, command=win.destroy).pack(anchor="e", pady=(8, 0))


__all__ = ["open_settings_panel"]
