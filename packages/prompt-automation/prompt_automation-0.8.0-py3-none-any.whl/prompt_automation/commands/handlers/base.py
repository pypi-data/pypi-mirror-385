"""Base handler interface for commands."""
from abc import ABC, abstractmethod
from typing import Any, Optional

from ..models import Command, CommandResult


class BaseHandler(ABC):
    """Abstract base class for command handlers.
    
    Attributes:
        mcp_client: MCP client for Obsidian vault operations
        llm_client: LLM client for AI operations
    """
    
    def __init__(self, mcp_client: Optional[Any] = None, llm_client: Optional[Any] = None):
        """Initialize handler with optional clients.
        
        Args:
            mcp_client: Optional MCP client instance
            llm_client: Optional LLM client instance
        """
        self.mcp_client = mcp_client
        self.llm_client = llm_client
    
    @abstractmethod
    def execute(self, command: Command) -> CommandResult:
        """Execute the command.
        
        Args:
            command: Command to execute
        
        Returns:
            CommandResult with execution outcome
        
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _call_mcp(self, method: str, **kwargs) -> Any:
        """Helper to call MCP methods with error handling.
        
        Args:
            method: MCP method name (e.g., 'search_notes')
            **kwargs: Method arguments
        
        Returns:
            MCP method result
        
        Raises:
            ConnectionError: If MCP client not available
            RuntimeError: If MCP call fails
        """
        if not self.mcp_client:
            raise ConnectionError("MCP client not configured")
        
        try:
            # Call method on MCP client (synchronous)
            method_func = getattr(self.mcp_client, method, None)
            if not method_func:
                raise AttributeError(f"MCP client has no method: {method}")
            
            result = method_func(**kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"MCP call failed: {method}") from e
