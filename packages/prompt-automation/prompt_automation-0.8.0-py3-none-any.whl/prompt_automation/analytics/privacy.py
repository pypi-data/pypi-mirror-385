"""Privacy controls for analytics."""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from ..errorlog import get_logger

_log = get_logger(__name__)


class PrivacyControls:
    """Privacy controls for analytics data.
    
    Features:
    - Hash prompts using SHA256
    - Preview prompts (first 50 chars)
    - Sanitize stack traces (remove user paths)
    - Opt-out support via environment variable
    """
    
    def __init__(self):
        """Initialize privacy controls."""
        self._home_pattern = re.compile(re.escape(str(Path.home())))
    
    def hash_prompt(self, prompt: str) -> str:
        """Hash prompt using SHA256.
        
        Args:
            prompt: Prompt text to hash
            
        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(prompt.encode()).hexdigest()
    
    def get_prompt_preview(self, prompt: str, max_chars: int = 50) -> str:
        """Get preview of prompt (first N characters).
        
        Args:
            prompt: Prompt text
            max_chars: Maximum characters to return (default: 50)
            
        Returns:
            First max_chars of prompt
        """
        return prompt[:max_chars]
    
    def sanitize_event_data(self, event: dict[str, Any]) -> dict[str, Any]:
        """Sanitize event data to remove PII.
        
        Args:
            event: Event data dictionary
            
        Returns:
            Sanitized event data
        """
        sanitized = event.copy()
        
        # Hash prompt if present
        if "prompt" in sanitized:
            prompt = sanitized.pop("prompt")
            sanitized["prompt_hash"] = self.hash_prompt(prompt)
            sanitized["prompt_preview"] = self.get_prompt_preview(prompt)
        
        # Hash variables if present
        if "variables" in sanitized and isinstance(sanitized["variables"], dict):
            sanitized["variables"] = {
                k: self.hash_prompt(str(v)) if v else ""
                for k, v in sanitized["variables"].items()
            }
        
        # Sanitize stack trace if present
        if "stack_trace" in sanitized:
            sanitized["stack_trace"] = self.sanitize_stack_trace(sanitized["stack_trace"])
        
        return sanitized
    
    def sanitize_stack_trace(self, stack_trace: str) -> str:
        """Sanitize stack trace to remove sensitive paths.
        
        Args:
            stack_trace: Stack trace string
            
        Returns:
            Sanitized stack trace
        """
        # Replace home directory with ~
        sanitized = self._home_pattern.sub("~", stack_trace)
        
        # Replace other user-specific paths
        sanitized = re.sub(r'/home/[^/]+', '/home/~', sanitized)
        # Windows paths - use forward slashes in replacement
        sanitized = sanitized.replace('C:\\Users\\', 'C:/Users/~/')
        
        return sanitized
    
    def is_analytics_enabled(self) -> bool:
        """Check if analytics is enabled.
        
        Returns:
            True if analytics is enabled (default), False if opted out
        """
        env_value = os.environ.get("PA_ANALYTICS_ENABLED", "true").lower()
        return env_value not in ("false", "0", "no", "off")
