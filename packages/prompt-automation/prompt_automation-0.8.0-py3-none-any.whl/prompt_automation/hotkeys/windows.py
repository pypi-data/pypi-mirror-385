from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable, Sequence

from ..launchers import iter_windows_launch_commands


def _to_ahk(hotkey: str) -> str:
    """Convert a human hotkey like 'ctrl+shift+j' to AHK '^+j' with normalized order.

    AHK expects modifiers in a consistent order and does not care about case.
    We canonicalize modifier order to: ctrl, shift, alt, win/cmd.
    """
    mapping = {"ctrl": "^", "shift": "+", "alt": "!", "win": "#", "cmd": "#"}
    order = {"ctrl": 0, "shift": 1, "alt": 2, "win": 3, "cmd": 3}
    parts = hotkey.lower().split("+")
    mods, key = parts[:-1], parts[-1]
    # normalize modifier order
    mods_sorted = sorted((m for m in mods if m), key=lambda m: order.get(m, 99))
    return "".join(mapping.get(m, m) for m in mods_sorted) + key


def _update_windows(hotkey: str) -> None:
    # Observability: registration start
    if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
        print(
            f"[prompt-automation] hotkey_registration_start os=Windows hotkey={hotkey}"
        )

    ahk_hotkey = _to_ahk(hotkey)
    startup = (
        Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    startup.mkdir(parents=True, exist_ok=True)
    script_path = startup / "prompt-automation.ahk"

    commands = iter_windows_launch_commands()

    def _normalize(command: str) -> str:
        command = command.strip()
        if (" " in command or "\t" in command) and ("\\" in command or "/" in command):
            if not command.startswith('"'):
                return f'"{command}"'
        return command

    normalized = [_normalize(cmd) for cmd in commands]

    def _format_run(command: str, args: Sequence[str], hide: bool, indent: str) -> str:
        arg_text = " ".join(args)
        space = f" {arg_text}" if arg_text else ""
        hide_text = ",, Hide" if hide else ""
        return f"{indent}Run, {command}{space}{hide_text}\n"

    def _failure(indent: str) -> str:
        return (
            f"{indent}; Final fallback - show error\n"
            f"{indent}MsgBox, 16, Error, prompt-automation failed to start. Please check installation.\n"
        )

    def _build_nested(
        command_list: Sequence[str],
        args: Sequence[str],
        hide: bool,
        indent: str,
        fallback: Callable[[str], str] | None,
    ) -> str:
        if not command_list:
            return fallback(indent) if fallback else ""

        head = command_list[0]
        tail = command_list[1:]
        block = [_format_run(head, args, hide, indent)]
        if tail:
            block.append(f"{indent}if ErrorLevel\n")
            block.append(f"{indent}{{\n")
            block.append(_build_nested(tail, args, hide, indent + "    ", fallback))
            block.append(f"{indent}}}\n")
        elif fallback is not None:
            block.append(f"{indent}if ErrorLevel\n")
            block.append(f"{indent}{{\n")
            block.append(fallback(indent + "    "))
            block.append(f"{indent}}}\n")
        return "".join(block)

    def _terminal_block(indent: str) -> str:
        return _build_nested(normalized, ["--terminal"], False, indent, lambda i: _failure(i))

    def _gui_block(indent: str) -> str:
        return _build_nested(normalized, ["--gui"], True, indent, _terminal_block)

    def _focus_block(indent: str) -> str:
        return _build_nested(normalized, ["--focus"], True, indent, _gui_block)

    focus_block = _focus_block("    ")

    # Build AHK script without shell chaining operators. Each attempt is a
    # separate Run with ErrorLevel checks for deterministic fallback.
    content = (
        "#NoEnv\n#SingleInstance Force\n#InstallKeybdHook\n#InstallMouseHook\n"
        "#MaxHotkeysPerInterval 99000000\n#HotkeyInterval 99000000\n#KeyHistory 0\n\n"
        f"; {hotkey} launches prompt-automation with GUI focus and fallbacks\n"
        f"{ahk_hotkey}::\n"
        "{\n"
        "    ; Try to focus existing GUI instance via preferred launch order\n"
        f"{focus_block}"
        "    return\n"
        "}\n"
    )
    script_path.write_text(content)
    try:  # pragma: no cover - external tool
        subprocess.Popen(["AutoHotkey", str(script_path)])
        if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
            print(
                f"[prompt-automation] hotkey_registration_success os=Windows script={script_path}"
            )
    except Exception as e:
        if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
            print(
                f"[prompt-automation] hotkey_registration_failure os=Windows reason={e}"
            )
        pass
