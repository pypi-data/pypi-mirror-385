"""Command Executor - orchestrates command execution."""
from typing import Optional

from prompt_automation.commands.models import Command, CommandResult
from prompt_automation.commands.parser import CommandParser
from prompt_automation.commands.registry import CommandRegistry


class CommandExecutor:
    """Orchestrates command parsing and execution."""
    
    def __init__(
        self,
        mcp_client,
        llm_client: Optional[object] = None,
        registry: Optional[CommandRegistry] = None
    ):
        """Initialize executor.
        
        Args:
            mcp_client: MCP client for Obsidian operations
            llm_client: Optional LLM client for natural language
            registry: Optional command registry (created if None)
        """
        self.mcp_client = mcp_client
        self.llm_client = llm_client
        self.registry = registry or CommandRegistry()
        self.parser = CommandParser(llm_client=llm_client)
    
    def execute(self, command: Command) -> CommandResult:
        """Execute a command.
        
        Args:
            command: Parsed command to execute
            
        Returns:
            CommandResult with success status and output
        """
        try:
            # Get handler from registry
            handler = self.registry.get(command.name)
        except KeyError:
            return CommandResult(
                success=False,
                formatted="",
                error=f"No handler found for command: {command.name}"
            )
        
        try:
            # Execute handler
            result = handler.execute(command)
            return result
        except Exception as e:
            return CommandResult(
                success=False,
                formatted="",
                error=f"Handler error: {str(e)}"
            )
    
    def parse_and_execute(self, user_input: str) -> CommandResult:
        """Parse user input and execute command.
        
        Args:
            user_input: Raw user input (slash command or natural language)
            
        Returns:
            CommandResult from execution
        """
        if not user_input or not user_input.strip():
            return CommandResult(
                success=False,
                formatted="",
                error="Empty input"
            )
        
        try:
            # Parse input to command
            command = self.parser.parse(user_input)
            
            # Execute command
            return self.execute(command)
        except Exception as e:
            return CommandResult(
                success=False,
                formatted="",
                error=f"Parse error: {str(e)}"
            )
