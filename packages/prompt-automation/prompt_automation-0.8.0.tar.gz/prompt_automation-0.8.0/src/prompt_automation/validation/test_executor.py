"""Test executor for validation runner.

Runs pytest with timeout and retry logic to catch flaky tests.
"""

import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

PYTEST_TIMEOUT = 300  # 5 minutes


def run_pytest() -> Tuple[bool, str, str]:
    """
    Run pytest and return results.
    
    Returns:
        Tuple of (passed, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["pytest", "-q", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=PYTEST_TIMEOUT
        )
        
        passed = result.returncode == 0
        
        logger.info(f"pytest {'PASSED' if passed else 'FAILED'}")
        
        return passed, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"Tests timed out after {PYTEST_TIMEOUT} seconds"
        logger.error(error_msg)
        return False, "", error_msg
    except FileNotFoundError:
        error_msg = "pytest not found - is it installed?"
        logger.error(error_msg)
        return False, "", error_msg
    except Exception as e:
        error_msg = f"pytest execution failed: {e}"
        logger.error(error_msg)
        return False, "", error_msg


def run_pytest_with_retry() -> Tuple[bool, str, str]:
    """
    Run pytest twice if first run fails (catch flaky tests).
    
    Returns:
        Tuple of (passed, stdout, stderr)
    """
    # First attempt
    passed_1, stdout_1, stderr_1 = run_pytest()
    
    if passed_1:
        return True, stdout_1, stderr_1
    
    # Retry on failure
    logger.warning("Tests failed, retrying once to catch flaky tests...")
    passed_2, stdout_2, stderr_2 = run_pytest()
    
    if passed_2:
        logger.warning("Tests passed on retry - possible flaky tests detected")
        return True, stdout_2, stderr_2
    
    # Both runs failed - combine outputs
    combined_stdout = stdout_1 + "\n\n" + stdout_2
    combined_stderr = stderr_1 + "\n\n" + stderr_2
    
    return False, combined_stdout, combined_stderr
