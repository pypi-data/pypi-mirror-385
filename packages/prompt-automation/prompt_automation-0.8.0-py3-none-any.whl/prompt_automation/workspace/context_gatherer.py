"""Context gatherer - main orchestrator for workspace context collection.

Gathers comprehensive context for feature requests by:
1. Extracting keywords from feature description
2. Searching codebase (ripgrep → git-grep → pathlib fallback)
3. Querying Obsidian vault via MCP bridge (optional)
4. Extracting constraints from AGENTS.md
5. Finding related test files
6. Formatting all context as LLM-friendly Markdown

Example:
    >>> from prompt_automation.workspace.context_gatherer import ContextGatherer
    >>> gatherer = ContextGatherer()
    >>> context = gatherer.gather_for_feature("Add fuzzy search to templates")
    >>> print(context)
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import search
from .. import features

logger = logging.getLogger(__name__)

# Stop words to filter out
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for",
    "from", "has", "he", "in", "is", "it", "its", "of", "on",
    "that", "the", "to", "was", "will", "with", "the", "this",
    "but", "or", "not", "can", "could", "should", "would",
}


class ContextGatherer:
    """Gathers workspace context for feature requests."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize context gatherer.
        
        Args:
            workspace_root: Root directory of workspace (defaults to cwd)
        """
        self.workspace_root = workspace_root or Path.cwd()

    def gather_for_feature(self, feature_description: str) -> str:
        """
        Gather all relevant context for a feature request.
        
        Args:
            feature_description: User's feature request text
            
        Returns:
            Formatted context string for LLM consumption
        """
        logger.info(f"Gathering context for: {feature_description}")
        
        # Extract keywords
        keywords = self._extract_keywords(feature_description)
        logger.debug(f"Extracted keywords: {keywords}")
        
        # Search codebase
        codebase_files = self._search_codebase(keywords)
        logger.debug(f"Found {len(codebase_files)} codebase files")
        
        # Search Obsidian (optional)
        obsidian_context = self._search_obsidian(keywords)
        
        # Extract constraints
        constraints = self._extract_constraints()
        
        # Find related tests
        related_tests = self._find_related_tests(keywords)
        logger.debug(f"Found {len(related_tests)} related test files")
        
        # Format all context
        return self._format_context(
            feature_description=feature_description,
            keywords=keywords,
            codebase_files=codebase_files,
            obsidian_context=obsidian_context,
            constraints=constraints,
            related_tests=related_tests,
        )

    def _extract_keywords(self, description: str) -> List[str]:
        """
        Extract search keywords from description.
        
        Args:
            description: Feature description text
            
        Returns:
            List of unique keywords (max 10)
        """
        if not description:
            return []
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-z]+\b', description.lower())
        
        # Filter stop words and duplicates
        keywords = []
        seen = set()
        for word in words:
            if word not in STOP_WORDS and word not in seen and len(word) > 2:
                keywords.append(word)
                seen.add(word)
                if len(keywords) >= 10:
                    break
        
        return keywords

    def _search_codebase(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search codebase using ripgrep or fallbacks.
        
        Args:
            keywords: Search keywords
            
        Returns:
            List of file information dicts (max 20 results)
        """
        if not keywords:
            return []
        
        all_files = set()
        
        for keyword in keywords:
            # Try ripgrep first
            results = search.search_with_ripgrep(keyword, self.workspace_root)
            if results:
                all_files.update(results)
                continue
            
            # Fall back to git-grep
            results = search.search_with_git_grep(keyword, self.workspace_root)
            if results:
                all_files.update(results)
                continue
            
            # Final fallback: pathlib
            results = search.search_with_pathlib(keyword, self.workspace_root)
            all_files.update(results)
        
        # Convert to list of dicts with snippets
        file_list = []
        for file_path_str in sorted(all_files)[:20]:  # Limit to 20
            file_path = Path(file_path_str)
            try:
                # Extract snippet (first 5 lines)
                content = file_path.read_text(errors="ignore")
                snippet = "\n".join(content.splitlines()[:5])
                file_list.append({
                    "path": file_path_str,
                    "snippet": snippet,
                })
            except Exception:
                # Skip files that can't be read
                continue
        
        return file_list

    def _search_obsidian(self, keywords: List[str]) -> str:
        """
        Search Obsidian vault via MCP bridge.
        
        Args:
            keywords: Search keywords
            
        Returns:
            Markdown-formatted Obsidian context (empty string if unavailable)
        """
        # Check feature flag
        if not features.is_workspace_context_obsidian_enabled():
            logger.debug("Obsidian MCP integration disabled by feature flag")
            return ""
        
        try:
            # Import here to avoid circular dependency
            from ..menus.meta_prompt.mcp_bridge import MetaPromptMCPBridge
            
            bridge = MetaPromptMCPBridge(mcp_enabled=True)
            query = " ".join(keywords)
            
            return bridge.search_obsidian(
                query=query,
                components=[],
                max_results=5,
            )
        except ImportError:
            logger.debug("MCP bridge not available (meta-prompt feature not implemented)")
            return ""
        except Exception as e:
            logger.warning(f"Obsidian search failed: {e}")
            return ""

    def _extract_constraints(self) -> str:
        """
        Extract constraints from AGENTS.md.
        
        Returns:
            Markdown-formatted constraints (empty string if file missing)
        """
        agents_file = self.workspace_root / "AGENTS.md"
        if not agents_file.exists():
            logger.debug("AGENTS.md not found")
            return ""
        
        try:
            content = agents_file.read_text()
            
            # Extract key sections
            sections_to_extract = [
                "Mandatory Constraints",
                "TDD Requirements",
                "Performance & Resource Budgets",
                "Rollout & Safety",
            ]
            
            extracted = []
            for section in sections_to_extract:
                pattern = rf"## {section}\n+(.*?)(?=\n##|\Z)"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    extracted.append(f"## {section}\n{match.group(1).strip()}")
            
            return "\n\n".join(extracted) if extracted else ""
            
        except Exception as e:
            logger.warning(f"Failed to extract constraints: {e}")
            return ""

    def _find_related_tests(self, keywords: List[str]) -> List[str]:
        """
        Find test files matching keywords.
        
        Args:
            keywords: Search keywords
            
        Returns:
            List of test file paths
        """
        test_files = []
        
        # Search for test files
        for pattern in ["**/test_*.py", "**/tests/**/*.py"]:
            for test_file in self.workspace_root.glob(pattern):
                # Check if any keyword appears in file name or content
                file_name = test_file.stem.lower()
                if any(keyword in file_name for keyword in keywords):
                    test_files.append(str(test_file))
                    continue
                
                # Check content
                try:
                    content = test_file.read_text(errors="ignore").lower()
                    if any(keyword in content for keyword in keywords):
                        test_files.append(str(test_file))
                except Exception:
                    continue
        
        return sorted(set(test_files))

    def _format_file_context(self, files: List[Dict[str, Any]]) -> str:
        """
        Format file search results for LLM.
        
        Args:
            files: List of file information dicts
            
        Returns:
            Markdown-formatted file context
        """
        if not files:
            return ""
        
        lines = ["# Relevant Codebase Files\n"]
        for file_info in files:
            lines.append(f"## {file_info['path']}")
            lines.append(f"```\n{file_info['snippet']}\n```\n")
        
        return "\n".join(lines)

    def _format_context(
        self,
        feature_description: str,
        keywords: List[str],
        codebase_files: List[Dict[str, Any]],
        obsidian_context: str,
        constraints: str,
        related_tests: List[str],
    ) -> str:
        """
        Format all context into LLM-friendly Markdown.
        
        Returns:
            Complete formatted context
        """
        sections = []
        
        # Feature description
        sections.append(f"# Feature Request\n{feature_description}\n")
        
        # Keywords
        sections.append(f"# Extracted Keywords\n{', '.join(keywords)}\n")
        
        # Codebase files
        if codebase_files:
            sections.append(self._format_file_context(codebase_files))
        
        # Obsidian context
        if obsidian_context:
            sections.append(f"# Workspace Context from Obsidian\n{obsidian_context}\n")
        
        # Constraints
        if constraints:
            sections.append(f"# Constraints from AGENTS.md\n{constraints}\n")
        
        # Related tests
        if related_tests:
            sections.append("# Related Test Files")
            for test_file in related_tests:
                sections.append(f"- {test_file}")
            sections.append("")  # Empty line
        
        return "\n".join(sections)
