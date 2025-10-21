"""
VersionManager - Version control and rollback for templates.

Maintains version history for templates with automatic cleanup (max 10 versions).
Allows rollback to previous versions.
"""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any


class VersionManager:
    """
    Manages template version history.
    
    Features:
    - Save version snapshots
    - List version history
    - Rollback to previous versions
    - Automatic cleanup (max 10 versions per template)
    
    Args:
        db_conn: SQLite database connection
        version_limit: Maximum versions to retain per template (default: 10)
    """
    
    def __init__(self, db_conn: sqlite3.Connection, version_limit: int = 10):
        """Initialize VersionManager with database connection."""
        self.conn = db_conn
        self.conn.row_factory = sqlite3.Row
        self.version_limit = version_limit
        self._init_db()
    
    def _init_db(self):
        """Create template_versions table."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS template_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()
    
    def save(self, template_id: int, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save version snapshot.
        
        Args:
            template_id: Template ID
            template_data: Complete template dict to snapshot
        
        Returns:
            Version info dict with version number and template_id
        """
        # Get next version number
        cursor = self.conn.execute("""
            SELECT MAX(version) FROM template_versions 
            WHERE template_id = ?
        """, (template_id,))
        row = cursor.fetchone()
        max_version = row[0] if row[0] is not None else 0
        next_version = max_version + 1
        
        # Save snapshot
        self.conn.execute("""
            INSERT INTO template_versions (template_id, version, data, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            template_id,
            next_version,
            json.dumps(template_data),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        
        # Enforce version limit
        self._enforce_limit(template_id)
        
        return {
            "version": next_version,
            "template_id": template_id
        }
    
    def list(self, template_id: int) -> List[Dict[str, Any]]:
        """
        List version history for a template.
        
        Args:
            template_id: Template ID
        
        Returns:
            List of version dicts (most recent first)
        """
        cursor = self.conn.execute("""
            SELECT version, created_at, data 
            FROM template_versions 
            WHERE template_id = ?
            ORDER BY version DESC
        """, (template_id,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                "version": row["version"],
                "created_at": row["created_at"],
                "data": json.loads(row["data"])
            })
        
        return versions
    
    def rollback(self, template_id: int, version: int) -> Optional[Dict[str, Any]]:
        """
        Restore old version.
        
        Args:
            template_id: Template ID
            version: Version number to restore
        
        Returns:
            Template data from that version, or None if not found
        """
        cursor = self.conn.execute("""
            SELECT data FROM template_versions 
            WHERE template_id = ? AND version = ?
        """, (template_id, version))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return json.loads(row["data"])
    
    def delete_all(self, template_id: int):
        """
        Delete all versions for a template.
        
        Args:
            template_id: Template ID
        """
        self.conn.execute("""
            DELETE FROM template_versions 
            WHERE template_id = ?
        """, (template_id,))
        self.conn.commit()
    
    def _enforce_limit(self, template_id: int):
        """
        Enforce version limit (keep only N most recent versions).
        
        Args:
            template_id: Template ID
        """
        self.conn.execute("""
            DELETE FROM template_versions 
            WHERE template_id = ? AND version NOT IN (
                SELECT version FROM template_versions 
                WHERE template_id = ?
                ORDER BY version DESC LIMIT ?
            )
        """, (template_id, template_id, self.version_limit))
        self.conn.commit()
    
    def get_version_count(self, template_id: int) -> int:
        """
        Get count of versions for a template.
        
        Args:
            template_id: Template ID
        
        Returns:
            Number of versions stored
        """
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM template_versions 
            WHERE template_id = ?
        """, (template_id,))
        return cursor.fetchone()[0]
