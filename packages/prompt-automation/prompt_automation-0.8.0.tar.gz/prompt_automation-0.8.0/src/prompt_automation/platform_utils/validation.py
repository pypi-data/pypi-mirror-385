"""
Cross-platform validation utilities for path and subprocess operations.

This module provides validation functions to detect and prevent platform
divergence issues, particularly when developing in WSL2 while targeting
Windows production environments.

Key Validation Functions:
- validate_path_accessible(): Check if path is accessible in target environment
- validate_subprocess_stdio(): Verify subprocess stdio pipes work correctly
- validate_cross_platform_compatibility(): Comprehensive pre-flight check

Usage:
    from prompt_automation.platform_utils.validation import validate_path_accessible
    
    result = validate_path_accessible(path, target_env="windows")
    if not result.success:
        logger.error(f"Path validation failed: {result.error}")
        # Fall back to alternative path or disable feature
"""

import logging
import os
import platform
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PureWindowsPath, PurePosixPath
from typing import Optional, Literal

logger = logging.getLogger(__name__)

EnvironmentType = Literal["wsl2", "windows", "linux", "macos", "unknown"]


# Inline implementations to avoid circular import
# (duplicated from __init__.py but necessary for isolation)

@lru_cache(maxsize=1)
def _detect_environment() -> EnvironmentType:
    """Detect the current runtime environment (internal copy)."""
    system = platform.system().lower()
    
    if system == "darwin":
        return "macos"
    
    if system == "windows":
        return "windows"
    
    if system == "linux":
        # Check if WSL2
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl2" in version_info:
                    return "wsl2"
        except FileNotFoundError:
            pass
        return "linux"
    
    return "unknown"


def _wsl_to_windows_path(wsl_path: str) -> str:
    """Convert WSL2 path to Windows path (internal copy)."""
    if not wsl_path.startswith("/mnt/"):
        raise ValueError(f"Path must start with /mnt/: {wsl_path}")
    
    # /mnt/c/Users/... → C:\Users\...
    parts = wsl_path.split("/")
    drive = parts[2].upper()
    remaining = "/".join(parts[3:])
    
    windows_path = f"{drive}:\\" + remaining.replace("/", "\\")
    return windows_path


def _windows_to_wsl_path(windows_path: str) -> str:
    """Convert Windows path to WSL2 path (internal copy)."""
    # C:\Users\... → /mnt/c/Users/...
    if len(windows_path) < 3 or windows_path[1] != ":":
        raise ValueError(f"Invalid Windows path: {windows_path}")
    
    drive = windows_path[0].lower()
    remaining = windows_path[3:].replace("\\", "/")
    
    wsl_path = f"/mnt/{drive}/{remaining}"
    return wsl_path



@dataclass
class ValidationResult:
    """Result of a validation operation."""
    success: bool
    message: str
    error: Optional[str] = None
    details: Optional[dict] = None


def validate_path_accessible(
    path: Path,
    target_env: Optional[EnvironmentType] = None,
    check_writable: bool = False
) -> ValidationResult:
    """
    Validate that a path is accessible in the target environment.
    
    This function detects cross-platform path issues, particularly:
    - WSL2 paths (/mnt/c/...) accessible in WSL2 but not from Windows .exe
    - Windows paths (C:\\...) accessible from Windows but may fail in WSL2
    - Path translation errors between environments
    
    Args:
        path: Path to validate
        target_env: Target environment ("wsl2", "windows", "linux", "macos")
                   If None, uses current environment
        check_writable: Also check if path is writable
    
    Returns:
        ValidationResult with success status and details
    
    Example:
        >>> result = validate_path_accessible(Path("/mnt/c/temp"), target_env="windows")
        >>> if not result.success:
        ...     logger.error(result.error)
    """
    current_env = _detect_environment()
    target_env = target_env or current_env
    
    # Check if path exists in current environment
    if not path.exists():
        return ValidationResult(
            success=False,
            message=f"Path does not exist: {path}",
            error=f"Path not found in {current_env}",
            details={"path": str(path), "current_env": current_env}
        )
    
    # WSL2 → Windows: Check for /mnt/c paths
    if current_env == "wsl2" and target_env == "windows":
        path_str = str(path)
        if path_str.startswith("/mnt/"):
            # This is a Windows path mounted in WSL2, accessible from Windows
            try:
                windows_path = _wsl_to_windows_path(path_str)
                return ValidationResult(
                    success=True,
                    message=f"WSL2 path translates to Windows: {windows_path}",
                    details={
                        "wsl2_path": path_str,
                        "windows_path": windows_path,
                        "translation": "success"
                    }
                )
            except Exception as e:
                return ValidationResult(
                    success=False,
                    message="Failed to translate WSL2 path to Windows",
                    error=str(e),
                    details={"path": path_str, "translation_error": str(e)}
                )
        else:
            # WSL2-only path (not under /mnt/), inaccessible from Windows
            return ValidationResult(
                success=False,
                message=f"WSL2 path inaccessible from Windows: {path_str}",
                error="Path is in WSL2 filesystem, Windows .exe cannot access it",
                details={
                    "path": path_str,
                    "reason": "wsl2_filesystem_only",
                    "suggestion": "Use /mnt/c/... path instead"
                }
            )
    
    # Windows → WSL2: Check if Windows path is accessible
    if current_env == "windows" and target_env == "wsl2":
        path_str = str(path)
        if path_str[1:3] == ":\\":  # Windows path like C:\...
            try:
                wsl2_path = _windows_to_wsl_path(path_str)
                return ValidationResult(
                    success=True,
                    message=f"Windows path translates to WSL2: {wsl2_path}",
                    details={
                        "windows_path": path_str,
                        "wsl2_path": wsl2_path,
                        "translation": "success"
                    }
                )
            except Exception as e:
                return ValidationResult(
                    success=False,
                    message="Failed to translate Windows path to WSL2",
                    error=str(e),
                    details={"path": path_str, "translation_error": str(e)}
                )
    
    # Check write permission if requested
    if check_writable:
        if not path.is_dir():
            path = path.parent
        
        test_file = path / ".prompt_automation_write_test"
        try:
            test_file.touch()
            test_file.unlink()
            return ValidationResult(
                success=True,
                message=f"Path is readable and writable: {path}",
                details={"path": str(path), "writable": True}
            )
        except Exception as e:
            return ValidationResult(
                success=False,
                message=f"Path is not writable: {path}",
                error=str(e),
                details={"path": str(path), "writable": False}
            )
    
    # Same environment or compatible path
    return ValidationResult(
        success=True,
        message=f"Path is accessible in {target_env}",
        details={"path": str(path), "environment": target_env}
    )


def validate_subprocess_stdio(
    command: list[str],
    target_env: Optional[EnvironmentType] = None,
    timeout: float = 5.0
) -> ValidationResult:
    """
    Validate that subprocess stdio pipes work correctly for a command.
    
    This function detects stdio failures, particularly:
    - WSL2 → Windows .exe: stdio pipes broken across VM boundary
    - Process returns 0 but stdio is empty (false success)
    - Timeout issues when waiting for process output
    
    Args:
        command: Command to test (e.g., ["python", "--version"])
        target_env: Target environment for command execution
                   If None, uses current environment
        timeout: Max seconds to wait for command completion
    
    Returns:
        ValidationResult with success status and stdio details
    
    Example:
        >>> result = validate_subprocess_stdio(["python", "--version"])
        >>> if not result.success:
        ...     logger.warning("Subprocess stdio broken, use HTTP transport instead")
    """
    current_env = _detect_environment()
    target_env = target_env or current_env
    
    # WSL2 → Windows .exe: Known stdio issue
    if current_env == "wsl2" and len(command) > 0:
        cmd_path = command[0]
        # Check if command is a Windows .exe
        if cmd_path.endswith(".exe") or (
            "/" in cmd_path and "mnt/c" in cmd_path.lower()
        ):
            logger.warning(
                f"WSL2 → Windows .exe subprocess detected: {cmd_path}. "
                "Stdio pipes may not work across VM boundary."
            )
            return ValidationResult(
                success=False,
                message="WSL2 → Windows .exe subprocess stdio is broken",
                error="Cannot communicate with Windows .exe via stdio from WSL2",
                details={
                    "command": command,
                    "current_env": current_env,
                    "target_env": target_env,
                    "reason": "vm_boundary_stdio_broken",
                    "suggestion": "Use HTTP transport, disable feature, or run on Windows"
                }
            )
    
    # Test actual subprocess execution
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise on non-zero exit
        )
        
        # Check for false success (returncode=0 but no output)
        if result.returncode == 0 and not result.stdout and not result.stderr:
            logger.warning(
                f"Subprocess returned 0 but no stdio output: {command}. "
                "This may indicate broken stdio pipes."
            )
            return ValidationResult(
                success=False,
                message="Subprocess succeeded but stdio is empty",
                error="Possible stdio pipe failure (returncode=0, no output)",
                details={
                    "command": command,
                    "returncode": result.returncode,
                    "stdout_empty": True,
                    "stderr_empty": True,
                    "reason": "false_success_no_stdio"
                }
            )
        
        # Success: process ran and produced output
        return ValidationResult(
            success=True,
            message=f"Subprocess stdio works: {command[0]}",
            details={
                "command": command,
                "returncode": result.returncode,
                "stdout_len": len(result.stdout),
                "stderr_len": len(result.stderr),
                "stdio_working": True
            }
        )
        
    except subprocess.TimeoutExpired:
        return ValidationResult(
            success=False,
            message=f"Subprocess timed out after {timeout}s",
            error=f"Command did not complete: {command}",
            details={
                "command": command,
                "timeout": timeout,
                "reason": "timeout"
            }
        )
    except FileNotFoundError:
        return ValidationResult(
            success=False,
            message=f"Command not found: {command[0]}",
            error=f"Executable does not exist or is not in PATH",
            details={
                "command": command,
                "reason": "command_not_found"
            }
        )
    except Exception as e:
        return ValidationResult(
            success=False,
            message=f"Subprocess execution failed: {type(e).__name__}",
            error=str(e),
            details={
                "command": command,
                "exception": type(e).__name__,
                "reason": "execution_error"
            }
        )


def validate_cross_platform_compatibility(
    operation: str,
    paths: Optional[list[Path]] = None,
    commands: Optional[list[list[str]]] = None,
    target_env: Optional[EnvironmentType] = None
) -> ValidationResult:
    """
    Comprehensive validation for cross-platform operations.
    
    This function runs multiple validation checks to detect platform
    divergence issues before attempting the operation.
    
    Args:
        operation: Description of operation (for logging)
        paths: Paths to validate accessibility
        commands: Commands to validate stdio functionality
        target_env: Target environment for operation
    
    Returns:
        ValidationResult with comprehensive validation details
    
    Example:
        >>> result = validate_cross_platform_compatibility(
        ...     operation="MCP server initialization",
        ...     paths=[Path("~/.prompt-automation")],
        ...     commands=[["mcp-server.exe", "--version"]],
        ...     target_env="windows"
        ... )
        >>> if not result.success:
        ...     logger.error(f"Pre-flight check failed: {result.error}")
    """
    current_env = _detect_environment()
    target_env = target_env or current_env
    
    failures = []
    warnings = []
    details = {
        "operation": operation,
        "current_env": current_env,
        "target_env": target_env,
        "checks_run": []
    }
    
    # Validate paths
    if paths:
        for path in paths:
            result = validate_path_accessible(path, target_env=target_env)
            details["checks_run"].append({
                "type": "path",
                "path": str(path),
                "success": result.success
            })
            
            if not result.success:
                failures.append(f"Path validation failed: {path} - {result.error}")
                logger.error(f"Path validation failed for {operation}: {result.error}")
    
    # Validate commands
    if commands:
        for command in commands:
            result = validate_subprocess_stdio(command, target_env=target_env)
            details["checks_run"].append({
                "type": "subprocess",
                "command": command,
                "success": result.success
            })
            
            if not result.success:
                failures.append(f"Subprocess validation failed: {command[0]} - {result.error}")
                logger.error(f"Subprocess validation failed for {operation}: {result.error}")
    
    # WSL2 → Windows cross-VM warning
    if current_env == "wsl2" and target_env == "windows":
        warnings.append(
            "Developing in WSL2 while targeting Windows. "
            "Test in real Windows environment before release."
        )
        logger.warning(f"Cross-VM operation detected for {operation}")
    
    # Compile result
    if failures:
        return ValidationResult(
            success=False,
            message=f"Pre-flight validation failed for {operation}",
            error="; ".join(failures),
            details=details
        )
    elif warnings:
        return ValidationResult(
            success=True,
            message=f"Pre-flight validation passed with warnings for {operation}",
            details={**details, "warnings": warnings}
        )
    else:
        return ValidationResult(
            success=True,
            message=f"Pre-flight validation passed for {operation}",
            details=details
        )
