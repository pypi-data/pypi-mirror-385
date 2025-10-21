"""Override and logging maintenance commands for CLI split out for size."""
from __future__ import annotations

import json
from typing import Iterable

from .. import logger
from ..variables import (
    reset_file_overrides,
    reset_single_file_override,
    list_file_overrides,
)
from ..variables.inventory import (
    VariableInventory,
    coerce_variable_value,
    parse_variable_path,
)


def clear_usage_log() -> None:
    logger.clear_usage_log()
    print("[prompt-automation] usage log cleared")


def clear_all_overrides() -> None:
    if reset_file_overrides():
        print("[prompt-automation] reference file overrides cleared")
    else:
        print("[prompt-automation] no overrides to clear")


def clear_one_override(tid: str, name: str) -> None:
    if not tid.isdigit():
        print("[prompt-automation] TEMPLATE_ID must be an integer")
        return
    removed = reset_single_file_override(int(tid), name)
    if removed:
        print(f"[prompt-automation] override removed for template {tid} placeholder '{name}'")
    else:
        print(f"[prompt-automation] no override found for template {tid} placeholder '{name}'")


def show_overrides() -> None:
    rows = list_file_overrides()
    if not rows:
        print("[prompt-automation] no overrides present")
    else:
        print("TemplateID | Placeholder | Data")
        for tid, name, info in rows:
            print(f"{tid:>9} | {name:<12} | {json.dumps(info)}")


def set_global_variable(path: str, value: str) -> bool:
    tokens = parse_variable_path(path)
    if not tokens:
        print("[prompt-automation] variable path is required (e.g. namespace.key)")
        return False
    inventory = VariableInventory()
    payload = coerce_variable_value(value)
    try:
        inventory.set_global(tokens, payload)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[prompt-automation] failed to update variable: {exc}")
        return False
    print(f"[prompt-automation] updated global variable {'.'.join(tokens)}")
    return True


def delete_global_variable(path: str) -> bool:
    tokens = parse_variable_path(path)
    if not tokens:
        print("[prompt-automation] variable path is required (e.g. namespace.key)")
        return False
    inventory = VariableInventory()
    try:
        removed = inventory.delete_global(tokens)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[prompt-automation] failed to delete variable: {exc}")
        return False
    if removed:
        print(f"[prompt-automation] deleted global variable {'.'.join(tokens)}")
    else:
        print(f"[prompt-automation] no global variable found for {'.'.join(tokens)}")
    return removed


__all__ = [
    "clear_usage_log",
    "clear_all_overrides",
    "clear_one_override",
    "show_overrides",
    "set_global_variable",
    "delete_global_variable",
]

