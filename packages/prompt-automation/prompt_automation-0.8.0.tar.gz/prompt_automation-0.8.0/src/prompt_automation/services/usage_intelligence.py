"""Usage tracking helpers for ranking and autocomplete."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Dict, List

from ..errorlog import get_logger

_log = get_logger(__name__)


class UsageIntelligence:
    """In-memory usage model with lightweight exponential decay."""

    def __init__(self, decay: float = 0.9, clock=None) -> None:
        self._decay = float(decay)
        self._clock = clock or time.perf_counter
        self._template_scores: Dict[Path, float] = {}
        self._query_counts: Dict[str, int] = {}
        self._query_original: Dict[str, str] = {}
        self._last_decay = self._clock()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    def record_template_usage(self, path: Path, weight: float = 1.0) -> None:
        resolved = Path(path).resolve()
        with self._lock:
            self._maybe_decay()
            self._template_scores[resolved] = self._template_scores.get(
                resolved, 0.0
            ) + float(weight)
        try:
            _log.debug("%s", {"event": "usage.template", "path": str(resolved)})
        except Exception:  # pragma: no cover - logging safety
            pass

    def template_score(self, path: Path) -> float:
        resolved = Path(path).resolve()
        with self._lock:
            return float(self._template_scores.get(resolved, 0.0))

    # ------------------------------------------------------------------
    def record_search_query(self, query: str) -> None:
        cleaned = query.strip()
        if not cleaned:
            return
        lowered = cleaned.lower()
        with self._lock:
            self._maybe_decay()
            self._query_counts[lowered] = self._query_counts.get(lowered, 0) + 1
            self._query_original.setdefault(lowered, cleaned)
        try:
            _log.debug("%s", {"event": "usage.search_query", "query": lowered})
        except Exception:  # pragma: no cover
            pass

    def suggest_queries(self, prefix: str, limit: int = 5) -> List[str]:
        cleaned = prefix.strip().lower()
        if not cleaned:
            return []
        with self._lock:
            matches = [
                (count, key)
                for key, count in self._query_counts.items()
                if key.startswith(cleaned)
            ]
        matches.sort(key=lambda item: (-item[0], item[1]))
        suggestions = [self._query_original[key] for _, key in matches[:limit]]
        return suggestions

    # ------------------------------------------------------------------
    def _maybe_decay(self) -> None:
        now = self._clock()
        if now - self._last_decay < 300:
            return
        for path in list(self._template_scores.keys()):
            new_score = self._template_scores[path] * self._decay
            if new_score < 0.01:
                self._template_scores.pop(path, None)
            else:
                self._template_scores[path] = new_score
        for key in list(self._query_counts.keys()):
            new_count = int(self._query_counts[key] * self._decay)
            if new_count <= 0:
                self._query_counts.pop(key, None)
                self._query_original.pop(key, None)
            else:
                self._query_counts[key] = new_count
        self._last_decay = now


__all__ = ["UsageIntelligence"]
