"""
Template Management System - Core CRUD operations and SQLite coordination.

This module provides the main TemplateManager class for creating, reading,
updating, and deleting templates. Templates are stored as JSON files with
SQLite indexing for fast search.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class TemplateManager:
    """
    Manages template CRUD operations with dual storage.
    
    Templates are stored as:
    - JSON files (source of truth) in prompts_dir/style/template_id.json
    - SQLite metadata (for fast indexing/search) in db_path
    
    Args:
        prompts_dir: Directory containing template JSON files (default: config.PROMPTS_DIR)
        db_path: Path to SQLite database (default: ~/.prompt-automation/templates.db)
        auto_index: If True, automatically index templates in SearchEngine (default: True)
        auto_version: If True, automatically save versions on update (default: True)
    """
    
    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        db_path: Optional[Path] = None,
        auto_index: bool = True,
        auto_version: bool = True
    ):
        """Initialize TemplateManager with storage paths and hooks."""
        if prompts_dir is None:
            from ..config import PROMPTS_DIR
            self.prompts_dir = PROMPTS_DIR
        else:
            self.prompts_dir = Path(prompts_dir)
        
        if db_path is None:
            from ..platform_utils import get_app_home
            self.db_path = get_app_home() / "templates.db"
        else:
            self.db_path = Path(db_path)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self._init_db()
        
        # Initialize hooks (lazy-loaded to avoid circular imports)
        self._auto_index = auto_index
        self._auto_version = auto_version
        self._search_engine = None
        self._version_manager = None
    
    def _get_search_engine(self):
        """Lazy-load SearchEngine."""
        if self._search_engine is None and self._auto_index:
            from .search import SearchEngine
            self._search_engine = SearchEngine(self.conn)  # Pass connection, not path
        return self._search_engine
    
    def _get_version_manager(self):
        """Lazy-load VersionManager."""
        if self._version_manager is None and self._auto_version:
            from .versions import VersionManager
            self._version_manager = VersionManager(self.conn)  # Pass connection, not path
        return self._version_manager
    
    def _init_db(self):
        """Create templates metadata table."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                style TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        self.conn.commit()
    
    def _generate_id(self) -> int:
        """Generate next available template ID."""
        cursor = self.conn.execute("SELECT MAX(id) FROM templates")
        max_id = cursor.fetchone()[0]
        return (max_id or 10000) + 1
    
    def create(
        self,
        title: str,
        style: str,
        placeholders: List[Dict[str, str]],
        template: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create new template.
        
        Args:
            title: Template title
            style: Template style (LLM, NTSK, etc.)
            placeholders: List of placeholder dicts with 'name' and 'label'
            template: List of template content lines
            metadata: Optional additional metadata
        
        Returns:
            Template dict with generated ID
        """
        # Generate ID
        new_id = self._generate_id()
        
        # Build template dict
        template_data = {
            "id": new_id,
            "title": title,
            "style": style,
            "placeholders": placeholders,
            "template": template,
            "metadata": metadata or {}
        }
        
        # Add creation timestamp if not in metadata
        if "created" not in template_data["metadata"]:
            template_data["metadata"]["created"] = datetime.now().isoformat()
        
        # Save to JSON file
        style_dir = self.prompts_dir / style
        style_dir.mkdir(parents=True, exist_ok=True)
        json_file = style_dir / f"{new_id}.json"
        
        with open(json_file, "w") as f:
            json.dump(template_data, f, indent=2)
        
        # Index in SQLite
        self.conn.execute("""
            INSERT INTO templates (id, title, style, path, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            new_id,
            title,
            style,
            str(json_file),
            template_data["metadata"]["created"]
        ))
        self.conn.commit()
        
        # Auto-hook: Index in SearchEngine
        search = self._get_search_engine()
        if search:
            try:
                # Extract fields for search index
                description = template_data.get("description", "")
                content = " ".join(template_data.get("template", []))
                tags = template_data.get("metadata", {}).get("tags", [])
                search.index(new_id, title, description, content, tags)
            except Exception as e:
                # Log but don't fail (search is optional)
                from ..errorlog import get_logger
                get_logger(__name__).warning(f"Auto-index failed for {new_id}: {e}")
        
        return template_data
    
    def get(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID
        
        Returns:
            Template dict or None if not found
        """
        cursor = self.conn.execute(
            "SELECT path FROM templates WHERE id = ?",
            (template_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Load from JSON file (source of truth)
        json_file = Path(row["path"])
        if not json_file.exists():
            # File was deleted but still in DB - clean up
            self.conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            self.conn.commit()
            return None
        
        with open(json_file) as f:
            return json.load(f)
    
    def update(
        self,
        template_id: int,
        title: Optional[str] = None,
        style: Optional[str] = None,
        placeholders: Optional[List[Dict[str, str]]] = None,
        template: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing template.
        
        Args:
            template_id: Template ID to update
            title: New title (if provided)
            style: New style (if provided)
            placeholders: New placeholders (if provided)
            template: New template content (if provided)
            metadata: New metadata (if provided)
        
        Returns:
            True if updated, False if not found
        """
        # Get existing template
        existing = self.get(template_id)
        if not existing:
            return False
        
        # Auto-hook: Save version before update
        version_mgr = self._get_version_manager()
        if version_mgr:
            try:
                version_mgr.save(template_id, existing)
            except Exception as e:
                # Log but don't fail (versioning is optional)
                from ..errorlog import get_logger
                get_logger(__name__).warning(f"Auto-version failed for {template_id}: {e}")
        
        # Update fields
        if title is not None:
            existing["title"] = title
        if style is not None:
            existing["style"] = style
        if placeholders is not None:
            existing["placeholders"] = placeholders
        if template is not None:
            existing["template"] = template
        if metadata is not None:
            existing["metadata"].update(metadata)
        
        # Update timestamp
        existing["metadata"]["updated"] = datetime.now().isoformat()
        
        # Save to JSON
        cursor = self.conn.execute(
            "SELECT path FROM templates WHERE id = ?",
            (template_id,)
        )
        row = cursor.fetchone()
        json_file = Path(row["path"])
        
        with open(json_file, "w") as f:
            json.dump(existing, f, indent=2)
        
        # Update SQLite index
        self.conn.execute("""
            UPDATE templates 
            SET title = ?, style = ?, updated_at = ?
            WHERE id = ?
        """, (
            existing["title"],
            existing["style"],
            existing["metadata"]["updated"],
            template_id
        ))
        self.conn.commit()
        
        # Auto-hook: Update search index
        search = self._get_search_engine()
        if search:
            try:
                # Extract fields for search index
                description = existing.get("description", "")
                content = " ".join(existing.get("template", []))
                tags = existing.get("metadata", {}).get("tags", [])
                search.update(template_id, existing["title"], description, content, tags)
            except Exception as e:
                # Log but don't fail
                from ..errorlog import get_logger
                get_logger(__name__).warning(f"Auto-index update failed for {template_id}: {e}")
        
        return True
    
    def delete(self, template_id: int) -> bool:
        """
        Delete template.
        
        Args:
            template_id: Template ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        # Get path from DB
        cursor = self.conn.execute(
            "SELECT path FROM templates WHERE id = ?",
            (template_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Delete JSON file
        json_file = Path(row["path"])
        if json_file.exists():
            json_file.unlink()
        
        # Delete from SQLite
        self.conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        self.conn.commit()
        
        # Auto-hook: Delete from search index
        search = self._get_search_engine()
        if search:
            try:
                search.delete(template_id)
            except Exception as e:
                # Log but don't fail
                from ..errorlog import get_logger
                get_logger(__name__).warning(f"Auto-index delete failed for {template_id}: {e}")
        
        # Auto-hook: Delete all versions
        version_mgr = self._get_version_manager()
        if version_mgr:
            try:
                version_mgr.delete_all(template_id)
            except Exception as e:
                # Log but don't fail
                from ..errorlog import get_logger
                get_logger(__name__).warning(f"Auto-version delete failed for {template_id}: {e}")
        
        return True
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all templates.
        
        Returns:
            List of template dicts
        """
        cursor = self.conn.execute("SELECT id FROM templates ORDER BY title")
        template_ids = [row["id"] for row in cursor.fetchall()]
        
        templates = []
        for template_id in template_ids:
            template = self.get(template_id)
            if template:  # Skip if file was deleted
                templates.append(template)
        
        return templates
    
    def list_by_style(self, style: str) -> List[Dict[str, Any]]:
        """
        List templates by style.
        
        Args:
            style: Template style (LLM, NTSK, etc.)
        
        Returns:
            List of template dicts matching style
        """
        cursor = self.conn.execute(
            "SELECT id FROM templates WHERE style = ? ORDER BY title",
            (style,)
        )
        template_ids = [row["id"] for row in cursor.fetchall()]
        
        templates = []
        for template_id in template_ids:
            template = self.get(template_id)
            if template:
                templates.append(template)
        
        return templates
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
