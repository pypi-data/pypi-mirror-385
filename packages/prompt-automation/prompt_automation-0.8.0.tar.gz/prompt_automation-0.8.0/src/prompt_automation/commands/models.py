"""Command system models."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Command:
    """Represents a parsed command.
    
    Attributes:
        name: Command name (e.g., 'rag', 'daily', 'note', 'open')
        args: Command arguments as key-value pairs
        raw_input: Original user input
        is_natural_language: Whether command came from NL interpretation
    """
    name: str
    args: Dict[str, Any]
    raw_input: str
    is_natural_language: bool = False
    
    def validate(self) -> None:
        """Validate command has required arguments.
        
        Raises:
            ValueError: If required arguments are missing
        """
        required_args = {
            "rag": ["query"],
            "daily": ["note"],
            "note": ["title", "content"],
            "open": ["path"]
        }
        
        if self.name in required_args:
            for arg in required_args[self.name]:
                if arg not in self.args or not self.args[arg]:
                    raise ValueError(
                        f"Missing required argument '{arg}' for command '{self.name}'"
                    )


@dataclass
class CommandResult:
    """Represents the result of command execution.
    
    Attributes:
        success: Whether command executed successfully
        formatted: Human-readable formatted output
        diff: Optional diff string for write operations
        requires_approval: Whether result needs user approval
        error: Optional error message if failed
    """
    success: bool
    formatted: str
    diff: Optional[str] = None
    requires_approval: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary.
        
        Returns:
            Dictionary representation of result
        """
        return {
            "success": self.success,
            "formatted": self.formatted,
            "diff": self.diff,
            "requires_approval": self.requires_approval,
            "error": self.error
        }
