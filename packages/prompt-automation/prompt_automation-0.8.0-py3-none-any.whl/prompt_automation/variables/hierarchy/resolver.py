"""Resolvers for hierarchical variables and related integrations."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Protocol

from ...config import PROMPTS_DIR as _CONFIG_PROMPTS_DIR
from ...errorlog import get_logger
from .storage import HierarchicalVariableStore


_PerformanceHook = Callable[[str, float], None]


class EspansoDiscoveryAdapter(Protocol):
    """Protocol describing discovery adapters for Espanso configuration data."""

    def collect(self) -> Mapping[str, Any]:
        """Return a mapping of global variable keys sourced from Espanso."""


_STUB_PAYLOAD_PATH = Path(__file__).with_name("_stub_payload.json")


def _load_stub_payload() -> dict[str, Any]:
    try:
        data = json.loads(_STUB_PAYLOAD_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {
        "__espanso__": {
            "match_files": [
                "packages/prompt-automation/0.6.9/match/base.yml",
                "packages/prompt-automation/0.6.9/match/tf.yml",
            ],
            "repository_hint": "~/.config/espanso",
        },
        "base": "Think Deeply. If you are unsure of the answer, respond with 'I don't know' or do not answer.",
        "tf": "Think deeply, Don't hallucinate. If you don't know, say 'I don't know'. Ask follow up questions if clarification is needed",
    }


_STUB_ESPANSO_PAYLOAD = _load_stub_payload()


class StubEspansoDiscoveryAdapter:
    """Deterministic stub returning sample Espanso data.

    The stub keeps integration points exercised during tests without requiring
    filesystem probing and mirrors critical replacements so templates still
    resolve when repo discovery or PyYAML are unavailable. Real adapters can
    implement the same interface and be injected when wiring the production
    Espanso sync.
    """

    def collect(self) -> Mapping[str, Any]:
        # Use JSON round-trip to ensure callers receive an isolated copy.
        return json.loads(json.dumps(_STUB_ESPANSO_PAYLOAD))


class RepoEspansoDiscoveryAdapter:
    """Load Espanso match replacements from the local espanso-package repo."""

    def __init__(
        self,
        *,
        repo: Path | None = None,
        fallback: EspansoDiscoveryAdapter | None = None,
    ) -> None:
        self._explicit_repo = repo
        self._fallback = fallback or StubEspansoDiscoveryAdapter()
        self._cached_dir: Path | None = None
        self._cached_mtime: float | None = None
        self._cached_payload: Mapping[str, Any] | None = None

    def collect(self) -> Mapping[str, Any]:
        match_info = self._resolve_match_dir()
        if match_info is None:
            return self._fallback.collect()
        repo_root, match_dir = match_info
        try:
            import yaml
        except ModuleNotFoundError:
            self._log_debug("variables.espanso.yaml_missing")
            return self._fallback.collect()

        newest_mtime = max((p.stat().st_mtime for p in match_dir.glob("*.yml")), default=0.0)
        if (
            self._cached_dir == match_dir
            and self._cached_mtime is not None
            and newest_mtime <= self._cached_mtime
            and self._cached_payload is not None
        ):
            return self._cached_payload

        replacements: dict[str, Any] = {}
        match_files: list[str] = []
        for path in sorted(match_dir.glob("*.yml")):
            if path.name.startswith("_"):
                continue
            try:
                rel = path.relative_to(repo_root).as_posix()
            except Exception:
                try:
                    rel = path.relative_to(match_dir.parent).as_posix()
                except Exception:
                    rel = path.name
            match_files.append(rel)
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception as exc:  # pragma: no cover - defensive
                self._log_error("variables.espanso.parse_error", exc, extra={"file": rel})
                continue
            value = _extract_replace(data)
            if value is None:
                continue
            key = path.stem
            replacements.setdefault(key, value)

        payload: dict[str, Any] = {
            "__espanso__": {
                "match_files": match_files,
                "repository_hint": str(Path.home() / ".config" / "espanso"),
            }
        }
        payload.update(replacements)
        self._cached_dir = match_dir
        self._cached_mtime = newest_mtime
        self._cached_payload = payload
        return payload

    def _resolve_match_dir(self) -> tuple[Path, Path] | None:
        env_match = os.environ.get("PROMPT_AUTOMATION_ESPANSO_MATCH")
        if env_match:
            match_path = Path(env_match).expanduser().resolve()
            if match_path.is_dir():
                return match_path, match_path

        def _find_from_base(base: Path | None) -> tuple[Path, Path] | None:
            if base is None:
                return None
            base = base.resolve()
            direct_match = base / "match"
            if direct_match.exists():
                return base, direct_match
            direct = base / "espanso-package" / "match"
            if direct.exists():
                return base, direct
            packaged_root = base / "packages" / "prompt-automation"
            if packaged_root.exists():
                version_dirs = [
                    d
                    for d in packaged_root.iterdir()
                    if d.is_dir() and not d.name.startswith("_")
                ]

                def _semver_key(path: Path) -> tuple[int, int, int, str]:
                    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", path.name)
                    if match is None:
                        return (0, 0, 0, path.name)
                    major, minor, patch = match.groups()
                    return (int(major), int(minor), int(patch), path.name)

                version_dirs.sort(key=_semver_key, reverse=True)
                for version_dir in version_dirs:
                    match_dir = version_dir / "match"
                    if match_dir.exists():
                        return base, match_dir
            return None

        if self._explicit_repo:
            res = _find_from_base(self._explicit_repo)
            if res:
                return res

        env_repo = os.environ.get("PROMPT_AUTOMATION_REPO")
        if env_repo:
            res = _find_from_base(Path(env_repo).expanduser())
            if res:
                return res

        try:
            from ...espanso_sync import _find_repo_root as _repo_helper

            try:
                discovered = _repo_helper(None)
            except SystemExit:
                discovered = None
            if discovered:
                res = _find_from_base(discovered)
                if res:
                    return res
        except Exception:  # pragma: no cover - helper import best-effort
            pass

        anchors = [Path.cwd(), PROMPTS_DIR, Path(__file__).resolve()]
        for anchor in anchors:
            for candidate in [anchor, *anchor.parents]:
                res = _find_from_base(candidate)
                if res:
                    return res

        return None

    def _log_debug(self, event: str) -> None:
        try:
            _log.debug(event)
        except Exception:  # pragma: no cover - logging safety
            pass

    def _log_error(self, event: str, exc: Exception, *, extra: Mapping[str, Any] | None = None) -> None:
        payload = {"error": str(exc)}
        if extra:
            payload.update({k: str(v) for k, v in extra.items()})
        try:
            _log.error(event, extra=payload)
        except Exception:  # pragma: no cover - logging safety
            pass


def _extract_replace(payload: Any) -> Any | None:
    if not isinstance(payload, Mapping):
        return None
    matches = payload.get("matches")
    if isinstance(matches, list):
        for entry in matches:
            if isinstance(entry, Mapping) and "replace" in entry:
                value = entry.get("replace")
                if value is not None:
                    return value
    return None


PROMPTS_DIR = Path(_CONFIG_PROMPTS_DIR)

_log = get_logger(__name__)


class GlobalVariableResolver:
    """Resolve global variable mappings with optional hierarchical support."""

    def __init__(
        self,
        *,
        adapter: EspansoDiscoveryAdapter | None = None,
        performance_hook: _PerformanceHook | None = None,
    ) -> None:
        self._adapter = adapter or RepoEspansoDiscoveryAdapter()
        self._performance_hook = performance_hook

    def resolve(self, template_globals: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return merged globals respecting precedence rules.

        Precedence (lowest -> highest):
            1. Legacy ``globals.json`` entries
            2. Hierarchical store namespace ``globals`` (when flag enabled)
            3. Espanso discovery data (flag-enabled)
            4. ``template_globals`` provided by the caller
        """

        effective: dict[str, Any] = {}
        flag_enabled = is_variable_hierarchy_enabled()

        if flag_enabled:
            hierarchy = self._load_hierarchical_globals()
            effective.update(hierarchy)
            legacy = self._load_legacy_globals()
            for key, value in legacy.items():
                effective.setdefault(key, value)
            self._inject_espanso(effective)
        else:
            effective.update(self._load_legacy_globals())

        if template_globals:
            for key, value in template_globals.items():
                effective[key] = value

        return effective

    # Internal helpers --------------------------------------------------
    def _load_legacy_globals(self) -> dict[str, Any]:
        start = time.perf_counter()
        data: dict[str, Any] = {}
        path = self._globals_path()
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                gph = payload.get("global_placeholders")
                if isinstance(gph, dict):
                    data = dict(gph)
            except Exception as exc:  # pragma: no cover - defensive
                self._log_error("variables.resolver.legacy_error", exc)
        self._record_phase("legacy_load", start)
        return data

    def _load_hierarchical_globals(self) -> dict[str, Any]:
        start = time.perf_counter()
        data: dict[str, Any] = {}
        try:
            store = HierarchicalVariableStore()
            namespace = store.export_namespace("globals")
            if isinstance(namespace, dict):
                data = namespace
        except Exception as exc:  # pragma: no cover - defensive
            self._log_error("variables.resolver.hierarchy_error", exc)
        self._record_phase("hierarchy_load", start)
        return data

    def _inject_espanso(self, target: MutableMapping[str, Any]) -> None:
        start = time.perf_counter()
        payload: Mapping[str, Any] | None = None
        try:
            payload = self._adapter.collect()
        except Exception as exc:  # pragma: no cover - defensive
            self._log_error("variables.resolver.espanso_error", exc)
        finally:
            self._record_phase("espanso_discovery", start)
        if isinstance(payload, Mapping):
            for key, value in payload.items():
                target.setdefault(key, value)

    def _globals_path(self) -> Path:
        module = sys.modules.get("prompt_automation.variables")
        candidate: Any | None = None
        if module is not None:
            candidate = getattr(module, "PROMPTS_DIR", None)
        if candidate:
            try:
                return Path(candidate) / "globals.json"
            except Exception:  # pragma: no cover - defensive
                pass
        return PROMPTS_DIR / "globals.json"

    def _record_phase(self, name: str, start: float) -> None:
        duration_ms = (time.perf_counter() - start) * 1000.0
        if self._performance_hook:
            try:
                self._performance_hook(name, duration_ms)
            except Exception:  # pragma: no cover - defensive
                pass
        try:
            _log.info(
                "variables.resolver.timing", extra={"phase": name, "duration_ms": int(duration_ms)}
            )
        except Exception:  # pragma: no cover - logging safety
            pass

    def _log_error(self, event: str, exc: Exception) -> None:
        try:
            _log.error(event, extra={"error": str(exc)})
        except Exception:  # pragma: no cover - logging safety
            pass


__all__ = [
    "EspansoDiscoveryAdapter",
    "StubEspansoDiscoveryAdapter",
    "RepoEspansoDiscoveryAdapter",
    "GlobalVariableResolver",
    "is_variable_hierarchy_enabled",
]


def _is_variable_hierarchy_enabled() -> bool:
    from ... import features

    return features.is_variable_hierarchy_enabled()


def is_variable_hierarchy_enabled() -> bool:
    """Expose feature flag helper for monkeypatch-heavy tests."""

    return _is_variable_hierarchy_enabled()
