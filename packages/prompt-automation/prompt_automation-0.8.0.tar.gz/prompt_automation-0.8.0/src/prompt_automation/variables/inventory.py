"""Coordinated access to hierarchical and legacy global variable stores."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Sequence

from ..config import PROMPTS_DIR
from ..errorlog import get_logger
from .hierarchy.storage import HierarchicalVariableStore


_LOG = get_logger(__name__)


def parse_variable_path(dotted_path: str) -> tuple[str, ...]:
    """Normalize dotted or slash-separated paths into tokens."""

    cleaned = dotted_path.replace("\\", "/").replace(".", "/")
    parts = [segment.strip() for segment in cleaned.split("/") if segment.strip()]
    return tuple(parts)


def coerce_variable_value(value: Any) -> Any:
    """Best effort coercion mirroring GUI semantics."""

    if isinstance(value, str):
        candidate = value.strip()
        if candidate:
            if (candidate.startswith("{") and candidate.endswith("}")) or (
                candidate.startswith("[") and candidate.endswith("]")
            ):
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
            lowered = candidate.lower()
            if lowered in {"true", "false"}:
                return lowered == "true"
            if candidate.isdigit():
                try:
                    return int(candidate)
                except ValueError:
                    return value
        return value
    return value


class VariableInventory:
    """Synchronize hierarchical variables with legacy globals.json."""

    def __init__(
        self,
        store: HierarchicalVariableStore | None = None,
        *,
        prompts_dir: Path | None = None,
    ) -> None:
        self._store = store or HierarchicalVariableStore()
        self._prompts_dir = prompts_dir or PROMPTS_DIR
        self._legacy_path = (self._prompts_dir / "globals.json").resolve()

    # Public API ----------------------------------------------------------
    def set_global(self, path: Sequence[str], value: Any) -> None:
        """Persist ``value`` at ``path`` in both backends atomically."""

        if not path:
            raise ValueError("path must not be empty")

        # Ensure hierarchical payload is loaded before mutating legacy store.
        self._store.export_namespace("globals")

        legacy_before = self._load_legacy_payload()
        legacy_after = copy.deepcopy(legacy_before)
        gph = legacy_after.setdefault("global_placeholders", {})
        _set_nested(gph, path, copy.deepcopy(value))

        self._write_legacy_payload(legacy_after)

        try:
            self._store.set_value(
                "globals",
                path,
                value,
                source="inventory_set",
                propagate_errors=True,
            )
        except Exception:
            self._write_legacy_payload(legacy_before)
            raise

    def delete_global(self, path: Sequence[str]) -> bool:
        """Remove ``path`` from both backends, returning True if deleted."""

        if not path:
            return False

        # Ensure hierarchical payload is loaded before mutating legacy store.
        self._store.export_namespace("globals")

        legacy_before = self._load_legacy_payload()
        legacy_after = copy.deepcopy(legacy_before)
        gph = legacy_after.get("global_placeholders")
        if not isinstance(gph, dict):
            return False

        if not _delete_nested(gph, path):
            return False

        self._write_legacy_payload(legacy_after)

        removed = False
        try:
            removed = self._store.delete_value(
                "globals", path, source="inventory_delete", propagate_errors=True
            )
        except Exception:
            self._write_legacy_payload(legacy_before)
            raise

        if not removed:
            self._write_legacy_payload(legacy_before)
            return False

        return True

    # Internal helpers ----------------------------------------------------
    def _load_legacy_payload(self) -> dict[str, Any]:
        payload = {
            "schema": 1,
            "type": "globals",
            "global_placeholders": {},
            "notes": {},
        }
        if self._legacy_path.exists():
            try:
                loaded = json.loads(self._legacy_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    payload.update(loaded)
            except Exception as exc:  # pragma: no cover - defensive logging
                try:
                    _LOG.error("inventory.legacy_read_failed", extra={"error": str(exc)})
                except Exception:
                    pass
        gph = payload.get("global_placeholders")
        if not isinstance(gph, dict):
            payload["global_placeholders"] = {}
        return payload

    def _write_legacy_payload(self, payload: dict[str, Any]) -> None:
        try:
            self._legacy_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._legacy_path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(self._legacy_path)
        except Exception as exc:  # pragma: no cover - defensive logging
            try:
                _LOG.error("inventory.legacy_write_failed", extra={"error": str(exc)})
            except Exception:
                pass
            raise


def _set_nested(target: dict[str, Any], path: Sequence[str], value: Any) -> None:
    cursor: dict[str, Any] = target
    for key in path[:-1]:
        child = cursor.get(key)
        if not isinstance(child, dict):
            child = {}
            cursor[key] = child
        cursor = child
    cursor[path[-1]] = value


def _delete_nested(target: dict[str, Any], path: Sequence[str]) -> bool:
    cursor: dict[str, Any] = target
    trail: list[tuple[dict[str, Any], str]] = []
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            return False
        trail.append((cursor, key))
        cursor = cursor[key]
    parent, last = trail.pop()
    parent.pop(last, None)
    changed = True
    while trail:
        holder, key = trail.pop()
        node = holder.get(key)
        if isinstance(node, dict) and not node:
            holder.pop(key, None)
        else:
            break
    return changed


__all__ = [
    "VariableInventory",
    "coerce_variable_value",
    "parse_variable_path",
]

