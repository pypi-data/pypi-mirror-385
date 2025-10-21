"""Utilities for syncing packaged globals from the authoritative inventory."""

import copy
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any, Mapping

_AUTHORITATIVE_FILENAME = "_authoritative_globals.json"


def _repository_root(root: Path | None) -> Path:
    return Path(root) if root is not None else Path(__file__).resolve().parents[3]


def _authoritative_path(root: Path | None) -> Path:
    base = _repository_root(root)
    return (
        base
        / "src"
        / "prompt_automation"
        / "variables"
        / _AUTHORITATIVE_FILENAME
    )


def _load_authoritative_payload(root: Path | None) -> Mapping[str, Any]:
    path = _authoritative_path(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError(
            f"Authoritative globals payload must be a mapping (file: {path})"
        )
    return data


def _build_globals_payload(data: Mapping[str, Any]) -> OrderedDict[str, Any]:
    placeholders: OrderedDict[str, Any] = OrderedDict()
    notes: OrderedDict[str, Any] = OrderedDict()

    for entry in data.get("globals", []):
        if not isinstance(entry, Mapping):
            continue
        key = entry.get("key")
        if not isinstance(key, str) or not key:
            continue
        placeholders[key] = copy.deepcopy(entry.get("value"))
        note = entry.get("notes")
        if isinstance(note, str) and note:
            notes[key] = note

    payload: OrderedDict[str, Any] = OrderedDict()
    payload["schema"] = data.get("schema", 1)
    payload["type"] = "globals"
    payload["global_placeholders"] = placeholders
    if notes:
        payload["notes"] = notes
    if "version" in data:
        payload["version"] = data["version"]
    metadata = data.get("metadata")
    if isinstance(metadata, Mapping) and metadata:
        payload["metadata"] = copy.deepcopy(metadata)
    return payload


def _build_stub_payload(data: Mapping[str, Any]) -> OrderedDict[str, Any]:
    payload: OrderedDict[str, Any] = OrderedDict()
    espanso = data.get("espanso")
    if isinstance(espanso, Mapping):
        payload["__espanso__"] = copy.deepcopy(espanso)
    for entry in data.get("globals", []):
        if not isinstance(entry, Mapping):
            continue
        if not entry.get("include_in_stub"):
            continue
        key = entry.get("key")
        if not isinstance(key, str) or not key:
            continue
        payload[key] = copy.deepcopy(entry.get("value"))
    return payload


def _write_json(target: Path, payload: Mapping[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    try:
        existing = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    if existing == text:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return True


def sync_authoritative_globals(root: Path | None = None) -> dict[str, bool]:
    """Synchronize packaged globals and stub payload with the inventory definition."""

    repo_root = _repository_root(root)
    data = _load_authoritative_payload(root)

    globals_path = (
        repo_root / "src" / "prompt_automation" / "prompts" / "styles" / "globals.json"
    )
    stub_path = (
        repo_root
        / "src"
        / "prompt_automation"
        / "variables"
        / "hierarchy"
        / "_stub_payload.json"
    )

    globals_payload = _build_globals_payload(data)
    stub_payload = _build_stub_payload(data)

    changed_globals = _write_json(globals_path, globals_payload)
    changed_stub = _write_json(stub_path, stub_payload)

    return {"globals": changed_globals, "stub": changed_stub}


__all__ = ["sync_authoritative_globals"]
