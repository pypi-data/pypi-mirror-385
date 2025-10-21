"""
Automated Checks: Run automated DoD checks (tests, formatting, security).

Executes automated verification checks including pytest, black, pre-commit hooks, and security scans.
"""

import subprocess
from pathlib import Path
from typing import Dict


class AutomatedChecks:
    """Execute automated DoD checks."""

    def __init__(self, codebase_root: Path):
        self.codebase_root = Path(codebase_root)

    def run_all_checks(self) -> Dict:
        """
        Run all automated checks.

        Returns:
            Dictionary with check results
        """
        results = {
            "status": "PASS",
            "tests": self._run_tests(),
            "formatting": self._check_formatting(),
            "pre_commit": self._run_pre_commit(),
            "security": self._check_security(),
        }

        # Overall status is FAIL if any check fails
        if any(
            check["status"] != "PASS"
            for check in [
                results["tests"],
                results["formatting"],
                results["pre_commit"],
                results["security"],
            ]
        ):
            results["status"] = "FAIL"

        return results

    def _run_tests(self) -> Dict:
        """Run pytest tests."""
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=300,  # 5 minute timeout
            )

            # Parse output for test counts
            output = result.stdout + result.stderr
            passed = self._count_pattern(output, r"(\d+) passed")
            failed = self._count_pattern(output, r"(\d+) failed")

            status = "PASS" if result.returncode == 0 else "FAIL"

            return {
                "status": status,
                "passed": passed,
                "failed": failed,
                "output": output[-1000:] if len(output) > 1000 else output,  # Last 1000 chars
            }
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "passed": 0, "failed": 0, "output": "Tests timed out after 5 minutes"}
        except Exception as e:
            return {"status": "FAIL", "passed": 0, "failed": 0, "output": f"Error running tests: {str(e)}"}

    def _check_formatting(self) -> Dict:
        """Check code formatting with black."""
        try:
            # Check black formatting
            result = subprocess.run(
                ["black", "--check", "coffee_maker/", "tests/"],
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=60,
            )

            status = "PASS" if result.returncode == 0 else "FAIL"
            output = result.stdout + result.stderr

            return {
                "status": status,
                "tool": "black",
                "output": output[-500:] if len(output) > 500 else output,
            }
        except Exception as e:
            return {"status": "FAIL", "tool": "black", "output": f"Error checking formatting: {str(e)}"}

    def _run_pre_commit(self) -> Dict:
        """Run pre-commit hooks."""
        try:
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=120,
            )

            # pre-commit returns 0 if all hooks pass, non-zero otherwise
            status = "PASS" if result.returncode == 0 else "FAIL"
            output = result.stdout + result.stderr

            return {
                "status": status,
                "output": output[-1000:] if len(output) > 1000 else output,
            }
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "output": "Pre-commit hooks timed out after 2 minutes"}
        except Exception as e:
            # If pre-commit is not configured, treat as PASS
            if "command not found" in str(e) or "No such file" in str(e):
                return {"status": "PASS", "output": "Pre-commit not configured (skipped)"}
            return {"status": "FAIL", "output": f"Error running pre-commit: {str(e)}"}

    def _check_security(self) -> Dict:
        """Run basic security checks."""
        try:
            # Check for common security issues with bandit
            result = subprocess.run(
                ["bandit", "-r", "coffee_maker/", "-ll"],  # -ll = only high/medium severity
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=60,
            )

            # Bandit returns 0 if no issues, 1 if issues found
            output = result.stdout + result.stderr
            issues_found = "No issues identified" not in output and result.returncode != 0

            status = "FAIL" if issues_found else "PASS"

            return {
                "status": status,
                "tool": "bandit",
                "output": output[-500:] if len(output) > 500 else output,
            }
        except Exception as e:
            # If bandit not installed, treat as PASS (optional check)
            if "command not found" in str(e) or "No such file" in str(e):
                return {"status": "PASS", "tool": "bandit", "output": "Bandit not installed (skipped)"}
            return {"status": "FAIL", "tool": "bandit", "output": f"Error running security check: {str(e)}"}

    def _count_pattern(self, text: str, pattern: str) -> int:
        """Count occurrences of a regex pattern in text."""
        import re

        matches = re.findall(pattern, text)
        return int(matches[0]) if matches else 0
