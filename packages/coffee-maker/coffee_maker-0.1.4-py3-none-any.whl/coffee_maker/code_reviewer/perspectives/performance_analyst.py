"""Performance Analyst perspective - Analyzes performance issues using Gemini.

This perspective focuses on:
- Algorithmic complexity (O(n²), etc.)
- Inefficient loops and iterations
- Memory usage patterns
- Database query optimization
- Caching opportunities
- I/O bottlenecks
"""

import re
from typing import List

from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.models import ReviewIssue


class PerformanceAnalyst(BasePerspective):
    """Analyzes code for performance issues and optimization opportunities.

    Uses Gemini (or mock analysis) to identify:
    - Algorithm complexity issues
    - Inefficient iterations
    - Memory waste
    - I/O inefficiencies
    - Missing caching

    Example:
        >>> analyst = PerformanceAnalyst()
        >>> issues = analyst.analyze(code_content, "service.py")
        >>> perf_issues = [i for i in issues if i.category == "performance"]
    """

    def __init__(self, model_name: str = "gemini-pro"):
        """Initialize Performance Analyst.

        Args:
            model_name: Gemini model to use (default: gemini-pro)
        """
        super().__init__(model_name=model_name, perspective_name="Performance Analyst")

    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code for performance issues.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of performance issues found
        """
        issues = []

        # Mock analysis - In production, this would call Gemini API
        issues.extend(self._check_nested_loops(code_content))
        issues.extend(self._check_list_operations(code_content))
        issues.extend(self._check_string_concatenation(code_content))
        issues.extend(self._check_database_queries(code_content))

        self.last_analysis_summary = (
            f"Analyzed {len(code_content.splitlines())} lines, found {len(issues)} performance concerns"
        )

        return issues

    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code asynchronously.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of performance issues found
        """
        return self.analyze(code_content, file_path)

    def _check_nested_loops(self, code: str) -> List[ReviewIssue]:
        """Check for nested loops that may cause O(n²) or worse complexity.

        Args:
            code: Code to analyze

        Returns:
            List of nested loop issues
        """
        issues = []

        lines = code.splitlines()
        loop_depth = 0
        loop_stack = []

        for i, line in enumerate(lines, 1):
            indent = len(line) - len(line.lstrip())

            # Detect loop start
            if re.search(r"^\s*for\s+", line) or re.search(r"^\s*while\s+", line):
                loop_depth += 1
                loop_stack.append((i, indent, line.strip()))

                # Flag if nesting is deep
                if loop_depth >= 3:
                    issues.append(
                        self._create_issue(
                            severity="high",
                            category="performance",
                            title="Deep loop nesting detected",
                            description=f"Loop nesting depth of {loop_depth} may cause O(n^{loop_depth}) complexity",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Consider algorithmic optimization or caching to reduce complexity",
                        )
                    )

            # Detect when we exit a loop (indent decreases)
            if loop_stack and indent <= loop_stack[-1][1] and line.strip():
                loop_stack.pop()
                loop_depth = max(0, loop_depth - 1)

        return issues

    def _check_list_operations(self, code: str) -> List[ReviewIssue]:
        """Check for inefficient list operations.

        Args:
            code: Code to analyze

        Returns:
            List of list operation issues
        """
        issues = []

        # Check for list concatenation in loops
        lines = code.splitlines()
        in_loop = False

        for i, line in enumerate(lines, 1):
            if re.search(r"^\s*for\s+", line):
                in_loop = True

            # Check for += with lists in loop
            if in_loop and "+=" in line and ("[" in line or "list" in line.lower()):
                issues.append(
                    self._create_issue(
                        severity="medium",
                        category="performance",
                        title="List concatenation in loop",
                        description="Using += to concatenate lists in a loop is O(n²). Each concatenation creates a new list",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Use list.append() or list comprehension instead",
                    )
                )

            # Check for membership testing in list (should use set)
            if "in [" in line or "not in [" in line:
                issues.append(
                    self._create_issue(
                        severity="low",
                        category="performance",
                        title="List membership testing",
                        description="Membership testing in list is O(n). Use set for O(1) lookups",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Convert to set: if item in set(items):",
                    )
                )

            # Reset loop flag when we exit
            if in_loop and line and not line[0].isspace():
                in_loop = False

        return issues

    def _check_string_concatenation(self, code: str) -> List[ReviewIssue]:
        """Check for inefficient string concatenation.

        Args:
            code: Code to analyze

        Returns:
            List of string concatenation issues
        """
        issues = []

        lines = code.splitlines()
        in_loop = False

        for i, line in enumerate(lines, 1):
            if re.search(r"^\s*for\s+", line):
                in_loop = True

            # Check for string concatenation in loop
            if in_loop and "+=" in line and ('"' in line or "'" in line):
                issues.append(
                    self._create_issue(
                        severity="medium",
                        category="performance",
                        title="String concatenation in loop",
                        description="String concatenation with += in loop is inefficient. Strings are immutable",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Use list.append() and ''.join() at the end, or use io.StringIO",
                    )
                )

            if in_loop and line and not line[0].isspace():
                in_loop = False

        return issues

    def _check_database_queries(self, code: str) -> List[ReviewIssue]:
        """Check for N+1 query problems and missing eager loading.

        Args:
            code: Code to analyze

        Returns:
            List of database query issues
        """
        issues = []

        lines = code.splitlines()
        in_loop = False

        for i, line in enumerate(lines, 1):
            if re.search(r"^\s*for\s+", line):
                in_loop = True

            # Check for database queries in loop
            if in_loop and (
                ".query(" in line
                or ".filter(" in line
                or ".get(" in line
                or "SELECT" in line.upper()
                or "execute(" in line
            ):
                issues.append(
                    self._create_issue(
                        severity="critical",
                        category="performance",
                        title="Database query in loop (N+1 problem)",
                        description="Executing queries in a loop causes N+1 query problem. This can severely impact performance",
                        line_number=i,
                        code_snippet=line.strip(),
                        suggestion="Use eager loading, batch queries, or prefetch data before the loop",
                    )
                )

            if in_loop and line and not line[0].isspace():
                in_loop = False

        return issues
