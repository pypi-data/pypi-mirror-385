"""
Code Quality Checker: Verify code quality patterns (docstrings, type hints, etc.).

Checks for code quality best practices in implementation files.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List


class CodeQualityChecker:
    """Check code quality patterns."""

    def __init__(self, codebase_root: Path):
        self.codebase_root = Path(codebase_root)

    def check_quality(self, files_changed: List[str]) -> Dict:
        """
        Check code quality for changed files.

        Args:
            files_changed: List of files to check

        Returns:
            Dictionary with quality check results
        """
        results = {
            "status": "PASS",
            "files_checked": len(files_changed),
            "issues": {
                "missing_docstrings": [],
                "missing_type_hints": [],
                "print_statements": [],
                "commented_code": [],
                "hardcoded_values": [],
            },
        }

        for file_path in files_changed:
            full_path = self.codebase_root / file_path

            # Only check Python files
            if not file_path.endswith(".py"):
                continue

            # Skip test files (less strict)
            if "test_" in file_path or "/tests/" in file_path:
                continue

            if full_path.exists():
                self._check_file(full_path, file_path, results["issues"])

        # Determine overall status
        total_issues = sum(len(issues) for issues in results["issues"].values())
        if total_issues > 0:
            results["status"] = "FAIL" if total_issues > 5 else "WARN"  # Warn for minor issues

        results["total_issues"] = total_issues
        return results

    def _check_file(self, file_path: Path, relative_path: str, issues: Dict[str, List]):
        """Check a single file for quality issues."""
        try:
            content = file_path.read_text()

            # Parse AST for docstrings and type hints
            try:
                tree = ast.parse(content)
                self._check_ast(tree, relative_path, issues)
            except SyntaxError:
                # If file has syntax errors, skip AST checks
                pass

            # Check for print statements
            self._check_print_statements(content, relative_path, issues)

            # Check for commented code
            self._check_commented_code(content, relative_path, issues)

            # Check for hardcoded values
            self._check_hardcoded_values(content, relative_path, issues)

        except Exception:
            # If file can't be read, skip it
            pass

    def _check_ast(self, tree: ast.AST, file_path: str, issues: Dict[str, List]):
        """Check AST for docstrings and type hints."""
        for node in ast.walk(tree):
            # Check classes
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    issues["missing_docstrings"].append(f"{file_path}:class {node.name}")

            # Check functions/methods
            elif isinstance(node, ast.FunctionDef):
                # Skip private functions (less strict)
                if not node.name.startswith("_"):
                    if not ast.get_docstring(node):
                        issues["missing_docstrings"].append(f"{file_path}:function {node.name}")

                    # Check type hints
                    if not node.returns and node.name not in ["__init__", "__str__", "__repr__"]:
                        issues["missing_type_hints"].append(f"{file_path}:function {node.name} (no return type)")

    def _check_print_statements(self, content: str, file_path: str, issues: Dict[str, List]):
        """Check for print statements (should use logging instead)."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue

            # Check for print statements
            if re.search(r"\bprint\s*\(", line):
                issues["print_statements"].append(f"{file_path}:{i}")

    def _check_commented_code(self, content: str, file_path: str, issues: Dict[str, List]):
        """Check for commented-out code."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for commented code patterns
            if stripped.startswith("#") and len(stripped) > 2:
                # Look for code-like patterns
                code_patterns = [
                    r"#\s*(def|class|import|from|if|for|while|return)",
                    r"#\s*\w+\s*=\s*",
                    r"#\s*\w+\.\w+\(",
                ]

                for pattern in code_patterns:
                    if re.search(pattern, stripped):
                        issues["commented_code"].append(f"{file_path}:{i}")
                        break

    def _check_hardcoded_values(self, content: str, file_path: str, issues: Dict[str, List]):
        """Check for potential hardcoded values."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comments and imports
            stripped = line.strip()
            if stripped.startswith("#") or "import " in stripped:
                continue

            # Check for hardcoded URLs
            if re.search(r"https?://[\w\./:-]+", line):
                # Exclude docstrings and common patterns
                if '"""' not in line and "'''" not in line:
                    issues["hardcoded_values"].append(f"{file_path}:{i} (URL)")

            # Check for hardcoded API keys (common patterns)
            if re.search(r'["\']sk-[a-zA-Z0-9]{40,}["\']', line):
                issues["hardcoded_values"].append(f"{file_path}:{i} (potential API key)")
