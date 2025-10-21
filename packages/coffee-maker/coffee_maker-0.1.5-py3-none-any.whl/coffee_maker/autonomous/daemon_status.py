"""Status Management Mixin for DevDaemon.

This module provides status tracking and notification operations for the autonomous
development daemon, extracted from daemon.py to improve code organization and maintainability.

Classes:
    StatusMixin: Mixin providing _write_status(), _update_subtask(), and notification methods

Usage:
    class DevDaemon(StatusMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_TYPE_ERROR,
    NOTIF_TYPE_INFO,
)
from coffee_maker.utils.file_io import write_json_file

logger = logging.getLogger(__name__)


class StatusMixin:
    """Mixin providing status tracking and notifications for daemon.

    This mixin provides methods for writing daemon status, tracking subtasks,
    and sending notifications to the user.

    Required attributes (provided by DevDaemon):
        - self.notifications: NotificationDB instance
        - self.metrics_db: TaskMetricsDB instance
        - self.running: bool
        - self.start_time: datetime
        - self.iteration_count: int
        - self.current_priority_start_time: datetime
        - self.current_priority_info: dict
        - self.current_subtasks: list
        - self.crash_count: int
        - self.max_crashes: int
        - self.crash_history: list
        - self.iterations_since_compact: int
        - self.compact_interval: int
        - self.last_compact_time: datetime

    Methods:
        - _notify_completion(): Send completion notification
        - _notify_persistent_failure(): Send failure notification
        - _write_status(): Write daemon status to file
        - _update_subtask(): Update subtask tracking

    Example:
        >>> class DevDaemon(StatusMixin):
        ...     def __init__(self):
        ...         self.notifications = NotificationDB()
        ...         self.running = True
        >>> daemon = DevDaemon()
        >>> daemon._write_status()
    """

    def _notify_completion(self):
        """Notify user that all priorities are complete."""
        self.notifications.create_notification(
            type=NOTIF_TYPE_INFO,
            title="🎉 All Priorities Complete!",
            message="The DevDaemon has completed all planned priorities in the ROADMAP!\n\nCheck your PRs for review.",
            priority=NOTIF_PRIORITY_HIGH,
            sound=False,
            agent_id="code_developer",
        )

    def _notify_persistent_failure(self, crash_info: dict):
        """Notify user of persistent daemon failure.

        Creates a critical notification when the daemon hits max crashes
        and needs to stop. Includes crash history and debugging information.

        Args:
            crash_info: Dictionary with last crash details
                - timestamp: ISO timestamp
                - exception: Exception message
                - exception_type: Exception class name
                - priority: Priority being worked on
                - iteration: Iteration number

        Example:
            >>> daemon._notify_persistent_failure({
            ...     "timestamp": "2025-10-11T10:30:00",
            ...     "exception": "API timeout",
            ...     "exception_type": "TimeoutError",
            ...     "priority": "PRIORITY 2.7",
            ...     "iteration": 5
            ... })
        """
        # Build crash history summary
        crash_summary = "\n".join(
            [
                f"{i+1}. {c['timestamp']} - {c['exception_type']}: {c['exception'][:100]}"
                for i, c in enumerate(self.crash_history[-5:])  # Last 5 crashes
            ]
        )

        message = f"""🚨 CRITICAL: code_developer daemon has crashed {self.crash_count} times and stopped.

**Last Crash Details**:
- Time: {crash_info['timestamp']}
- Priority: {crash_info['priority']}
- Exception: {crash_info['exception_type']}
- Message: {crash_info['exception'][:200]}

**Recent Crash History** ({len(self.crash_history)} total):
{crash_summary}

**Action Required**:
1. Review crash logs for root cause
2. Check ROADMAP.md for problematic priority
3. Fix underlying issue (API, network, code bug)
4. Restart daemon: `poetry run code-developer`

**Debugging Steps**:
1. Check daemon logs: `tail -f ~/.coffee_maker/daemon.log`
2. Test Claude CLI: `claude -p "test"`
3. Verify API credits: Check Anthropic dashboard
4. Check network: `ping api.anthropic.com`
5. Review priority: `poetry run project-manager view {crash_info['priority']}`

The daemon will remain stopped until manually restarted.
"""

        self.notifications.create_notification(
            type=NOTIF_TYPE_ERROR,
            title="🚨 Daemon Persistent Failure",
            message=message,
            priority=NOTIF_PRIORITY_CRITICAL,
            context={
                "crash_count": self.crash_count,
                "crash_info": crash_info,
                "crash_history": self.crash_history,
                "requires_manual_intervention": True,
            },
            sound=False,
            agent_id="code_developer",
        )

        logger.critical("Created critical notification for persistent failure")

    def _write_status(self, priority=None):
        """Write current daemon status to file.

        PRIORITY 2.8: Daemon Status Reporting

        This method writes the daemon's current status to ~/.coffee_maker/daemon_status.json
        so that `project-manager status` can read and display it to the user.

        Called at:
        - Start of each iteration
        - After priority completion
        - After crash/recovery
        - On daemon stop

        Args:
            priority: Optional priority dictionary being worked on

        Status file format:
            {
                "pid": 12345,
                "status": "running" | "stopped",
                "started_at": "2025-10-11T10:30:00",
                "current_priority": {
                    "name": "PRIORITY 2.8",
                    "title": "Daemon Status Reporting",
                    "started_at": "2025-10-11T10:35:00"
                },
                "iteration": 5,
                "crashes": {
                    "count": 0,
                    "max": 3,
                    "history": [...]
                },
                "context": {
                    "iterations_since_compact": 2,
                    "compact_interval": 10,
                    "last_compact": "2025-10-11T10:00:00"
                },
                "last_update": "2025-10-11T10:45:00"
            }

        Example:
            >>> daemon = DevDaemon()
            >>> daemon._write_status(priority={"name": "PRIORITY 2.8", "title": "..."})
        """
        try:
            # Build status dictionary
            status = {
                "pid": os.getpid(),
                "status": "running" if self.running else "stopped",
                "started_at": (
                    getattr(self, "start_time", datetime.now()).isoformat() if hasattr(self, "start_time") else None
                ),
                "current_priority": (
                    {
                        "name": priority["name"] if priority else None,
                        "title": priority["title"] if priority else None,
                        "started_at": (
                            getattr(self, "current_priority_start_time", None).isoformat()
                            if hasattr(self, "current_priority_start_time") and self.current_priority_start_time
                            else None
                        ),
                    }
                    if priority
                    else None
                ),
                "iteration": getattr(self, "iteration_count", 0),
                "subtasks": self.current_subtasks,  # Include subtasks for status bar display
                "crashes": {
                    "count": self.crash_count,
                    "max": self.max_crashes,
                    "history": self.crash_history[-5:],  # Last 5 crashes
                },
                "context": {
                    "iterations_since_compact": self.iterations_since_compact,
                    "compact_interval": self.compact_interval,
                    "last_compact": (self.last_compact_time.isoformat() if self.last_compact_time else None),
                },
                "last_update": datetime.now().isoformat(),
            }

            # Write to status file
            status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

            write_json_file(status_file, status)

            logger.debug(f"Status written to {status_file}")

        except Exception as e:
            logger.error(f"Failed to write status file: {e}")

    def _update_subtask(
        self,
        name: str,
        status: str,
        start_time: datetime = None,
        estimated_seconds: int = 0,
    ):
        """Update or add a subtask to tracking list.

        This method tracks individual subtasks within a priority implementation
        for display in the project-manager status bar.

        Args:
            name: Subtask name (e.g., "Creating branch", "Calling Claude API")
            status: One of "pending", "in_progress", "completed", "failed"
            start_time: When subtask started (for duration calculation)
            estimated_seconds: Estimated time for this task in seconds

        Status meanings:
            - pending: Task not yet started (⏳)
            - in_progress: Currently working on this task (🔄)
            - completed: Task finished successfully (✓)
            - failed: Task encountered an error (❌)

        Example:
            >>> daemon._update_subtask("Creating branch", "in_progress", datetime.now(), estimated_seconds=10)
            >>> daemon._update_subtask("Creating branch", "completed", start_time, estimated_seconds=10)
        """
        # Calculate duration if start_time provided
        duration_seconds = 0
        if start_time and status in ["completed", "failed"]:
            duration_seconds = int((datetime.now() - start_time).total_seconds())
        elif start_time and status == "in_progress":
            # For in-progress tasks, show current elapsed time
            duration_seconds = int((datetime.now() - start_time).total_seconds())

        # Check if subtask already exists
        existing_idx = None
        for idx, subtask in enumerate(self.current_subtasks):
            if subtask["name"] == name:
                existing_idx = idx
                break

        subtask_entry = {
            "name": name,
            "status": status,
            "duration_seconds": duration_seconds,
            "estimated_seconds": estimated_seconds,
        }

        if existing_idx is not None:
            # Update existing subtask, preserve estimated_seconds if not provided
            if estimated_seconds == 0 and "estimated_seconds" in self.current_subtasks[existing_idx]:
                subtask_entry["estimated_seconds"] = self.current_subtasks[existing_idx]["estimated_seconds"]
            self.current_subtasks[existing_idx] = subtask_entry
        else:
            # Add new subtask
            self.current_subtasks.append(subtask_entry)

        logger.debug(f"Subtask updated: {name} -> {status} ({duration_seconds}s / est: {estimated_seconds}s)")

        # Record metrics to database when subtask completes or fails
        if status in ["completed", "failed"] and duration_seconds > 0 and self.current_priority_info:
            try:
                self.metrics_db.record_subtask(
                    priority_name=self.current_priority_info.get("name", "Unknown"),
                    subtask_name=name,
                    estimated_seconds=estimated_seconds,
                    actual_seconds=duration_seconds,
                    status=status,
                    priority_title=self.current_priority_info.get("title"),
                )
            except Exception as e:
                logger.warning(f"Failed to record metrics for subtask '{name}': {e}")

        # Write status to file immediately so status bar updates
        self._write_status()
