"""Multi-Model Code Reviewer orchestrator.

This module coordinates multiple specialized code review agents to provide
comprehensive code analysis from different perspectives.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.code_reviewer.models import ReviewReport
from coffee_maker.code_reviewer.perspectives import (
    ArchitectCritic,
    BasePerspective,
    BugHunter,
    PerformanceAnalyst,
    SecurityAuditor,
)


class MultiModelCodeReviewer:
    """Orchestrates multi-perspective code review using different LLMs.

    This class coordinates multiple specialized review agents, each using
    a different LLM optimized for their specific task:
    - BugHunter: GPT-4 for bug detection
    - ArchitectCritic: Claude for architecture review
    - PerformanceAnalyst: Gemini for performance analysis
    - SecurityAuditor: Specialized model for security audit

    Example:
        >>> reviewer = MultiModelCodeReviewer()
        >>> report = reviewer.review_file("mycode.py")
        >>> print(f"Found {report.metrics['total_issues']} issues")
        >>> report.save_html("review.html")
    """

    def __init__(self, enable_perspectives: Optional[List[str]] = None):
        """Initialize the multi-model code reviewer.

        Args:
            enable_perspectives: List of perspectives to enable.
                                Options: "bug_hunter", "architect_critic",
                                "performance_analyst", "security_auditor"
                                If None, all perspectives are enabled.
        """
        self.enabled_perspectives = enable_perspectives or [
            "bug_hunter",
            "architect_critic",
            "performance_analyst",
            "security_auditor",
        ]

        # Initialize perspectives
        self.perspectives: Dict[str, BasePerspective] = {}
        if "bug_hunter" in self.enabled_perspectives:
            self.perspectives["bug_hunter"] = BugHunter()
        if "architect_critic" in self.enabled_perspectives:
            self.perspectives["architect_critic"] = ArchitectCritic()
        if "performance_analyst" in self.enabled_perspectives:
            self.perspectives["performance_analyst"] = PerformanceAnalyst()
        if "security_auditor" in self.enabled_perspectives:
            self.perspectives["security_auditor"] = SecurityAuditor()

    def review_file(self, file_path: str) -> ReviewReport:
        """Review a single file with all enabled perspectives.

        Args:
            file_path: Path to file to review

        Returns:
            Complete review report

        Example:
            >>> reviewer = MultiModelCodeReviewer()
            >>> report = reviewer.review_file("app.py")
            >>> critical_issues = report.get_issues_by_severity("critical")
        """
        # Read file content
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        code_content = file_path_obj.read_text()

        # Create report
        report = ReviewReport(file_path=file_path, timestamp=datetime.now())

        # Run each perspective synchronously
        for name, perspective in self.perspectives.items():
            try:
                issues = perspective.analyze(code_content, file_path)
                for issue in issues:
                    issue.perspective = name
                    report.add_issue(issue)

                # Store individual perspective report
                report.perspective_reports[name] = perspective.get_summary()

            except Exception as e:
                # Log error but continue with other perspectives
                print(f"Error in {name}: {e}")

        # Calculate metrics and generate summary
        report.calculate_metrics()
        report.summary = self._generate_summary(report)

        return report

    async def review_file_async(self, file_path: str) -> ReviewReport:
        """Review a file asynchronously with all perspectives running in parallel.

        Args:
            file_path: Path to file to review

        Returns:
            Complete review report

        Example:
            >>> reviewer = MultiModelCodeReviewer()
            >>> report = await reviewer.review_file_async("app.py")
        """
        # Read file content
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        code_content = file_path_obj.read_text()

        # Create report
        report = ReviewReport(file_path=file_path, timestamp=datetime.now())

        # Run all perspectives in parallel
        tasks = []
        for name, perspective in self.perspectives.items():
            task = self._run_perspective(name, perspective, code_content, file_path, report)
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Calculate metrics and generate summary
        report.calculate_metrics()
        report.summary = self._generate_summary(report)

        return report

    async def _run_perspective(
        self, name: str, perspective, code_content: str, file_path: str, report: ReviewReport
    ) -> None:
        """Run a single perspective analysis asynchronously.

        Args:
            name: Perspective name
            perspective: Perspective instance
            code_content: Code to analyze
            file_path: File path
            report: Report to add issues to
        """
        try:
            issues = await perspective.analyze_async(code_content, file_path)
            for issue in issues:
                issue.perspective = name
                report.add_issue(issue)

            # Store individual perspective report
            report.perspective_reports[name] = perspective.get_summary()

        except Exception as e:
            print(f"Error in {name}: {e}")

    def review_directory(self, directory_path: str, file_pattern: str = "*.py") -> List[ReviewReport]:
        """Review all files in a directory matching pattern.

        Args:
            directory_path: Path to directory to review
            file_pattern: File pattern to match (default: *.py)

        Returns:
            List of review reports, one per file

        Example:
            >>> reviewer = MultiModelCodeReviewer()
            >>> reports = reviewer.review_directory("src/", "*.py")
            >>> total_issues = sum(r.metrics['total_issues'] for r in reports)
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        reports = []
        for file_path in directory.rglob(file_pattern):
            if file_path.is_file():
                try:
                    report = self.review_file(str(file_path))
                    reports.append(report)
                except Exception as e:
                    print(f"Error reviewing {file_path}: {e}")

        return reports

    def _generate_summary(self, report: ReviewReport) -> str:
        """Generate executive summary from report.

        Args:
            report: Review report to summarize

        Returns:
            Summary text
        """
        critical_count = report.metrics.get("critical", 0)
        high_count = report.metrics.get("high", 0)
        total_count = report.metrics.get("total_issues", 0)

        if total_count == 0:
            return "✅ No issues found. Code looks good!"

        summary_parts = [
            f"Found {total_count} issue(s) in {report.file_path}",
        ]

        if critical_count > 0:
            summary_parts.append(f"⚠️  {critical_count} CRITICAL issue(s) require immediate attention")

        if high_count > 0:
            summary_parts.append(f"🔴 {high_count} HIGH severity issue(s) should be addressed soon")

        # Top issues by category
        category_counts = [
            (cat, report.metrics.get(cat, 0)) for cat in ["bugs", "security", "performance", "architecture"]
        ]
        category_counts.sort(key=lambda x: x[1], reverse=True)

        top_categories = [f"{count} {cat}" for cat, count in category_counts if count > 0]
        if top_categories:
            summary_parts.append(f"Categories: {', '.join(top_categories)}")

        return "\n".join(summary_parts)
