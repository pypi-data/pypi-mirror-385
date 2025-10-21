"""Base class for code review perspectives.

All specialized perspectives inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from coffee_maker.code_reviewer.models import ReviewIssue


class BasePerspective(ABC):
    """Abstract base class for code review perspectives.

    Each perspective analyzes code from a specific angle (bugs, architecture,
    performance, security) using an LLM optimized for that task.

    Subclasses must implement:
        - analyze(): Synchronous analysis
        - analyze_async(): Asynchronous analysis
        - get_summary(): Get perspective summary
    """

    def __init__(self, model_name: str = "", perspective_name: str = ""):
        """Initialize the perspective.

        Args:
            model_name: Name of LLM model to use
            perspective_name: Human-readable perspective name
        """
        self.model_name = model_name
        self.perspective_name = perspective_name
        self.last_analysis_summary = ""

    @abstractmethod
    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code and return found issues.

        Args:
            code_content: Source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of issues found during analysis
        """

    @abstractmethod
    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code asynchronously.

        Args:
            code_content: Source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of issues found during analysis
        """

    def get_summary(self) -> str:
        """Get summary of last analysis.

        Returns:
            Summary text from last analysis
        """
        return self.last_analysis_summary

    def _create_issue(
        self,
        severity: str,
        category: str,
        title: str,
        description: str,
        line_number: Optional[int] = None,
        code_snippet: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> ReviewIssue:
        """Helper to create a ReviewIssue.

        Args:
            severity: Issue severity
            category: Issue category
            title: Issue title
            description: Issue description
            line_number: Line number (optional)
            code_snippet: Code snippet (optional)
            suggestion: Suggested fix (optional)

        Returns:
            ReviewIssue instance
        """
        return ReviewIssue(
            severity=severity,
            category=category,
            title=title,
            description=description,
            line_number=line_number,
            code_snippet=code_snippet,
            suggestion=suggestion,
            perspective=self.perspective_name,
        )
