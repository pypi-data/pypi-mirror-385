"""Lightweight configuration registry helpers.

The configuration registry is an optional JSON document that lives alongside
the user's Prompt Automation home directory.  It is intended for feature flag
rollouts where we want a durable default that can be overridden by
environment variables or the persisted ``Settings/settings.json`` payload.

Only a very small subset of the schema is required for the current tests: a
top-level ``"features"`` object whose values may be nested mappings.  Boolean
values are interpreted in a permissive way (strings such as ``"1"`` and
``"true"`` are accepted) to match the behaviour of :mod:`features`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .config import HOME_DIR
from .errorlog import get_logger

_log = get_logger(__name__)

ENV_REGISTRY_PATH = "PROMPT_AUTOMATION_CONFIG_REGISTRY"

_CACHE: Tuple[Path, Optional[float], Dict[str, Any]] | None = None


def _resolve_registry_path() -> Path:
    override = os.environ.get(ENV_REGISTRY_PATH)
    if override:
        try:
            return Path(override).expanduser().resolve()
        except Exception:
            return Path(override)
    return HOME_DIR / "config" / "registry.json"


def _load_registry() -> Dict[str, Any]:
    path = _resolve_registry_path()
    global _CACHE

    mtime: Optional[float] = None
    if path.exists():
        try:
            mtime = path.stat().st_mtime
        except OSError:
            mtime = None

        if _CACHE and _CACHE[0] == path and _CACHE[1] == mtime:
            return _CACHE[2]

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except Exception as exc:  # pragma: no cover - defensive logging
            try:
                _log.debug("config_registry_load_failed path=%s error=%s", path, exc)
            except Exception:
                pass
            data = {}

        _CACHE = (path, mtime, data)
        return data

    _CACHE = (path, None, {})
    return {}


def clear_cache() -> None:
    """Reset the memoized registry payload (used heavily in tests)."""

    global _CACHE
    _CACHE = None


def get_feature_flag(*segments: str) -> Any:
    """Return the value stored under ``features`` for ``segments``.

    Example::

        >>> get_feature_flag("mcp", "enabled")

    ``None`` is returned when the path does not exist.  Callers are responsible
    for coercing the value into the desired type.
    """

    data = _load_registry()
    node: Any = data.get("features")
    for segment in segments:
        if not isinstance(node, dict):
            return None
        node = node.get(segment)
    return node


__all__ = ["get_feature_flag", "clear_cache", "ENV_REGISTRY_PATH"]

