"""Daily note handler with diff generation."""
import difflib
from datetime import datetime
from typing import Optional

from ..models import Command, CommandResult
from .base import BaseHandler


class DailyHandler(BaseHandler):
    """Handler for /daily command - appends to today's daily note.
    
    Reads existing daily note, appends new entry with timestamp,
    generates unified diff, and returns for user approval.
    """
    
    def execute(self, command: Command) -> CommandResult:
        """Execute daily note append command.
        
        Args:
            command: Command with 'note' arg
        
        Returns:
            CommandResult with diff and formatted output
        """
        # Validate args
        if "note" not in command.args:
            return CommandResult(
                success=False,
                formatted="",
                error="Missing required argument: note"
            )
        
        note_content = command.args["note"]
        
        # Get today's date for file path
        today = datetime.now().strftime("%Y-%m-%d")
        daily_path = f"Daily/{today}.md"
        
        # Read existing daily note
        try:
            response = self._call_mcp("read_note", path=daily_path)
            old_content = response.get("content", "")
        except RuntimeError:
            # Note doesn't exist yet, start with empty
            old_content = ""
        
        # Generate new content with timestamp
        timestamp = datetime.now().strftime("%H:%M")
        new_entry = f"- [{timestamp}] {note_content}"
        
        if old_content:
            new_content = old_content.rstrip() + "\n" + new_entry + "\n"
        else:
            # Create new note with header
            new_content = f"# {today}\n\n{new_entry}\n"
        
        # Generate unified diff
        diff = self._generate_diff(old_content, new_content, daily_path)
        
        # Write to vault (via MCP)
        try:
            self._call_mcp("upsert_note", path=daily_path, content=new_content)
        except RuntimeError as e:
            return CommandResult(
                success=False,
                formatted="",
                error=str(e)
            )
        
        # Format result
        formatted = self._format_result(daily_path, new_entry)
        
        return CommandResult(
            success=True,
            formatted=formatted,
            diff=diff,
            requires_approval=True  # Write operations need approval
        )
    
    def _generate_diff(self, old: str, new: str, filename: str) -> str:
        """Generate unified diff between old and new content.
        
        Args:
            old: Original content
            new: New content
            filename: File path for diff header
        
        Returns:
            Unified diff string
        """
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        
        diff_lines = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=""
        )
        
        return "".join(diff_lines)
    
    def _format_result(self, path: str, entry: str) -> str:
        """Format result message.
        
        Args:
            path: Daily note path
            entry: New entry added
        
        Returns:
            Formatted message
        """
        return f"**Daily Note Updated**: `{path}`\n\n{entry}"
