"""Command registry for managing handlers."""
from threading import Lock
from typing import Dict, List

from .handlers.base import BaseHandler


class CommandRegistry:
    """Registry for command handlers.
    
    Manages registration and retrieval of command handlers.
    Thread-safe for concurrent access.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._handlers: Dict[str, BaseHandler] = {}
        self._lock = Lock()
    
    def register(self, name: str, handler: BaseHandler) -> None:
        """Register a command handler.
        
        Args:
            name: Command name (e.g., 'rag', 'daily')
            handler: Handler instance for this command
        
        Note:
            Registering the same name twice will overwrite the previous handler.
        """
        with self._lock:
            self._handlers[name] = handler
    
    def get(self, name: str) -> BaseHandler:
        """Get handler for command name.
        
        Args:
            name: Command name to look up
        
        Returns:
            Handler instance for the command
        
        Raises:
            KeyError: If no handler registered for this command
        """
        with self._lock:
            if name not in self._handlers:
                raise KeyError(
                    f"No handler registered for command '{name}'. "
                    f"Available: {', '.join(self._handlers.keys())}"
                )
            return self._handlers[name]
    
    def list_commands(self) -> List[str]:
        """List all registered command names.
        
        Returns:
            List of command names (sorted)
        """
        with self._lock:
            return sorted(self._handlers.keys())
