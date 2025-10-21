"""Command parser for slash commands and natural language."""
import shlex
from typing import Dict, Any, Optional

from .models import Command


class CommandParser:
    """Parser for command input (slash commands and natural language).
    
    Attributes:
        llm_client: Optional LLM client for natural language interpretation
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize parser with optional LLM client.
        
        Args:
            llm_client: Optional LLM client for natural language interpretation
        """
        self.llm_client = llm_client
    
    def parse(self, user_input: str) -> Command:
        """Parse user input into a Command.
        
        Args:
            user_input: Raw user input (slash command or natural language)
        
        Returns:
            Parsed Command object
        
        Raises:
            ValueError: If input is empty or command is invalid
            NotImplementedError: If natural language parsing not yet supported
        """
        # Validate input
        if not user_input or not user_input.strip():
            raise ValueError("Empty input")
        
        user_input = user_input.strip()
        
        # Route based on input type
        if user_input.startswith('/'):
            return self._parse_slash_command(user_input)
        else:
            # Natural language - use LLM to interpret
            return self._parse_natural_language(user_input)
    
    def _parse_natural_language(self, user_input: str) -> Command:
        """Parse natural language into Command using LLM.
        
        Args:
            user_input: Natural language query
        
        Returns:
            Command object with is_natural_language=True
        
        Raises:
            NotImplementedError: If LLM client not available
        """
        if not self.llm_client:
            raise NotImplementedError("Natural language not yet supported")
        
        # Call LLM to interpret natural language
        slash_command = self.llm_client.interpret_natural_language(user_input)
        
        # Parse the resulting slash command
        cmd = self._parse_slash_command(slash_command)
        
        # Mark as natural language origin
        cmd.is_natural_language = True
        cmd.raw_input = user_input  # Keep original NL input
        
        return cmd
    
    def _parse_slash_command(self, cmd: str) -> Command:
        """Parse slash command into Command object.
        
        Args:
            cmd: Slash command string (e.g., '/rag query text')
        
        Returns:
            Command object with parsed name and args
        
        Raises:
            ValueError: If command format invalid or unknown
        """
        # Remove leading slash
        cmd_str = cmd[1:].strip()
        
        if not cmd_str:
            raise ValueError("Command name missing after /")
        
        # Use shlex to handle quoted arguments
        try:
            parts = shlex.split(cmd_str)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {e}")
        
        if not parts:
            raise ValueError("Command name missing")
        
        name = parts[0]
        args_parts = parts[1:]
        
        # Parse arguments based on command type
        args = self._parse_args(name, args_parts, cmd)
        
        return Command(name=name, args=args, raw_input=cmd, is_natural_language=False)
    
    def _parse_args(self, name: str, args_parts: list, raw_cmd: str) -> Dict[str, Any]:
        """Parse command arguments based on command type.
        
        Args:
            name: Command name
            args_parts: List of argument tokens
            raw_cmd: Original raw command string
        
        Returns:
            Dictionary of parsed arguments
        
        Raises:
            ValueError: If command unknown or args invalid
        """
        if name == "rag":
            return self._parse_rag_args(args_parts, raw_cmd)
        elif name == "daily":
            return self._parse_daily_args(args_parts, raw_cmd)
        elif name == "note":
            return self._parse_note_args(args_parts, raw_cmd)
        elif name == "open":
            return self._parse_open_args(args_parts, raw_cmd)
        else:
            raise ValueError(f"Unknown command: {name}")
    
    def _parse_rag_args(self, args_parts: list, raw_cmd: str) -> Dict[str, Any]:
        """Parse arguments for /rag command.
        
        Args:
            args_parts: Argument tokens
            raw_cmd: Original command (unused, for consistency)
        
        Returns:
            Dict with 'query' key
        
        Raises:
            ValueError: If query missing
        """
        if not args_parts:
            raise ValueError("/rag requires arguments: /rag <query>")
        
        return {"query": " ".join(args_parts)}
    
    def _parse_daily_args(self, args_parts: list, raw_cmd: str) -> Dict[str, Any]:
        """Parse arguments for /daily command.
        
        Args:
            args_parts: Argument tokens
            raw_cmd: Original command (unused, for consistency)
        
        Returns:
            Dict with 'note' key
        
        Raises:
            ValueError: If note content missing
        """
        if not args_parts:
            raise ValueError("/daily requires arguments: /daily <note content>")
        
        return {"note": " ".join(args_parts)}
    
    def _parse_note_args(self, args_parts: list, raw_cmd: str) -> Dict[str, Any]:
        """Parse arguments for /note command.
        
        Args:
            args_parts: Argument tokens
            raw_cmd: Original command (unused, for consistency)
        
        Returns:
            Dict with 'title' and 'content' keys
        
        Raises:
            ValueError: If title or content missing
        """
        if len(args_parts) < 2:
            raise ValueError("/note requires arguments: /note <title> <content>")
        
        return {
            "title": args_parts[0],
            "content": " ".join(args_parts[1:])
        }
    
    def _parse_open_args(self, args_parts: list, raw_cmd: str) -> Dict[str, Any]:
        """Parse arguments for /open command.
        
        Args:
            args_parts: Argument tokens
            raw_cmd: Original command (unused, for consistency)
        
        Returns:
            Dict with 'path' key
        
        Raises:
            ValueError: If path missing
        """
        if not args_parts:
            raise ValueError("/open requires arguments: /open <note path>")
        
        return {"path": " ".join(args_parts)}
