"""Coverage checker for validation runner.

Runs pytest with coverage and validates against threshold.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

COVERAGE_THRESHOLD = 85.0
COVERAGE_JSON = Path("coverage.json")
COVERAGE_TIMEOUT = 300  # 5 minutes


def check_coverage() -> Tuple[bool, float, str]:
    """
    Check test coverage meets threshold.
    
    Returns:
        Tuple of (passed, coverage_percent, report)
    """
    try:
        # Run pytest with coverage
        result = subprocess.run(
            [
                "pytest",
                "--cov=src/prompt_automation",
                "--cov-report=json",
                "--cov-report=term-missing"
            ],
            capture_output=True,
            text=True,
            timeout=COVERAGE_TIMEOUT
        )
        
        # Parse coverage JSON
        if not COVERAGE_JSON.exists():
            return False, 0.0, "Coverage report not generated"
        
        with open(COVERAGE_JSON) as f:
            cov_data = json.load(f)
        
        total_coverage = cov_data["totals"]["percent_covered"]
        
        passed = total_coverage >= COVERAGE_THRESHOLD
        
        logger.info(f"Coverage: {total_coverage:.1f}% (threshold: {COVERAGE_THRESHOLD}%)")
        
        return passed, total_coverage, result.stdout
        
    except subprocess.TimeoutExpired:
        return False, 0.0, "Coverage check timed out"
    except FileNotFoundError:
        return False, 0.0, "pytest or coverage tool not found"
    except KeyError as e:
        return False, 0.0, f"Coverage JSON format unexpected: {e}"
    except Exception as e:
        return False, 0.0, f"Coverage check failed: {e}"
