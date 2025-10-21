"""Bug Hunter perspective - Identifies bugs and logical errors using GPT-4.

This perspective focuses on:
- Logic errors and edge cases
- Type mismatches
- Null/None dereferences
- Off-by-one errors
- Resource leaks
- Exception handling issues
"""

import re
from typing import List

from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.models import ReviewIssue


class BugHunter(BasePerspective):
    """Identifies bugs and logical errors in code.

    Uses GPT-4 (or mock analysis) to detect:
    - Logic errors
    - Edge case handling
    - Type safety issues
    - Resource management
    - Exception handling

    Example:
        >>> hunter = BugHunter()
        >>> issues = hunter.analyze(code_content, "app.py")
        >>> print(f"Found {len(issues)} potential bugs")
    """

    def __init__(self, model_name: str = "gpt-4-turbo"):
        """Initialize Bug Hunter.

        Args:
            model_name: GPT model to use (default: gpt-4-turbo)
        """
        super().__init__(model_name=model_name, perspective_name="Bug Hunter")

    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code for potential bugs.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of bug issues found
        """
        issues = []

        # Mock analysis - In production, this would call GPT-4 API
        # For now, we do pattern-based detection

        # Check for common bug patterns
        issues.extend(self._check_exception_handling(code_content))
        issues.extend(self._check_resource_leaks(code_content))
        issues.extend(self._check_null_dereference(code_content))
        issues.extend(self._check_type_issues(code_content))

        self.last_analysis_summary = (
            f"Analyzed {len(code_content.splitlines())} lines, found {len(issues)} potential bugs"
        )

        return issues

    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code asynchronously.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of bug issues found
        """
        # For async, we'd call the API asynchronously
        # For now, just delegate to sync version
        return self.analyze(code_content, file_path)

    def _check_exception_handling(self, code: str) -> List[ReviewIssue]:
        """Check for bare except clauses and missing exception handling.

        Args:
            code: Code to analyze

        Returns:
            List of exception handling issues
        """
        issues = []

        # Check for bare except
        bare_except_pattern = r"^\s*except\s*:\s*$"
        for i, line in enumerate(code.splitlines(), 1):
            if re.search(bare_except_pattern, line):
                issues.append(
                    self._create_issue(
                        severity="medium",
                        category="bug",
                        title="Bare except clause",
                        description="Bare except catches all exceptions including system exits and keyboard interrupts",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Specify exception type: except Exception: or except ValueError:",
                    )
                )

        return issues

    def _check_resource_leaks(self, code: str) -> List[ReviewIssue]:
        """Check for file opens without context managers.

        Args:
            code: Code to analyze

        Returns:
            List of resource leak issues
        """
        issues = []

        # Check for open() without "with"
        # Look for: variable = open(...) not preceded by "with"
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            if "open(" in line and "with" not in line and "=" in line:
                # Check if previous lines don't have "with" for this statement
                if i == 1 or "with" not in lines[i - 2]:
                    issues.append(
                        self._create_issue(
                            severity="high",
                            category="bug",
                            title="Potential resource leak",
                            description="File opened without context manager may not be properly closed",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Use: with open(...) as f: to ensure file is properly closed",
                        )
                    )

        return issues

    def _check_null_dereference(self, code: str) -> List[ReviewIssue]:
        """Check for potential None dereference.

        Args:
            code: Code to analyze

        Returns:
            List of null dereference issues
        """
        issues = []

        # Check for .get() followed by attribute access without None check
        # This is a simplified check - real implementation would use AST
        get_pattern = r'\.get\(["\'][\w]+["\']\)(\.|\[)'
        for i, line in enumerate(code.splitlines(), 1):
            if re.search(get_pattern, line) and "if" not in line and "or {}" not in line:
                issues.append(
                    self._create_issue(
                        severity="high",
                        category="bug",
                        title="Potential None dereference",
                        description="Calling .get() can return None, which is then dereferenced",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Add None check or use .get() with default value",
                    )
                )

        return issues

    def _check_type_issues(self, code: str) -> List[ReviewIssue]:
        """Check for potential type-related issues.

        Args:
            code: Code to analyze

        Returns:
            List of type-related issues
        """
        issues = []

        # Check for string concatenation with non-strings
        for i, line in enumerate(code.splitlines(), 1):
            # Look for + operator with mixed types
            if "+" in line and "str(" not in line:
                # Simplified check - would need AST for accuracy
                if '"' in line and "int(" in line:
                    issues.append(
                        self._create_issue(
                            severity="medium",
                            category="bug",
                            title="Potential type mismatch in concatenation",
                            description="Mixing strings and integers in concatenation may cause TypeError",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Convert to string: str(value) before concatenation",
                        )
                    )

        return issues
