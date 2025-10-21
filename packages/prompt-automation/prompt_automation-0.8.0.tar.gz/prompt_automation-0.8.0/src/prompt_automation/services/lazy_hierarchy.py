"""Lazy, cached hierarchy loader for prompt templates."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from ..config import PROMPTS_DIR
from ..errorlog import get_logger
from .cache.manager import TTLCache

_log = get_logger(__name__)


def _numeric_prefix(name: str) -> tuple[int, str]:
    import re

    m = re.match(r"^(\d+)_", name)
    if m:
        try:
            return int(m.group(1)), name
        except Exception:  # pragma: no cover - defensive
            pass
    return (10**9, name)


def _sort_key(node: "HierarchyNode") -> tuple[int, tuple[int, str]]:
    if node.type == "folder":
        return (0, (0, node.name.lower()))
    return (1, _numeric_prefix(node.name))


@dataclass(init=False)
class HierarchyNode:
    """Node returned by hierarchy scanners (supports lazy child loading)."""

    type: str
    name: str
    relpath: str
    _children: List["HierarchyNode"] = field(default_factory=list, repr=False)
    _loader: Optional[Callable[[], List["HierarchyNode"]]] = field(
        default=None, repr=False
    )
    _loaded: bool = field(default=True, repr=False)

    def __init__(
        self,
        type: str,
        name: str,
        relpath: str,
        children: Optional[List["HierarchyNode"]] = None,
        loader: Optional[Callable[[], List["HierarchyNode"]]] = None,
    ) -> None:
        object.__setattr__(self, "type", type)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "relpath", relpath)
        object.__setattr__(self, "_children", list(children or []))
        object.__setattr__(self, "_loader", loader)
        object.__setattr__(self, "_loaded", True)
        if type == "folder" and loader is not None and not children:
            object.__setattr__(self, "_loaded", False)
        if type != "folder":
            object.__setattr__(self, "_loader", None)

    def set_loader(self, loader: Optional[Callable[[], List["HierarchyNode"]]]) -> None:
        object.__setattr__(self, "_loader", loader)
        object.__setattr__(self, "_loaded", loader is None)

    def _ensure_loaded(self) -> None:
        if self.type != "folder" or self._loaded:
            return
        loader = self._loader
        if loader is None:
            object.__setattr__(self, "_loaded", True)
            object.__setattr__(self, "_children", [])
            return
        loaded = loader()
        object.__setattr__(self, "_children", list(loaded))
        object.__setattr__(self, "_loaded", True)

    @property
    def children(self) -> List["HierarchyNode"]:
        self._ensure_loaded()
        return self._children

    @children.setter
    def children(self, value: List["HierarchyNode"]) -> None:
        object.__setattr__(self, "_children", list(value))
        object.__setattr__(self, "_loaded", True)


class LazyHierarchyManager:
    """Expose filesystem hierarchy with on-demand directory expansion."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        ttl: float = 5.0,
        time_fn: Callable[[], float] | None = None,
    ) -> None:
        self.root = (root or PROMPTS_DIR).resolve()
        self._ttl = ttl
        self._clock = time_fn or time.perf_counter
        self._dir_cache: Dict[Path, TTLCache[List[HierarchyNode]]] = {}

    # ------------------------------------------------------------------
    def invalidate(self, relpath: Optional[Path] = None) -> None:
        if relpath is None:
            for cache in self._dir_cache.values():
                cache.invalidate()
            return
        rel = Path(relpath)
        cache = self._dir_cache.get(rel)
        if cache:
            cache.invalidate()

    # ------------------------------------------------------------------
    def get_root(self) -> HierarchyNode:
        return HierarchyNode(
            type="folder",
            name="",
            relpath="",
            loader=lambda: self._load_children(self.root, Path("")),
        )

    # ------------------------------------------------------------------
    def _cache_for(self, rel: Path) -> TTLCache[List[HierarchyNode]]:
        cache = self._dir_cache.get(rel)
        if cache is None:
            label = rel.as_posix() or "/"
            cache = TTLCache[List[HierarchyNode]](
                ttl=self._ttl, name=f"hierarchy:{label}", clock=self._clock
            )
            self._dir_cache[rel] = cache
        return cache

    def _directory_has_visible_children(self, path: Path) -> bool:
        try:
            with os.scandir(path) as it:
                for child in it:
                    if child.name.startswith("."):
                        continue
                    if child.is_symlink():
                        continue
                    if child.is_file() and child.name.endswith(".json"):
                        if child.name.lower() == "settings.json":
                            continue
                        return True
                    if child.is_dir(follow_symlinks=False):
                        return True
        except FileNotFoundError:
            return False
        return False

    def _load_children(self, base: Path, rel: Path) -> List[HierarchyNode]:
        cache = self._cache_for(rel)
        cached = cache.get()
        if cached is not None:
            return list(cached)

        nodes: List[HierarchyNode] = []
        try:
            with os.scandir(base) as it:
                for entry in it:
                    try:
                        if entry.name.startswith("."):
                            continue
                        path = Path(entry.path)
                        try:
                            path.resolve().relative_to(self.root)
                        except ValueError:
                            continue
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            child_rel = rel / entry.name
                            node = HierarchyNode(
                                type="folder",
                                name=entry.name,
                                relpath=str(child_rel.as_posix()),
                                loader=lambda p=path, r=child_rel: self._load_children(
                                    p, r
                                ),
                            )
                            if (
                                entry.name == "Settings"
                                and not self._directory_has_visible_children(path)
                            ):
                                continue
                            nodes.append(node)
                        elif entry.is_file() and entry.name.endswith(".json"):
                            if (
                                entry.name.lower() == "settings.json"
                                and rel.name == "Settings"
                            ):
                                continue
                            node = HierarchyNode(
                                type="template",
                                name=entry.name,
                                relpath=str((rel / entry.name).as_posix()),
                                children=[],
                            )
                            nodes.append(node)
                    except Exception:
                        continue
        except FileNotFoundError:
            nodes = []
        nodes.sort(key=_sort_key)
        snapshot = list(nodes)
        cache.set(snapshot)
        try:
            _log.debug(
                "%s",
                {
                    "event": "lazy_hierarchy.dir_loaded",
                    "relpath": str(rel.as_posix()),
                    "count": len(nodes),
                },
            )
        except Exception:  # pragma: no cover - logging safety
            pass
        return list(snapshot)

    # ------------------------------------------------------------------
    def walk(self, node: HierarchyNode) -> Iterable[HierarchyNode]:
        yield node
        if node.type != "folder":
            return
        for child in node.children:
            yield from self.walk(child)


__all__ = ["HierarchyNode", "LazyHierarchyManager"]
