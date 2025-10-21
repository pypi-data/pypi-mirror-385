"""Size checker for validation runner.

Uses AST parsing (Pattern 8) for accurate function size detection.
"""

import ast
import logging
from pathlib import Path
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

MAX_FILE_LOC = 400
MAX_FUNCTION_LOC = 75


def check_file_sizes(src_dir: Path = Path("src/prompt_automation")) -> Tuple[bool, List[Dict[str, int]]]:
    """
    Check all Python files meet size limits.
    
    Args:
        src_dir: Directory to scan
        
    Returns:
        Tuple of (all_passed, violations_list)
    """
    violations = []
    
    for py_file in src_dir.rglob("*.py"):
        try:
            lines = py_file.read_text().splitlines()
            loc = len(lines)
            
            if loc > MAX_FILE_LOC:
                violations.append({
                    "file": str(py_file),
                    "loc": loc,
                    "limit": MAX_FILE_LOC
                })
                logger.warning(f"{py_file}: {loc} LOC (limit: {MAX_FILE_LOC})")
        
        except Exception as e:
            logger.error(f"Failed to check {py_file}: {e}")
    
    all_passed = len(violations) == 0
    return all_passed, violations


def check_function_sizes(src_dir: Path = Path("src/prompt_automation")) -> Tuple[bool, List[Dict[str, int]]]:
    """
    Check all functions meet size limits using AST (Pattern 8).
    
    Args:
        src_dir: Directory to scan
        
    Returns:
        Tuple of (all_passed, violations_list)
    """
    violations = []
    
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Calculate function LOC using AST node positions
                    func_start = node.lineno
                    func_end = node.end_lineno or func_start
                    func_loc = func_end - func_start + 1
                    
                    if func_loc > MAX_FUNCTION_LOC:
                        violations.append({
                            "file": str(py_file),
                            "function": node.name,
                            "loc": func_loc,
                            "limit": MAX_FUNCTION_LOC,
                            "line": func_start
                        })
                        logger.warning(f"{py_file}:{node.name}() {func_loc} LOC (limit: {MAX_FUNCTION_LOC})")
        
        except SyntaxError as e:
            logger.error(f"Syntax error in {py_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to parse {py_file}: {e}")
    
    all_passed = len(violations) == 0
    return all_passed, violations
