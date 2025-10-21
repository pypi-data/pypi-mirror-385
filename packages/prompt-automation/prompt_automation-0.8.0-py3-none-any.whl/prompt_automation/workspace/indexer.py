"""Workspace indexer for fast context lookup.

Builds and maintains an index of workspace files with metadata:
- Python: Functions, classes, imports (AST-based)
- JSON: Top-level keys
- Markdown: Headers

Example:
    >>> from prompt_automation.workspace.indexer import WorkspaceIndexer
    >>> indexer = WorkspaceIndexer(Path.cwd())
    >>> index = indexer.build_index()
    >>> print(f"Indexed {len(index['files'])} files")
"""
from __future__ import annotations

import ast
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Exclude patterns (similar to .gitignore)
EXCLUDE_PATTERNS = [
    "venv", "env", ".venv", ".env",
    "node_modules", "__pycache__", ".git",
    ".pytest_cache", ".mypy_cache", ".tox",
    "build", "dist", "*.egg-info",
]


class WorkspaceIndexer:
    """Builds and maintains workspace index for fast context lookup."""

    def __init__(self, workspace_root: Path):
        """
        Initialize indexer for a workspace.
        
        Args:
            workspace_root: Root directory of the workspace to index
        """
        self.workspace_root = workspace_root
        self.index_file = workspace_root / ".prompt-automation-index.json"

    def build_index(self) -> Dict[str, Any]:
        """
        Build complete index from scratch.
        
        Returns:
            Dictionary with index metadata and file information
        """
        index = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "workspace_root": str(self.workspace_root),
            "files": {},
        }
        
        # Index Python files
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_exclude(py_file):
                continue
            try:
                file_info = self._index_python_file(py_file)
                index["files"][str(py_file.relative_to(self.workspace_root))] = file_info
            except Exception as e:
                logger.debug(f"Failed to index {py_file}: {e}")
        
        # Index JSON files
        for json_file in self.workspace_root.rglob("*.json"):
            if self._should_exclude(json_file):
                continue
            try:
                file_info = self._index_json_file(json_file)
                index["files"][str(json_file.relative_to(self.workspace_root))] = file_info
            except Exception as e:
                logger.debug(f"Failed to index {json_file}: {e}")
        
        # Index Markdown files
        for md_file in self.workspace_root.rglob("*.md"):
            if self._should_exclude(md_file):
                continue
            try:
                file_info = self._index_markdown_file(md_file)
                index["files"][str(md_file.relative_to(self.workspace_root))] = file_info
            except Exception as e:
                logger.debug(f"Failed to index {md_file}: {e}")
        
        return index

    def load_index(self) -> Dict[str, Any]:
        """
        Load existing index from disk.
        
        Returns:
            Index dictionary, or empty dict if file doesn't exist or is corrupted
        """
        if not self.index_file.exists():
            return {}
        
        try:
            return json.loads(self.index_file.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load index from {self.index_file}: {e}")
            return {}

    def save_index(self, index: Dict[str, Any]) -> None:
        """
        Save index to disk.
        
        Args:
            index: Index dictionary to save
        """
        try:
            self.index_file.write_text(json.dumps(index, indent=2))
        except OSError as e:
            logger.error(f"Failed to save index to {self.index_file}: {e}")

    def is_stale(self) -> bool:
        """
        Check if index needs rebuilding.
        
        Returns:
            True if >10% of indexed files have changed
        """
        index = self.load_index()
        if not index or "files" not in index:
            return True
        
        indexed_files = index["files"]
        if not indexed_files:
            return True
        
        changed_count = 0
        for rel_path, file_info in indexed_files.items():
            abs_path = self.workspace_root / rel_path
            if not abs_path.exists():
                changed_count += 1
                continue
            
            # Check modification time
            if "modified" in file_info:
                current_mtime = abs_path.stat().st_mtime
                if current_mtime != file_info["modified"]:
                    changed_count += 1
        
        change_percentage = (changed_count / len(indexed_files)) * 100
        return change_percentage > 10

    def _index_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract functions, classes, imports from Python file using AST.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary with file metadata
        """
        content = file_path.read_text(errors="ignore")
        stat = file_path.stat()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # File has syntax errors, still return basic info
            return {
                "type": "python",
                "size": stat.st_size,
                "loc": len(content.splitlines()),
                "modified": stat.st_mtime,
                "error": "syntax_error",
            }
        
        functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        
        classes = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return {
            "type": "python",
            "size": stat.st_size,
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "loc": len(content.splitlines()),
            "modified": stat.st_mtime,
        }

    def _index_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract top-level keys from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with file metadata
        """
        content = file_path.read_text(errors="ignore")
        stat = file_path.stat()
        
        try:
            data = json.loads(content)
            keys = list(data.keys()) if isinstance(data, dict) else []
        except json.JSONDecodeError:
            keys = []
        
        return {
            "type": "json",
            "size": stat.st_size,
            "keys": keys,
            "loc": len(content.splitlines()),
            "modified": stat.st_mtime,
        }

    def _index_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract headers from Markdown file.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            Dictionary with file metadata
        """
        content = file_path.read_text(errors="ignore")
        stat = file_path.stat()
        
        # Extract headers (lines starting with #)
        headers = []
        for line in content.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                headers.append(match.group(2).strip())
        
        return {
            "type": "markdown",
            "size": stat.st_size,
            "headers": headers,
            "loc": len(content.splitlines()),
            "modified": stat.st_mtime,
        }

    def _should_exclude(self, file_path: Path) -> bool:
        """
        Check if file should be excluded from indexing.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be excluded
        """
        # Exclude hidden files/directories
        parts = file_path.relative_to(self.workspace_root).parts
        if any(part.startswith(".") for part in parts):
            return True
        
        # Exclude pattern matches (check parts, not full path)
        for part in parts:
            for pattern in EXCLUDE_PATTERNS:
                if pattern == part or (pattern.endswith("*") and part.startswith(pattern[:-1])):
                    return True
        
        return False
