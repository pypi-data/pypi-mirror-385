"""
Documentation Checker: Verify documentation completeness.

Checks that code documentation, user documentation, and technical documentation are complete.
"""

from pathlib import Path
from typing import Dict, List


class DocumentationChecker:
    """Check documentation completeness."""

    def __init__(self, codebase_root: Path):
        self.codebase_root = Path(codebase_root)

    def check_documentation(self, files_changed: List[str]) -> Dict:
        """
        Check documentation for changed files.

        Args:
            files_changed: List of files changed

        Returns:
            Dictionary with documentation check results
        """
        results = {
            "status": "PASS",
            "code_docs": "PASS",
            "user_docs": "NOT_APPLICABLE",
            "technical_docs": "NOT_APPLICABLE",
            "missing_docs": [],
        }

        # Check if code documentation exists
        code_issues = self._check_code_documentation(files_changed)
        if code_issues:
            results["code_docs"] = "FAIL"
            results["missing_docs"].extend(code_issues)
            results["status"] = "FAIL"

        # Check if user-facing changes require user documentation
        if self._has_user_facing_changes(files_changed):
            user_docs_ok = self._check_user_documentation()
            results["user_docs"] = "PASS" if user_docs_ok else "WARN"
            if not user_docs_ok:
                results["missing_docs"].append("User documentation may need updating (README, guides)")

        # Check if architectural changes require technical documentation
        if self._has_architectural_changes(files_changed):
            tech_docs_ok = self._check_technical_documentation()
            results["technical_docs"] = "PASS" if tech_docs_ok else "WARN"
            if not tech_docs_ok:
                results["missing_docs"].append("Technical documentation may need updating (ADRs, specs)")

        return results

    def _check_code_documentation(self, files_changed: List[str]) -> List[str]:
        """Check if code files have proper documentation."""
        issues = []

        for file_path in files_changed:
            # Only check Python files
            if not file_path.endswith(".py"):
                continue

            # Skip test files and __init__.py
            if "test_" in file_path or file_path.endswith("__init__.py"):
                continue

            full_path = self.codebase_root / file_path

            if full_path.exists():
                try:
                    content = full_path.read_text()

                    # Check for module docstring
                    if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                        issues.append(f"{file_path}: Missing module docstring")

                except Exception:
                    pass

        return issues

    def _has_user_facing_changes(self, files_changed: List[str]) -> bool:
        """Check if changes are user-facing (CLI, UI, API)."""
        user_facing_patterns = ["cli/", "api/", "streamlit", "app.py", "main.py"]

        return any(pattern in file_path for file_path in files_changed for pattern in user_facing_patterns)

    def _has_architectural_changes(self, files_changed: List[str]) -> bool:
        """Check if changes are architectural."""
        architectural_patterns = ["autonomous/agents/", "daemon", "mixins", "agent_registry"]

        return any(pattern in file_path for file_path in files_changed for pattern in architectural_patterns)

    def _check_user_documentation(self) -> bool:
        """Check if user documentation exists."""
        # Check if README was updated recently (simple heuristic)
        readme = self.codebase_root / "README.md"

        if readme.exists():
            # For now, assume README is up to date if it exists
            # More sophisticated check would look at git history
            return True

        return False

    def _check_technical_documentation(self) -> bool:
        """Check if technical documentation exists."""
        # Check for ADRs or specs in architecture directory
        specs_dir = self.codebase_root / "docs" / "architecture" / "specs"
        adrs_dir = self.codebase_root / "docs" / "architecture" / "decisions"

        # If directories exist, assume documentation is being maintained
        return specs_dir.exists() and adrs_dir.exists()
