from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence, Callable


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _iter_pipx_candidates(env: Mapping[str, str]) -> Iterable[Path]:
    launcher = env.get("PROMPT_AUTOMATION_PREFERRED_LAUNCHER")
    if launcher:
        yield Path(launcher).expanduser()

    pipx_bin = env.get("PIPX_BIN_DIR")
    if pipx_bin:
        root = Path(pipx_bin)
        yield root / "prompt-automation.exe"
        yield root / "prompt-automation"

    pipx_home = env.get("PIPX_HOME")
    if pipx_home:
        home = Path(pipx_home)
        yield home / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation.exe"
        yield home / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation"

    profile = env.get("USERPROFILE")
    if profile:
        user_root = Path(profile)
        yield user_root / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation.exe"
        yield user_root / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation"
        yield user_root / ".local" / "bin" / "prompt-automation.exe"
        yield user_root / ".local" / "bin" / "prompt-automation"
        yield user_root / ".local" / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation.exe"
        yield user_root / ".local" / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation"

    local_app = env.get("LOCALAPPDATA")
    if local_app:
        local_root = Path(local_app)
        yield local_root / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation.exe"
        yield local_root / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation"

    # Fallback to Path.home for completeness
    home = Path.home()
    yield home / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation.exe"
    yield home / "pipx" / "venvs" / "prompt-automation" / "Scripts" / "prompt-automation"


def resolve_windows_launcher(env: Mapping[str, str] | None = None) -> Path | None:
    """Return the preferred executable when a pipx install is available."""

    env_map: Mapping[str, str] = env if env is not None else os.environ
    if _is_truthy(env_map.get("PROMPT_AUTOMATION_FORCE_PACKAGED")):
        return None

    seen: set[Path] = set()
    for candidate in _iter_pipx_candidates(env_map):
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue
    return None


def iter_windows_launch_commands(env: Mapping[str, str] | None = None) -> list[str]:
    """Return launch command candidates ordered by preference."""

    env_map: Mapping[str, str] = env if env is not None else os.environ
    commands: list[str] = []
    preferred = resolve_windows_launcher(env_map)
    if preferred is not None:
        commands.append(str(preferred))
    commands.extend(
        [
            "prompt-automation",
            "prompt-automation.exe",
            "python -m prompt_automation",
            "py -m prompt_automation",
        ]
    )
    ordered: list[str] = []
    for cmd in commands:
        if cmd not in ordered:
            ordered.append(cmd)
    return ordered


def _resolve_current_candidates(current_executable: Path | None = None) -> list[Path]:
    if current_executable is not None:
        return [current_executable]

    candidates: list[Path] = []
    try:
        candidates.append(Path(sys.argv[0]).resolve())
    except Exception:
        pass
    try:
        candidates.append(Path(sys.executable).resolve())
    except Exception:
        pass
    return candidates


Runner = Callable[[Sequence[str], MutableMapping[str, str]], int]


def maybe_handoff_to_preferred_installation(
    *,
    argv: Sequence[str],
    env: MutableMapping[str, str] | None = None,
    current_executable: Path | None = None,
    runner: Runner | None = None,
) -> int | None:
    """Re-execute the CLI inside the pipx environment when available."""

    env_map: MutableMapping[str, str] = env if env is not None else os.environ.copy()
    if _is_truthy(env_map.get("PROMPT_AUTOMATION_FORCE_PACKAGED")):
        return None
    if _is_truthy(env_map.get("PROMPT_AUTOMATION_LAUNCH_HANDOFF")):
        return None

    target = resolve_windows_launcher(env_map)
    if target is None:
        return None

    try:
        target_resolved = target.resolve()
    except Exception:
        target_resolved = target

    for candidate in _resolve_current_candidates(current_executable):
        try:
            if candidate.resolve() == target_resolved:
                return None
        except Exception:
            if candidate == target_resolved:
                return None

    new_env = dict(env_map)
    new_env["PROMPT_AUTOMATION_LAUNCH_HANDOFF"] = "1"
    command = [str(target), *argv]

    if runner is None:
        return subprocess.call(command, env=new_env)
    return runner(command, new_env)


__all__ = [
    "iter_windows_launch_commands",
    "maybe_handoff_to_preferred_installation",
    "resolve_windows_launcher",
]
