"""Open note handler."""
from typing import Optional

from ..models import Command, CommandResult
from .base import BaseHandler


class OpenHandler(BaseHandler):
    """Handler for /open command - opens note in Obsidian.
    
    Executes Obsidian command to open specified note file.
    Read-only operation, no diff or approval needed.
    """
    
    def execute(self, command: Command) -> CommandResult:
        """Execute open note command.
        
        Args:
            command: Command with 'path' arg
        
        Returns:
            CommandResult confirming note opened
        """
        # Validate args
        if "path" not in command.args:
            return CommandResult(
                success=False,
                formatted="",
                error="Missing required argument: path"
            )
        
        path = command.args["path"]
        
        # Execute Obsidian command to open note
        try:
            self._call_mcp("exec_command", command="open-note", path=path)
        except RuntimeError as e:
            return CommandResult(
                success=False,
                formatted="",
                error=str(e)
            )
        
        # Format result
        formatted = self._format_result(path)
        
        return CommandResult(
            success=True,
            formatted=formatted,
            diff=None,  # Read operation, no diff
            requires_approval=False  # Read operation
        )
    
    def _format_result(self, path: str) -> str:
        """Format result message.
        
        Args:
            path: Note file path
        
        Returns:
            Formatted message
        """
        filename = path.split("/")[-1]
        return f"**Opened Note**: `{filename}`\n\nPath: `{path}`"
