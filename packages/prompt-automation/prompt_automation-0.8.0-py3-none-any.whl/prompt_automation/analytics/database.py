"""SQLite database for analytics storage."""
from __future__ import annotations

import gzip
import json
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Any

from ..config import HOME_DIR
from ..errorlog import get_logger

_log = get_logger(__name__)


class Database:
    """SQLite database for analytics storage.
    
    Features:
    - WAL mode for better concurrency
    - Auto-rotation at max size (default 100MB)
    - Automatic backups with compression
    - Keeps last 30 days of data
    """
    
    def __init__(
        self,
        db_path: Path | None = None,
        max_size_mb: int = 100
    ):
        """Initialize database.
        
        Args:
            db_path: Path to database file (default: ~/.prompt-automation/analytics.db)
            max_size_mb: Maximum database size before rotation (default: 100MB)
        """
        if db_path is None:
            db_path = HOME_DIR / "analytics.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.max_size_mb = max_size_mb
        self.conn = None
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        
        # Enable WAL mode (better concurrency)
        self.conn.execute("PRAGMA journal_mode=WAL")
        
        # Create schema
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                data TEXT NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
            
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self.conn.commit()
    
    def insert_event(self, event: dict[str, Any]):
        """Insert event into database.
        
        Args:
            event: Event dict with event_type, timestamp, and data keys
        """
        if not self.conn:
            _log.warning("Database connection closed, skipping event insert")
            return
            
        self.conn.execute(
            "INSERT INTO events (event_type, timestamp, data) VALUES (?, ?, ?)",
            (event["event_type"], event["timestamp"], event["data"])
        )
        self.conn.commit()
        
        # Check if rotation needed (with some buffer to avoid frequent rotations)
        if self.size_mb() > self.max_size_mb * 1.1:
            self.rotate()
    
    def query(self, sql: str, params: tuple | None = None) -> list[tuple]:
        """Execute SQL query.
        
        Args:
            sql: SQL query string
            params: Optional query parameters
            
        Returns:
            List of result tuples
        """
        if not self.conn:
            _log.warning("Database connection closed, returning empty results")
            return []
            
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def size_mb(self) -> float:
        """Get database size in MB.
        
        Includes main DB file plus WAL and SHM files when in WAL mode.
        
        Returns:
            Database size in megabytes
        """
        if not self.db_path.exists():
            return 0.0
        
        total_size = self.db_path.stat().st_size
        
        # Include WAL file if it exists (Write-Ahead Log)
        wal_path = Path(str(self.db_path) + "-wal")
        if wal_path.exists():
            total_size += wal_path.stat().st_size
        
        # Include SHM file if it exists (Shared Memory)
        shm_path = Path(str(self.db_path) + "-shm")
        if shm_path.exists():
            total_size += shm_path.stat().st_size
        
        return total_size / (1024 * 1024)
    
    def rotate(self):
        """Archive old data and rotate database.
        
        Creates compressed backup and deletes data older than 30 days.
        """
        try:
            # Create backup directory
            backup_dir = self.db_path.parent / "analytics-backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Archive current DB
            timestamp = time.strftime("%Y-%m-%d-%H%M%S")
            archive_path = backup_dir / f"analytics-{timestamp}.db"
            
            # Copy DB
            shutil.copy2(self.db_path, archive_path)
            
            # Compress
            with open(archive_path, 'rb') as f_in:
                with gzip.open(f"{archive_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Delete uncompressed backup
            archive_path.unlink()
            
            # Delete old data from main DB (keep last 30 days)
            cutoff = int(time.time()) - (30 * 24 * 60 * 60)
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,))
            self.conn.commit()
            
            # Close connection before VACUUM
            self.conn.close()
            
            # Vacuum to reclaim space (needs fresh connection)
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("VACUUM")
            conn.close()
            
            # Reopen connection
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            
            # Update metadata
            self.set_metadata("last_rotation", str(int(time.time())))
            
            _log.info(f"Database rotated: {self.size_mb():.2f} MB after rotation")
            
        except Exception as e:
            _log.error(f"Database rotation failed: {e}")
    
    def set_metadata(self, key: str, value: str):
        """Set metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if not self.conn:
            return
            
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()
    
    def get_metadata(self, key: str) -> str | None:
        """Get metadata value.
        
        Args:
            key: Metadata key
            
        Returns:
            Metadata value or None if not found
        """
        if not self.conn:
            return None
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
