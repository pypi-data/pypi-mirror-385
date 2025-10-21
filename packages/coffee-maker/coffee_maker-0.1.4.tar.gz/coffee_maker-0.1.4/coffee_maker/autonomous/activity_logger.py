"""High-level interface for logging developer activities.

Provides convenient methods for code_developer daemon to log various activities
without directly dealing with database operations. Handles session management
and priority tracking automatically.

Example:
    >>> logger = ActivityLogger()
    >>> logger.start_priority("2.5", "CI Testing")
    >>> logger.log_commit(
    ...     message="Add pytest configuration",
    ...     files_changed=3,
    ...     lines_added=45
    ... )
    >>> logger.log_test_run(passed=12, failed=0)
    >>> logger.complete_priority("2.5", success=True)
"""

import logging
import uuid
from typing import Optional

from coffee_maker.autonomous.activity_db import (
    ActivityDB,
    ACTIVITY_TYPE_COMMIT,
    ACTIVITY_TYPE_FILE_CHANGED,
    ACTIVITY_TYPE_TEST_RUN,
    ACTIVITY_TYPE_PR_CREATED,
    ACTIVITY_TYPE_BRANCH_CREATED,
    ACTIVITY_TYPE_PRIORITY_STARTED,
    ACTIVITY_TYPE_PRIORITY_COMPLETED,
    ACTIVITY_TYPE_ERROR_ENCOUNTERED,
    ACTIVITY_TYPE_DEPENDENCY_INSTALLED,
    ACTIVITY_TYPE_DOCUMENTATION_UPDATED,
    OUTCOME_SUCCESS,
    OUTCOME_FAILURE,
    OUTCOME_PARTIAL,
)

logger = logging.getLogger(__name__)


class ActivityLogger:
    """High-level interface for logging developer activities.

    Provides convenient methods for code_developer to log various activities
    without directly dealing with database operations. Automatically manages
    session IDs and priority context.

    Attributes:
        db: ActivityDB instance for storing activities
        current_session_id: UUID of current session
        current_priority: Currently active priority number
        current_priority_name: Currently active priority name

    Example:
        >>> logger = ActivityLogger()
        >>> logger.start_priority("2.5", "CI Testing")
        >>> logger.log_commit(
        ...     message="Add pytest config",
        ...     files_changed=3,
        ...     lines_added=45
        ... )
        >>> logger.complete_priority("2.5", success=True)
    """

    def __init__(self, db: Optional[ActivityDB] = None):
        """Initialize activity logger.

        Args:
            db: ActivityDB instance. Creates new if None.
        """
        self.db = db or ActivityDB()
        self.current_session_id = str(uuid.uuid4())
        self.current_priority: Optional[str] = None
        self.current_priority_name: Optional[str] = None

    def start_priority(self, priority_number: str, priority_name: str) -> None:
        """Log start of a new priority.

        Creates a new session ID for all activities related to this priority.

        Args:
            priority_number: Priority number (e.g., "2.5")
            priority_name: Priority name (e.g., "CI Testing")

        Example:
            >>> logger.start_priority("2.5", "CI Testing")
        """
        self.current_priority = priority_number
        self.current_priority_name = priority_name
        self.current_session_id = str(uuid.uuid4())

        self.db.log_activity(
            activity_type=ACTIVITY_TYPE_PRIORITY_STARTED,
            title=f"Started {priority_name}",
            priority_number=priority_number,
            priority_name=priority_name,
            session_id=self.current_session_id,
        )

        logger.info(f"Started priority {priority_number}: {priority_name}")

    def complete_priority(self, priority_number: str, success: bool = True, summary: Optional[str] = None) -> None:
        """Log completion of a priority.

        Args:
            priority_number: Priority number
            success: Whether completed successfully. Defaults to True
            summary: Optional summary of work done

        Example:
            >>> logger.complete_priority(
            ...     "2.5",
            ...     success=True,
            ...     summary="Implemented CI pipeline with GitHub Actions"
            ... )
        """
        outcome = OUTCOME_SUCCESS if success else OUTCOME_FAILURE

        self.db.log_activity(
            activity_type=ACTIVITY_TYPE_PRIORITY_COMPLETED,
            title=f"Completed {self.current_priority_name}",
            description=summary,
            priority_number=priority_number,
            priority_name=self.current_priority_name,
            outcome=outcome,
            session_id=self.current_session_id,
        )

        logger.info(f"Completed priority {priority_number}: {outcome}")

    def log_commit(
        self,
        message: str,
        files_changed: int = 0,
        lines_added: int = 0,
        lines_removed: int = 0,
        commit_hash: Optional[str] = None,
    ) -> int:
        """Log a git commit.

        Args:
            message: Commit message
            files_changed: Number of files changed. Defaults to 0
            lines_added: Lines added. Defaults to 0
            lines_removed: Lines removed. Defaults to 0
            commit_hash: Git commit hash (SHA). Defaults to None

        Returns:
            Activity ID of the logged commit

        Example:
            >>> logger.log_commit(
            ...     message="Add CI configuration",
            ...     files_changed=3,
            ...     lines_added=120,
            ...     commit_hash="abc123def456"
            ... )
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_COMMIT,
            title=message[:100],  # Truncate to fit
            description=message,
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={
                "files_changed": files_changed,
                "lines_added": lines_added,
                "lines_removed": lines_removed,
                "commit_hash": commit_hash,
            },
            session_id=self.current_session_id,
        )

    def log_test_run(
        self,
        passed: int,
        failed: int,
        skipped: int = 0,
        duration_seconds: float = 0,
        test_framework: str = "pytest",
    ) -> int:
        """Log a test run.

        Args:
            passed: Number of tests passed
            failed: Number of tests failed
            skipped: Number of tests skipped. Defaults to 0
            duration_seconds: Test run duration in seconds. Defaults to 0
            test_framework: Test framework used. Defaults to "pytest"

        Returns:
            Activity ID of the logged test run

        Example:
            >>> logger.log_test_run(
            ...     passed=47,
            ...     failed=0,
            ...     skipped=2,
            ...     duration_seconds=12.5
            ... )
        """
        outcome = OUTCOME_SUCCESS if failed == 0 else OUTCOME_FAILURE

        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_TEST_RUN,
            title=f"Tests: {passed} passed, {failed} failed",
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "duration_seconds": duration_seconds,
                "framework": test_framework,
            },
            outcome=outcome,
            session_id=self.current_session_id,
        )

    def log_pr_created(self, pr_number: int, pr_title: str, pr_url: str, branch: str) -> int:
        """Log creation of a pull request.

        Args:
            pr_number: Pull request number
            pr_title: Pull request title
            pr_url: Pull request URL
            branch: Branch name

        Returns:
            Activity ID of the logged PR

        Example:
            >>> logger.log_pr_created(
            ...     pr_number=42,
            ...     pr_title="Add CI testing and GitHub Actions",
            ...     pr_url="https://github.com/org/repo/pull/42",
            ...     branch="feature/ci-testing"
            ... )
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_PR_CREATED,
            title=f"Created PR #{pr_number}: {pr_title}",
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={"pr_number": pr_number, "pr_url": pr_url, "branch": branch},
            session_id=self.current_session_id,
        )

    def log_branch_created(self, branch: str, description: Optional[str] = None) -> int:
        """Log creation of a git branch.

        Args:
            branch: Branch name
            description: Optional branch description

        Returns:
            Activity ID of the logged branch creation
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_BRANCH_CREATED,
            title=f"Created branch {branch}",
            description=description,
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            session_id=self.current_session_id,
        )

    def log_error(
        self,
        error_message: str,
        error_type: Optional[str] = None,
        is_blocking: bool = False,
    ) -> int:
        """Log an error encountered during development.

        Args:
            error_message: Description of the error
            error_type: Type of error (e.g., "AssertionError", "APIError")
            is_blocking: Whether this error blocks progress. Defaults to False

        Returns:
            Activity ID of the logged error

        Example:
            >>> logger.log_error(
            ...     error_message="Database connection timeout",
            ...     error_type="TimeoutError",
            ...     is_blocking=False
            ... )
        """
        outcome = OUTCOME_PARTIAL if not is_blocking else OUTCOME_FAILURE

        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_ERROR_ENCOUNTERED,
            title=f"Error: {error_message[:100]}",
            description=error_message,
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={"error_type": error_type, "is_blocking": is_blocking},
            outcome=outcome,
            session_id=self.current_session_id,
        )

    def log_dependency_installed(self, package_name: str, version: Optional[str] = None) -> int:
        """Log installation of a new dependency.

        Args:
            package_name: Name of the package installed
            version: Version installed. Defaults to None

        Returns:
            Activity ID of the logged dependency
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_DEPENDENCY_INSTALLED,
            title=f"Installed {package_name}" + (f" ({version})" if version else ""),
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={"package_name": package_name, "version": version},
            session_id=self.current_session_id,
        )

    def log_documentation_updated(self, file_path: str, description: Optional[str] = None) -> int:
        """Log update to documentation.

        Args:
            file_path: Path to documentation file updated
            description: Optional description of changes

        Returns:
            Activity ID of the logged documentation update
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_DOCUMENTATION_UPDATED,
            title=f"Updated documentation: {file_path}",
            description=description,
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            session_id=self.current_session_id,
        )

    def log_file_changed(
        self,
        file_path: str,
        change_type: str,
        description: Optional[str] = None,
    ) -> int:
        """Log a file change event.

        Args:
            file_path: Path to file that changed
            change_type: Type of change (created, modified, deleted, moved)
            description: Optional description of the change

        Returns:
            Activity ID of the logged file change

        Example:
            >>> logger.log_file_changed(
            ...     file_path="coffee_maker/utils/new_util.py",
            ...     change_type="created",
            ...     description="New utility module for logging"
            ... )
        """
        return self.db.log_activity(
            activity_type=ACTIVITY_TYPE_FILE_CHANGED,
            title=f"{change_type.capitalize()}: {file_path}",
            description=description,
            priority_number=self.current_priority,
            priority_name=self.current_priority_name,
            metadata={"file_path": file_path, "change_type": change_type},
            session_id=self.current_session_id,
        )
