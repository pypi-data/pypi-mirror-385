"""Persistence helpers for variable overrides and settings."""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, Callable

from ..config import HOME_DIR, PROMPTS_DIR
from ..errorlog import get_logger


_log = get_logger(__name__)

# Persistence for file placeholders & skip flags
_PERSIST_DIR = HOME_DIR
_PERSIST_FILE = _PERSIST_DIR / "placeholder-overrides.json"

# Settings file (lives alongside templates so it can be edited via GUI / under VCS if desired)
_SETTINGS_DIR = PROMPTS_DIR / "Settings"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"

# Registered observers for boolean settings
_BOOLEAN_OBSERVERS: Dict[str, list[Callable[[bool], None]]] = {}


_MCP_DEBUG_VALID_MODES = {"off", "cli", "observability"}


def _normalize_mcp_debug_mode(value: object) -> str:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _MCP_DEBUG_VALID_MODES:
            return lowered
    return "off"

def _load_settings_payload() -> Dict[str, Any]:
    if not _SETTINGS_FILE.exists():
        return {}
    try:
        return json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover - corrupted file edge case
        _log.error("failed to load settings file: %s", e)
        return {}

def _write_settings_payload(payload: Dict[str, Any]) -> None:
    try:
        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _SETTINGS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(_SETTINGS_FILE)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to write settings file: %s", e)


def add_boolean_setting_observer(key: str, callback: Callable[[bool], None]) -> None:
    """Register ``callback`` to run when ``key`` is updated via :func:`set_boolean_setting`.

    Observers are lightweight and best-effort; failures are logged but do not
    propagate. Callbacks receive the new boolean value.
    """

    _BOOLEAN_OBSERVERS.setdefault(key, []).append(callback)


def _notify_boolean_observers(key: str, value: bool) -> None:
    for cb in _BOOLEAN_OBSERVERS.get(key, []):
        try:
            cb(value)
        except Exception as e:  # pragma: no cover - defensive
            try:
                _log.error("settings_observer_failed key=%s error=%s", key, e)
            except Exception:
                pass

# --- Theme settings accessors ----------------------------------------------
def get_setting_theme() -> str | None:
    """Return the preferred theme name from settings.json (light/dark/system)."""
    try:
        payload = _load_settings_payload()
        val = payload.get("theme")
        if isinstance(val, str) and val.strip():
            return val.strip()
    except Exception:
        pass
    return None


def set_setting_theme(name: str) -> None:
    """Persist preferred theme name to settings.json."""
    try:
        payload = _load_settings_payload()
        if name:
            payload["theme"] = str(name)
        else:
            payload.pop("theme", None)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist theme: %s", e)


def get_setting_enable_theming() -> bool:
    """Return global enable_theming flag (default True)."""
    try:
        payload = _load_settings_payload()
        val = payload.get("enable_theming")
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in {"1", "true", "yes", "on"}
    except Exception:
        pass
    return True


def set_setting_enable_theming(enabled: bool) -> None:
    try:
        payload = _load_settings_payload()
        payload["enable_theming"] = bool(enabled)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist enable_theming: %s", e)

# --- Espanso repo root (optional) -------------------------------------------
def get_setting_espanso_repo_root() -> str | None:
    """Return an explicit repo root for espanso sync if configured.

    Looks for the key ``espanso_repo_root`` (preferred) or ``repo_root``
    inside Settings/settings.json. Returns a normalized absolute path or
    None if missing/invalid. This enables the GUI "Sync Espanso?" action
    to locate the repo when the app is launched outside of the repo.
    """
    try:
        payload = _load_settings_payload()
        val = payload.get("espanso_repo_root") or payload.get("repo_root")
        if isinstance(val, str) and val.strip():
            return str(Path(val).expanduser().resolve())
    except Exception:
        pass
    return None

# --- Espanso default repo URL (HTTPS) ---------------------------------------
def get_setting_espanso_repo_url() -> str | None:
    """Return preferred HTTPS Git URL for installing the Espanso package.

    Reads ``espanso_repo_url`` from Settings/settings.json if set. This helps
    GUI installers avoid guessing the remote when elevation or UNC paths make
    discovery unreliable.
    """
    try:
        payload = _load_settings_payload()
        val = payload.get("espanso_repo_url")
        if isinstance(val, str) and val.strip():
            return val.strip()
    except Exception:
        pass
    return None


# --- Manual packaging preferences -------------------------------------------
def get_manual_packaging_verbose_logs() -> bool:
    """Return whether manual packaging logs should default to verbose mode."""

    try:
        payload = _load_settings_payload()
        section = payload.get("manual_packaging") or {}
        val = section.get("verbose_logs")
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            lowered = val.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
    except Exception:
        pass
    return False


def set_manual_packaging_verbose_logs(enabled: bool) -> None:
    """Persist preference for verbose log streaming in the packaging wizard."""

    try:
        payload = _load_settings_payload()
        section = payload.setdefault("manual_packaging", {})
        section["verbose_logs"] = bool(enabled)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist manual packaging preference: %s", e)


def set_setting_espanso_repo_url(url: str | None) -> None:
    """Persist or clear the preferred HTTPS Git URL for Espanso installs."""
    try:
        payload = _load_settings_payload()
        if url and url.strip():
            payload["espanso_repo_url"] = url.strip()
        else:
            payload.pop("espanso_repo_url", None)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist espanso_repo_url: %s", e)

def _sync_settings_from_overrides(overrides: Dict[str, Any]) -> None:
    """Persist selected override data into settings file.

    We intentionally mirror only *stable* user editable sections so that
    version controlled settings can provide defaults while local runtime
    state (placeholder-overrides.json) remains the source of truth for
    ephemeral fields. Currently mirrored:

    - file_overrides.templates
    - global_files (reference file selections)

    A future extension may include additional explicit keys; keep this
    focused to avoid surprising churn in user-maintained settings.
    """
    payload = _load_settings_payload()
    file_overrides = payload.setdefault("file_overrides", {})
    file_overrides["templates"] = overrides.get("templates", {})
    # Mirror global reference file selections (if any)
    gfiles = overrides.get("global_files") or {}
    if gfiles:
        payload["global_files"] = {k: v for k, v in gfiles.items() if k == "reference_file" and isinstance(v, str)}
    payload.setdefault("metadata", {})["last_sync"] = platform.platform()
    _write_settings_payload(payload)

def _merge_overrides_with_settings(overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Merge editable settings values into overrides object.

    Precedence rules:
      - settings.json "file_overrides.templates" entries override local
        placeholder path/skip for each template/placeholder.
      - settings.json "global_files.reference_file" overrides local
        global reference file selection (useful to provide a default
        checked into a repo without touching user state).
    """
    settings_payload = _load_settings_payload()
    merged = json.loads(json.dumps(overrides))  # deep copy via json
    # --- Merge file overrides -------------------------------------------------
    settings_templates = settings_payload.get("file_overrides", {}).get("templates", {})
    if isinstance(settings_templates, dict):
        tmap = merged.setdefault("templates", {})
        for tid, entries in settings_templates.items():
            if not isinstance(entries, dict):
                continue
            target = tmap.setdefault(tid, {})
            for name, info in entries.items():
                if isinstance(info, dict):
                    filtered = {k: info[k] for k in ("path", "skip") if k in info}
                    if filtered:
                        target[name] = {**target.get(name, {}), **filtered}
    # --- Merge global reference file -----------------------------------------
    gfiles_settings = settings_payload.get("global_files", {})
    if isinstance(gfiles_settings, dict) and isinstance(gfiles_settings.get("reference_file"), str):
        merged.setdefault("global_files", {})["reference_file"] = gfiles_settings["reference_file"]
    return merged

def _read_hotkey_from_settings() -> str | None:
    """Return hotkey value from settings.json if defined.

    This accessor is intentionally kept lightweight (no caching) so that
    test patches of _SETTINGS_FILE take effect immediately. Returns None
    if file missing or key absent/invalid.
    """
    try:
        payload = _load_settings_payload()
        hk = payload.get("hotkey")
        if isinstance(hk, str) and hk.strip():
            return hk.strip()
    except Exception:
        pass
    return None

# --- Generic settings accessors ---------------------------------------------
def get_setting_auto_copy_review() -> bool:
    """Return True if auto-copy-on-review is enabled in settings.json.

    Missing or invalid values default to False. This is intentionally
    lightweight (no caching) so tests that patch the settings file path or
    contents see immediate effects.
    """
    try:
        payload = _load_settings_payload()
        if "auto_copy_review" not in payload:
            # Default ON when unset
            return True
        val = payload.get("auto_copy_review")
        return bool(val is True or (isinstance(val, str) and val.lower() in {"1", "true", "yes", "on"}))
    except Exception:
        return False

def set_setting_auto_copy_review(enabled: bool) -> None:
    """Persist auto-copy-on-review flag to settings.json.

    Stores a boolean under the key ``auto_copy_review``. Failures are logged
    but not raised so callers (GUI) remain resilient.
    """
    try:
        payload = _load_settings_payload()
        payload["auto_copy_review"] = bool(enabled)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist auto_copy_review setting: %s", e)

def is_auto_copy_enabled_for_template(template_id: int) -> bool:
    """Return True if auto-copy is globally enabled and not disabled for this template.

    Default: if global auto-copy disabled -> False. If enabled and template not
    explicitly disabled -> True.
    """
    if not get_setting_auto_copy_review():
        return False
    try:
        payload = _load_settings_payload()
        disabled = payload.get("auto_copy_review_disabled") or []
        if isinstance(disabled, list):
            return str(template_id) not in {str(x) for x in disabled}
    except Exception:
        pass
    return True

def set_template_auto_copy_disabled(template_id: int, disabled: bool) -> None:
    """Persist per-template disable flag in settings.json.

    We only store templates that are disabled to keep file minimal. Passing
    disabled=False removes template id from list.
    """
    try:
        payload = _load_settings_payload()
        current = payload.get("auto_copy_review_disabled")
        if not isinstance(current, list):
            current = []
        sid = str(template_id)
        if disabled:
            if sid not in {str(x) for x in current}:
                current.append(sid)
        else:
            current = [x for x in current if str(x) != sid]
        # Normalize list (unique, sorted for stability)
        uniq = sorted({str(x) for x in current}, key=lambda x: int(x) if x.isdigit() else x)
        if uniq:
            payload["auto_copy_review_disabled"] = uniq
        else:
            payload.pop("auto_copy_review_disabled", None)
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O / formatting issues
        _log.error("failed to persist per-template auto-copy flag: %s", e)

# --- Generic boolean from settings by key (helper) -------------------------
def get_boolean_setting(key: str, default: bool = False) -> bool:
    try:
        payload = _load_settings_payload()
        val = payload.get(key)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in {"1", "true", "yes", "on"}
    except Exception:
        pass
    return default

def set_boolean_setting(key: str, value: bool) -> None:
    try:
        payload = _load_settings_payload()
        payload[key] = bool(value)
        _write_settings_payload(payload)
        _notify_boolean_observers(key, bool(value))
    except Exception as e:  # pragma: no cover
        _log.error("failed to persist boolean setting %s: %s", key, e)


# --- Specific boolean settings --------------------------------------------

def get_background_hotkey_enabled() -> bool:
    """Return True if background hotkey feature is enabled (default True)."""
    return get_boolean_setting("background_hotkey_enabled", True)


def set_background_hotkey_enabled(enabled: bool) -> None:
    """Persist background hotkey enabled flag."""
    set_boolean_setting("background_hotkey_enabled", enabled)


def get_espanso_enabled() -> bool:
    """Return True if Espanso integration is enabled (default True)."""
    return get_boolean_setting("espanso_enabled", True)


def set_espanso_enabled(enabled: bool) -> None:
    """Persist Espanso integration enabled flag."""
    set_boolean_setting("espanso_enabled", enabled)


def get_use_mcp_server() -> bool:
    """Return True when MCP should be accessed via a server bridge (default False)."""

    return get_boolean_setting("use_mcp_server", False)


def set_use_mcp_server(enabled: bool) -> None:
    """Persist MCP server usage preference."""

    set_boolean_setting("use_mcp_server", enabled)


def get_mcp_debug_mode() -> str:
    """Return the persisted MCP debug mode ("off", "cli", "observability")."""

    try:
        payload = _load_settings_payload()
        return _normalize_mcp_debug_mode(payload.get("mcp_debug_mode"))
    except Exception:
        return "off"


def is_mcp_debug_cli_enabled() -> bool:
    """Return True when the CLI debug helpers should be exposed."""

    return get_mcp_debug_mode() in {"cli", "observability"}


def is_mcp_observability_enabled() -> bool:
    """Return True when observability hooks should default to enabled."""

    return get_mcp_debug_mode() == "observability"


def set_mcp_debug_mode(mode: str) -> None:
    """Persist the MCP debug mode and notify observers."""

    normalized = _normalize_mcp_debug_mode(mode)
    try:
        payload = _load_settings_payload()
        payload["mcp_debug_mode"] = normalized
        _write_settings_payload(payload)
    except Exception as e:  # pragma: no cover - I/O errors
        _log.error("failed to persist mcp_debug_mode: %s", e)
        return

    _notify_boolean_observers("mcp_debug_cli_enabled", normalized in {"cli", "observability"})
    _notify_boolean_observers("mcp_observability_enabled", normalized == "observability")


def _normalize_reference_path(path: str) -> str:
    """Normalize reference file path for cross-platform consistency.

    - Expands user (~)
    - Converts Windows backslashes to forward slashes when running under WSL/Linux for consistent display
    - Resolves redundant separators / up-level references when possible
    """
    try:
        p = Path(path.strip().strip('"')).expanduser()
        txt = str(p)
        if os.name != 'nt':
            if ':' in txt and '\\' in txt:
                txt = txt.replace('\\', '/')
        return txt
    except Exception:
        return path

def _load_overrides() -> dict:
    base = {"templates": {}, "reminders": {}, "template_globals": {}, "template_values": {}, "session": {}, "global_files": {}}
    if _PERSIST_FILE.exists():
        try:
            base = json.loads(_PERSIST_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            _log.error("failed to load overrides: %s", e)
    # Migration: consolidate legacy reference file keys to global_files.reference_file
    try:
        gfiles = base.setdefault("global_files", {})
        if "reference_file" not in gfiles:
            legacy = None
            for section in ("template_values", "template_globals"):
                seg = base.get(section, {})
                if not isinstance(seg, dict):
                    continue
                for _tid, data in seg.items():
                    if not isinstance(data, dict):
                        continue
                    for k, v in data.items():
                        if k in {"reference_file_default", "reference_file_content", "reference_file"} and isinstance(v, str) and v.strip():
                            legacy = v.strip()
                            break
                    if legacy:
                        break
                if legacy:
                    break
            if legacy and Path(legacy).expanduser().exists():
                gfiles["reference_file"] = legacy
    except Exception:
        pass
    # Remove any persisted reference_file_content snapshots (we now always re-read live)
    try:
        tv = base.get("template_values", {})
        if isinstance(tv, dict):
            for tid, mapping in list(tv.items()):
                if not isinstance(mapping, dict):
                    continue
                if "reference_file_content" in mapping:
                    mapping.pop("reference_file_content", None)
            for tid in [k for k, v in tv.items() if isinstance(v, dict) and not v]:
                tv.pop(tid, None)
    except Exception:
        pass
    # Normalize global reference file path (Windows path usable under WSL etc.)
    try:
        refp = base.get("global_files", {}).get("reference_file")
        if isinstance(refp, str) and refp:
            norm = _normalize_reference_path(refp)
            if norm != refp:
                base.setdefault("global_files", {})["reference_file"] = norm
                try:
                    _save_overrides(base)
                except Exception:
                    pass
    except Exception:
        pass
    merged = _merge_overrides_with_settings(base)
    return merged

def _save_overrides(data: dict) -> None:
    """Save overrides and propagate to settings file."""
    try:
        _PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _PERSIST_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(_PERSIST_FILE)
    except Exception as e:
        _log.error("failed to save overrides: %s", e)
    try:
        _sync_settings_from_overrides(data)
    except Exception as e:  # pragma: no cover - defensive
        _log.error("failed to sync overrides to settings: %s", e)

def _get_template_entry(data: dict, template_id: int, name: str) -> dict | None:
    return data.get("templates", {}).get(str(template_id), {}).get(name)

def _set_template_entry(data: dict, template_id: int, name: str, payload: dict) -> None:
    data.setdefault("templates", {}).setdefault(str(template_id), {})[name] = payload

def get_remembered_context() -> str | None:
    """Return remembered context text if set this session (persisted in overrides)."""
    data = _load_overrides()
    return data.get("session", {}).get("remembered_context")

def set_remembered_context(text: str | None) -> None:
    data = _load_overrides()
    sess = data.setdefault("session", {})
    if text:
        sess["remembered_context"] = text
    else:
        sess.pop("remembered_context", None)
    _save_overrides(data)

def get_template_global_overrides(template_id: int) -> dict:
    data = _load_overrides()
    return data.get("template_globals", {}).get(str(template_id), {})

def ensure_template_global_snapshot(template_id: int, gph: dict) -> None:
    """If no snapshot exists for this template, persist current global placeholders."""
    if not isinstance(template_id, int):
        return
    data = _load_overrides()
    tgl = data.setdefault("template_globals", {})
    key = str(template_id)
    if key not in tgl:
        snap = {}
        for k, v in (gph or {}).items():
            if isinstance(v, (str, int, float)) or v is None:
                snap[k] = v
            elif isinstance(v, list):
                snap[k] = [x for x in v]
        tgl[key] = snap
        _save_overrides(data)

def apply_template_global_overrides(template_id: int, gph: dict) -> dict:
    """Return merged globals (snapshot overrides > template-defined > original globals)."""
    merged = dict(gph or {})
    overrides = get_template_global_overrides(template_id)
    if overrides:
        merged.update(overrides)
    return merged
