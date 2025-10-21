"""Cross-platform path resolution and environment detection.

This module provides a global solution for WSL2/Windows hybrid environments where:
- Development happens in WSL2
- Installation is on Windows
- Runtime can be either environment

Key features:
- Auto-detects WSL2, Windows, Linux environments
- Bidirectional path translation (POSIX ↔ Windows)
- Centralizes all path resolution logic
- Makes the codebase environment-agnostic
- Validation layer to prevent cross-platform failures
"""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path, PureWindowsPath, PurePosixPath
from typing import Optional, Literal
from functools import lru_cache

from ..errorlog import get_logger

_log = get_logger(__name__)


EnvironmentType = Literal["wsl2", "windows", "linux", "macos", "unknown"]


@lru_cache(maxsize=1)
def detect_environment() -> EnvironmentType:
    """Detect the current runtime environment.
    
    Returns:
        "wsl2": Running in WSL2 (Windows Subsystem for Linux 2)
        "windows": Running on native Windows
        "linux": Running on native Linux
        "macos": Running on macOS
        "unknown": Could not determine
    """
    system = platform.system().lower()
    
    if system == "darwin":
        return "macos"
    
    if system == "windows":
        return "windows"
    
    if system == "linux":
        # Check if WSL2
        try:
            # WSL2 has /proc/sys/kernel/osrelease with "microsoft" in it
            with open("/proc/sys/kernel/osrelease", "r") as f:
                release_info = f.read().lower()
                if "microsoft" in release_info or "wsl" in release_info:
                    return "wsl2"
        except (FileNotFoundError, PermissionError):
            pass
        
        # Check alternative WSL detection method
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    return "wsl2"
        except (FileNotFoundError, PermissionError):
            pass
        
        return "linux"
    
    return "unknown"


@lru_cache(maxsize=1)
def get_windows_username_from_wsl2() -> Optional[str]:
    """Get Windows username when running in WSL2.
    
    Returns:
        Windows username (e.g., "JosiahHunter") or None if not in WSL2
    """
    if detect_environment() != "wsl2":
        return None
    
    # Method 1: Check WSLENV environment variable
    wsl_user = os.environ.get("WSLENV", "")
    if wsl_user:
        # Parse WSLENV to extract username
        pass  # Usually doesn't contain username
    
    # Method 2: Execute Windows command from WSL2
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "echo", "%USERNAME%"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            username = result.stdout.strip()
            if username and username != "%USERNAME%":
                return username
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Method 3: Parse Windows paths from environment
    for var in ["USERPROFILE", "HOMEPATH", "HOME"]:
        value = os.environ.get(var, "")
        if "Users" in value or "users" in value:
            parts = value.replace("\\", "/").split("/")
            try:
                users_idx = next(i for i, p in enumerate(parts) if p.lower() == "users")
                if users_idx + 1 < len(parts):
                    return parts[users_idx + 1]
            except StopIteration:
                pass
    
    # Method 4: Check /mnt/c/Users directory
    try:
        users_dir = Path("/mnt/c/Users")
        if users_dir.exists():
            # Look for most recently modified user directory
            user_dirs = [
                d for d in users_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
                and d.name not in ["Public", "Default", "All Users"]
            ]
            if user_dirs:
                # Sort by modification time, return most recent
                user_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
                return user_dirs[0].name
    except (OSError, PermissionError):
        pass
    
    return None


@lru_cache(maxsize=1)
def get_windows_home_in_wsl2() -> Optional[Path]:
    """Get Windows home directory path accessible from WSL2.
    
    Returns:
        Path like /mnt/c/Users/JosiahHunter or None if not in WSL2
    """
    if detect_environment() != "wsl2":
        return None
    
    username = get_windows_username_from_wsl2()
    if username:
        win_home = Path(f"/mnt/c/Users/{username}")
        if win_home.exists():
            return win_home
    
    # Fallback: Check common locations
    for drive in ["c", "d"]:
        users_dir = Path(f"/mnt/{drive}/Users")
        if users_dir.exists():
            for user_dir in users_dir.iterdir():
                if user_dir.is_dir() and (user_dir / ".prompt-automation").exists():
                    return user_dir
    
    return None


def wsl_to_windows_path(wsl_path: Path) -> Optional[str]:
    """Convert WSL2 path to Windows path format.
    
    Args:
        wsl_path: WSL2 path (e.g., /mnt/c/Users/John/file.txt)
        
    Returns:
        Windows path (e.g., C:\\Users\\John\\file.txt) or None if not convertible
    """
    if detect_environment() != "wsl2":
        return None
    
    path_str = str(wsl_path)
    
    # Handle /mnt/X/ paths
    if path_str.startswith("/mnt/"):
        parts = path_str[5:].split("/", 1)
        if len(parts) >= 1:
            drive = parts[0].upper()
            rest = parts[1] if len(parts) > 1 else ""
            return f"{drive}:\\{rest.replace('/', '\\')}"
    
    # Try using wslpath command
    try:
        result = subprocess.run(
            ["wslpath", "-w", path_str],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return None


def windows_to_wsl_path(windows_path: str) -> Optional[Path]:
    """Convert Windows path to WSL2 path format.
    
    Args:
        windows_path: Windows path (e.g., C:\\Users\\John\\file.txt)
        
    Returns:
        WSL2 path (e.g., /mnt/c/Users/John/file.txt) or None if not convertible
    """
    if detect_environment() != "wsl2":
        return None
    
    # Handle C:\... paths
    if len(windows_path) >= 2 and windows_path[1] == ":":
        drive = windows_path[0].lower()
        rest = windows_path[2:].replace("\\", "/")
        return Path(f"/mnt/{drive}{rest}")
    
    # Try using wslpath command
    try:
        result = subprocess.run(
            ["wslpath", "-u", windows_path],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return None


def normalize_path(path: Path | str) -> Path:
    """Normalize path for the current environment.
    
    Converts paths between WSL2 and Windows formats automatically.
    
    Args:
        path: Path in any format
        
    Returns:
        Path normalized for current environment
    """
    if isinstance(path, str):
        path = Path(path)
    
    env = detect_environment()
    
    if env == "wsl2":
        # If path looks like Windows path, convert to WSL2
        path_str = str(path)
        if len(path_str) >= 2 and path_str[1] == ":":
            converted = windows_to_wsl_path(path_str)
            if converted:
                return converted
    
    return path


@lru_cache(maxsize=1)
def get_app_home() -> Path:
    """Get the application home directory, automatically handling WSL2/Windows.
    
    **CRITICAL**: This function enforces config path convergence to prevent divergence
    between WSL2 and Windows installations. In WSL2, it ALWAYS prefers the Windows
    home directory to ensure both environments share the same config/data.
    
    Priority:
    1. PROMPT_AUTOMATION_HOME environment variable (explicit override)
    2. Windows home (if in WSL2) - **CREATES IT IF MISSING**
    3. Standard home directory (~/.prompt-automation)
    
    Returns:
        Path to application home directory
    
    Note:
        Cached after first call. To force refresh, call get_app_home.cache_clear()
        
    Example:
        WSL2: /mnt/c/Users/Josiah/.prompt-automation (Windows path via WSL2)
        Windows: C:\\Users\\Josiah\\.prompt-automation
        Linux: /home/user/.prompt-automation
    """
    # Priority 1: Explicit override
    env_home = os.environ.get("PROMPT_AUTOMATION_HOME")
    if env_home:
        return Path(env_home).expanduser()
    
    # Priority 2: Windows home for WSL2 (ALWAYS prefer, create if missing)
    env = detect_environment()
    if env == "wsl2":
        win_home = get_windows_home_in_wsl2()
        if win_home:
            app_home = win_home / ".prompt-automation"
            # CRITICAL: Create Windows path to enforce convergence
            # This ensures WSL2 and Windows use the SAME config directory
            existed_before = app_home.exists()
            app_home.mkdir(parents=True, exist_ok=True)
            _log.info(
                "platform.enforced_windows_home wsl2_path=%s status=%s",
                app_home,
                "existing" if existed_before else "created"
            )
            return app_home
    
    # Priority 3: Standard home
    return Path.home() / ".prompt-automation"


def migrate_wsl2_config_to_windows() -> bool:
    """Migrate WSL2-only config to Windows path for convergence.
    
    **Purpose**: Ensures WSL2 and Windows share the same config directory.
    Called automatically on first import in WSL2 if old config detected.
    
    **Strategy**: Smart merge - newer files win, preserve both envs' logs/cache
    
    Files copied (shared):
    - config.json, mcp-registry.json, hotkey.json, template-shortcuts.json
    - placeholder-overrides.json, usage.db, variables/
    
    Files NOT copied (environment-specific):
    - logs/ (keep separate per environment)
    - cache/ (keep separate per environment)
    - gui.sock (Unix socket, WSL2-only)
    - environment (marker file, environment-specific)
    
    Returns:
        True if migration performed, False if not needed
        
    Example:
        WSL2-only: ~/.prompt-automation → /mnt/c/Users/Josiah/.prompt-automation
    """
    env = detect_environment()
    if env != "wsl2":
        return False  # Only needed in WSL2
    
    wsl2_home = Path.home() / ".prompt-automation"
    win_home = get_windows_home_in_wsl2()
    if not win_home:
        return False  # Can't migrate without Windows home
    
    win_app_home = win_home / ".prompt-automation"
    
    # Check if migration needed
    if not wsl2_home.exists():
        return False  # No old config to migrate
    
    # Environment-specific files/dirs (don't copy)
    SKIP_ITEMS = {"logs", "cache", "gui.sock", "environment", "__pycache__", ".wsl2-old"}
    
    # Check if we have real config files to migrate
    config_files = [
        "config.json", "mcp-registry.json", "hotkey.json",
        "template-shortcuts.json", "placeholder-overrides.json",
        "usage.db", "gui-settings.json", "auto-update.json"
    ]
    has_config = any((wsl2_home / f).exists() for f in config_files)
    if not has_config:
        return False  # No config to migrate
    
    # Check if Windows already has newer config
    if win_app_home.exists():
        # Compare timestamps of key config files
        for config_file in config_files:
            wsl2_file = wsl2_home / config_file
            win_file = win_app_home / config_file
            if win_file.exists() and wsl2_file.exists():
                # Both exist - check if Windows is newer
                if win_file.stat().st_mtime > wsl2_file.stat().st_mtime:
                    _log.info(
                        "platform.skip_migration_newer_windows_config file=%s",
                        config_file
                    )
                    return False  # Windows has newer config
    
    # Perform migration
    import shutil
    _log.info(
        "platform.migrating_config source=%s dest=%s strategy=smart_merge",
        wsl2_home,
        win_app_home
    )
    
    try:
        # Create Windows directory
        win_app_home.mkdir(parents=True, exist_ok=True)
        
        # Copy ONLY shared files/dirs from WSL2-only to Windows path
        migrated_count = 0
        for item in wsl2_home.iterdir():
            if item.name in SKIP_ITEMS:
                _log.info("platform.skip_environment_specific item=%s", item.name)
                continue
            
            dest = win_app_home / item.name
            try:
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    # Only copy if dest doesn't exist or source is newer
                    if not dest.exists() or item.stat().st_mtime > dest.stat().st_mtime:
                        shutil.copy2(item, dest)
                        migrated_count += 1
            except Exception as e:
                _log.warning("platform.skip_item_error item=%s error=%s", item.name, str(e))
        
        _log.info("platform.migration_complete items_migrated=%d", migrated_count)
        
        # Create marker file to indicate migration happened
        marker = wsl2_home / ".migrated-to-windows"
        marker.write_text(f"Migrated to: {win_app_home}\nTimestamp: {Path.home()}")
        
        return True
    except Exception as e:
        _log.error("platform.migration_failed error=%s", str(e))
        return False


def translate_path_for_subprocess(path: Path, target_env: Optional[str] = None) -> str:
    """Translate path for use in subprocess calls across environments.
    
    Example: MCP server running on Windows needs Windows paths,
    but caller is in WSL2.
    
    Args:
        path: Path to translate
        target_env: Target environment ("windows" or "wsl2"), or None to auto-detect
        
    Returns:
        Path string in the format expected by target environment
    """
    current_env = detect_environment()
    
    if target_env is None:
        # Auto-detect: if calling Windows binary from WSL2, use Windows paths
        # This is a heuristic - may need refinement
        target_env = "windows" if current_env == "wsl2" else current_env
    
    if current_env == "wsl2" and target_env == "windows":
        # WSL2 → Windows
        converted = wsl_to_windows_path(path)
        if converted:
            return converted
    elif current_env == "windows" and target_env == "wsl2":
        # Windows → WSL2
        converted = windows_to_wsl_path(str(path))
        if converted:
            return str(converted)
    
    return str(path)


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating if necessary.
    
    Handles cross-platform path normalization.
    
    Args:
        path: Directory path
        
    Returns:
        Normalized path
    """
    normalized = normalize_path(path)
    normalized.mkdir(parents=True, exist_ok=True)
    return normalized


# Export environment info for logging/debugging
ENVIRONMENT = detect_environment()
WINDOWS_HOME_WSL2 = get_windows_home_in_wsl2() if ENVIRONMENT == "wsl2" else None

# Auto-migrate WSL2 config to Windows path for convergence (runs once per import)
if ENVIRONMENT == "wsl2":
    migrate_wsl2_config_to_windows()

APP_HOME = get_app_home()

# Import validation functions
from .validation import (  # noqa: E402
    validate_path_accessible,
    validate_subprocess_stdio,
    validate_cross_platform_compatibility,
    ValidationResult,
)

__all__ = [
    # Environment detection
    "EnvironmentType",
    "detect_environment",
    "get_windows_username_from_wsl2",
    "get_windows_home_in_wsl2",
    # Path translation
    "wsl_to_windows_path",
    "windows_to_wsl_path",
    "normalize_path",
    "get_app_home",
    "migrate_wsl2_config_to_windows",
    "translate_path_for_subprocess",
    "ensure_directory",
    # Validation
    "validate_path_accessible",
    "validate_subprocess_stdio",
    "validate_cross_platform_compatibility",
    "ValidationResult",
    # Constants
    "ENVIRONMENT",
    "WINDOWS_HOME_WSL2",
    "APP_HOME",
]
