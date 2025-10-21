"""Common queries for analytics data."""
from __future__ import annotations

import json
import time
from typing import Any

from .database import Database
from ..errorlog import get_logger

_log = get_logger(__name__)


class Queries:
    """Common queries for analytics data.
    
    Provides high-level query methods for:
    - Top templates
    - Cache hit rates
    - Error frequency
    - Resource usage trends
    - Latency percentiles
    """
    
    def __init__(self, db: Database):
        """Initialize queries.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def get_top_templates(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> list[dict[str, Any]]:
        """Get top templates by usage count.
        
        Args:
            limit: Maximum number of templates to return
            hours: Time window in hours (default: 24)
            
        Returns:
            List of dicts with template_id, count, avg_duration_ms
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        sql = """
            SELECT 
                json_extract(data, '$.template_id') as template_id,
                COUNT(*) as count,
                AVG(json_extract(data, '$.duration_ms')) as avg_duration_ms
            FROM events
            WHERE event_type = 'template_render'
              AND timestamp > ?
            GROUP BY template_id
            ORDER BY count DESC
            LIMIT ?
        """
        
        rows = self.db.query(sql, (cutoff, limit))
        
        return [
            {
                "template_id": row[0],
                "count": row[1],
                "avg_duration_ms": row[2]
            }
            for row in rows
        ]
    
    def get_cache_hit_rate(self, hours: int = 24) -> float:
        """Get cache hit rate across all cacheable events.
        
        Args:
            hours: Time window in hours (default: 24)
            
        Returns:
            Cache hit rate as float (0.0 to 1.0)
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        sql = """
            SELECT 
                SUM(CASE WHEN json_extract(data, '$.cache_hit') = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as hit_rate
            FROM events
            WHERE event_type IN ('llm_call', 'template_render', 'mcp_call')
              AND timestamp > ?
        """
        
        rows = self.db.query(sql, (cutoff,))
        return rows[0][0] if rows and rows[0][0] is not None else 0.0
    
    def get_recent_errors(
        self,
        limit: int = 100,
        hours: int = 24
    ) -> list[dict[str, Any]]:
        """Get recent errors.
        
        Args:
            limit: Maximum number of errors to return
            hours: Time window in hours (default: 24)
            
        Returns:
            List of error dicts
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        sql = """
            SELECT timestamp, data
            FROM events
            WHERE event_type = 'error'
              AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        rows = self.db.query(sql, (cutoff, limit))
        
        errors = []
        for row in rows:
            data = json.loads(row[1])
            data["timestamp"] = row[0]
            errors.append(data)
        
        return errors
    
    def get_resource_usage(
        self,
        hours: int = 1
    ) -> list[dict[str, Any]]:
        """Get resource usage over time.
        
        Args:
            hours: Time window in hours (default: 1)
            
        Returns:
            List of resource usage dicts with timestamp
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        sql = """
            SELECT timestamp, data
            FROM events
            WHERE event_type = 'resource_usage'
              AND timestamp > ?
            ORDER BY timestamp ASC
        """
        
        rows = self.db.query(sql, (cutoff,))
        
        usage = []
        for row in rows:
            data = json.loads(row[1])
            data["timestamp"] = row[0]
            usage.append(data)
        
        return usage
    
    def get_latency_percentiles(
        self,
        event_type: str = "llm_call",
        hours: int = 24
    ) -> dict[str, float]:
        """Calculate latency percentiles.
        
        Args:
            event_type: Event type to analyze (default: llm_call)
            hours: Time window in hours (default: 24)
            
        Returns:
            Dict with p50, p95, p99 percentiles
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        # Get all durations
        sql = """
            SELECT json_extract(data, '$.duration_ms') as duration
            FROM events
            WHERE event_type = ?
              AND timestamp > ?
            ORDER BY duration ASC
        """
        
        rows = self.db.query(sql, (event_type, cutoff))
        
        if not rows:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        durations = [row[0] for row in rows if row[0] is not None]
        
        if not durations:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        # Calculate percentiles
        count = len(durations)
        
        def percentile(p: float) -> float:
            index = int((count - 1) * p)
            return durations[index]
        
        return {
            "p50": percentile(0.50),
            "p95": percentile(0.95),
            "p99": percentile(0.99)
        }
    
    def get_event_count_by_type(
        self,
        hours: int = 24
    ) -> dict[str, int]:
        """Get event counts grouped by type.
        
        Args:
            hours: Time window in hours (default: 24)
            
        Returns:
            Dict mapping event type to count
        """
        cutoff = int(time.time()) - (hours * 60 * 60)
        
        sql = """
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE timestamp > ?
            GROUP BY event_type
        """
        
        rows = self.db.query(sql, (cutoff,))
        
        return {row[0]: row[1] for row in rows}
