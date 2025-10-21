from __future__ import annotations

"""Backward-compatible wrappers over :mod:`validation.error_recovery`."""

from typing import Iterable, Set

from ...validation.error_recovery import SelectorStateStore

_STORE = SelectorStateStore()


def load_expanded() -> Set[str]:
    return set(_STORE.load().expanded)


def save_expanded(paths: Iterable[str]) -> None:
    _STORE.update(expanded=paths)


__all__ = ["load_expanded", "save_expanded"]
