"""SQLite-based persistent cache backend (Feature 24: Local Cache)."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

from prompt_automation.errorlog import get_logger

_log = get_logger(__name__)


class SQLiteCacheBackend:
    """L2 disk cache using SQLite with TTL and LRU eviction.
    
    This is a standalone implementation that can work independently
    or integrate with Feature 19 (Multi-Tier Caching) when available.
    
    Features:
    - TTL-based expiration
    - LRU eviction when size limit exceeded
    - Thread-safe operations
    - Corruption recovery (regenerate DB on error)
    - WAL mode for better concurrency
    """

    def __init__(
        self,
        cache_path: Path,
        max_size_mb: int = 100,
        ttl_seconds: int = 3600,
    ) -> None:
        """Initialize SQLite cache backend.
        
        Args:
            cache_path: Path to SQLite database file
            max_size_mb: Maximum cache size in MB (default 100MB)
            ttl_seconds: Default TTL in seconds (default 1 hour)
        """
        self.cache_path = Path(cache_path)
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        
        # Ensure directory exists
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema with WAL mode."""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                
                # Create cache table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        expires_at INTEGER,
                        last_accessed INTEGER,
                        size_bytes INTEGER
                    )
                """)
                
                # Create index for expiration queries
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON cache(expires_at)
                """)
                
                # Create index for LRU eviction
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_last_accessed 
                    ON cache(last_accessed)
                """)
                
                conn.commit()
                
        except sqlite3.Error as e:
            _log.error("cache_db_init_failed error=%s path=%s", e, self.cache_path)
            # Try to recover by deleting corrupted DB
            if self.cache_path.exists():
                try:
                    self.cache_path.unlink()
                    self._init_db()  # Retry
                except Exception as retry_err:
                    _log.error("cache_db_recovery_failed error=%s", retry_err)

    def read(self, key: str) -> Optional[Any]:
        """Read value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            try:
                with sqlite3.connect(self.cache_path) as conn:
                    now = int(time.time())
                    
                    cursor = conn.execute(
                        """
                        SELECT value, expires_at FROM cache 
                        WHERE key = ?
                        """,
                        (key,)
                    )
                    row = cursor.fetchone()
                    
                    if row is None:
                        return None
                    
                    value_json, expires_at = row
                    
                    # Check expiration
                    if expires_at and now >= expires_at:
                        # Delete expired entry
                        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                        conn.commit()
                        return None
                    
                    # Update last accessed time
                    conn.execute(
                        "UPDATE cache SET last_accessed = ? WHERE key = ?",
                        (now, key)
                    )
                    conn.commit()
                    
                    # Deserialize value
                    try:
                        return json.loads(value_json)
                    except json.JSONDecodeError:
                        return value_json  # Return raw if not JSON
                        
            except sqlite3.Error as e:
                _log.error("cache_read_failed key=%s error=%s", key, e)
                return None

    def write(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Write value to cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl_seconds: TTL in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
                now = int(time.time())
                expires_at = now + ttl if ttl > 0 else 0
                
                # Serialize value
                if isinstance(value, str):
                    value_json = value
                else:
                    value_json = json.dumps(value)
                
                size_bytes = len(value_json.encode('utf-8'))
                
                with sqlite3.connect(self.cache_path) as conn:
                    # UPSERT operation
                    conn.execute(
                        """
                        INSERT INTO cache (key, value, expires_at, last_accessed, size_bytes)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(key) DO UPDATE SET
                            value = excluded.value,
                            expires_at = excluded.expires_at,
                            last_accessed = excluded.last_accessed,
                            size_bytes = excluded.size_bytes
                        """,
                        (key, value_json, expires_at, now, size_bytes)
                    )
                    conn.commit()
                    
                # Check size and evict if needed
                self._evict_if_needed()
                
                return True
                
            except (sqlite3.Error, json.JSONEncodeError) as e:
                _log.error("cache_write_failed key=%s error=%s", key, e)
                return False

    def delete(self, key: str) -> bool:
        """Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        with self._lock:
            try:
                with sqlite3.connect(self.cache_path) as conn:
                    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    conn.commit()
                return True
            except sqlite3.Error as e:
                _log.error("cache_delete_failed key=%s error=%s", key, e)
                return False

    def prune_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            try:
                now = int(time.time())
                with sqlite3.connect(self.cache_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM cache WHERE expires_at > 0 AND expires_at <= ?",
                        (now,)
                    )
                    conn.commit()
                    return cursor.rowcount
            except sqlite3.Error as e:
                _log.error("cache_prune_failed error=%s", e)
                return 0

    def _evict_if_needed(self) -> None:
        """Evict old entries if cache size exceeds limit (LRU)."""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                # Get total cache size
                cursor = conn.execute("SELECT SUM(size_bytes) FROM cache")
                total_bytes = cursor.fetchone()[0] or 0
                max_bytes = self.max_size_mb * 1024 * 1024
                
                if total_bytes > max_bytes:
                    # Delete oldest accessed entries until under limit
                    bytes_to_free = total_bytes - max_bytes
                    cursor = conn.execute(
                        """
                        SELECT key, size_bytes FROM cache 
                        ORDER BY last_accessed ASC
                        """
                    )
                    
                    freed = 0
                    for key, size in cursor.fetchall():
                        if freed >= bytes_to_free:
                            break
                        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                        freed += size
                    
                    conn.commit()
                    _log.debug(
                        "cache_eviction bytes_freed=%d entries_evicted=%d",
                        freed, cursor.rowcount
                    )
                    
        except sqlite3.Error as e:
            _log.error("cache_eviction_failed error=%s", e)

    def clear(self) -> bool:
        """Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                with sqlite3.connect(self.cache_path) as conn:
                    conn.execute("DELETE FROM cache")
                    conn.commit()
                return True
            except sqlite3.Error as e:
                _log.error("cache_clear_failed error=%s", e)
                return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as entries,
                        SUM(size_bytes) as total_bytes,
                        MIN(last_accessed) as oldest_access,
                        MAX(last_accessed) as newest_access
                    FROM cache
                """)
                row = cursor.fetchone()
                
                return {
                    "entries": row[0] or 0,
                    "size_mb": (row[1] or 0) / (1024 * 1024),
                    "oldest_access": row[2] or 0,
                    "newest_access": row[3] or 0,
                    "max_size_mb": self.max_size_mb,
                }
        except sqlite3.Error as e:
            _log.error("cache_stats_failed error=%s", e)
            return {
                "entries": 0,
                "size_mb": 0.0,
                "error": str(e),
            }


__all__ = ["SQLiteCacheBackend"]
