from __future__ import annotations

"""Hierarchy scanner integrating the lazy loading manager."""

import time
from pathlib import Path
from typing import Callable, List, Optional

from ..config import PROMPTS_DIR
from ..errorlog import get_logger
from .cache.manager import TTLCache
from .lazy_hierarchy import HierarchyNode, LazyHierarchyManager

_log = get_logger(__name__)


class TemplateHierarchyScanner:
    def __init__(
        self,
        root: Path | None = None,
        cache_ttl: int = 5,
        time_fn: Callable[[], float] | None = None,
    ) -> None:
        self.root = (root or PROMPTS_DIR).resolve()
        self._manager = LazyHierarchyManager(self.root, ttl=cache_ttl)
        self._time = time_fn or time.perf_counter
        self._cache: TTLCache[HierarchyNode] = TTLCache(
            ttl=cache_ttl, clock=time.perf_counter, name="hierarchy:root"
        )

    def invalidate(self) -> None:
        self._manager.invalidate()
        self._cache.invalidate()

    def scan(self) -> HierarchyNode:
        cached = self._cache.get()
        if cached is not None:
            try:
                _log.debug("%s", {"event": "hierarchy.scan.cache_hit"})
            except Exception:  # pragma: no cover - defensive logging
                pass
            return cached
        start = self._time()
        root = self._manager.get_root()
        self._cache.set(root)
        folders, templates = self._count(root)
        duration = int((self._time() - start) * 1000)
        try:
            _log.info(
                "%s",
                {
                    "event": "hierarchy.scan.success",
                    "duration_ms": duration,
                    "folder_count": folders,
                    "template_count": templates,
                },
            )
        except Exception:  # pragma: no cover - defensive logging
            pass
        return root

    def _count(self, node: HierarchyNode) -> tuple[int, int]:
        folders = 0
        templates = 0
        for child in node.children:
            if child.type == "folder":
                folders += 1
                c_f, c_t = self._count(child)
                folders += c_f
                templates += c_t
            else:
                templates += 1
        return folders, templates

    def list_flat(self) -> List[Path]:
        results: List[Path] = []
        for p in self.root.rglob("*.json"):
            if p.name.lower() == "settings.json" and p.parent.name == "Settings":
                continue
            results.append(p)
        return sorted(results)

    def scan_filtered(self, pattern: str | None) -> HierarchyNode:
        tree = self.scan()
        if not pattern:
            return tree
        return filter_tree(tree, pattern)


def filter_tree(root: HierarchyNode, pattern: str) -> HierarchyNode:
    pat = pattern.lower()

    def _filter(node: HierarchyNode) -> Optional[HierarchyNode]:
        if node.type == "folder":
            kept: List[HierarchyNode] = []
            for ch in node.children:
                res = _filter(ch)
                if res is not None:
                    kept.append(res)
            if pat in node.name.lower():
                clone = HierarchyNode(
                    type=node.type,
                    name=node.name,
                    relpath=node.relpath,
                    children=list(node.children),
                )
                return clone
            if kept:
                return HierarchyNode(
                    type=node.type, name=node.name, relpath=node.relpath, children=kept
                )
            return None
        if pat in node.name.lower():
            return HierarchyNode(
                type=node.type,
                name=node.name,
                relpath=node.relpath,
                children=list(node.children),
            )
        return None

    filtered = _filter(root)
    if filtered is not None:
        return filtered
    return HierarchyNode(
        type="folder", name=root.name, relpath=root.relpath, children=[]
    )


__all__ = [
    "TemplateHierarchyScanner",
    "HierarchyNode",
    "LazyHierarchyManager",
    "filter_tree",
]
