"""Developer status tracking for daemon.

This module provides real-time status tracking for the code-developer daemon.
The daemon reports its status, progress, and activities, which the project-manager
CLI can display to the user.

PRIORITY 4: Developer Status Dashboard
"""

import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from coffee_maker.utils.file_io import atomic_write_json


class DeveloperState(str, Enum):
    """Developer status states."""

    WORKING = "working"  # 🟢 Actively implementing
    TESTING = "testing"  # 🟡 Running tests
    BLOCKED = "blocked"  # 🔴 Waiting for user response
    IDLE = "idle"  # ⚪ Between tasks
    THINKING = "thinking"  # 🔵 Analyzing codebase
    REVIEWING = "reviewing"  # 🟣 Creating PR/docs
    STOPPED = "stopped"  # ⚫ Daemon not running


class ActivityType(str, Enum):
    """Activity log types."""

    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    CODE_CHANGE = "code_change"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"
    GIT_BRANCH = "git_branch"
    TEST_RUN = "test_run"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    QUESTION_ASKED = "question_asked"
    DEPENDENCY_REQUESTED = "dependency_requested"
    ERROR_ENCOUNTERED = "error_encountered"
    STATUS_UPDATE = "status_update"


class DeveloperStatus:
    """Track and report developer status.

    This class is used by the daemon to track its current state, progress,
    and activities. Status is written to a JSON file that can be read by
    the project-manager CLI.

    Example:
        status = DeveloperStatus()

        # Start working on a task
        status.update_status(
            DeveloperState.WORKING,
            task={"priority": 4, "name": "Developer Status Dashboard"},
            progress=0
        )

        # Report activities
        status.report_activity(ActivityType.GIT_COMMIT, "Committed status logic")

        # Update progress
        status.report_progress(50, "Core functionality complete")
    """

    def __init__(self, status_file: Optional[Path] = None):
        """Initialize status tracker.

        Args:
            status_file: Path to status JSON file (default: data/developer_status.json)
        """
        if status_file is None:
            status_file = Path("data/developer_status.json")
        self.status_file = status_file
        self.current_state = DeveloperState.IDLE
        self.current_task: Optional[Dict] = None
        self.activity_log: list = []
        self.questions: list = []
        self.daemon_started_at = datetime.utcnow().isoformat() + "Z"

        # Metrics
        self.metrics = {
            "tasks_completed_today": 0,
            "total_commits_today": 0,
            "tests_passed_today": 0,
            "tests_failed_today": 0,
        }

        # Ensure data directory exists
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def update_status(
        self,
        status: DeveloperState,
        task: Optional[Dict] = None,
        progress: int = 0,
        current_step: str = "",
    ):
        """Update current developer status.

        Args:
            status: Current state
            task: Current task details (priority, name, etc.)
            progress: Progress percentage (0-100)
            current_step: Description of current step
        """
        self.current_state = status

        if task:
            # If this is a new task, set started_at
            if not self.current_task or self.current_task.get("name") != task.get("name"):
                task["started_at"] = datetime.utcnow().isoformat() + "Z"

            self.current_task = {
                "priority": task.get("priority", 0),
                "name": task.get("name", "Unknown"),
                "started_at": task.get("started_at", datetime.utcnow().isoformat() + "Z"),
                "progress": progress,
                "current_step": current_step,
                "eta_seconds": self._calculate_eta(task, progress),
            }
        elif self.current_task:
            # Update existing task
            self.current_task["progress"] = progress
            self.current_task["current_step"] = current_step
            self.current_task["eta_seconds"] = self._calculate_eta(self.current_task, progress)

        # Log status update as activity
        self.report_activity(
            ActivityType.STATUS_UPDATE,
            f"Status changed to {status.value}",
            auto_write=False,
        )

        self._write_status()

    def report_activity(
        self,
        activity_type: ActivityType,
        description: str,
        details: Optional[Dict] = None,
        auto_write: bool = True,
    ):
        """Log an activity.

        Args:
            activity_type: Type of activity
            description: Human-readable description
            details: Additional details (optional)
            auto_write: Whether to automatically write status file (default: True)
        """
        activity: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": activity_type.value,
            "description": description,
        }

        if details:
            activity["details"] = details

        self.activity_log.append(activity)

        # Keep only last 50 activities
        self.activity_log = self.activity_log[-50:]

        # Update metrics
        if activity_type == ActivityType.GIT_COMMIT:
            self.metrics["total_commits_today"] += 1
        elif activity_type == ActivityType.TEST_PASSED:
            self.metrics["tests_passed_today"] += 1
        elif activity_type == ActivityType.TEST_FAILED:
            self.metrics["tests_failed_today"] += 1

        if auto_write:
            self._write_status()

    def report_progress(self, progress: int, current_step: str):
        """Update progress percentage.

        Args:
            progress: Progress percentage (0-100)
            current_step: Description of current step
        """
        if self.current_task:
            self.current_task["progress"] = progress
            self.current_task["current_step"] = current_step
            self.current_task["eta_seconds"] = self._calculate_eta(self.current_task, progress)

            # Log progress milestone
            self.report_activity(
                ActivityType.STATUS_UPDATE,
                f"Progress: {progress}% - {current_step}",
                auto_write=False,
            )

        self._write_status()

    def add_question(self, question_id: str, question_type: str, message: str, context: str = ""):
        """Add a pending question.

        Args:
            question_id: Unique question ID
            question_type: Type of question (dependency_approval, design_decision, etc.)
            message: Question message
            context: Additional context
        """
        question = {
            "id": question_id,
            "type": question_type,
            "message": message,
            "context": context,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "pending",
        }

        self.questions.append(question)

        # Log question as activity
        self.report_activity(ActivityType.QUESTION_ASKED, f"Asked: {message}", auto_write=False)

        self._write_status()

        # Update state to BLOCKED
        if self.current_state != DeveloperState.BLOCKED:
            self.update_status(DeveloperState.BLOCKED)

    def remove_question(self, question_id: str):
        """Remove a question (after it's answered).

        Args:
            question_id: Question ID to remove
        """
        self.questions = [q for q in self.questions if q["id"] != question_id]
        self._write_status()

        # If no more questions, return to previous state
        if not self.questions and self.current_state == DeveloperState.BLOCKED:
            self.update_status(DeveloperState.WORKING)

    def task_completed(self):
        """Mark current task as completed."""
        if self.current_task:
            self.metrics["tasks_completed_today"] += 1
            self.report_progress(100, "Task complete")

    def _calculate_eta(self, task: Dict, progress: int) -> int:
        """Calculate estimated time remaining.

        Args:
            task: Task details
            progress: Current progress (0-100)

        Returns:
            Estimated seconds remaining
        """
        if progress <= 0:
            # No progress yet, can't estimate
            return 0

        # Parse started_at
        try:
            started_at = datetime.fromisoformat(task["started_at"].replace("Z", ""))
        except (KeyError, ValueError):
            return 0

        elapsed = datetime.utcnow() - started_at

        # Calculate total estimated time based on progress
        total_estimated = elapsed.total_seconds() * (100 / progress)

        # Calculate remaining
        remaining = total_estimated - elapsed.total_seconds()

        return max(0, int(remaining))

    def _write_status(self):
        """Write current status to JSON file."""
        status_data = {
            "status": self.current_state.value,
            "current_task": self.current_task,
            "last_activity": self.activity_log[-1] if self.activity_log else None,
            "activity_log": self.activity_log[-20:],  # Last 20 activities in file
            "questions": self.questions,
            "metrics": self.metrics,
            "daemon_info": {
                "pid": os.getpid(),
                "started_at": self.daemon_started_at,
                "version": "1.0.0",
            },
        }

        try:
            # Write atomically using file_io utility
            atomic_write_json(self.status_file, status_data)
        except Exception as e:
            # If write fails, log but don't crash daemon
            print(f"Warning: Failed to write status file: {e}")
