from __future__ import annotations

"""Helpers for building hierarchical list items for the selector UI.

Keeps UI module concise by encapsulating tree traversal and item shaping.
"""

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ... import config
from ...services.hierarchy import HierarchyNode
from ..visual_feedback import indicators as _indicators


def find_node_for(tree: HierarchyNode, rel: str) -> HierarchyNode:
    if not rel:
        return tree
    parts = [p for p in Path(rel).parts if p]
    node = tree
    for name in parts:
        found = None
        for ch in node.children:
            if ch.type == "folder" and ch.name == name:
                found = ch
                break
        if found is None:
            return node
        node = found
    return node


def build_browse_items(node: HierarchyNode, cwd_rel: str, expanded: set[str]) -> List[Tuple[str, Dict]]:
    """Return display rows (text, meta) for the current node.

    This now supports unlimited folder nesting. ``expanded`` contains
    canonicalised relative folder paths (posix) which control inline
    expansion in browse mode.
    """

    def _indent(level: int) -> str:
        return "  " * max(level, 0)

    def _canon(rel: Path | str) -> str:
        rel_path = rel if isinstance(rel, Path) else Path(rel)
        parts = [p for p in rel_path.parts if p]
        return "/".join(parts)

    def _expanded(rel: str) -> bool:
        if not rel:
            return False
        return _canon(rel) in expanded_norm

    def _folder_rows(folder: HierarchyNode, parent_rel: Path, depth: int) -> Iterable[Tuple[str, Dict]]:
        rel_path = parent_rel / folder.name if folder.name else parent_rel
        rel_canon = _canon(rel_path)
        label = _indicators.format_folder_label(folder.name or "", depth, _expanded(rel_canon))
        meta = {"type": "folder", "rel": rel_canon, "indent": depth}
        yield (label, meta)
        if not _expanded(rel_canon):
            return
        for child in folder.children:
            if child.type == "folder":
                yield from _folder_rows(child, rel_path, depth + 1)
        for child in folder.children:
            if child.type == "template":
                yield from _template_row(child, depth + 1)

    def _template_row(tmpl: HierarchyNode, depth: int) -> Iterable[Tuple[str, Dict]]:
        name = Path(tmpl.relpath).name
        meta = {
            "type": "template",
            "path": (config.PROMPTS_DIR / tmpl.relpath),
            "indent": depth,
        }
        yield (f"{_indent(depth)}{name}", meta)

    rows: List[Tuple[str, Dict]] = []
    expanded_norm = {_canon(rel) for rel in expanded}

    # Show folders first when browsing root-level view
    for child in node.children:
        if child.type == "folder":
            rows.extend(_folder_rows(child, Path(cwd_rel), 0))

    # Only show templates inline when cwd_rel is not root (navigated into folder)
    if cwd_rel:
        for child in node.children:
            if child.type == "template":
                rows.extend(_template_row(child, 0))

    return rows


def flatten_matches(paths: List[Path], query: str) -> List[Tuple[str, Dict]]:
    q = query.strip().lower()
    rows: List[Tuple[str, Dict]] = []
    if not q:
        return rows
    for p in paths:
        rel = p.relative_to(config.PROMPTS_DIR)
        if q in str(rel).lower():
            rows.append((str(rel), {"type": "template", "path": p, "indent": 0}))
    return rows


__all__ = ["find_node_for", "build_browse_items", "flatten_matches"]
