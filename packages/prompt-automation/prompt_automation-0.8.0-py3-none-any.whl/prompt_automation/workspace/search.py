"""Search utilities with fallback chain for workspace scanning.

Provides three search strategies in order of preference:
1. ripgrep (fastest, external tool)
2. git-grep (fast, requires git repo)
3. pathlib (slowest, guaranteed available)

Example:
    >>> from prompt_automation.workspace.search import search_with_ripgrep
    >>> results = search_with_ripgrep("template", Path.cwd(), ["py", "json"])
    >>> print(f"Found {len(results)} files")
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Constants
DEFAULT_FILE_TYPES = ["py", "json", "md"]
DEFAULT_FILE_PATTERNS = ["**/*.py", "**/*.json", "**/*.md"]
SEARCH_TIMEOUT_SECONDS = 5
MAX_RESULTS = 20


def search_with_ripgrep(
    keyword: str,
    workspace_root: Path,
    file_types: Optional[List[str]] = None,
) -> List[str]:
    """
    Search using ripgrep for fast results.
    
    Args:
        keyword: Search term
        workspace_root: Project root directory
        file_types: File extensions to search (default: py, json, md)
        
    Returns:
        List of file paths matching keyword (empty list if ripgrep unavailable)
    """
    if file_types is None:
        file_types = DEFAULT_FILE_TYPES
    
    try:
        cmd = ["rg", "-l", "--no-messages"]  # -l = files-with-matches
        # Use glob patterns instead of --type for broader compatibility
        for ft in file_types:
            cmd.extend(["-g", f"*.{ft}"])
        cmd.append(keyword)
        cmd.append(str(workspace_root))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SEARCH_TIMEOUT_SECONDS,
        )
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return []
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.debug(f"Ripgrep unavailable or timeout for keyword '{keyword}'")
        return []


def search_with_git_grep(
    keyword: str,
    workspace_root: Path,
) -> List[str]:
    """
    Fallback search using git grep.
    
    Args:
        keyword: Search term
        workspace_root: Project root directory
        
    Returns:
        List of file paths matching keyword (empty list if git unavailable or not a repo)
    """
    try:
        result = subprocess.run(
            ["git", "grep", "-l", keyword],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=SEARCH_TIMEOUT_SECONDS,
        )
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return []
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.debug(f"Git grep unavailable or timeout for keyword '{keyword}'")
        return []


def search_with_pathlib(
    keyword: str,
    workspace_root: Path,
    file_patterns: Optional[List[str]] = None,
) -> List[str]:
    """
    Slowest fallback using Python's Path.rglob.
    
    Args:
        keyword: Search term
        workspace_root: Project root directory
        file_patterns: Glob patterns to search (default: **/*.py, **/*.json, **/*.md)
        
    Returns:
        List of file paths containing keyword (limited to MAX_RESULTS)
    """
    if file_patterns is None:
        file_patterns = DEFAULT_FILE_PATTERNS
    
    matches = []
    keyword_lower = keyword.lower()
    
    for pattern in file_patterns:
        for file_path in workspace_root.glob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(errors="ignore")
                    if keyword_lower in content.lower():
                        matches.append(str(file_path))
                except Exception:
                    # Skip files that can't be read
                    continue
                    
                # Limit results to prevent memory issues
                if len(matches) >= MAX_RESULTS:
                    return matches
    
    return matches[:MAX_RESULTS]  # Ensure limit even if multiple patterns
