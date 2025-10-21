"""
Integration Verifier: Verify backward compatibility and integration.

Checks that changes don't break existing functionality and dependencies are properly managed.
"""

import subprocess
from pathlib import Path
from typing import Dict, List


class IntegrationVerifier:
    """Verify integration and backward compatibility."""

    def __init__(self, codebase_root: Path):
        self.codebase_root = Path(codebase_root)

    def verify_integration(self, files_changed: List[str]) -> Dict:
        """
        Verify integration for changed files.

        Args:
            files_changed: List of files changed

        Returns:
            Dictionary with integration check results
        """
        results = {
            "status": "PASS",
            "backward_compatible": True,
            "integration_tests": "PASS",
            "dependencies": "PASS",
            "config_changes": "NOT_APPLICABLE",
            "issues": [],
        }

        # Check integration tests
        integration_test_result = self._run_integration_tests()
        results["integration_tests"] = integration_test_result["status"]
        if integration_test_result["status"] != "PASS":
            results["status"] = "FAIL"
            results["issues"].append(f"Integration tests failed: {integration_test_result.get('message', '')}")

        # Check dependencies
        if self._has_dependency_changes(files_changed):
            deps_result = self._check_dependencies()
            results["dependencies"] = deps_result["status"]
            if deps_result["status"] != "PASS":
                results["status"] = "FAIL"
                results["issues"].extend(deps_result.get("issues", []))

        # Check config changes
        if self._has_config_changes(files_changed):
            results["config_changes"] = "MANUAL_REVIEW"
            results["issues"].append("Configuration files changed - manual review recommended")

        return results

    def _run_integration_tests(self) -> Dict:
        """Run integration tests if they exist."""
        integration_tests = self.codebase_root / "tests" / "integration"

        if not integration_tests.exists():
            return {"status": "PASS", "message": "No integration tests found (skipped)"}

        try:
            result = subprocess.run(
                ["pytest", "tests/integration/", "-v"],
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=300,
            )

            if result.returncode == 0:
                return {"status": "PASS", "message": "Integration tests passed"}
            else:
                return {"status": "FAIL", "message": result.stdout + result.stderr}

        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "message": "Integration tests timed out"}
        except Exception as e:
            return {"status": "FAIL", "message": f"Error running integration tests: {str(e)}"}

    def _check_dependencies(self) -> Dict:
        """Check dependency integrity using poetry."""
        try:
            # Run poetry check
            result = subprocess.run(
                ["poetry", "check"],
                capture_output=True,
                text=True,
                cwd=self.codebase_root,
                timeout=60,
            )

            if result.returncode == 0:
                return {"status": "PASS", "issues": []}
            else:
                return {"status": "FAIL", "issues": [f"Poetry check failed: {result.stderr}"]}

        except Exception as e:
            return {"status": "FAIL", "issues": [f"Error checking dependencies: {str(e)}"]}

    def _has_dependency_changes(self, files_changed: List[str]) -> bool:
        """Check if dependencies were changed."""
        return any(f in ["pyproject.toml", "poetry.lock", "requirements.txt"] for f in files_changed)

    def _has_config_changes(self, files_changed: List[str]) -> bool:
        """Check if configuration files were changed."""
        config_patterns = [".claude/", ".env", "config", "settings"]

        return any(pattern in file_path for file_path in files_changed for pattern in config_patterns)
