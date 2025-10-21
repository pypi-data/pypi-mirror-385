"""Team daemon status commands for user-listener.

This module provides commands for querying the multi-agent team daemon status:
- /team - Show overall team daemon status
- /agents - Show detailed status for all agents

These commands allow users to monitor the orchestrator and all 6 background agents
when running `poetry run user-listener --with-team`.

Example:
    >>> from coffee_maker.cli.commands.team import TeamStatusCommand, AgentsStatusCommand
    >>> team_cmd = TeamStatusCommand()
    >>> result = team_cmd.execute([], None)
    >>> print(result)
"""

import json
import logging
from pathlib import Path
from typing import List

from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.autonomous.message_queue import MessageQueue

logger = logging.getLogger(__name__)


class TeamStatusCommand(BaseCommand):
    """Show multi-agent team daemon status.

    Command: /team

    Displays:
    - Team daemon uptime
    - Number of agents running
    - Total tasks completed
    - Message queue depth
    - Overall team health
    """

    @property
    def name(self) -> str:
        return "team"

    @property
    def description(self) -> str:
        return "Show multi-agent team daemon status"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute /team command.

        Args:
            args: Command arguments (unused)
            editor: Roadmap editor instance (unused)

        Returns:
            Formatted status message
        """
        try:
            # Check if orchestrator database exists
            db_path = Path("data/orchestrator.db")
            if not db_path.exists():
                return (
                    "❌ Team daemon is NOT running\n\n"
                    "The multi-agent team daemon is not currently active.\n\n"
                    "To start it:\n"
                    "  1. Exit this session (Ctrl+D or /exit)\n"
                    "  2. Run: poetry run user-listener --with-team\n\n"
                    "Or start it separately:\n"
                    "  poetry run team-daemon start"
                )

            # Load message queue for metrics
            queue = MessageQueue(db_path=str(db_path))
            metrics = queue.get_task_metrics()

            # Format status message
            status_msg = [
                "=" * 70,
                "🤖 Multi-Agent Team Daemon Status",
                "=" * 70,
                "",
                f"Database: {db_path}",
                "",
                "📊 Task Metrics:",
                f"  Total tasks: {metrics['total_tasks']}",
                f"  Completed: {metrics['completed_tasks']} ✅",
                f"  Failed: {metrics['failed_tasks']} ❌",
                f"  Queued: {metrics['queued_tasks']} ⏳",
                f"  Running: {metrics['running_tasks']} 🔄",
                f"  Average duration: {metrics['avg_duration_ms']:.0f}ms",
                "",
                "💡 TIP: Use /agents to see detailed agent statuses",
                "=" * 70,
            ]

            return "\n".join(status_msg)

        except Exception as e:
            logger.error(f"Error getting team status: {e}")
            return f"❌ Error getting team status: {e}"


class AgentsStatusCommand(BaseCommand):
    """Show detailed status for all agents.

    Command: /agents

    Displays for each agent:
    - Agent name
    - Status (running, stopped, crashed)
    - Total tasks completed
    - Average task duration
    - Current activity
    """

    @property
    def name(self) -> str:
        return "agents"

    @property
    def description(self) -> str:
        return "Show detailed status for all agents"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute /agents command.

        Args:
            args: Optional agent name to filter by
            editor: Roadmap editor instance (unused)

        Returns:
            Formatted agents status message
        """
        try:
            # Check if orchestrator database exists
            db_path = Path("data/orchestrator.db")
            if not db_path.exists():
                return (
                    "❌ Team daemon is NOT running\n\n"
                    "The multi-agent team daemon is not currently active.\n\n"
                    "To start it:\n"
                    "  1. Exit this session (Ctrl+D or /exit)\n"
                    "  2. Run: poetry run user-listener --with-team\n\n"
                    "Or start it separately:\n"
                    "  poetry run team-daemon start"
                )

            # Load message queue for agent performance
            queue = MessageQueue(db_path=str(db_path))
            performance = queue.get_agent_performance()

            # Check if filtering by specific agent
            filter_agent = args[0] if args else None

            # Format agents status
            status_lines = [
                "=" * 70,
                "🤖 Agent Status Details",
                "=" * 70,
                "",
            ]

            if not performance:
                status_lines.append("⚠️  No agent performance data available yet")
                status_lines.append("")
                status_lines.append("Agents may still be initializing...")
            else:
                for agent_perf in performance:
                    agent_name = agent_perf["agent"]

                    # Skip if filtering and doesn't match
                    if filter_agent and filter_agent != agent_name:
                        continue

                    # Determine status emoji
                    if agent_perf["total_tasks"] > 0:
                        status_emoji = "🟢"  # Active
                    else:
                        status_emoji = "🟡"  # Idle

                    # Format duration safely (might be None if no completed tasks)
                    avg_duration = agent_perf["avg_duration_ms"] or 0
                    max_duration = agent_perf["max_duration_ms"] or 0

                    status_lines.extend(
                        [
                            f"{status_emoji} {agent_name}:",
                            f"  Total tasks: {agent_perf['total_tasks']}",
                            f"  Completed: {agent_perf['completed_tasks']} ✅",
                            f"  Failed: {agent_perf['failed_tasks']} ❌",
                            f"  Avg duration: {avg_duration:.0f}ms",
                            f"  Max duration: {max_duration:.0f}ms",
                            "",
                        ]
                    )

            # Check agent status files for additional info
            status_dir = Path("data/agent_status")
            if status_dir.exists():
                status_lines.append("📁 Agent Status Files:")
                for status_file in sorted(status_dir.glob("*_status.json")):
                    try:
                        with open(status_file, "r") as f:
                            status_data = json.load(f)
                        agent_name = status_file.stem.replace("_status", "")
                        state = status_data.get("state", "unknown")
                        last_update = status_data.get("last_heartbeat", "N/A")
                        status_lines.append(f"  {agent_name}: {state} (last: {last_update})")
                    except Exception as e:
                        logger.debug(f"Error reading {status_file}: {e}")

            status_lines.extend(
                [
                    "",
                    "💡 TIP: Use /team to see overall team status",
                    "=" * 70,
                ]
            )

            return "\n".join(status_lines)

        except Exception as e:
            logger.error(f"Error getting agents status: {e}")
            return f"❌ Error getting agents status: {e}"


__all__ = ["TeamStatusCommand", "AgentsStatusCommand"]
