from __future__ import annotations

"""Feature flags and configuration toggles.

Currently supports:
  - hierarchical_templates: enable hierarchical template browsing in UI/CLI.
  - hierarchical_variables: enable hierarchical variable storage backend.
  - reminders: enable read-only reminders parsing and rendering.
  - background_hotkey: enable background hotkey integration.
  - analytics: enable usage analytics and telemetry.

Resolution order for hierarchical_templates (mimics theme behavior):
  1. Environment variable PROMPT_AUTOMATION_HIERARCHICAL_TEMPLATES
     - truthy: "1", "true", "yes", "on"
     - falsy:  "0", "false", "no", "off"
  2. Settings file under PROMPTS_DIR/Settings/settings.json key "hierarchical_templates"
  3. Default: True (auto-enabled unless explicitly off)

Resolution order for analytics:
  1. Environment variable PA_ANALYTICS_ENABLED
     - truthy: "1", "true", "yes", "on"
     - falsy:  "0", "false", "no", "off"
  2. Default: True (auto-enabled unless explicitly off)
"""

import json
import os
from pathlib import Path
from typing import Any

from . import config_registry
from .config import PROMPTS_DIR
from .errorlog import get_logger
from .variables import storage

_log = get_logger(__name__)

_FASTPATH_CACHE_ENV: str | None = None
_FASTPATH_CACHE_PATH: Path | None = None
_FASTPATH_CACHE_MTIME: float | None = None
_FASTPATH_CACHE_VALUE: bool | None = None


def _coerce_bool(val: Any) -> bool | None:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        v = val.strip().lower()
        if v in {"1", "true", "yes", "on"}:
            return True
        if v in {"0", "false", "no", "off"}:
            return False
    return None


def is_hierarchy_enabled() -> bool:
    env = os.environ.get("PROMPT_AUTOMATION_HIERARCHICAL_TEMPLATES")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("hierarchical_templates")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("feature_flag_read_failed error=%s", e)
        except Exception:
            pass
    # Default to enabled unless explicitly disabled
    return True


def set_user_hierarchy_preference(enabled: bool) -> None:
    """Persist the hierarchical_templates preference in settings.json.

    Creates the Settings directory/file if missing and preserves other keys.
    """
    try:
        settings_dir = PROMPTS_DIR / "Settings"
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_path = settings_dir / "settings.json"
        data: dict[str, Any] = {}
        if settings_path.exists():
            try:
                data = json.loads(settings_path.read_text())
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}
        data["hierarchical_templates"] = bool(enabled)
        settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:  # pragma: no cover - defensive
        try:
            _log.error("failed_to_persist_hierarchy_preference error=%s", e)
        except Exception:
            pass


def is_variable_hierarchy_enabled() -> bool:
    """Resolve hierarchical variable storage flag (default disabled)."""

    env = os.environ.get("PROMPT_AUTOMATION_HIERARCHICAL_VARIABLES")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            val = data.get("hierarchical_variables_enabled")
            coerced = _coerce_bool(val)
            if coerced is not None:
                return coerced
    except Exception as exc:  # pragma: no cover - permissive
        try:
            _log.debug("variable_hierarchy_flag_read_failed error=%s", exc)
        except Exception:
            pass
    return False


def set_variable_hierarchy_enabled(enabled: bool) -> None:
    """Persist hierarchical variable storage preference to settings."""

    try:
        settings_dir = PROMPTS_DIR / "Settings"
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_path = settings_dir / "settings.json"
        data: dict[str, Any] = {}
        if settings_path.exists():
            try:
                existing = json.loads(settings_path.read_text())
                if isinstance(existing, dict):
                    data = existing
            except Exception:
                data = {}
        data["hierarchical_variables_enabled"] = bool(enabled)
        settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        try:
            _log.error("variable_hierarchy_flag_write_failed error=%s", exc)
        except Exception:
            pass


__all__ = [
    "is_hierarchy_enabled",
    "set_user_hierarchy_preference",
    "is_variable_hierarchy_enabled",
    "set_variable_hierarchy_enabled",
    "is_mcp_notes_enabled",
    "is_analytics_enabled",
]


def _config_flag(*segments: str) -> bool | None:
    try:
        raw = config_registry.get_feature_flag(*segments)
    except Exception as exc:  # pragma: no cover - defensive logging
        try:
            _log.debug("config_flag_read_failed path=%s error=%s", ".".join(segments), exc)
        except Exception:
            pass
        return None
    if raw is None:
        return None
    coerced = _coerce_bool(raw)
    if coerced is None and isinstance(raw, str):
        lowered = raw.strip().lower()
        if lowered in {"enabled", "enable", "observability"}:
            return True
        if lowered in {"disabled", "disable"}:
            return False
    return coerced


def is_mcp_enabled() -> bool:
    """Resolve the overall MCP feature flag.

    Precedence order (highest wins):

    1. ``PROMPT_AUTOMATION_MCP_ENABLED`` environment variable
    2. ``PROMPT_AUTOMATION_MCP_DEBUG`` environment variable (legacy)
    3. Configuration registry ``features.mcp.enabled`` value
    4. Persisted settings via :func:`storage.is_mcp_debug_cli_enabled`
    """

    env = os.environ.get("PROMPT_AUTOMATION_MCP_ENABLED")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced

    legacy_env = os.environ.get("PROMPT_AUTOMATION_MCP_DEBUG")
    legacy_coerced = _coerce_bool(legacy_env) if legacy_env is not None else None
    if legacy_coerced is not None:
        return legacy_coerced

    config_value = _config_flag("mcp", "enabled")
    if config_value is not None:
        return config_value

    return storage.is_mcp_debug_cli_enabled()


def is_mcp_notes_enabled() -> bool:
    """Return whether the MCP note tools should be exposed."""

    env = os.environ.get("PROMPT_AUTOMATION_MCP_NOTES_ENABLED")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced

    config_value = _config_flag("mcp", "notes", "enabled")
    if config_value is not None:
        return config_value

    return False


def is_mcp_debug_enabled() -> bool:
    """Return True when MCP debugging commands should be exposed."""

    env = os.environ.get("PROMPT_AUTOMATION_MCP_DEBUG")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    return is_mcp_enabled()


def is_mcp_observability_enabled() -> bool:
    """Resolve whether MCP observability hooks should be active by default."""

    env = os.environ.get("PROMPT_AUTOMATION_MCP_OBSERVABILITY")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced

    config_value = _config_flag("mcp", "observability")
    if config_value is not None:
        return config_value

    return storage.is_mcp_observability_enabled()


def is_mcp_server_enabled() -> bool:
    """Resolve whether MCP interactions should occur via the local server bridge."""

    env = os.environ.get("PROMPT_AUTOMATION_USE_MCP_SERVER")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced

    config_value = _config_flag("mcp", "use_server")
    if config_value is not None:
        return config_value

    return storage.get_use_mcp_server()


__all__.extend([
    "is_mcp_enabled",
    "is_mcp_debug_enabled",
    "is_mcp_observability_enabled",
    "is_mcp_server_enabled",
])

def is_analytics_enabled() -> bool:
    """Resolve analytics feature flag.
    
    Resolution order:
      1. Env PA_ANALYTICS_ENABLED (1/true/on vs 0/false/off)
      2. Default: True (enabled, opt-out model)
    """
    env = os.environ.get("PA_ANALYTICS_ENABLED")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    return True

def is_reminders_enabled() -> bool:
    """Resolve reminders feature flag.

    Resolution order:
      1. Env PROMPT_AUTOMATION_REMINDERS (1/true/on vs 0/false/off)
      2. Settings Settings/settings.json key "reminders_enabled"
      3. Default: True (enabled)
    """
    env = os.environ.get("PROMPT_AUTOMATION_REMINDERS")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("reminders_enabled")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("reminders_flag_read_failed error=%s", e)
        except Exception:
            pass
    return True


__all__.append("is_reminders_enabled")


def is_reminders_timing_enabled() -> bool:
    """Dev-only flag to log reminder parsing timing.

    Env: PROMPT_AUTOMATION_REMINDERS_TIMING (1/true/on vs 0/false/off)
    Settings: Settings/settings.json key "reminders_timing"
    Default: False
    """
    env = os.environ.get("PROMPT_AUTOMATION_REMINDERS_TIMING")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("reminders_timing")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception:
        pass
    return False


__all__.append("is_reminders_timing_enabled")


# --- Background hotkey ------------------------------------------------------
def is_background_hotkey_enabled() -> bool:
    """Resolve background hotkey feature flag.

    Resolution order:
      1. Env PA_FEAT_BG_HOTKEY (1/true/on vs 0/false/off)
      2. Settings Settings/settings.json key "feature_background_hotkey"
      3. Default: True (enabled)
    """
    env = os.environ.get("PA_FEAT_BG_HOTKEY")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("feature_background_hotkey")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("bg_hotkey_flag_read_failed error=%s", e)
        except Exception:
            pass
    return True


__all__.append("is_background_hotkey_enabled")


# --- Placeholder fast-path (auto-skip collect stage) ------------------------
def is_placeholder_fastpath_enabled() -> bool:
    """Return True if the placeholder-empty fast-path is enabled.

    Resolution order (env overrides settings):
      1. Env PROMPT_AUTOMATION_DISABLE_PLACEHOLDER_FASTPATH
         - truthy (1/true/on)  => disabled (return False)
         - falsy  (0/false/off)=> enabled  (return True)
      2. Settings Settings/settings.json key "disable_placeholder_fastpath"
         - truthy => disabled (False)
         - falsy  => enabled  (True)
      3. Default: enabled (True)
    """
    global _FASTPATH_CACHE_ENV, _FASTPATH_CACHE_PATH, _FASTPATH_CACHE_MTIME, _FASTPATH_CACHE_VALUE

    env_raw = os.environ.get("PROMPT_AUTOMATION_DISABLE_PLACEHOLDER_FASTPATH")
    coerced = _coerce_bool(env_raw) if env_raw is not None else None
    if coerced is not None:
        _FASTPATH_CACHE_ENV = env_raw
        _FASTPATH_CACHE_PATH = None
        _FASTPATH_CACHE_MTIME = None
        _FASTPATH_CACHE_VALUE = not coerced
        return _FASTPATH_CACHE_VALUE

    settings = PROMPTS_DIR / "Settings" / "settings.json"
    settings_exists = settings.exists()
    mtime: float | None = None
    if settings_exists:
        try:
            mtime = settings.stat().st_mtime
        except OSError:
            mtime = None

    if (
        _FASTPATH_CACHE_VALUE is not None
        and _FASTPATH_CACHE_ENV is None
        and env_raw is None
        and _FASTPATH_CACHE_PATH == settings
        and _FASTPATH_CACHE_MTIME == mtime
    ):
        return _FASTPATH_CACHE_VALUE

    result = True
    if settings_exists:
        try:
            data = json.loads(settings.read_text())
            v = data.get("disable_placeholder_fastpath")
            coerced = _coerce_bool(v)
            if coerced is not None:
                result = not coerced
        except Exception:
            result = True

    _FASTPATH_CACHE_ENV = None
    _FASTPATH_CACHE_PATH = settings
    _FASTPATH_CACHE_MTIME = mtime
    _FASTPATH_CACHE_VALUE = result
    return result


__all__.append("is_placeholder_fastpath_enabled")


# --- Workspace Context Gatherer (Feature 001) -------------------------------
def is_workspace_context_obsidian_enabled() -> bool:
    """Resolve whether workspace context gatherer should query Obsidian via MCP.

    Resolution order:
      1. Env PROMPT_AUTOMATION_WORKSPACE_OBSIDIAN (1/true/on vs 0/false/off)
      2. Settings Settings/settings.json key "workspace_context_obsidian_enabled"
      3. Default: False (disabled - optional feature)
    """
    env = os.environ.get("PROMPT_AUTOMATION_WORKSPACE_OBSIDIAN")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("workspace_context_obsidian_enabled")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("workspace_context_obsidian_flag_read_failed error=%s", e)
        except Exception:
            pass
    return False


__all__.append("is_workspace_context_obsidian_enabled")


# --- Local Cache (Feature 24) -----------------------------------------------
def is_local_cache_enabled() -> bool:
    """Resolve local cache feature flag (Feature 24).
    
    Resolution order:
      1. Env PROMPT_AUTOMATION_LOCAL_CACHE (1/true/on vs 0/false/off)
      2. Settings Settings/settings.json key "local_cache_enabled"
      3. Default: False (disabled - opt-in for safety)
    """
    env = os.environ.get("PROMPT_AUTOMATION_LOCAL_CACHE")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("local_cache_enabled")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("local_cache_flag_read_failed error=%s", e)
        except Exception:
            pass
    return False


__all__.append("is_local_cache_enabled")


def is_template_management_enabled() -> bool:
    """Resolve template_management feature flag.
    
    Resolution order:
      1. Env PROMPT_AUTOMATION_TEMPLATE_MANAGEMENT (1/true/on vs 0/false/off)
      2. Settings Settings/settings.json key "template_management_enabled"
      3. Default: True (enabled, opt-out model)
    
    When enabled, uses new TemplateBrowser GUI. When disabled, falls back
    to old inline template management dialog.
    """
    env = os.environ.get("PROMPT_AUTOMATION_TEMPLATE_MANAGEMENT")
    coerced = _coerce_bool(env) if env is not None else None
    if coerced is not None:
        return coerced
    try:
        settings = PROMPTS_DIR / "Settings" / "settings.json"
        if settings.exists():
            data = json.loads(settings.read_text())
            v = data.get("template_management_enabled")
            coerced = _coerce_bool(v)
            if coerced is not None:
                return coerced
    except Exception as e:  # pragma: no cover - permissive
        try:
            _log.debug("template_management_flag_read_failed error=%s", e)
        except Exception:
            pass
    return True  # Default ON


__all__.append("is_template_management_enabled")
