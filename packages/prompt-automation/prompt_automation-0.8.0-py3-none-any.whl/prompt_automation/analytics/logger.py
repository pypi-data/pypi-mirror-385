"""Event logging for analytics."""
from __future__ import annotations

import json
import time
import traceback
from typing import Any

from .database import Database
from .privacy import PrivacyControls
from ..errorlog import get_logger

_log = get_logger(__name__)


class EventLogger:
    """Event logger for analytics.
    
    Features:
    - Log template renders, LLM calls, MCP calls, errors, resource usage
    - Privacy-aware (hash prompts, sanitize stack traces)
    - Self-instrumentation exclusion (prevent recursion)
    - Batching support for performance
    """
    
    def __init__(
        self,
        db: Database | None = None,
        privacy: PrivacyControls | None = None,
        batch_size: int = 10
    ):
        """Initialize event logger.
        
        Args:
            db: Database instance (creates default if None)
            privacy: Privacy controls instance (creates default if None)
            batch_size: Number of events to batch before auto-flush
        """
        self.db = db if db else Database()
        self.privacy = privacy if privacy else PrivacyControls()
        self.batch_size = batch_size
        self._batch: list[dict] = []
    
    def log_event(
        self,
        event_type: str,
        data: dict[str, Any],
        auto_flush: bool = True
    ):
        """Log a generic event.
        
        Args:
            event_type: Type of event
            data: Event data
            auto_flush: Whether to auto-flush on batch size (default: True)
        """
        # Check if analytics is enabled
        if not self.privacy.is_analytics_enabled():
            return
        
        # Check if this is an analytics operation (prevent recursion)
        if self._is_analytics_operation(event_type, data):
            return
        
        # Create event
        event = {
            "event_type": event_type,
            "timestamp": int(time.time()),
            "data": json.dumps(data)
        }
        
        # Add to batch
        self._batch.append(event)
        
        # Auto-flush if batch size reached
        if auto_flush and len(self._batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Flush batched events to database."""
        if not self._batch:
            return
        
        for event in self._batch:
            self.db.insert_event(event)
        
        self._batch.clear()
    
    def _is_analytics_operation(self, event_type: str, data: dict) -> bool:
        """Check if event is from analytics module itself.
        
        Args:
            event_type: Event type
            data: Event data
            
        Returns:
            True if this is an analytics operation (should not be tracked)
        """
        # Exclude analytics-specific events
        if event_type in ("analytics_query", "analytics_export", "analytics_rotation"):
            return True
        
        # Exclude based on operation or module
        operation = data.get("operation", "")
        module = data.get("module", "")
        
        if operation.startswith("analytics."):
            return True
        
        if module == "prompt_automation.analytics":
            return True
        
        return False
    
    def log_template_render(
        self,
        template_id: int,
        template_title: str,
        duration_ms: int,
        cache_hit: bool,
        variables: dict[str, Any] | None = None
    ):
        """Log template render event.
        
        Args:
            template_id: Template ID
            template_title: Template title
            duration_ms: Render duration in milliseconds
            cache_hit: Whether cache was hit
            variables: Template variables (will be hashed for privacy)
        """
        data = {
            "template_id": template_id,
            "template_title": template_title,
            "duration_ms": duration_ms,
            "cache_hit": cache_hit
        }
        
        if variables:
            # Hash variables for privacy
            data["variables"] = {
                k: self.privacy.hash_prompt(str(v)) if v else ""
                for k, v in variables.items()
            }
        
        self.log_event("template_render", data)
        self.flush()  # Flush immediately for simplicity
    
    def log_llm_call(
        self,
        prompt: str,
        model: str,
        duration_ms: int,
        tokens_input: int,
        tokens_output: int,
        device: str | None = None,
        cache_hit: bool = False
    ):
        """Log LLM call event.
        
        Args:
            prompt: Prompt text (will be hashed for privacy)
            model: Model name
            duration_ms: Call duration in milliseconds
            tokens_input: Input tokens
            tokens_output: Output tokens
            device: Device (e.g., "cuda:0")
            cache_hit: Whether cache was hit
        """
        data = {
            "prompt_hash": self.privacy.hash_prompt(prompt),
            "prompt_preview": self.privacy.get_prompt_preview(prompt),
            "model": model,
            "duration_ms": duration_ms,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cache_hit": cache_hit
        }
        
        if device:
            data["device"] = device
        
        self.log_event("llm_call", data)
        self.flush()  # Flush immediately for simplicity
    
    def log_mcp_call(
        self,
        tool: str,
        duration_ms: int,
        cache_hit: bool,
        status: str
    ):
        """Log MCP call event.
        
        Args:
            tool: Tool name
            duration_ms: Call duration in milliseconds
            cache_hit: Whether cache was hit
            status: Call status (e.g., "success", "error")
        """
        data = {
            "tool": tool,
            "duration_ms": duration_ms,
            "cache_hit": cache_hit,
            "status": status
        }
        
        self.log_event("mcp_call", data)
        self.flush()  # Flush immediately for simplicity
    
    def log_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None
    ):
        """Log error event.
        
        Args:
            error: Exception instance
            context: Additional context (e.g., template_id, operation)
        """
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": self.privacy.sanitize_stack_trace(
                traceback.format_exc()
            ),
            "context": context or {}
        }
        
        self.log_event("error", data)
        self.flush()  # Flush immediately for simplicity
    
    def log_resource_usage(
        self,
        cpu_percent: float,
        ram_used_mb: int,
        ram_percent: float,
        gpu_available: bool = False,
        vram_used_mb: int | None = None,
        vram_percent: float | None = None
    ):
        """Log resource usage event.
        
        Args:
            cpu_percent: CPU usage percentage
            ram_used_mb: RAM used in MB
            ram_percent: RAM usage percentage
            gpu_available: Whether GPU is available
            vram_used_mb: VRAM used in MB (if GPU available)
            vram_percent: VRAM usage percentage (if GPU available)
        """
        data = {
            "cpu_percent": cpu_percent,
            "ram_used_mb": ram_used_mb,
            "ram_percent": ram_percent,
            "gpu_available": gpu_available
        }
        
        if gpu_available:
            if vram_used_mb is not None:
                data["vram_used_mb"] = vram_used_mb
            if vram_percent is not None:
                data["vram_percent"] = vram_percent
        
        self.log_event("resource_usage", data)
        self.flush()  # Flush immediately for simplicity
