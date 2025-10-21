"""WSL2-specific Windows hotkey integration.

This module generates AutoHotkey scripts that bridge Windows → WSL2 → prompt-automation.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _to_ahk(hotkey: str) -> str:
    """Convert a human hotkey like 'ctrl+shift+j' to AHK '^+j' with normalized order."""
    mapping = {"ctrl": "^", "shift": "+", "alt": "!", "win": "#", "cmd": "#"}
    order = {"ctrl": 0, "shift": 1, "alt": 2, "win": 3, "cmd": 3}
    parts = hotkey.lower().split("+")
    mods, key = parts[:-1], parts[-1]
    # normalize modifier order
    mods_sorted = sorted((m for m in mods if m), key=lambda m: order.get(m, 99))
    return "".join(mapping.get(m, m) for m in mods_sorted) + key


def _detect_ahk_version() -> int:
    """Detect AutoHotkey version (1 or 2) installed on Windows.
    
    Returns:
        1 for AutoHotkey v1.x
        2 for AutoHotkey v2.x
    """
    try:
        # Check if v2 directory exists (most reliable method)
        result = subprocess.run(
            ["powershell.exe", "-Command", "Test-Path 'C:\\Program Files\\AutoHotkey\\v2'"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip().lower() == "true":
            return 2
        
        # Check if AutoHotkey.exe exists in v2 location
        result = subprocess.run(
            ["powershell.exe", "-Command", "Test-Path 'C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe'"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip().lower() == "true":
            return 2
    except Exception:
        pass
    
    # Default to v1 (more forgiving syntax)
    return 1


def _get_wsl_distro_name() -> str:
    """Get the current WSL2 distro name from /etc/wsl.conf or environment."""
    # Try environment variable first (most reliable)
    wsl_distro = os.environ.get("WSL_DISTRO_NAME")
    if wsl_distro:
        return wsl_distro
    
    # Fallback: Try to read from /etc/wsl.conf
    try:
        wsl_conf = Path("/etc/wsl.conf")
        if wsl_conf.exists():
            content = wsl_conf.read_text()
            for line in content.splitlines():
                if line.strip().startswith("name"):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    
    # Final fallback: assume Ubuntu (most common)
    return "Ubuntu"


def _update_windows_wsl2(hotkey: str, wsl_distro: str | None = None) -> None:
    """Generate Windows AutoHotkey script that launches WSL2 prompt-automation.
    
    Args:
        hotkey: The hotkey combination (e.g., "ctrl+shift+j")
        wsl_distro: WSL2 distribution name (auto-detected if None)
    """
    # Observability: registration start
    if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
        print(
            f"[prompt-automation] hotkey_registration_start os=Windows-WSL2 hotkey={hotkey}"
        )

    if wsl_distro is None:
        wsl_distro = _get_wsl_distro_name()

    ahk_hotkey = _to_ahk(hotkey)
    
    # Get Windows Startup folder path using PowerShell environment variables
    # This is completely agnostic to username, drive letter, and Windows version
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", 
             "[System.Environment]::GetFolderPath('Startup')"],
            capture_output=True,
            text=True,
            check=True
        )
        windows_startup_path = result.stdout.strip()
        if not windows_startup_path:
            raise ValueError("Empty path returned")
    except Exception as e:
        # Fallback: Use standard Windows path with detected username
        try:
            windows_user = subprocess.check_output(
                ["cmd.exe", "/c", "echo %USERNAME%"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception:
            windows_user = os.environ.get("USER", "user")
        
        windows_startup_path = f"C:\\Users\\{windows_user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    
    # Convert Windows path to WSL2 mount path
    # Replace C:\ with /mnt/c/ and backslashes with forward slashes
    startup_win = Path(windows_startup_path.replace("C:\\", "/mnt/c/").replace("\\", "/"))
    
    # Ensure directory exists (it should already exist, but check)
    if not startup_win.exists():
        raise FileNotFoundError(
            f"Windows Startup folder not found at {startup_win}. "
            f"Windows path: {windows_startup_path}"
        )
    
    script_path = startup_win / "prompt-automation.ahk"
    
    # Detect AutoHotkey version (v1 vs v2)
    ahk_version = _detect_ahk_version()

    # Get full path to prompt-automation executable
    prompt_automation_path = "/home/josiah/.local/bin/prompt-automation"
    
    # Generate AHK script that calls wsl.exe
    # Simplified: Just launch GUI directly (focus is handled internally)
    if ahk_version == 2:
        # AutoHotkey v2 syntax
        content = f"""#Requires AutoHotkey v2.0
#SingleInstance Force

; {hotkey} launches prompt-automation via WSL2 ({wsl_distro})
; Uses full path to avoid PATH issues
{ahk_hotkey}::
{{
    ; WSL2 Bridge: Launch GUI (hidden terminal)
    ; The application handles focus/reuse internally
    try {{
        Run("wsl.exe -d {wsl_distro} {prompt_automation_path} --gui",, "Hide")
    }} catch Error as err {{
        ; If launch fails, show error dialog
        MsgBox("Failed to launch prompt-automation via WSL2.`n`n"
            . "Distro: {wsl_distro}`n"
            . "Command: wsl.exe -d {wsl_distro} {prompt_automation_path} --gui`n`n"
            . "Error: " . err.Message . "`n`n"
            . "Please check:`n"
            . "1. WSL2 is running (wsl --status)`n"
            . "2. prompt-automation is installed in WSL2`n"
            . "3. Test: wsl -d {wsl_distro} {prompt_automation_path} --version",
            "Error", 16)
    }}
}}
"""
    else:
        # AutoHotkey v1 syntax (legacy)
        content = f"""#NoEnv
#SingleInstance Force
#InstallKeybdHook
#InstallMouseHook
#MaxHotkeysPerInterval 99000000
#HotkeyInterval 99000000
#KeyHistory 0

; {hotkey} launches prompt-automation via WSL2 ({wsl_distro})
; Uses full path to avoid PATH issues
{ahk_hotkey}::
    ; WSL2 Bridge: Launch GUI (hidden terminal)
    ; The application handles focus/reuse internally
    Run, wsl.exe -d {wsl_distro} {prompt_automation_path} --gui,, Hide
    return
"""
    
    script_path.write_text(content)
    
    # Try to launch AutoHotkey to activate the script
    try:
        # Convert WSL path to Windows path for PowerShell
        # /mnt/c/... → C:\...
        windows_script_path = str(script_path).replace("/mnt/c/", "C:\\").replace("/", "\\")
        
        # AutoHotkey must be launched from Windows side
        # Start the .ahk file directly (Windows associates .ahk with AutoHotkey)
        ps_command = f'Start-Process "{windows_script_path}"'
        subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            check=False
        )
        
        if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
            print(
                f"[prompt-automation] hotkey_registration_success os=Windows-WSL2 "
                f"distro={wsl_distro} script={windows_script_path}"
            )
    except Exception as e:
        if os.environ.get("PROMPT_AUTOMATION_DEBUG"):
            print(
                f"[prompt-automation] hotkey_registration_failure os=Windows-WSL2 "
                f"distro={wsl_distro} reason={e}"
            )
        # Non-fatal: script is still created in Startup folder


def is_wsl2() -> bool:
    """Detect if running inside WSL2."""
    try:
        # Check for WSL-specific indicators
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                version = f.read().lower()
                return "microsoft" in version or "wsl" in version
        return False
    except Exception:
        return False
