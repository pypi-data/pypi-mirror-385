"""
SearchEngine - SQLite FTS5 full-text search for templates.

Provides fast full-text search across template title, description, content, and tags.
Uses SQLite FTS5 virtual table for optimal performance.
"""
import sqlite3
from typing import List, Optional


class SearchEngine:
    """
    Full-text search engine using SQLite FTS5.
    
    Indexes template metadata for fast search across:
    - Title
    - Description
    - Content
    - Tags
    
    Args:
        db_conn: SQLite database connection
    """
    
    def __init__(self, db_conn: sqlite3.Connection):
        """Initialize SearchEngine with database connection."""
        self.conn = db_conn
        self._init_fts()
    
    def _init_fts(self):
        """Create FTS5 virtual table for full-text search."""
        try:
            self.conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS templates_fts 
                USING fts5(title, description, content, tags)
            """)
            self.conn.commit()
            self.fts5_available = True
        except sqlite3.OperationalError:
            # FTS5 not available - will use fallback
            self.fts5_available = False
    
    def index(
        self,
        template_id: int,
        title: str,
        description: str,
        content: str,
        tags: List[str]
    ):
        """
        Add template to search index.
        
        Args:
            template_id: Template ID (used as rowid)
            title: Template title
            description: Template description
            content: Template content
            tags: List of tags
        """
        if not self.fts5_available:
            # Skip indexing if FTS5 not available
            return
        
        # Convert tags list to space-separated string
        tags_str = " ".join(tags) if isinstance(tags, list) else tags
        
        # Check if already indexed
        cursor = self.conn.execute(
            "SELECT rowid FROM templates_fts WHERE rowid = ?",
            (template_id,)
        )
        if cursor.fetchone():
            # Already indexed - update instead
            self.update(template_id, title, description, content, tags)
            return
        
        # Insert into FTS5 table
        self.conn.execute("""
            INSERT INTO templates_fts (rowid, title, description, content, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (template_id, title, description or "", content, tags_str))
        self.conn.commit()
    
    def update(
        self,
        template_id: int,
        title: str,
        description: str,
        content: str,
        tags: List[str]
    ):
        """
        Update indexed template.
        
        Args:
            template_id: Template ID
            title: New title
            description: New description
            content: New content
            tags: New tags
        """
        if not self.fts5_available:
            return
        
        tags_str = " ".join(tags) if isinstance(tags, list) else tags
        
        self.conn.execute("""
            UPDATE templates_fts 
            SET title = ?, description = ?, content = ?, tags = ?
            WHERE rowid = ?
        """, (title, description or "", content, tags_str, template_id))
        self.conn.commit()
    
    def delete(self, template_id: int):
        """
        Remove template from search index.
        
        Args:
            template_id: Template ID to remove
        """
        if not self.fts5_available:
            return
        
        self.conn.execute(
            "DELETE FROM templates_fts WHERE rowid = ?",
            (template_id,)
        )
        self.conn.commit()
    
    def search(self, query: str) -> List[int]:
        """
        Full-text search across all indexed fields.
        
        Args:
            query: Search query (supports FTS5 query syntax)
        
        Returns:
            List of template IDs ranked by relevance
        """
        if not query or not query.strip():
            return []
        
        if self.fts5_available:
            return self._search_fts5(query)
        else:
            return self._search_fallback(query)
    
    def _search_fts5(self, query: str) -> List[int]:
        """
        Search using FTS5 (fast).
        
        Args:
            query: Search query
        
        Returns:
            List of template IDs ranked by relevance
        """
        try:
            cursor = self.conn.execute("""
                SELECT rowid, rank 
                FROM templates_fts 
                WHERE templates_fts MATCH ?
                ORDER BY rank
            """, (query,))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Invalid FTS5 query - try fallback
            return self._search_fallback(query)
    
    def _search_fallback(self, query: str) -> List[int]:
        """
        Fallback search using LIKE (slower, for when FTS5 unavailable).
        
        Args:
            query: Search query
        
        Returns:
            List of template IDs
        """
        # Use templates table with LIKE queries
        pattern = f"%{query}%"
        cursor = self.conn.execute("""
            SELECT id FROM templates 
            WHERE title LIKE ? OR style LIKE ?
        """, (pattern, pattern))
        return [row[0] for row in cursor.fetchall()]
