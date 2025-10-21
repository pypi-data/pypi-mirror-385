"""Note creation handler with location suggestion."""
import difflib
from typing import Optional

from ..models import Command, CommandResult
from .base import BaseHandler


class NoteHandler(BaseHandler):
    """Handler for /note command - creates new note with LLM location suggestion.
    
    Uses LLM to suggest folder location based on note title/content,
    generates Markdown file, creates unified diff, and returns for approval.
    """
    
    def execute(self, command: Command) -> CommandResult:
        """Execute note creation command.
        
        Args:
            command: Command with 'title' and 'content' args
        
        Returns:
            CommandResult with diff and suggested location
        """
        # Validate args
        if "title" not in command.args:
            return CommandResult(
                success=False,
                formatted="",
                error="Missing required argument: title"
            )
        
        if "content" not in command.args:
            return CommandResult(
                success=False,
                formatted="",
                error="Missing required argument: content"
            )
        
        title = command.args["title"]
        content = command.args["content"]
        
        # Suggest location using LLM (if available)
        location = self._suggest_location(title, content)
        
        # Build full path
        note_path = f"{location}{title}.md"
        
        # Generate note content (Markdown)
        note_content = self._generate_markdown(title, content)
        
        # Generate diff (empty -> new content)
        diff = self._generate_diff("", note_content, note_path)
        
        # Write to vault
        try:
            self._call_mcp("upsert_note", path=note_path, content=note_content)
        except RuntimeError as e:
            return CommandResult(
                success=False,
                formatted="",
                error=str(e)
            )
        
        # Format result
        formatted = self._format_result(note_path, title)
        
        return CommandResult(
            success=True,
            formatted=formatted,
            diff=diff,
            requires_approval=True
        )
    
    def _suggest_location(self, title: str, content: str) -> str:
        """Suggest folder location for new note using LLM.
        
        Args:
            title: Note title
            content: Note content
        
        Returns:
            Suggested folder path (e.g., "Engineering/")
        """
        if not self.llm_client:
            # Default location if no LLM
            return "Notes/"
        
        try:
            # Call LLM for location suggestion
            location = self.llm_client.suggest_location(title=title, content=content)
            return location
        except Exception:
            # Fallback to default
            return "Notes/"
    
    def _generate_markdown(self, title: str, content: str) -> str:
        """Generate Markdown content for note.
        
        Args:
            title: Note title
            content: Note content
        
        Returns:
            Formatted Markdown string
        """
        return f"# {title}\n\n{content}\n"
    
    def _generate_diff(self, old: str, new: str, filename: str) -> str:
        """Generate unified diff.
        
        Args:
            old: Original content (empty for new notes)
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
    
    def _format_result(self, path: str, title: str) -> str:
        """Format result message.
        
        Args:
            path: Note file path
            title: Note title
        
        Returns:
            Formatted message
        """
        return f"**Note Created**: `{path}`\n\n# {title}"
