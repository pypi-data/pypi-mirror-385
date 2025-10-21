"""Developer status display for CLI.

This module provides formatted display of developer status from the daemon.
Used by project-manager developer-status command.

PRIORITY 4: Developer Status Dashboard
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from coffee_maker.utils.file_io import read_json_file


class DeveloperStatusDisplay:
    """Display developer status in the terminal.

    Reads data/developer_status.json and formats it for terminal display
    using Rich library for colors, progress bars, and formatting.

    Example:
        >>> display = DeveloperStatusDisplay()
        >>> display.show()  # One-time display
        >>> display.watch()  # Continuous updates
    """

    def __init__(self, status_file: Optional[Path] = None):
        """Initialize status display.

        Args:
            status_file: Path to status JSON file (default: data/developer_status.json)
        """
        if status_file is None:
            status_file = Path("data/developer_status.json")
        self.status_file = status_file
        self.console = Console()

    def show(self) -> bool:
        """Show current developer status once.

        Returns:
            True if status displayed, False if not available
        """
        status = self._read_status()

        if not status:
            self.console.print("[yellow]⚠️  Developer status not available[/yellow]")
            self.console.print()
            self.console.print("The code_developer daemon may not be running.")
            self.console.print()
            self.console.print("To start the daemon:")
            self.console.print("  poetry run code-developer")
            return False

        self.console.print(self._format_status(status))
        return True

    def watch(self, interval: int = 5):
        """Continuously watch and update developer status.

        Args:
            interval: Update interval in seconds (default: 5)
        """
        try:
            with Live(
                self._format_status(self._read_status() or {}),
                refresh_per_second=0.2,
                console=self.console,
            ) as live:
                while True:
                    time.sleep(interval)
                    status = self._read_status()
                    if status:
                        live.update(self._format_status(status))
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Watch mode stopped[/yellow]")

    def _read_status(self) -> Optional[dict]:
        """Read status from JSON file.

        Returns:
            Status dictionary or None if not available
        """
        if not self.status_file.exists():
            return None

        try:
            return read_json_file(self.status_file, default=None)
        except Exception as e:
            self.console.print(f"[red]Error reading status file: {e}[/red]")
            return None

    def _format_status(self, status: dict) -> Panel:
        """Format status dictionary for display.

        Args:
            status: Status dictionary

        Returns:
            Rich Panel with formatted status
        """
        if not status:
            return Panel(
                Text("Developer status not available", style="yellow"),
                title="Developer Status",
                border_style="yellow",
            )

        # Build status content
        content = Table.grid(padding=(0, 2))
        content.add_column(style="bold cyan", justify="right")
        content.add_column()

        # State with emoji
        state = status.get("status", "stopped")
        state_emoji = self._get_state_emoji(state)
        content.add_row("State:", f"{state_emoji} {state.upper()}")

        # Current task
        current_task = status.get("current_task")
        if current_task:
            task_name = current_task.get("name", "Unknown")
            content.add_row("Task:", task_name)

            # Progress bar
            progress = current_task.get("progress", 0)
            content.add_row("Progress:", self._format_progress_bar(progress))

            # Current step
            current_step = current_task.get("current_step", "")
            if current_step:
                content.add_row("Step:", current_step)

            # ETA
            eta_seconds = current_task.get("eta_seconds", 0)
            if eta_seconds > 0:
                eta_formatted = self._format_duration(eta_seconds)
                content.add_row("ETA:", eta_formatted)

            # Task started
            started_at = current_task.get("started_at")
            if started_at:
                elapsed = self._format_elapsed(started_at)
                content.add_row("Elapsed:", elapsed)

        # Last activity
        last_activity = status.get("last_activity")
        if last_activity:
            last_activity.get("type", "unknown")
            activity_desc = last_activity.get("description", "")
            timestamp = last_activity.get("timestamp", "")

            if timestamp:
                time_ago = self._format_time_ago(timestamp)
                activity_text = f"{activity_desc} ({time_ago})"
            else:
                activity_text = activity_desc

            content.add_row("Last Activity:", activity_text)

        # Pending questions
        questions = status.get("questions", [])
        if questions:
            content.add_row("")  # Spacer
            content.add_row("Pending Questions:", f"[red]{len(questions)} question(s)[/red]")

            for i, question in enumerate(questions[:3], 1):  # Show max 3
                q_message = question.get("message", "")
                content.add_row(f"  Q{i}:", q_message)

        # Metrics
        metrics = status.get("metrics", {})
        if metrics:
            content.add_row("")  # Spacer
            content.add_row(
                "Today:",
                f"Tasks: {metrics.get('tasks_completed_today', 0)} | "
                f"Commits: {metrics.get('total_commits_today', 0)} | "
                f"Tests: {metrics.get('tests_passed_today', 0)}/{metrics.get('tests_failed_today', 0)}",
            )

        # Daemon info
        daemon_info = status.get("daemon_info", {})
        if daemon_info:
            pid = daemon_info.get("pid")
            started_at = daemon_info.get("started_at")

            if pid:
                content.add_row("")  # Spacer
                content.add_row("Daemon PID:", str(pid))

            if started_at:
                uptime = self._format_elapsed(started_at)
                content.add_row("Uptime:", uptime)

        # Border style based on state
        border_style = self._get_border_style(state)

        return Panel(
            content,
            title=f"[bold]Developer Status Dashboard[/bold]",
            border_style=border_style,
            padding=(1, 2),
        )

    def _get_state_emoji(self, state: str) -> str:
        """Get emoji for developer state.

        Args:
            state: State string

        Returns:
            Emoji character
        """
        emoji_map = {
            "working": "🟢",
            "testing": "🟡",
            "blocked": "🔴",
            "idle": "⚪",
            "thinking": "🔵",
            "reviewing": "🟣",
            "stopped": "⚫",
        }
        return emoji_map.get(state, "⚪")

    def _get_border_style(self, state: str) -> str:
        """Get border style for state.

        Args:
            state: State string

        Returns:
            Rich color style
        """
        style_map = {
            "working": "green",
            "testing": "yellow",
            "blocked": "red",
            "idle": "white",
            "thinking": "blue",
            "reviewing": "magenta",
            "stopped": "dim",
        }
        return style_map.get(state, "white")

    def _format_progress_bar(self, progress: int) -> str:
        """Format progress as a bar.

        Args:
            progress: Progress percentage (0-100)

        Returns:
            Rich formatted progress bar
        """
        # Create progress bar
        bar_width = 30
        filled = int((progress / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        # Color based on progress
        if progress < 30:
            color = "red"
        elif progress < 70:
            color = "yellow"
        else:
            color = "green"

        return f"[{color}]{bar}[/{color}] {progress}%"

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration (e.g., "2h 30m", "45s")
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def _format_elapsed(self, started_at: str) -> str:
        """Format elapsed time since started_at.

        Args:
            started_at: ISO timestamp string

        Returns:
            Formatted elapsed time
        """
        try:
            start = datetime.fromisoformat(started_at.replace("Z", ""))
            elapsed = datetime.utcnow() - start
            return self._format_duration(int(elapsed.total_seconds()))
        except Exception:
            return "unknown"

    def _format_time_ago(self, timestamp: str) -> str:
        """Format timestamp as 'X ago'.

        Args:
            timestamp: ISO timestamp string

        Returns:
            Formatted time ago (e.g., "2m ago", "just now")
        """
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", ""))
            elapsed = datetime.utcnow() - ts
            seconds = int(elapsed.total_seconds())

            if seconds < 10:
                return "just now"
            elif seconds < 60:
                return f"{seconds}s ago"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes}m ago"
            else:
                hours = seconds // 3600
                return f"{hours}h ago"
        except Exception:
            return "unknown"
