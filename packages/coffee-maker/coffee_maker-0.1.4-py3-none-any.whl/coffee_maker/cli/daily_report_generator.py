"""Daily Report Generator for code_developer daemon.

PRIORITY 9: Enhanced code_developer Communication & Daily Standup
SPEC-009: Enhanced Communication & Daily Standup

This module generates daily reports showing code_developer's work from existing
infrastructure (git, developer_status.json, notifications.db).

Key Principle: REUSE existing data sources, don't create new infrastructure.
Timeline: 2 days (16 hours total)

Architecture:
- Read git commits (since yesterday)
- Read developer_status.json (current task, metrics)
- Query notifications.db (blockers)
- Format as markdown
- Display with rich.Console

Data Sources:
✅ Git: All commits tracked automatically
✅ developer_status.json: Current task, metrics, activity log
✅ notifications.db: Blockers, issues, questions
✅ rich library: Beautiful terminal rendering

Non-Goals:
❌ Complex scheduling (simple file-based tracking)
❌ Multi-channel delivery (terminal only)
❌ Real-time streaming (daily batch summary)
❌ Advanced metrics (reuse existing data)
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


class DailyReportGenerator:
    """Generate daily reports from existing data sources.

    SIMPLIFICATION: Uses existing infrastructure only. No new modules, databases,
    or complex abstractions.

    Data Sources:
    - Git log: All commits
    - developer_status.json: Current task, metrics, activity log
    - notifications.db: Blockers, issues
    """

    def __init__(self):
        """Initialize report generator with data file paths."""
        self.status_file = Path("data/developer_status.json")
        self.notifications_db = Path("data/notifications.db")
        self.interaction_file = Path("data/last_interaction.json")
        self.repo_root = Path.cwd()

    def should_show_report(self) -> bool:
        """Check if daily report should be shown.

        Returns True if:
        1. last_interaction.json doesn't exist (first time)
        2. Last report was shown on a different day

        Returns:
            True if report should be shown
        """
        if not self.interaction_file.exists():
            return True

        try:
            data = json.loads(self.interaction_file.read_text())
            last_report_shown = data.get("last_report_shown")

            if not last_report_shown:
                return True

            # Parse date (YYYY-MM-DD format)
            last_date = datetime.fromisoformat(last_report_shown).date()
            today = datetime.now().date()

            return last_date < today
        except (json.JSONDecodeError, ValueError):
            return True

    def update_interaction_timestamp(self) -> None:
        """Update last_interaction.json with current timestamp and date."""
        data = {
            "last_check_in": datetime.now().isoformat(),
            "last_report_shown": datetime.now().date().isoformat(),
        }
        self.interaction_file.parent.mkdir(parents=True, exist_ok=True)
        self.interaction_file.write_text(json.dumps(data, indent=2))

    def generate_report(self, since_date: Optional[datetime] = None, until_date: Optional[datetime] = None) -> str:
        """Generate markdown report for date range.

        Args:
            since_date: Start date (default: yesterday)
            until_date: End date (default: now)

        Returns:
            Markdown-formatted report string
        """
        # Set defaults
        if until_date is None:
            until_date = datetime.now()

        if since_date is None:
            since_date = datetime.now() - timedelta(days=1)

        # Collect data from all sources
        commits = self._collect_git_commits(since_date)
        status_data = self._load_developer_status()
        blockers = self._collect_blockers()

        # Calculate stats
        stats = self._calculate_stats(commits)

        # Group commits by priority
        grouped_commits = self._group_commits_by_priority(commits)

        # Format as markdown
        report = self._format_as_markdown(
            since_date=since_date,
            commits=grouped_commits,
            stats=stats,
            status_data=status_data,
            blockers=blockers,
        )

        return report

    def _collect_git_commits(self, since: datetime) -> list[dict]:
        """Get commits since date using git log.

        Args:
            since: Only get commits after this datetime

        Returns:
            List of commit dictionaries with hash, author, date, message, stats
        """
        try:
            # Use git log to get commits
            cmd = [
                "git",
                "log",
                f"--since={since.isoformat()}",
                "--pretty=format:%H|%an|%ai|%s",
                "--numstat",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            commits = []
            lines = result.stdout.strip().split("\n")

            i = 0
            while i < len(lines):
                line = lines[i]

                if not line or "|" not in line:
                    i += 1
                    continue

                # Parse commit line: hash|author|date|message
                parts = line.split("|", 3)
                if len(parts) < 4:
                    i += 1
                    continue

                commit_hash, author, date_str, message = parts

                # Collect file statistics (lines after commit line)
                files_changed = 0
                lines_added = 0
                lines_removed = 0

                i += 1
                while i < len(lines) and lines[i].strip() and "|" not in lines[i]:
                    stat_parts = lines[i].split("\t")
                    if len(stat_parts) >= 2:
                        try:
                            added = int(stat_parts[0]) if stat_parts[0] != "-" else 0
                            removed = int(stat_parts[1]) if stat_parts[1] != "-" else 0
                            lines_added += added
                            lines_removed += removed
                            files_changed += 1
                        except (ValueError, IndexError):
                            pass
                    i += 1

                commits.append(
                    {
                        "hash": commit_hash[:8],
                        "author": author,
                        "date": date_str,
                        "message": message,
                        "files_changed": files_changed,
                        "lines_added": lines_added,
                        "lines_removed": lines_removed,
                    }
                )

            return commits

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _group_commits_by_priority(self, commits: list[dict]) -> dict:
        """Group commits by priority mentioned in message.

        Args:
            commits: List of commit dictionaries

        Returns:
            Dictionary with priority as key, list of commits as value
        """
        grouped = {}
        untagged = []

        for commit in commits:
            message = commit["message"]

            # Try to extract priority (feat: PRIORITY 9 - ...)
            match = re.search(r"PRIORITY\s+(\d+)", message)

            if match:
                priority = f"PRIORITY {match.group(1)}"
                if priority not in grouped:
                    grouped[priority] = []
                grouped[priority].append(commit)
            else:
                untagged.append(commit)

        # Add untagged to "Other" category if any
        if untagged:
            grouped["Other"] = untagged

        return grouped

    def _calculate_stats(self, commits: list[dict]) -> dict:
        """Calculate summary statistics.

        Args:
            commits: List of commit dictionaries

        Returns:
            Dictionary with stats
        """
        return {
            "total_commits": len(commits),
            "files_changed": sum(c.get("files_changed", 0) for c in commits),
            "lines_added": sum(c.get("lines_added", 0) for c in commits),
            "lines_removed": sum(c.get("lines_removed", 0) for c in commits),
        }

    def _load_developer_status(self) -> dict:
        """Load developer status from JSON file.

        Returns:
            Status dictionary
        """
        try:
            if self.status_file.exists():
                return json.loads(self.status_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

        return {}

    def _collect_blockers(self) -> list[dict]:
        """Collect blockers from notifications.

        Returns:
            List of blocker notifications
        """
        # For MVP, return empty list
        # Phase 2 will integrate with notifications.db
        return []

    def _format_as_markdown(
        self,
        since_date: datetime,
        commits: dict,
        stats: dict,
        status_data: dict,
        blockers: list,
    ) -> str:
        """Format all data as markdown report.

        Args:
            since_date: Report start date
            commits: Grouped commits by priority
            stats: Summary statistics
            status_data: Developer status data
            blockers: List of blockers

        Returns:
            Markdown-formatted report string
        """
        lines = []

        # Header
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_date = since_date.strftime("%Y-%m-%d")
        lines.append(f"# 🤖 code_developer Daily Report - {report_date}")
        lines.append("=" * 60)
        lines.append("")

        # Yesterday's work section
        lines.append(f"## 📊 Yesterday's Work ({report_date})")
        lines.append("")

        if not commits or stats["total_commits"] == 0:
            lines.append("No activity yesterday.")
        else:
            # Group by priority
            for priority, priority_commits in sorted(commits.items()):
                lines.append(f"### ✅ {priority}")
                lines.append("")

                # Show commits for this priority
                for commit in priority_commits:
                    message = commit["message"][:60]
                    lines.append(f"- {message}")

                # Stats for this priority
                priority_stats = self._calculate_stats(priority_commits)
                lines.append("")
                lines.append(f"  **Commits**: {priority_stats['total_commits']}")
                lines.append(f"  **Files**: {priority_stats['files_changed']} modified")
                if priority_stats["lines_added"] > 0 or priority_stats["lines_removed"] > 0:
                    lines.append(f"  **Lines**: +{priority_stats['lines_added']} / -{priority_stats['lines_removed']}")
                lines.append("")

        # Overall stats
        lines.append("## 📈 Overall Stats")
        lines.append("")
        lines.append(f"- **Total Commits**: {stats['total_commits']}")
        lines.append(f"- **Files Modified**: {stats['files_changed']}")
        if stats["lines_added"] > 0 or stats["lines_removed"] > 0:
            lines.append(f"- **Lines Added**: +{stats['lines_added']}")
            lines.append(f"- **Lines Removed**: -{stats['lines_removed']}")
        lines.append("")

        # Current task
        current_task = status_data.get("current_task", {})
        if current_task:
            lines.append("## 🔄 Today's Focus")
            lines.append("")
            task_name = current_task.get("name", "Unknown")
            lines.append(f"- {task_name}")
            progress = current_task.get("progress", 0)
            if progress > 0:
                lines.append(f"  Progress: {progress}%")
            lines.append("")

        # Blockers
        if blockers:
            lines.append("## ⚠️ Blockers")
            lines.append("")
            for blocker in blockers:
                lines.append(f"- {blocker['title']}")
            lines.append("")
        else:
            lines.append("## ✅ Blockers")
            lines.append("")
            lines.append("None")
            lines.append("")

        # Footer
        lines.append("-" * 60)
        lines.append(f"Report generated: {now}")
        lines.append("")

        return "\n".join(lines)


def should_show_report() -> bool:
    """Check if daily report should be shown.

    Returns:
        True if report should be shown on first interaction of new day
    """
    generator = DailyReportGenerator()
    return generator.should_show_report()


def show_daily_report() -> None:
    """Show daily report and update interaction timestamp."""
    generator = DailyReportGenerator()

    # Generate report for yesterday
    since_date = datetime.now() - timedelta(days=1)
    report = generator.generate_report(since_date=since_date)

    # Display with rich
    panel = Panel(
        Markdown(report),
        title="[bold cyan]📊 DAILY STANDUP[/bold cyan]",
        style="cyan",
    )
    console.print(panel)
    console.print()

    # Update interaction timestamp
    generator.update_interaction_timestamp()
