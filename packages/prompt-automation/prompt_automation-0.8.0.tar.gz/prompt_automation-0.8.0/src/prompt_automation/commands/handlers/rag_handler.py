"""RAG (Retrieval-Augmented Generation) command handler."""
from typing import Optional, Any

from ..models import Command, CommandResult
from .base import BaseHandler


class RAGHandler(BaseHandler):
    """Handler for /rag command - searches Obsidian vault.
    
    Executes semantic search via MCP client and formats results.
    """
    
    def execute(self, command: Command) -> CommandResult:
        """Execute RAG search command.
        
        Args:
            command: Command with 'query' arg
        
        Returns:
            CommandResult with formatted search results
        """
        # Validate args
        if "query" not in command.args:
            return CommandResult(
                success=False,
                formatted="",
                error="Missing required argument: query"
            )
        
        query = command.args["query"]
        
        # Call MCP search
        try:
            response = self._call_mcp("search_notes", query=query)
        except RuntimeError as e:
            return CommandResult(
                success=False,
                formatted="",
                error=str(e)
            )
        
        # Format results
        results = response.get("results", [])
        
        if not results:
            return CommandResult(
                success=True,
                formatted="No results found for query: " + query,
                requires_approval=False
            )
        
        # Format as Markdown
        formatted = self._format_results(results, query)
        
        return CommandResult(
            success=True,
            formatted=formatted,
            requires_approval=False
        )
    
    def _format_results(self, results: list, query: str) -> str:
        """Format search results as Markdown.
        
        Args:
            results: List of search result dicts
            query: Original query string
        
        Returns:
            Markdown formatted results
        """
        lines = [f"## Search Results for: {query}\n"]
        
        for i, result in enumerate(results, 1):
            path = result.get("path", "Unknown")
            snippet = result.get("snippet", "")
            
            lines.append(f"**{i}. {path}**")
            lines.append(f"> {snippet}\n")
        
        return "\n".join(lines)
