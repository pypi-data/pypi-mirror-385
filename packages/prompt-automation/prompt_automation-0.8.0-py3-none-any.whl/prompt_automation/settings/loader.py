"""Configuration loader.

Loads configuration from multiple sources with priority:
1. Defaults (from Pydantic models)
2. Config file (config.json)
3. Environment variables (PA_* prefix)
4. Profile overrides (lightweight/standard/performance)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from .models import Config
from .profiles import PROFILES


class Loader:
    """Load configuration from file, environment, and profiles."""
    
    def __init__(self, config_path: Path):
        """Initialize loader with config file path.
        
        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
    
    def load(self, profile: Optional[str] = None) -> Config:
        """Load configuration with priority: defaults → file → env vars → profile.
        
        Args:
            profile: Optional profile name (lightweight/standard/performance)
            
        Returns:
            Validated Config instance
            
        Raises:
            ValueError: If profile name is unknown
            json.JSONDecodeError: If config file contains invalid JSON
        """
        # 1. Start with defaults (Pydantic model defaults)
        config_dict = Config().model_dump()
        
        # 2. Load from file (if exists)
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
            config_dict = self._deep_merge(config_dict, file_config)
        
        # 3. Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # 4. Apply profile overrides (if specified)
        if profile:
            config_dict = self._merge_profile(config_dict, profile)
        
        # 5. Validate and return
        return Config(**config_dict)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary (takes precedence)
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides.
        
        Environment variables use PA_ prefix with double underscore for nesting:
        - PA_LLM__HOST=localhost
        - PA_LLM__PORT=9090
        - PA_CACHE__ENABLED=true
        
        Args:
            config: Base configuration dict
            
        Returns:
            Configuration dict with env var overrides applied
        """
        for key, value in os.environ.items():
            if not key.startswith("PA_"):
                continue
            
            # PA_LLM__HOST -> ["llm", "host"]
            path = key[3:].lower().split("__")
            
            # Navigate to nested dict and set value
            current = config
            for part in path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set value with type coercion
            current[path[-1]] = self._coerce_type(value)
        
        return config
    
    def _coerce_type(self, value: str) -> Any:
        """Coerce string value to appropriate type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Coerced value (bool, int, or str)
        """
        # Boolean values
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        
        # Integer values
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # String value (fallback)
        return value
    
    def _merge_profile(self, config: Dict[str, Any], profile_name: str) -> Dict[str, Any]:
        """Merge profile overrides into config.
        
        Args:
            config: Base configuration dict
            profile_name: Profile name (lightweight/standard/performance)
            
        Returns:
            Configuration dict with profile overrides applied
            
        Raises:
            ValueError: If profile name is unknown
        """
        if profile_name not in PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}")
        
        profile = PROFILES[profile_name]
        return self._deep_merge(config, profile)
