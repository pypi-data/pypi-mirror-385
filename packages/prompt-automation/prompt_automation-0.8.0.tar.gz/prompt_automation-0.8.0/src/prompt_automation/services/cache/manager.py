"""Lightweight in-memory caches shared across background services."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generic, Optional, TypeVar

from ...errorlog import get_logger

_log = get_logger(__name__)

T = TypeVar("T")


@dataclass
class CacheRecord(Generic[T]):
    value: Optional[T] = None
    signature: Optional[int] = None
    expires_at: float = 0.0


class TTLCache(Generic[T]):
    """Small wrapper that stores a single value with a TTL and signature guard."""

    def __init__(
        self,
        ttl: float = 5.0,
        clock: Callable[[], float] | None = None,
        name: str | None = None,
    ) -> None:
        self.ttl = float(ttl)
        self._clock = clock or time.perf_counter
        self._lock = threading.Lock()
        self._record: CacheRecord[T] = CacheRecord()
        self._name = name or "cache"

    def get(self, signature: Optional[int] = None) -> Optional[T]:
        now = self._clock()
        with self._lock:
            rec = self._record
            if rec.value is None:
                return None
            if rec.expires_at and now >= rec.expires_at:
                self._record = CacheRecord()
                return None
            if (
                signature is not None
                and rec.signature is not None
                and signature != rec.signature
            ):
                self._record = CacheRecord()
                return None
            return rec.value

    def set(self, value: T, signature: Optional[int] = None) -> None:
        with self._lock:
            expires = self._clock() + self.ttl if self.ttl > 0 else 0.0
            self._record = CacheRecord(
                value=value, signature=signature, expires_at=expires
            )
        try:
            _log.debug(
                "%s", {"event": "cache.set", "name": self._name, "signature": signature}
            )
        except Exception:  # pragma: no cover - defensive logging
            pass

    def invalidate(self) -> None:
        with self._lock:
            self._record = CacheRecord()
        try:
            _log.debug("%s", {"event": "cache.invalidate", "name": self._name})
        except Exception:  # pragma: no cover
            pass


def validate_cache_path(root: Path, candidate: Path) -> Path:
    """Ensure *candidate* resides within *root* (prevents traversal)."""

    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"{candidate} escapes cache root {root}") from exc
    return candidate


def ensure_cache_subdir(root: Path, *parts: str) -> Path:
    """Create and return a cache sub-directory under *root* with validation."""

    base = validate_cache_path(root, root)
    target = base.joinpath(*parts)
    validate_cache_path(base, target)
    target.mkdir(parents=True, exist_ok=True)
    return target


__all__ = ["TTLCache", "CacheRecord", "validate_cache_path", "ensure_cache_subdir"]
