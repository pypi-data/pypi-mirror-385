"""Analytics orchestrator for prompt-automation.

This module provides the main Analytics class that coordinates:
- Event logging (templates, LLM calls, MCP, errors, resources)
- Privacy controls (hashing, sanitization, opt-out)
- Database storage (SQLite with rotation)
- Querying and reporting

Usage:
    from prompt_automation.analytics import Analytics
    
    analytics = Analytics()
    
    # Log events
    analytics.log_template_render(13008, "Test", 100, False)
    analytics.log_llm_call("prompt", "qwen", 1000, 100, 200)
    
    # Query data
    top_templates = analytics.get_top_templates(limit=10)
    cache_rate = analytics.get_cache_hit_rate(hours=24)
"""
from __future__ import annotations

from .database import Database
from .logger import EventLogger
from .privacy import PrivacyControls
from .queries import Queries

__all__ = [
    "Analytics",
    "Database",
    "EventLogger",
    "PrivacyControls",
    "Queries",
]


class Analytics:
    """Main analytics orchestrator.
    
    Coordinates all analytics operations:
    - Event logging
    - Privacy controls
    - Database management
    - Querying and reporting
    """
    
    def __init__(
        self,
        db_path: str | None = None,
        max_size_mb: int = 100
    ):
        """Initialize analytics.
        
        Args:
            db_path: Path to database file (default: ~/.prompt-automation/analytics.db)
            max_size_mb: Maximum database size before rotation (default: 100MB)
        """
        self.db = Database(db_path=db_path, max_size_mb=max_size_mb)
        self.privacy = PrivacyControls()
        self.logger = EventLogger(db=self.db, privacy=self.privacy)
        self.queries = Queries(db=self.db)
    
    # Event logging methods (delegate to logger)
    
    def log_template_render(self, *args, **kwargs):
        """Log template render event."""
        self.logger.log_template_render(*args, **kwargs)
    
    def log_llm_call(self, *args, **kwargs):
        """Log LLM call event."""
        self.logger.log_llm_call(*args, **kwargs)
    
    def log_mcp_call(self, *args, **kwargs):
        """Log MCP call event."""
        self.logger.log_mcp_call(*args, **kwargs)
    
    def log_error(self, *args, **kwargs):
        """Log error event."""
        self.logger.log_error(*args, **kwargs)
    
    def log_resource_usage(self, *args, **kwargs):
        """Log resource usage event."""
        self.logger.log_resource_usage(*args, **kwargs)
    
    # Query methods (delegate to queries)
    
    def get_top_templates(self, *args, **kwargs):
        """Get top templates by usage."""
        return self.queries.get_top_templates(*args, **kwargs)
    
    def get_cache_hit_rate(self, *args, **kwargs):
        """Get cache hit rate."""
        return self.queries.get_cache_hit_rate(*args, **kwargs)
    
    def get_recent_errors(self, *args, **kwargs):
        """Get recent errors."""
        return self.queries.get_recent_errors(*args, **kwargs)
    
    def get_resource_usage(self, *args, **kwargs):
        """Get resource usage trends."""
        return self.queries.get_resource_usage(*args, **kwargs)
    
    def get_latency_percentiles(self, *args, **kwargs):
        """Get latency percentiles."""
        return self.queries.get_latency_percentiles(*args, **kwargs)
    
    def get_event_count_by_type(self, *args, **kwargs):
        """Get event counts by type."""
        return self.queries.get_event_count_by_type(*args, **kwargs)
    
    # Utility methods
    
    def is_enabled(self) -> bool:
        """Check if analytics is enabled."""
        return self.privacy.is_analytics_enabled()
    
    def clear_all_data(self):
        """Clear all analytics data."""
        self.db.query("DELETE FROM events")
        self.db.query("DELETE FROM metadata")
    
    def export_data(self) -> dict:
        """Export all analytics data as JSON-serializable dict."""
        events = self.db.query("SELECT * FROM events ORDER BY timestamp DESC LIMIT 10000")
        return {
            "events": [
                {
                    "id": row[0],
                    "event_type": row[1],
                    "timestamp": row[2],
                    "data": row[3]
                }
                for row in events
            ],
            "database_size_mb": self.db.size_mb()
        }
    
    def close(self):
        """Close database connection."""
        self.db.close()
