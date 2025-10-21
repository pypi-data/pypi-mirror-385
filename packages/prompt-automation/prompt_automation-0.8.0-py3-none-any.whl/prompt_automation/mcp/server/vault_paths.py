"""Cross-platform path normalization and vault resolution helpers."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Iterable, NamedTuple


class VaultResolutionError(RuntimeError):
    """Raised when the vault root cannot be located."""


class VaultSecurityError(RuntimeError):
    """Raised when a candidate path escapes the resolved vault boundary."""


class VaultPlatform(NamedTuple):
    """Lightweight snapshot of platform traits relevant to vault path mapping."""

    os_name: str
    sys_platform: str
    is_wsl: bool
    mount_root: Path

    @classmethod
    def detect(cls) -> "VaultPlatform":
        """Return the current platform profile."""

        mount_root = Path(os.environ.get("PROMPT_AUTOMATION_WSL_MOUNT", "/mnt"))
        is_wsl = bool(os.environ.get("WSL_DISTRO_NAME"))
        return cls(os.name, sys.platform, is_wsl, mount_root)


@dataclass(frozen=True, slots=True)
class VaultContext:
    """Resolved vault metadata used by note tooling."""

    source_reference: str
    vault_root: Path
    reference_path: Path
    windows_path: str | None
    wsl_path: str

    def ensure_within_vault(self, candidate: Path | str) -> Path:
        """Return ``candidate`` as an absolute path confined to the vault."""

        candidate_path = Path(candidate)
        if not candidate_path.is_absolute():
            candidate_path = self.vault_root / candidate_path
        resolved_root = self.vault_root.resolve()
        resolved_candidate = candidate_path.expanduser().resolve(strict=False)
        if not _is_relative_to(resolved_candidate, resolved_root):
            raise VaultSecurityError(f"path '{resolved_candidate}' escapes vault '{resolved_root}'")
        return resolved_candidate

    def relative_path(self, path: Path) -> str:
        """Return the vault-relative POSIX path for ``path``."""

        resolved_root = self.vault_root.resolve()
        resolved_path = path.resolve(strict=False)
        return resolved_path.relative_to(resolved_root).as_posix()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _normalize_reference_string(raw: str) -> str:
    value = raw.strip().strip('"').strip("'")
    return os.path.expandvars(value)


def _as_windows_path(raw: str) -> PureWindowsPath | None:
    try:
        win_path = PureWindowsPath(raw)
    except Exception:
        return None
    if not win_path.drive:
        return None
    return win_path


def windows_to_wsl(path: str | Path, platform: VaultPlatform | None = None) -> Path:
    """Convert ``path`` from Windows format to a POSIX mount under ``platform``."""

    platform = platform or VaultPlatform.detect()
    win_path = _as_windows_path(str(path))
    if not win_path:
        return Path(path)
    drive = win_path.drive.rstrip(":").lower()
    if not drive:
        return Path(path)
    mount = platform.mount_root / drive
    tail = Path(*win_path.parts[1:])
    return (mount / tail).expanduser()


def wsl_to_windows(path: Path | str, platform: VaultPlatform | None = None) -> str | None:
    """Convert a WSL-style path under ``platform.mount_root`` back to Windows form."""

    platform = platform or VaultPlatform.detect()
    posix_path = Path(path)
    mount_parts = platform.mount_root.resolve(strict=False).parts
    candidate_parts = posix_path.resolve(strict=False).parts
    if len(candidate_parts) < len(mount_parts) + 1:
        return None
    if candidate_parts[: len(mount_parts)] != mount_parts:
        return None
    drive = candidate_parts[len(mount_parts)]
    if len(drive) != 1:
        return None
    remainder = candidate_parts[len(mount_parts) + 1 :]
    drive_letter = drive.upper()
    if remainder:
        return f"{drive_letter}:/{'/'.join(remainder)}"
    return f"{drive_letter}:/"


def _iter_parents_inclusive(path: Path) -> Iterable[Path]:
    current = path
    while True:
        yield current
        if current.parent == current:
            break
        current = current.parent


def _resolve_vault_root(start: Path) -> Path:
    for directory in _iter_parents_inclusive(start):
        marker = directory / ".obsidian"
        if marker.is_dir():
            return directory.resolve()
    raise VaultResolutionError(f"Unable to locate Obsidian vault root above '{start}'")


def resolve_vault_context(reference_file: str, platform: VaultPlatform | None = None) -> VaultContext:
    """Resolve vault metadata from a reference file placeholder."""

    platform = platform or VaultPlatform.detect()
    raw = _normalize_reference_string(reference_file)
    posix_candidate = Path(raw)
    windows_path: str | None = None

    win = _as_windows_path(raw)
    if win is not None:
        posix_candidate = windows_to_wsl(raw, platform=platform)
        windows_path = PureWindowsPath(win).as_posix()
    elif platform.is_wsl:
        translated = wsl_to_windows(posix_candidate, platform=platform)
        if translated:
            windows_path = translated

    reference_path = posix_candidate.expanduser().resolve(strict=False)
    start = reference_path if reference_path.is_dir() else reference_path.parent
    vault_root = _resolve_vault_root(start)
    wsl_path = reference_path.as_posix()

    return VaultContext(
        source_reference=reference_file,
        vault_root=vault_root,
        reference_path=reference_path,
        windows_path=windows_path,
        wsl_path=wsl_path,
    )


__all__ = [
    "VaultContext",
    "VaultPlatform",
    "VaultResolutionError",
    "VaultSecurityError",
    "resolve_vault_context",
    "windows_to_wsl",
    "wsl_to_windows",
]
