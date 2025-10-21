"""Hierarchical variable persistence with optional globals migration."""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ...config import HOME_DIR, PROMPTS_DIR
from ...errorlog import get_logger


_LOG = get_logger(__name__)

_MISSING = object()

HIERARCHICAL_VARIABLES_DIR = HOME_DIR / "variables"
HIERARCHICAL_VARIABLES_FILE = HIERARCHICAL_VARIABLES_DIR / "hierarchical-variables.json"
_STUB_PAYLOAD_PATH = Path(__file__).with_name("_stub_payload.json")


def _default_payload() -> dict[str, Any]:
    return {"version": 1, "namespaces": {}, "meta": {}}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_dict(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        value = {}
        parent[key] = value
    return value


def _touch_namespace_meta(
    meta: dict[str, Any], namespace: str, *, source: str, timestamp: str | None = None
) -> None:
    timestamp = timestamp or _utcnow_iso()
    namespaces_meta = _ensure_dict(meta, "namespaces")
    ns_meta = _ensure_dict(namespaces_meta, namespace)
    ns_meta["updated_at"] = timestamp
    ns_meta["last_source"] = source
    provenance = ns_meta.setdefault("provenance", [])
    if source not in provenance:
        provenance.append(source)


def _tombstone_key(path: Sequence[str]) -> str:
    return "/".join(path)


def _register_tombstone(meta: dict[str, Any], namespace: str, path: Sequence[str]) -> None:
    tombstones = _ensure_dict(meta, "tombstones")
    ns_tombstones = tombstones.setdefault(namespace, [])
    key = _tombstone_key(path)
    if key not in ns_tombstones:
        ns_tombstones.append(key)


def _clear_tombstone(meta: dict[str, Any], namespace: str, path: Sequence[str]) -> None:
    tombstones = meta.get("tombstones")
    if not isinstance(tombstones, dict):
        return
    ns_tombstones = tombstones.get(namespace)
    if not isinstance(ns_tombstones, list):
        return
    key = _tombstone_key(path)
    if key in ns_tombstones:
        ns_tombstones.remove(key)
    if not ns_tombstones:
        tombstones.pop(namespace, None)
    if not tombstones:
        meta.pop("tombstones", None)


def _is_tombstoned(meta: dict[str, Any], namespace: str, path: Sequence[str]) -> bool:
    tombstones = meta.get("tombstones", {})
    if not isinstance(tombstones, dict):
        return False
    ns_tombstones = tombstones.get(namespace)
    if not isinstance(ns_tombstones, list):
        return False
    return _tombstone_key(path) in ns_tombstones


def _load_stub_payload() -> dict[str, Any]:
    try:
        data = json.loads(_STUB_PAYLOAD_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:  # pragma: no cover - defensive
        try:
            _LOG.error("hierarchical_variables.stub_read_failed")
        except Exception:
            pass
    return {}


def _stub_signature(stub_payload: dict[str, Any]) -> str | None:
    relevant = {k: v for k, v in stub_payload.items() if k != "__espanso__"}
    if not relevant:
        return None
    canonical = json.dumps(relevant, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _globals_signature(payload: Mapping[str, Any]) -> str | None:
    if not payload:
        return None
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _flatten_leaf_values(data: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(data, Mapping):
        if not data and path:
            yield path, {}
        for key, value in data.items():
            yield from _flatten_leaf_values(value, path + (str(key),))
    else:
        yield path, data


def _lookup_path(payload: Mapping[str, Any], path: Sequence[str]) -> Any:
    node: Any = payload
    for segment in path:
        if isinstance(node, Mapping) and segment in node:
            node = node[segment]
        else:
            return _MISSING
    return node


def _set_path(payload: dict[str, Any], path: Sequence[str], value: Any) -> None:
    cursor: dict[str, Any] = payload
    for segment in path[:-1]:
        child = cursor.get(segment)
        if not isinstance(child, dict):
            child = {}
            cursor[segment] = child
        cursor = child
    cursor[path[-1]] = value


def _delete_path(payload: dict[str, Any], path: Sequence[str]) -> bool:
    cursor: dict[str, Any] = payload
    trail: list[tuple[dict[str, Any], str]] = []
    for segment in path:
        if not isinstance(cursor, dict) or segment not in cursor:
            return False
        trail.append((cursor, segment))
        cursor = cursor[segment]
    parent, last = trail.pop()
    parent.pop(last, None)
    removed = True
    while trail:
        holder, segment = trail.pop()
        node = holder.get(segment)
        if isinstance(node, dict) and not node:
            holder.pop(segment, None)
        else:
            break
    return removed


class HierarchicalVariableStore:
    """Read/write accessor for hierarchical variables backed by JSON."""

    def __init__(self, *, path: Path | None = None) -> None:
        if not is_variable_hierarchy_enabled():
            raise RuntimeError("Hierarchical variable storage feature flag is disabled")
        self._path = path or HIERARCHICAL_VARIABLES_FILE
        self._payload: dict[str, Any] | None = None
        self._migration_checked = False

    # Public API ------------------------------------------------------------
    def get_value(self, namespace: str, path: Sequence[str], default: Any | None = None) -> Any | None:
        data = self._ensure_payload()
        node: Any = data.get("namespaces", {}).get(namespace, {})
        for key in path:
            if not isinstance(node, dict):
                return default
            node = node.get(key)
            if node is None:
                return default
        if isinstance(node, (dict, list)):
            return copy.deepcopy(node)
        return node

    def set_value(
        self,
        namespace: str,
        path: Sequence[str],
        value: Any,
        *,
        source: str = "manual_set",
        propagate_errors: bool = False,
    ) -> None:
        if not namespace:
            raise ValueError("namespace must be provided")
        if not path:
            raise ValueError("path must contain at least one key")
        data = self._ensure_payload()
        names = data.setdefault("namespaces", {})
        cursor = names.setdefault(namespace, {})
        if not isinstance(cursor, dict):
            cursor = {}
            names[namespace] = cursor
        for key in path[:-1]:
            child = cursor.get(key)
            if not isinstance(child, dict):
                child = {}
                cursor[key] = child
            cursor = child
        cursor[path[-1]] = copy.deepcopy(value)
        meta = data.setdefault("meta", {})
        _clear_tombstone(meta, namespace, path)
        _touch_namespace_meta(meta, namespace, source=source)
        persisted = self._persist(data)
        if not persisted and propagate_errors:
            raise IOError("Failed to persist hierarchical variables")

    def delete_value(
        self,
        namespace: str,
        path: Sequence[str],
        *,
        source: str = "manual_delete",
        propagate_errors: bool = False,
    ) -> bool:
        if not namespace or not path:
            return False
        data = self._ensure_payload()
        names = data.get("namespaces", {})
        cursor = names.get(namespace)
        if not isinstance(cursor, dict):
            return False
        trail: list[tuple[dict[str, Any], str]] = []
        node: Any = cursor
        for key in path:
            if not isinstance(node, dict) or key not in node:
                return False
            trail.append((node, key))
            node = node[key]
        parent, key = trail.pop()
        if key not in parent:
            return False
        parent.pop(key)
        removed = True
        while trail:
            holder, key = trail.pop()
            child = holder.get(key)
            if isinstance(child, dict) and not child:
                holder.pop(key, None)
            else:
                break
        if isinstance(cursor, dict) and not cursor:
            names.pop(namespace, None)
        if removed:
            meta = data.setdefault("meta", {})
            _touch_namespace_meta(meta, namespace, source=source)
            _register_tombstone(meta, namespace, path)
            persisted = self._persist(data)
            if not persisted and propagate_errors:
                raise IOError("Failed to persist hierarchical variables")
        return removed

    def export_namespace(self, namespace: str) -> dict[str, Any]:
        data = self._ensure_payload()
        target = data.get("namespaces", {}).get(namespace, {})
        if isinstance(target, dict):
            return copy.deepcopy(target)
        return {}

    def list_namespaces(self) -> list[str]:
        data = self._ensure_payload()
        names = data.get("namespaces", {})
        if not isinstance(names, dict):
            return []
        return sorted(names.keys())

    # Internal helpers ------------------------------------------------------
    def _ensure_payload(self) -> dict[str, Any]:
        if self._payload is None:
            self._payload = self._load_payload()
        if not self._migration_checked:
            self._run_migration()
        return self._payload

    def _load_payload(self) -> dict[str, Any]:
        payload = _default_payload()
        if self._path.exists():
            try:
                loaded = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    if isinstance(loaded.get("namespaces"), dict):
                        payload["namespaces"] = loaded["namespaces"]
                    if isinstance(loaded.get("meta"), dict):
                        payload["meta"] = loaded["meta"]
                    if isinstance(loaded.get("version"), int):
                        payload["version"] = loaded["version"]
            except Exception as exc:  # pragma: no cover - defensive
                try:
                    _LOG.error("hierarchical_variables.read_failed", extra={"error": str(exc)})
                except Exception:
                    pass
        return payload

    def _run_migration(self) -> None:
        if self._payload is None:
            self._payload = _default_payload()
        payload = self._payload
        meta = payload.setdefault("meta", {})
        namespaces = payload.setdefault("namespaces", {})
        globals_namespace = _ensure_dict(namespaces, "globals")

        seeded_from_legacy = False
        seeded_from_stub = False
        packaged_payload: dict[str, Any] | None = None

        try:
            _LOG.info("hierarchical_variables.migration_start")
        except Exception:
            pass

        globals_path = PROMPTS_DIR / "globals.json"
        if globals_path.exists():
            try:
                packaged_payload = json.loads(globals_path.read_text(encoding="utf-8"))
                gph = packaged_payload.get("global_placeholders")
                if isinstance(gph, dict):
                    for key, value in gph.items():
                        if key not in globals_namespace and not _is_tombstoned(meta, "globals", [key]):
                            globals_namespace[key] = value
                            seeded_from_legacy = True
                notes = packaged_payload.get("notes")
                if isinstance(notes, dict) and "legacy_global_notes" not in meta:
                    meta["legacy_global_notes"] = notes
            except Exception as exc:  # pragma: no cover - defensive
                try:
                    _LOG.error("hierarchical_variables.migration_error", extra={"error": str(exc)})
                except Exception:
                    pass

        stub_payload = _load_stub_payload()
        stub_defaults = {k: v for k, v in stub_payload.items() if k != "__espanso__"}
        stub_sig = _stub_signature(stub_payload)
        if stub_defaults:
            for key, value in stub_defaults.items():
                if key not in globals_namespace and not _is_tombstoned(meta, "globals", [key]):
                    globals_namespace[key] = value
                    seeded_from_stub = True
        if stub_sig or stub_payload.get("__espanso__"):
            espanso_meta = _ensure_dict(meta, "espanso_defaults")
            timestamp = _utcnow_iso()
            if stub_sig:
                espanso_meta["signature"] = stub_sig
            stub_meta = stub_payload.get("__espanso__", {})
            if isinstance(stub_meta, dict):
                if isinstance(stub_meta.get("match_files"), list):
                    espanso_meta["match_files"] = list(stub_meta["match_files"])
                if "repository_hint" in stub_meta:
                    espanso_meta["repository_hint"] = stub_meta["repository_hint"]
            espanso_meta["last_checked_at"] = timestamp
            if seeded_from_stub:
                espanso_meta["last_seeded_at"] = timestamp
                espanso_meta["seeded_keys"] = sorted(stub_defaults.keys())

        if packaged_payload:
            self._sync_packaged_globals(
                meta,
                globals_namespace,
                packaged_payload,
                seeded_from_stub=seeded_from_stub,
                seeded_from_legacy=seeded_from_legacy,
            )

        if seeded_from_stub:
            _touch_namespace_meta(meta, "globals", source="espanso_stub")
        if seeded_from_legacy:
            _touch_namespace_meta(meta, "globals", source="legacy_globals")

        if seeded_from_legacy or seeded_from_stub or not meta.get("globals_migrated"):
            meta["globals_migrated"] = True

        legacy_meta = _ensure_dict(meta, "legacy_globals")
        legacy_meta["last_checked_at"] = _utcnow_iso()
        if seeded_from_legacy:
            legacy_meta["last_seeded_at"] = legacy_meta["last_checked_at"]
            legacy_meta["migrated"] = True
        elif not legacy_meta.get("migrated") and meta.get("globals_migrated"):
            legacy_meta["migrated"] = True

        self._migration_checked = True
        self._persist(payload)

    def _sync_packaged_globals(
        self,
        meta: dict[str, Any],
        namespace: dict[str, Any],
        packaged_payload: Mapping[str, Any],
        *,
        seeded_from_stub: bool = False,
        seeded_from_legacy: bool = False,
    ) -> None:
        gph = packaged_payload.get("global_placeholders")
        if not isinstance(gph, Mapping):
            return

        packaged_meta = _ensure_dict(meta, "packaged_globals")

        prev_pairs: dict[tuple[str, ...], Any] = {}
        baseline_json = packaged_meta.get("baseline_json")
        if isinstance(baseline_json, str):
            try:
                baseline_payload = json.loads(baseline_json)
                if isinstance(baseline_payload, Mapping):
                    prev_pairs = {
                        path: value for path, value in _flatten_leaf_values(baseline_payload)
                    }
            except json.JSONDecodeError:
                prev_pairs = {}
        else:
            prev_values = packaged_meta.get("values")
            if isinstance(prev_values, Mapping):
                prev_pairs = {path: value for path, value in _flatten_leaf_values(prev_values)}
        curr_pairs = {path: value for path, value in _flatten_leaf_values(gph)}

        changed = False
        for path, new_value in curr_pairs.items():
            if _is_tombstoned(meta, "globals", path):
                continue
            existing = _lookup_path(namespace, path)
            prev_value = prev_pairs.get(path, _MISSING)
            if existing is _MISSING:
                _set_path(namespace, path, copy.deepcopy(new_value))
                changed = True
            elif prev_value is not _MISSING and existing == prev_value:
                _set_path(namespace, path, copy.deepcopy(new_value))
                changed = True

        for path, prev_value in prev_pairs.items():
            if path in curr_pairs:
                continue
            if _is_tombstoned(meta, "globals", path):
                continue
            existing = _lookup_path(namespace, path)
            if existing is not _MISSING and existing == prev_value:
                _delete_path(namespace, path)
                changed = True

        if changed:
            _touch_namespace_meta(meta, "globals", source="packaged_sync")

        signature = _globals_signature(gph) or None
        if signature:
            packaged_meta["signature"] = signature
            packaged_meta["values"] = copy.deepcopy(gph)
            packaged_meta["leaf_values"] = {
                "/".join(path): copy.deepcopy(value) for path, value in curr_pairs.items()
            }
            packaged_meta["baseline_json"] = json.dumps(
                gph, sort_keys=True, separators=(",", ":")
            )
        else:
            packaged_meta.clear()
        try:
            _LOG.info(
                "hierarchical_variables.migration_complete",
                extra={
                    "seeded": bool(seeded_from_stub or seeded_from_legacy),
                },
            )
        except Exception:
            pass

    def _persist(self, payload: dict[str, Any]) -> bool:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(self._path)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            try:
                _LOG.error("hierarchical_variables.persist_failed", extra={"error": str(exc)})
            except Exception:
                pass
            return False

def _is_variable_hierarchy_enabled() -> bool:
    from ... import features

    return features.is_variable_hierarchy_enabled()


def is_variable_hierarchy_enabled() -> bool:
    """Expose feature flag helper for monkeypatch-heavy tests."""

    return _is_variable_hierarchy_enabled()


def bootstrap_hierarchical_globals() -> bool:
    """Ensure hierarchical storage exists and globals namespace is materialized."""

    try:
        store = HierarchicalVariableStore()
    except RuntimeError:
        return False
    try:
        store.export_namespace("globals")
        return True
    except Exception:
        return False
