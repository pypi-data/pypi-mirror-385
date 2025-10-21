"""Configuration management module.

This module provides a unified configuration system with:
- Type-safe Pydantic models
- Hot-reload capability
- Profile support (lightweight/standard/performance)
- Environment variable overrides
- Migration framework
"""

from pathlib import Path
from typing import Any, Callable, Optional, Dict
import logging

from .models import Config
from .loader import Loader
from .saver import Saver
from .watcher import ConfigFileWatcher

logger = logging.getLogger(__name__)


class ConfigManager:
    """Singleton configuration manager.
    
    Provides centralized access to application configuration with:
    - Lazy loading (config loaded on first access)
    - Hot-reload support
    - Subscriber notifications
    - Profile switching
    - Environment variable overrides
    
    Usage:
        config = ConfigManager()
        host = config.get("llm.host")
        config.set("llm.port", 9090)
        config.save()
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls, config_dir: Optional[Path] = None):
        """Create or return singleton instance.
        
        Args:
            config_dir: Optional config directory (default: ~/.prompt-automation)
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize ConfigManager (only once due to singleton).
        
        Args:
            config_dir: Optional config directory (default: HOME_DIR from config.py)
        """
        if self._initialized:
            return
        
        if config_dir is None:
            from ..config import HOME_DIR
            config_dir = HOME_DIR
        
        self.config_dir = Path(config_dir)
        self.config_path = self.config_dir / "config.json"
        self._config: Optional[Config] = None
        self._loader = Loader(self.config_path)
        self._saver = Saver(self.config_path)
        self._subscribers: list[Callable[[], None]] = []
        self._watcher: Optional[ConfigFileWatcher] = None
        
        self._initialized = True
    
    @property
    def config(self) -> Config:
        """Get current config (lazy load on first access).
        
        Returns:
            Current Config instance
        """
        if self._config is None:
            self.load()
        
        # After load(), _config is guaranteed to be non-None
        assert self._config is not None
        return self._config
    
    def load(self) -> None:
        """Load configuration from disk."""
        self._config = self._loader.load()
    
    def save(self) -> None:
        """Save configuration to disk atomically."""
        if self._config is not None:
            self._saver.save(self._config)
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path (e.g., "llm.host", "cache.memory_mb")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
            
        Example:
            host = config.get("llm.host")
            port = config.get("llm.port", default=8080)
        """
        keys = path.split('.')
        value = self.config.model_dump()
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> None:
        """Set configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path (e.g., "llm.port", "cache.enabled")
            value: New value
            
        Raises:
            ValidationError: If value fails Pydantic validation
            
        Example:
            config.set("llm.port", 9090)
            config.set("cache.enabled", True)
        """
        keys = path.split('.')
        config_dict = self.config.model_dump()
        
        # Navigate to nested dict
        current = config_dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set value
        current[keys[-1]] = value
        
        # Re-validate (will raise ValidationError if invalid)
        self._config = Config(**config_dict)
        
        # Notify subscribers
        self._notify_subscribers()
    
    def subscribe(self, callback: Callable[[], None]) -> None:
        """Subscribe to configuration changes.
        
        Args:
            callback: Function called when config changes (no arguments)
            
        Example:
            def on_config_change():
                print("Config changed!")
            
            config.subscribe(on_config_change)
        """
        self._subscribers.append(callback)
    
    def switch_profile(self, profile_name: str) -> None:
        """Switch to a different profile.
        
        Args:
            profile_name: Profile name (lightweight/standard/performance)
            
        Raises:
            ValueError: If profile name is unknown
            
        Example:
            config.switch_profile("performance")
        """
        # Load with profile
        self._config = self._loader.load(profile=profile_name)
        
        # Save to disk
        self.save()
        
        # Notify all subscribers
        self._notify_subscribers()
    
    def enable_hot_reload(self) -> None:
        """Enable automatic reload when config file changes."""
        if self._watcher is not None:
            logger.warning("Hot-reload already enabled")
            return
        
        self._watcher = ConfigFileWatcher(
            config_path=self.config_path,
            on_change=self._on_file_change,
        )
        self._watcher.start()
        logger.info("Hot-reload enabled")
    
    def disable_hot_reload(self) -> None:
        """Disable automatic reload."""
        if self._watcher is None:
            logger.warning("Hot-reload not enabled")
            return
        
        self._watcher.stop()
        self._watcher = None
        logger.info("Hot-reload disabled")
    
    def _on_file_change(self) -> None:
        """Handle config file change (internal callback for watcher)."""
        old_config = self._config
        try:
            logger.info("Reloading config due to file change")
            self.load()
            self._notify_subscribers()
        except Exception as e:
            logger.error(f"Failed to reload config: {e}", exc_info=True)
            # Restore old config on failure
            self._config = old_config
    
    def _notify_subscribers(self) -> None:
        """Notify all subscribers of configuration changes."""
        for callback in self._subscribers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Subscriber callback failed: {e}", exc_info=True)


# Version
__version__ = "1.0.0"

# Export public API
__all__ = ['ConfigManager', 'Config']
