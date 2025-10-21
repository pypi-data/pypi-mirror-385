"""Shared fuzzy search engine with in-memory indices."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ..config import PROMPTS_DIR
from ..errorlog import get_logger
from ..renderer import load_template, validate_template
from .cache.manager import TTLCache
from .usage_intelligence import UsageIntelligence

_log = get_logger(__name__)


@dataclass
class SearchDocument:
    path: Path
    relpath: str
    title: str
    blob: str
    data: dict


@dataclass
class SearchResult:
    path: Path
    relpath: str
    title: str
    score: float
    data: dict


class SearchEngine:
    """Index templates under a root folder and serve fuzzy search results."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        ttl: float = 30.0,
        time_fn=None,
        usage: UsageIntelligence | None = None,
    ) -> None:
        self.root = (root or PROMPTS_DIR).resolve()
        self._ttl = float(ttl)
        self._clock = time_fn or time.perf_counter
        self._index_cache: TTLCache[Dict[Path, SearchDocument]] = TTLCache(
            ttl=self._ttl, name="search:index", clock=self._clock
        )
        self._signature_cache: TTLCache[int] = TTLCache(
            ttl=self._ttl, name="search:sig", clock=self._clock
        )
        self.usage = usage or UsageIntelligence()

    # ------------------------------------------------------------------
    def invalidate(self) -> None:
        self._index_cache.invalidate()
        self._signature_cache.invalidate()

    # ------------------------------------------------------------------
    def search(self, query: str, *, limit: int | None = None) -> List[SearchResult]:
        tokens = _tokenize(query)
        if not tokens:
            return []
        index = self._ensure_index()
        matches: List[Tuple[float, SearchDocument]] = []
        for doc in index.values():
            score = _score_tokens(tokens, doc)
            if score == 0.0:
                continue
            score += self.usage.template_score(doc.path)
            matches.append((score, doc))
        matches.sort(key=lambda item: (-item[0], item[1].relpath))
        if limit is not None:
            matches = matches[:limit]
        results = [
            SearchResult(
                path=doc.path,
                relpath=doc.relpath,
                title=doc.title,
                score=score,
                data=doc.data,
            )
            for score, doc in matches
        ]
        try:
            _log.debug(
                "%s",
                {
                    "event": "search_engine.query",
                    "token_count": len(tokens),
                    "results": len(results),
                },
            )
        except Exception:  # pragma: no cover - logging safety
            pass
        return results

    # ------------------------------------------------------------------
    def autocomplete(self, prefix: str, *, limit: int = 5) -> List[str]:
        cleaned = prefix.strip().lower()
        if not cleaned:
            return []
        suggestions: List[str] = []
        seen: set[str] = set()
        for suggestion in self.usage.suggest_queries(cleaned, limit=limit):
            if suggestion.lower() in seen:
                continue
            suggestions.append(suggestion)
            seen.add(suggestion.lower())
            if len(suggestions) >= limit:
                return suggestions
        index = self._ensure_index()
        for doc in index.values():
            for candidate in (doc.title, doc.relpath):
                lower = candidate.lower()
                if not lower.startswith(cleaned):
                    continue
                if lower in seen:
                    continue
                suggestions.append(candidate)
                seen.add(lower)
                if len(suggestions) >= limit:
                    return suggestions
        return suggestions

    # ------------------------------------------------------------------
    def _ensure_index(self) -> Dict[Path, SearchDocument]:
        signature = self._build_signature()
        cached_sig = self._signature_cache.get()
        cached_index = self._index_cache.get(
            signature if cached_sig == signature else None
        )
        if cached_index is not None and cached_sig == signature:
            return cached_index
        index = self._build_index()
        self._index_cache.set(index, signature)
        self._signature_cache.set(signature, signature)
        return index

    def _build_signature(self) -> int:
        sig = 0
        for path in self.root.rglob("*.json"):
            if path.name.lower() == "settings.json" and path.parent.name == "Settings":
                continue
            try:
                stat = path.stat()
            except FileNotFoundError:
                continue
            sig ^= int(stat.st_mtime_ns) & 0xFFFFFFFF
        return sig

    def _build_index(self) -> Dict[Path, SearchDocument]:
        index: Dict[Path, SearchDocument] = {}
        for path in sorted(self.root.rglob("*.json")):
            if path.name.lower() == "settings.json" and path.parent.name == "Settings":
                continue
            try:
                data = load_template(path)
            except Exception:
                continue
            if not validate_template(data):
                continue
            relpath = path.relative_to(self.root).as_posix()
            title = str(data.get("title", ""))
            placeholders = _extract_placeholder_names(data)
            body = _extract_body_lines(data)
            blob = " \n".join(
                [
                    relpath.lower(),
                    title.lower(),
                    "\n".join(body).lower(),
                    " ".join(placeholders).lower(),
                ]
            )
            index[path.resolve()] = SearchDocument(
                path=path.resolve(),
                relpath=relpath,
                title=title or path.stem,
                blob=blob,
                data=data,
            )
        try:
            _log.info(
                "%s",
                {
                    "event": "search_engine.index_built",
                    "template_count": len(index),
                },
            )
        except Exception:  # pragma: no cover
            pass
        return index


# ----------------------------------------------------------------------


def _tokenize(query: str) -> List[str]:
    return [part.lower() for part in query.split() if part.strip()]


def _score_tokens(tokens: Iterable[str], doc: SearchDocument) -> float:
    total = 0.0
    for token in tokens:
        score = _score_token(token, doc)
        if score == 0.0:
            continue
        total += score
    return total


def _score_token(token: str, doc: SearchDocument) -> float:
    text = doc.blob
    if not text:
        return 0.0
    if token in text:
        base = 1.0
    else:
        base = _subsequence_score(token, text)
        if base == 0.0:
            return 0.0
    if doc.relpath.lower().startswith(token):
        base += 0.5
    if doc.title.lower().startswith(token):
        base += 0.5
    return base


def _subsequence_score(token: str, text: str) -> float:
    pos = 0
    hits = 0
    for ch in token:
        idx = text.find(ch, pos)
        if idx == -1:
            return 0.0
        hits += 1
        pos = idx + 1
    return max(0.3, hits / max(len(token), 1))


def _extract_placeholder_names(data: dict) -> List[str]:
    holders = data.get("placeholders", [])
    if not isinstance(holders, list):
        return []
    names = []
    for item in holders:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            if name:
                names.append(name)
    return names


def _extract_body_lines(data: dict) -> List[str]:
    body = data.get("template")
    if isinstance(body, list):
        return [str(line) for line in body]
    if isinstance(body, str):
        return [body]
    return []


__all__ = ["SearchEngine", "SearchResult", "SearchDocument"]
