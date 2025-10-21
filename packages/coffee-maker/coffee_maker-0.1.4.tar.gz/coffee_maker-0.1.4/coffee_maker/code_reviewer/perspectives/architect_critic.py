"""Architect Critic perspective - Reviews architecture and design using Claude.

This perspective focuses on:
- Design patterns and anti-patterns
- SOLID principles adherence
- Code organization and structure
- Coupling and cohesion
- Abstraction levels
- Architectural smells
"""

import re
from typing import List

from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.models import ReviewIssue


class ArchitectCritic(BasePerspective):
    """Reviews code architecture and design patterns.

    Uses Claude (or mock analysis) to evaluate:
    - Design patterns usage
    - SOLID principles
    - Code organization
    - Coupling/cohesion
    - Abstraction quality

    Example:
        >>> critic = ArchitectCritic()
        >>> issues = critic.analyze(code_content, "module.py")
        >>> architectural_issues = [i for i in issues if i.category == "architecture"]
    """

    def __init__(self, model_name: str = "claude-sonnet-4"):
        """Initialize Architect Critic.

        Args:
            model_name: Claude model to use (default: claude-sonnet-4)
        """
        super().__init__(model_name=model_name, perspective_name="Architect Critic")

    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code architecture and design.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of architectural issues found
        """
        issues = []

        # Mock analysis - In production, this would call Claude API
        issues.extend(self._check_class_size(code_content))
        issues.extend(self._check_function_complexity(code_content))
        issues.extend(self._check_solid_principles(code_content))
        issues.extend(self._check_coupling(code_content))

        self.last_analysis_summary = (
            f"Analyzed {len(code_content.splitlines())} lines, found {len(issues)} architectural concerns"
        )

        return issues

    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code asynchronously.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of architectural issues found
        """
        return self.analyze(code_content, file_path)

    def _check_class_size(self, code: str) -> List[ReviewIssue]:
        """Check for overly large classes (God Object anti-pattern).

        Args:
            code: Code to analyze

        Returns:
            List of class size issues
        """
        issues = []

        lines = code.splitlines()
        in_class = False
        class_name = ""
        class_start = 0
        class_line_count = 0

        for i, line in enumerate(lines, 1):
            # Detect class definition
            class_match = re.match(r"^class\s+(\w+)", line)
            if class_match:
                if in_class and class_line_count > 300:
                    # Previous class was too large
                    issues.append(
                        self._create_issue(
                            severity="medium",
                            category="architecture",
                            title=f"Large class: {class_name}",
                            description=f"Class has {class_line_count} lines. Classes over 300 lines may violate Single Responsibility Principle",
                            line_number=class_start,
                            suggestion="Consider splitting into smaller, more focused classes",
                        )
                    )

                in_class = True
                class_name = class_match.group(1)
                class_start = i
                class_line_count = 0

            if in_class:
                class_line_count += 1

        # Check last class
        if in_class and class_line_count > 300:
            issues.append(
                self._create_issue(
                    severity="medium",
                    category="architecture",
                    title=f"Large class: {class_name}",
                    description=f"Class has {class_line_count} lines. Classes over 300 lines may violate Single Responsibility Principle",
                    line_number=class_start,
                    suggestion="Consider splitting into smaller, more focused classes",
                )
            )

        return issues

    def _check_function_complexity(self, code: str) -> List[ReviewIssue]:
        """Check for overly complex functions.

        Args:
            code: Code to analyze

        Returns:
            List of function complexity issues
        """
        issues = []

        lines = code.splitlines()
        in_function = False
        function_name = ""
        function_start = 0
        function_line_count = 0
        indent_level = 0

        for i, line in enumerate(lines, 1):
            # Detect function definition
            func_match = re.match(r"^(\s*)def\s+(\w+)", line)
            if func_match:
                if in_function and function_line_count > 50:
                    issues.append(
                        self._create_issue(
                            severity="medium",
                            category="architecture",
                            title=f"Complex function: {function_name}",
                            description=f"Function has {function_line_count} lines. Functions over 50 lines are harder to test and maintain",
                            line_number=function_start,
                            suggestion="Consider breaking into smaller functions with clear responsibilities",
                        )
                    )

                in_function = True
                function_name = func_match.group(2)
                function_start = i
                function_line_count = 0
                indent_level = len(func_match.group(1))

            elif in_function:
                # Check if we've exited the function (decreased indent to function level or less)
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level:
                    if function_line_count > 50:
                        issues.append(
                            self._create_issue(
                                severity="medium",
                                category="architecture",
                                title=f"Complex function: {function_name}",
                                description=f"Function has {function_line_count} lines. Functions over 50 lines are harder to test and maintain",
                                line_number=function_start,
                                suggestion="Consider breaking into smaller functions with clear responsibilities",
                            )
                        )
                    in_function = False
                else:
                    function_line_count += 1

        return issues

    def _check_solid_principles(self, code: str) -> List[ReviewIssue]:
        """Check for SOLID principle violations.

        Args:
            code: Code to analyze

        Returns:
            List of SOLID violation issues
        """
        issues = []

        # Check for Multiple Responsibility (count methods in class)
        lines = code.splitlines()
        in_class = False
        class_name = ""
        class_start = 0
        method_count = 0

        for i, line in enumerate(lines, 1):
            class_match = re.match(r"^class\s+(\w+)", line)
            if class_match:
                if in_class and method_count > 10:
                    issues.append(
                        self._create_issue(
                            severity="low",
                            category="architecture",
                            title=f"Many responsibilities: {class_name}",
                            description=f"Class has {method_count} methods. May indicate multiple responsibilities (SRP violation)",
                            line_number=class_start,
                            suggestion="Consider if this class has multiple reasons to change. Split if necessary",
                        )
                    )

                in_class = True
                class_name = class_match.group(1)
                class_start = i
                method_count = 0

            elif in_class and re.match(r"^\s+def\s+", line):
                method_count += 1

        return issues

    def _check_coupling(self, code: str) -> List[ReviewIssue]:
        """Check for tight coupling issues.

        Args:
            code: Code to analyze

        Returns:
            List of coupling issues
        """
        issues = []

        # Count imports - many imports may indicate high coupling
        import_count = len([line for line in code.splitlines() if line.strip().startswith(("import ", "from "))])

        if import_count > 20:
            issues.append(
                self._create_issue(
                    severity="low",
                    category="architecture",
                    title="High coupling detected",
                    description=f"Module has {import_count} imports. High import count may indicate tight coupling",
                    line_number=1,
                    suggestion="Consider dependency injection or facade patterns to reduce coupling",
                )
            )

        return issues
