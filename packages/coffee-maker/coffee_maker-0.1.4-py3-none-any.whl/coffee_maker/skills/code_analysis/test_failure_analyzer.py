"""
Test Failure Analysis Skill

Rapidly analyze pytest failures, identify root causes, and suggest fixes.

Capabilities:
- parse_pytest_output: Parse pytest output to extract failures
- categorize_failures: Categorize failures by type (import, assertion, etc.)
- correlate_with_changes: Correlate failures with recent code changes
- generate_fix_recommendations: Suggest fixes with code snippets
- estimate_fix_time: Estimate time required to fix each failure

Used by: code_developer agent during implementation and testing

Time Savings: 30-60 minutes → 5-10 minutes per test failure session
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class FailureCategory(Enum):
    """Test failure categories."""

    IMPORT_ERROR = "import_error"
    ASSERTION_ERROR = "assertion_error"
    ATTRIBUTE_ERROR = "attribute_error"
    TYPE_ERROR = "type_error"
    FIXTURE_ERROR = "fixture_error"
    MOCK_ERROR = "mock_error"
    TIMEOUT_ERROR = "timeout_error"
    SYNTAX_ERROR = "syntax_error"
    UNKNOWN = "unknown"


@dataclass
class TestFailure:
    """Represents a single test failure."""

    test_name: str
    file: str
    line: Optional[int]
    error_type: str
    message: str
    traceback: str
    category: FailureCategory
    correlation: str = "UNKNOWN"  # HIGH, MEDIUM, LOW, UNKNOWN
    priority: int = 3  # 1=CRITICAL, 2=HIGH, 3=MEDIUM, 4=LOW


@dataclass
class FixRecommendation:
    """Fix recommendation for a test failure."""

    failure: TestFailure
    root_cause: str
    quick_fix: str
    quick_fix_time_min: int
    deep_fix: Optional[str] = None
    deep_fix_time_min: Optional[int] = None
    affected_file: Optional[str] = None
    affected_line: Optional[int] = None


@dataclass
class AnalysisResult:
    """Result of test failure analysis."""

    total_failures: int
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    failures: List[TestFailure] = field(default_factory=list)
    recommendations: List[FixRecommendation] = field(default_factory=list)
    estimated_total_time_min: int = 0
    recommended_fix_order: List[str] = field(default_factory=list)


class TestFailureAnalyzerSkill:
    """Analyze pytest failures and suggest fixes."""

    # Regex patterns for parsing pytest output
    FAILURE_PATTERN = re.compile(r"FAILED ([\w/_.]+::[\w_]+)")
    ERROR_PATTERN = re.compile(r"([\w]+Error|Exception): (.+)")
    TRACEBACK_FILE_LINE_PATTERN = re.compile(r'File "([^"]+)", line (\d+)')

    # Category detection patterns
    CATEGORY_PATTERNS = {
        FailureCategory.IMPORT_ERROR: [
            r"ImportError",
            r"ModuleNotFoundError",
            r"cannot import name",
        ],
        FailureCategory.ASSERTION_ERROR: [
            r"AssertionError",
            r"assert .+ == ",
            r"assert .+ is ",
        ],
        FailureCategory.ATTRIBUTE_ERROR: [
            r"AttributeError",
            r"has no attribute",
        ],
        FailureCategory.TYPE_ERROR: [
            r"TypeError",
            r"expected .+, got .+",
        ],
        FailureCategory.FIXTURE_ERROR: [
            r"fixture .+ not found",
            r"fixture .+ error",
        ],
        FailureCategory.MOCK_ERROR: [
            r"mock",
            r"patch",
            r"MagicMock",
        ],
        FailureCategory.TIMEOUT_ERROR: [
            r"timeout",
            r"TimeoutError",
        ],
        FailureCategory.SYNTAX_ERROR: [
            r"SyntaxError",
            r"invalid syntax",
        ],
    }

    def __init__(self, codebase_root: str = None):
        """Initialize test failure analyzer."""
        self.codebase_root = Path(codebase_root or Path.cwd())

    def analyze(
        self,
        test_output: str,
        files_changed: List[str] = None,
        priority_name: str = None,
    ) -> AnalysisResult:
        """
        Analyze test failures and generate recommendations.

        Args:
            test_output: Full pytest output (stdout + stderr)
            files_changed: List of files changed in current implementation
            priority_name: Current priority being implemented

        Returns:
            AnalysisResult with failures and recommendations
        """
        files_changed = files_changed or []

        # Step 1: Parse test output
        failures = self._parse_pytest_output(test_output)

        # Step 2: Categorize failures
        for failure in failures:
            failure.category = self._categorize_failure(failure)

        # Step 3: Correlate with recent changes
        for failure in failures:
            failure.correlation = self._correlate_with_changes(failure, files_changed)
            failure.priority = self._calculate_priority(failure)

        # Step 4: Generate fix recommendations
        recommendations = []
        for failure in failures:
            rec = self._generate_fix_recommendation(failure, priority_name)
            recommendations.append(rec)

        # Step 5: Estimate total time and prioritize
        estimated_total_time = sum(rec.quick_fix_time_min for rec in recommendations)
        recommended_fix_order = self._prioritize_fixes(recommendations)

        # Count by priority
        critical = sum(1 for f in failures if f.priority == 1)
        high = sum(1 for f in failures if f.priority == 2)
        medium = sum(1 for f in failures if f.priority == 3)
        low = sum(1 for f in failures if f.priority == 4)

        return AnalysisResult(
            total_failures=len(failures),
            critical_failures=critical,
            high_failures=high,
            medium_failures=medium,
            low_failures=low,
            failures=failures,
            recommendations=recommendations,
            estimated_total_time_min=estimated_total_time,
            recommended_fix_order=recommended_fix_order,
        )

    def _parse_pytest_output(self, test_output: str) -> List[TestFailure]:
        """
        Parse pytest output to extract failures.

        Args:
            test_output: Full pytest output

        Returns:
            List of TestFailure objects
        """
        failures = []
        lines = test_output.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for FAILED test_file::test_name
            match = self.FAILURE_PATTERN.search(line)
            if match:
                test_path = match.group(1)
                parts = test_path.split("::")
                file_path = parts[0] if parts else ""
                test_name = parts[1] if len(parts) > 1 else ""

                # Extract error details from following lines
                error_type = "Unknown"
                message = ""
                traceback = ""
                line_no = None

                # Scan forward to find error details
                j = i + 1
                found_error = False
                in_traceback = False
                while j < len(lines) and j < i + 100:  # Look ahead up to 100 lines
                    error_line = lines[j]

                    # Check if we're entering the traceback section (starts with underscore or test name)
                    if error_line.strip() and error_line.strip()[0] == "_":
                        in_traceback = True

                    # Extract error type and message (look for "E   ErrorType: message" format)
                    if error_line.strip().startswith("E   "):
                        error_match = self.ERROR_PATTERN.search(error_line)
                        if error_match and not found_error:
                            error_type = error_match.group(1)
                            message = error_match.group(2)
                            found_error = True

                    # Also check for error on the same line as FAILED (short format)
                    # Example: "FAILED tests/unit/test_auth.py::test_login - ImportError: cannot import name"
                    if " - " in line and "FAILED" in line and not found_error:
                        parts = line.split(" - ", 1)
                        if len(parts) == 2:
                            error_match = self.ERROR_PATTERN.search(parts[1])
                            if error_match:
                                error_type = error_match.group(1)
                                message = error_match.group(2)
                                found_error = True

                    # Check for error anywhere in line (fallback)
                    if not found_error and in_traceback:
                        error_match = self.ERROR_PATTERN.search(error_line)
                        if error_match and any(err in error_line for err in ["Error", "Exception"]):
                            error_type = error_match.group(1)
                            message = error_match.group(2)
                            found_error = True

                    # Extract file and line from traceback
                    traceback_match = self.TRACEBACK_FILE_LINE_PATTERN.search(error_line)
                    if traceback_match and not line_no:
                        line_no = int(traceback_match.group(2))

                    # Build traceback
                    if error_line.strip():
                        traceback += error_line + "\n"

                    # Stop at next test or end of section
                    if j > i + 5 and ("FAILED" in error_line or "PASSED" in error_line or "====" in error_line):
                        break

                    j += 1

                failures.append(
                    TestFailure(
                        test_name=test_name,
                        file=file_path,
                        line=line_no,
                        error_type=error_type,
                        message=message.strip(),
                        traceback=traceback.strip(),
                        category=FailureCategory.UNKNOWN,
                    )
                )

            i += 1

        return failures

    def _categorize_failure(self, failure: TestFailure) -> FailureCategory:
        """
        Categorize failure by type.

        Args:
            failure: TestFailure object

        Returns:
            FailureCategory
        """
        error_text = f"{failure.error_type} {failure.message} {failure.traceback}".lower()

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return category

        return FailureCategory.UNKNOWN

    def _correlate_with_changes(self, failure: TestFailure, files_changed: List[str]) -> str:
        """
        Correlate failure with recent changes.

        Args:
            failure: TestFailure object
            files_changed: List of changed files

        Returns:
            Correlation level: HIGH, MEDIUM, LOW, UNKNOWN
        """
        if not files_changed:
            return "UNKNOWN"

        # Extract module path from test file
        test_file = failure.file
        if not test_file:
            return "UNKNOWN"

        # Convert test file to source file
        # e.g., tests/unit/test_auth.py -> coffee_maker/auth/*
        source_module = test_file.replace("tests/unit/test_", "").replace("tests/integration/test_", "")
        source_module = source_module.replace(".py", "")

        # Check if any changed file matches the source module
        for changed_file in files_changed:
            if source_module in changed_file:
                return "HIGH"

        # Check if failure traceback mentions any changed files
        for changed_file in files_changed:
            if changed_file in failure.traceback:
                return "HIGH"

        # Check for same module family
        for changed_file in files_changed:
            changed_module = Path(changed_file).parent
            test_module = Path(test_file).parent
            if str(changed_module) in str(test_module):
                return "MEDIUM"

        return "LOW"

    def _calculate_priority(self, failure: TestFailure) -> int:
        """
        Calculate priority based on correlation and category.

        Args:
            failure: TestFailure object

        Returns:
            Priority: 1=CRITICAL, 2=HIGH, 3=MEDIUM, 4=LOW
        """
        # CRITICAL: High correlation + blocking errors
        if failure.correlation == "HIGH" and failure.category in [
            FailureCategory.IMPORT_ERROR,
            FailureCategory.SYNTAX_ERROR,
            FailureCategory.ASSERTION_ERROR,
        ]:
            return 1

        # HIGH: Medium correlation or important error types
        if failure.correlation in ["HIGH", "MEDIUM"] or failure.category in [
            FailureCategory.TYPE_ERROR,
            FailureCategory.ATTRIBUTE_ERROR,
        ]:
            return 2

        # MEDIUM: Low correlation or minor errors
        if failure.correlation == "LOW" or failure.category in [
            FailureCategory.FIXTURE_ERROR,
            FailureCategory.MOCK_ERROR,
        ]:
            return 3

        # LOW: Unknown or pre-existing issues
        return 4

    def _generate_fix_recommendation(self, failure: TestFailure, priority_name: str = None) -> FixRecommendation:
        """
        Generate fix recommendation for a failure.

        Args:
            failure: TestFailure object
            priority_name: Current priority name

        Returns:
            FixRecommendation
        """
        # Generate recommendations based on category
        if failure.category == FailureCategory.IMPORT_ERROR:
            return self._recommend_import_fix(failure)
        elif failure.category == FailureCategory.ASSERTION_ERROR:
            return self._recommend_assertion_fix(failure)
        elif failure.category == FailureCategory.ATTRIBUTE_ERROR:
            return self._recommend_attribute_fix(failure)
        elif failure.category == FailureCategory.TYPE_ERROR:
            return self._recommend_type_fix(failure)
        elif failure.category == FailureCategory.FIXTURE_ERROR:
            return self._recommend_fixture_fix(failure)
        elif failure.category == FailureCategory.MOCK_ERROR:
            return self._recommend_mock_fix(failure)
        elif failure.category == FailureCategory.TIMEOUT_ERROR:
            return self._recommend_timeout_fix(failure)
        elif failure.category == FailureCategory.SYNTAX_ERROR:
            return self._recommend_syntax_fix(failure)
        else:
            return self._recommend_generic_fix(failure)

    def _recommend_import_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for import errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Missing import or circular dependency",
            quick_fix="Add missing import or fix import order",
            quick_fix_time_min=5,
            deep_fix="Refactor to eliminate circular dependency",
            deep_fix_time_min=20,
        )

    def _recommend_assertion_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for assertion errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Implementation logic doesn't match expected behavior",
            quick_fix="Update implementation to return expected value",
            quick_fix_time_min=5,
            deep_fix="Review and correct business logic comprehensively",
            deep_fix_time_min=20,
        )

    def _recommend_attribute_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for attribute errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Missing method or property in implementation",
            quick_fix="Add missing method/property",
            quick_fix_time_min=5,
            deep_fix="Complete implementation with all required methods",
            deep_fix_time_min=15,
        )

    def _recommend_type_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for type errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Type mismatch between expected and actual",
            quick_fix="Add type conversion or fix type annotation",
            quick_fix_time_min=5,
            deep_fix="Add comprehensive type checking and validation",
            deep_fix_time_min=15,
        )

    def _recommend_fixture_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for fixture errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Missing pytest fixture or scope issue",
            quick_fix="Add missing fixture to conftest.py",
            quick_fix_time_min=5,
            deep_fix="Review fixture architecture and dependencies",
            deep_fix_time_min=15,
        )

    def _recommend_mock_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for mock errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Incorrect mock path or missing mock attributes",
            quick_fix="Fix mock path or add missing mock attributes",
            quick_fix_time_min=5,
            deep_fix="Refactor to reduce mocking complexity",
            deep_fix_time_min=20,
        )

    def _recommend_timeout_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for timeout errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Test execution taking too long",
            quick_fix="Increase timeout value",
            quick_fix_time_min=2,
            deep_fix="Optimize code to reduce execution time",
            deep_fix_time_min=30,
        )

    def _recommend_syntax_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for syntax errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Python syntax error in code",
            quick_fix="Fix syntax error at reported line",
            quick_fix_time_min=2,
            deep_fix="Run linter to find all syntax issues",
            deep_fix_time_min=10,
        )

    def _recommend_generic_fix(self, failure: TestFailure) -> FixRecommendation:
        """Recommend fix for unknown errors."""
        return FixRecommendation(
            failure=failure,
            root_cause="Unknown error type - needs investigation",
            quick_fix="Investigate error details and traceback",
            quick_fix_time_min=10,
            deep_fix="Debug with breakpoints or additional logging",
            deep_fix_time_min=30,
        )

    def _prioritize_fixes(self, recommendations: List[FixRecommendation]) -> List[str]:
        """
        Prioritize fix order based on priority and time.

        Args:
            recommendations: List of FixRecommendation objects

        Returns:
            List of test names in recommended fix order
        """
        # Sort by: priority (lower is better), then time (lower is better)
        sorted_recs = sorted(
            recommendations,
            key=lambda r: (r.failure.priority, r.quick_fix_time_min),
        )

        return [rec.failure.test_name for rec in sorted_recs]

    def format_analysis_report(self, result: AnalysisResult, priority_name: str = None) -> str:
        """
        Format analysis result as markdown report.

        Args:
            result: AnalysisResult object
            priority_name: Current priority name

        Returns:
            Formatted markdown report
        """
        report = []
        report.append("# Test Failure Analysis Report")

        if priority_name:
            report.append(f"**Priority**: {priority_name}")

        report.append(f"Total Failures: {result.total_failures}")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"- CRITICAL: {result.critical_failures} failures (blocking current work)")
        report.append(f"- HIGH: {result.high_failures} failures (related to changes)")
        report.append(f"- MEDIUM: {result.medium_failures} failures (minor issues)")
        report.append(f"- LOW: {result.low_failures} failures (pre-existing)")
        report.append(f"- Estimated fix time: {result.estimated_total_time_min} minutes")
        report.append("")

        # CRITICAL failures
        if result.critical_failures > 0:
            report.append("## CRITICAL Failures")
            report.append("")

            critical_recs = [r for r in result.recommendations if r.failure.priority == 1]
            for i, rec in enumerate(critical_recs, 1):
                report.append(f"### {i}. {rec.failure.test_name} ({rec.failure.file})")
                report.append(f"**Error**: {rec.failure.error_type} - {rec.failure.message}")
                report.append(f"**Root Cause**: {rec.root_cause}")
                report.append(f"**Quick Fix** ({rec.quick_fix_time_min} min): {rec.quick_fix}")
                if rec.deep_fix:
                    report.append(f"**Deep Fix** ({rec.deep_fix_time_min} min): {rec.deep_fix}")
                report.append("")

        # Recommended fix order
        report.append("## Recommended Fix Order")
        report.append("")
        for i, test_name in enumerate(result.recommended_fix_order, 1):
            rec = next(r for r in result.recommendations if r.failure.test_name == test_name)
            priority_label = ["", "CRITICAL", "HIGH", "MEDIUM", "LOW"][rec.failure.priority]
            report.append(
                f"{i}. **{test_name}** ({priority_label}) - "
                f"{rec.quick_fix_time_min} min (quick) / "
                f"{rec.deep_fix_time_min or 'N/A'} min (deep)"
            )

        report.append("")
        report.append(f"**Total time to unblock**: {result.estimated_total_time_min} minutes")

        return "\n".join(report)
