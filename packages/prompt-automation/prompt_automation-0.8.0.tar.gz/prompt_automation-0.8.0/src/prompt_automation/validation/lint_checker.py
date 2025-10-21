"""Lint checker for validation runner.

Runs flake8 and pylint for code quality checks.
"""

import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

LINT_TIMEOUT = 120  # 2 minutes


def check_flake8() -> Tuple[bool, int, str]:
    """
    Run flake8 style checker.
    
    Returns:
        Tuple of (passed, error_count, output)
    """
    try:
        result = subprocess.run(
            ["flake8", "src/"],
            capture_output=True,
            text=True,
            timeout=LINT_TIMEOUT
        )
        
        passed = result.returncode == 0
        error_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        
        logger.info(f"flake8: {error_count} errors")
        
        return passed, error_count, result.stdout
        
    except subprocess.TimeoutExpired:
        return False, -1, "flake8 timed out"
    except FileNotFoundError:
        return False, -1, "flake8 not found - is it installed?"
    except Exception as e:
        return False, -1, f"flake8 failed: {e}"


def check_pylint() -> Tuple[bool, int, str]:
    """
    Run pylint for function complexity.
    
    Returns:
        Tuple of (passed, error_count, output)
    """
    try:
        result = subprocess.run(
            [
                "pylint",
                "src/",
                "--disable=all",
                "--enable=too-many-lines,too-many-statements"
            ],
            capture_output=True,
            text=True,
            timeout=LINT_TIMEOUT
        )
        
        # pylint returns 0 if no issues
        passed = result.returncode == 0
        
        # Count errors in output
        error_count = result.stdout.count("E:")
        
        logger.info(f"pylint: {error_count} complexity errors")
        
        return passed, error_count, result.stdout
        
    except subprocess.TimeoutExpired:
        return False, -1, "pylint timed out"
    except FileNotFoundError:
        # pylint is optional
        logger.warning("pylint not found, skipping complexity check")
        return True, 0, "pylint not installed (skipped)"
    except Exception as e:
        return False, -1, f"pylint failed: {e}"


def check_lint() -> Tuple[bool, str]:
    """
    Run all lint checks.
    
    Returns:
        Tuple of (all_passed, combined_output)
    """
    flake8_pass, flake8_count, flake8_out = check_flake8()
    pylint_pass, pylint_count, pylint_out = check_pylint()
    
    all_passed = flake8_pass and pylint_pass
    
    combined = f"flake8: {flake8_count} errors\n{flake8_out}\n\n"
    combined += f"pylint: {pylint_count} errors\n{pylint_out}"
    
    return all_passed, combined
