"""Data model helpers for template browsing."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from ...menus import PROMPTS_DIR
from ...renderer import validate_template, load_template
from ...services.search_engine import SearchEngine


@dataclass
class TemplateEntry:
    path: Path
    data: Dict[str, Any]


@dataclass
class ListingItem:
    type: str  # 'dir' | 'template' | 'up' | 'empty'
    path: Optional[Path] = None
    template: Optional[TemplateEntry] = None
    display: str = ""


class BrowserState:
    def __init__(self, root: Path):
        self.root = root
        self.current = root
        self.items: List[ListingItem] = []
        self._search_engine = SearchEngine(root)

    def build(self) -> None:
        self.items.clear()
        # First collect dirs and templates
        for child in sorted([p for p in self.current.iterdir() if p.is_dir()]):
            if child.name.lower() == "settings":
                continue
            self.items.append(
                ListingItem(type="dir", path=child, display=child.name + "/")
            )
        for child in sorted(
            [
                p
                for p in self.current.iterdir()
                if p.is_file() and p.suffix.lower() == ".json"
            ]
        ):
            if child.name.lower() == "settings.json":
                continue
            try:
                data = load_template(child)
                if not validate_template(data):
                    continue
                self.items.append(
                    ListingItem(
                        type="template",
                        path=child,
                        template=TemplateEntry(child, data),
                        display=child.name,
                    )
                )
            except Exception:
                continue
        # Append navigation 'up' control at the bottom (requested UX)
        if self.current != self.root:
            self.items.append(ListingItem(type="up", display="[..]"))
        if not self.items:
            self.items.append(ListingItem(type="empty", display="<empty>"))

    def enter(self, item: ListingItem) -> Optional[TemplateEntry]:
        if item.type == "up":
            self.current = (
                self.current.parent if self.current != self.root else self.root
            )
            self.build()
            return None
        if item.type == "dir" and item.path:
            self.current = item.path
            self.build()
            return None
        if item.type == "template" and item.template:
            try:
                self._search_engine.usage.record_template_usage(item.path)
            except Exception:
                pass
            return item.template
        return None

    def breadcrumb(self) -> str:
        if self.current == self.root:
            return str(self.root)
        return f"{self.root.name}/{self.current.relative_to(self.root)}"

    def filter(self, query: str) -> List[ListingItem]:
        if not query:
            return self.items
        q = query.lower()
        return [
            it
            for it in self.items
            if it.display.lower().find(q) != -1
            or (it.template and str(it.path).lower().find(q) != -1)
        ]

    def search(self, query: str) -> List[ListingItem]:
        """Recursive search across all templates (path, title, placeholders, body).

        Implements simple AND token matching: all whitespace-separated tokens
        must appear (case-insensitive) somewhere in the aggregated text blob.
        """
        q = query.strip()
        if not q:
            return []
        try:
            self._search_engine.usage.record_search_query(q)
        except Exception:
            pass
        matches = self._search_engine.search(q)
        listing: List[ListingItem] = []
        for match in matches:
            entry = TemplateEntry(match.path, match.data)
            listing.append(
                ListingItem(
                    type="template",
                    path=match.path,
                    template=entry,
                    display=match.relpath,
                )
            )
        return listing

    def autocomplete(self, query: str, limit: int = 5) -> List[str]:
        return self._search_engine.autocomplete(query, limit=limit)


def create_browser_state() -> BrowserState:
    return BrowserState(PROMPTS_DIR)


__all__ = ["TemplateEntry", "ListingItem", "BrowserState", "create_browser_state"]
