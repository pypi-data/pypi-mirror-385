"""Data models for code review.

This module contains the data classes used throughout the code reviewer:
- ReviewIssue: Individual issues found during review
- ReviewReport: Complete review report with all issues
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ReviewIssue:
    """Represents a single issue found during code review.

    Attributes:
        severity: Issue severity (critical, high, medium, low, info)
        category: Issue category (bug, architecture, performance, security)
        title: Short issue title
        description: Detailed description
        line_number: Line number where issue was found (if applicable)
        code_snippet: Relevant code snippet
        suggestion: Suggested fix or improvement
        perspective: Which perspective found this issue
    """

    severity: str
    category: str
    title: str
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    perspective: str = ""


@dataclass
class ReviewReport:
    """Complete code review report from all perspectives.

    Attributes:
        file_path: Path to reviewed file
        timestamp: When review was performed
        issues: List of all issues found
        summary: Executive summary of findings
        metrics: Review metrics (total issues, by severity, etc.)
        perspective_reports: Individual reports from each perspective
    """

    file_path: str
    timestamp: datetime
    issues: List[ReviewIssue] = field(default_factory=list)
    summary: str = ""
    metrics: Dict[str, int] = field(default_factory=dict)
    perspective_reports: Dict[str, str] = field(default_factory=dict)

    def add_issue(self, issue: ReviewIssue) -> None:
        """Add an issue to the report.

        Args:
            issue: Issue to add
        """
        self.issues.append(issue)

    def get_issues_by_severity(self, severity: str) -> List[ReviewIssue]:
        """Get all issues of a specific severity.

        Args:
            severity: Severity level to filter by

        Returns:
            List of issues matching the severity
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: str) -> List[ReviewIssue]:
        """Get all issues of a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of issues matching the category
        """
        return [issue for issue in self.issues if issue.category == category]

    def calculate_metrics(self) -> None:
        """Calculate review metrics from collected issues."""
        self.metrics = {
            "total_issues": len(self.issues),
            "critical": len(self.get_issues_by_severity("critical")),
            "high": len(self.get_issues_by_severity("high")),
            "medium": len(self.get_issues_by_severity("medium")),
            "low": len(self.get_issues_by_severity("low")),
            "info": len(self.get_issues_by_severity("info")),
            "bugs": len(self.get_issues_by_category("bug")),
            "architecture": len(self.get_issues_by_category("architecture")),
            "performance": len(self.get_issues_by_category("performance")),
            "security": len(self.get_issues_by_category("security")),
        }
