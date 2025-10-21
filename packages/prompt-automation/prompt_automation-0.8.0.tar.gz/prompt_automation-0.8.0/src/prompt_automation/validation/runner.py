"""Validation runner for automated quality checks.

Uses parallel execution (Pattern 9) for independent checks.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .test_executor import run_pytest_with_retry
from .coverage_checker import check_coverage
from .lint_checker import check_lint
from .size_checker import check_file_sizes, check_function_sizes

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any]


class ValidationRunner:
    """Runs all validation checks for feature branches."""
    
    def run_all(self, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete validation suite in parallel.
        
        Args:
            branch: Feature branch name (for logging only)
            
        Returns:
            Dict with all validation results and overall pass/fail
        """
        logger.info(f"Starting validation for branch: {branch or 'current'}")
        
        results = {
            "branch": branch,
            "all_passed": False,
            "tests": None,
            "coverage": None,
            "lint": None,
            "file_sizes": None,
            "function_sizes": None
        }
        
        # Run checks in parallel (Pattern 9)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._run_tests): "tests",
                executor.submit(self._check_coverage): "coverage",
                executor.submit(self._check_lint): "lint"
            }
            
            for future in as_completed(futures):
                check_name = futures[future]
                try:
                    result = future.result()
                    results[check_name] = asdict(result)
                except Exception as e:
                    logger.error(f"{check_name} check failed: {e}")
                    results[check_name] = {
                        "check_name": check_name,
                        "passed": False,
                        "message": f"Check crashed: {e}",
                        "details": {}
                    }
        
        # Run size checks (fast, sequential)
        results["file_sizes"] = asdict(self._check_file_sizes())
        results["function_sizes"] = asdict(self._check_function_sizes())
        
        # Determine overall pass/fail
        results["all_passed"] = all(
            results[key]["passed"]
            for key in ["tests", "coverage", "lint", "file_sizes", "function_sizes"]
            if results[key] is not None
        )
        
        logger.info(f"Validation {'PASSED' if results['all_passed'] else 'FAILED'}")
        
        return results
    
    def _run_tests(self) -> ValidationResult:
        """Run pytest with retry."""
        passed, stdout, stderr = run_pytest_with_retry()
        
        return ValidationResult(
            check_name="tests",
            passed=passed,
            message="All tests passed" if passed else "Tests failed",
            details={"stdout": stdout, "stderr": stderr}
        )
    
    def _check_coverage(self) -> ValidationResult:
        """Check coverage threshold."""
        passed, coverage_pct, report = check_coverage()
        
        return ValidationResult(
            check_name="coverage",
            passed=passed,
            message=f"Coverage: {coverage_pct:.1f}%",
            details={"coverage_percent": coverage_pct, "report": report}
        )
    
    def _check_lint(self) -> ValidationResult:
        """Run lint checks."""
        passed, output = check_lint()
        
        return ValidationResult(
            check_name="lint",
            passed=passed,
            message="Lint checks passed" if passed else "Lint errors found",
            details={"output": output}
        )
    
    def _check_file_sizes(self) -> ValidationResult:
        """Check file size limits."""
        passed, violations = check_file_sizes()
        
        return ValidationResult(
            check_name="file_sizes",
            passed=passed,
            message=f"{len(violations)} files exceed 400 LOC" if violations else "All files within limits",
            details={"violations": violations}
        )
    
    def _check_function_sizes(self) -> ValidationResult:
        """Check function size limits."""
        passed, violations = check_function_sizes()
        
        return ValidationResult(
            check_name="function_sizes",
            passed=passed,
            message=f"{len(violations)} functions exceed 75 LOC" if violations else "All functions within limits",
            details={"violations": violations}
        )
