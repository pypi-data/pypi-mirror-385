"""Orchestrator Rich UI Dashboard.

Provides real-time visualization of:
- Active agents (architect, code_developer, project_manager)
- Current tasks and progress
- Success metrics
- System health

Author: code_developer
Date: 2025-10-19
"""

import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import agent management skill
skill_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "orchestrator-agent-management"
sys.path.insert(0, str(skill_dir))
from agent_management import OrchestratorAgentManagementSkill

sys.path.pop(0)

# Import roadmap management skill
roadmap_skill_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "roadmap-management"
sys.path.insert(0, str(roadmap_skill_dir))
from roadmap_management import RoadmapManagementSkill

sys.path.pop(0)

logger = logging.getLogger(__name__)


class OrchestratorDashboard:
    """Real-time dashboard for orchestrator activities."""

    def __init__(self):
        """Initialize dashboard."""
        self.console = Console()
        self.agent_mgmt = OrchestratorAgentManagementSkill()
        self.roadmap_mgmt = RoadmapManagementSkill()

        # Get orchestrator start time from database
        self.start_time = None
        self._load_start_time()

    def _load_start_time(self):
        """Load orchestrator start time from database (CFR-014 compliant)."""
        try:
            import sqlite3

            db_path = Path("data/orchestrator.db")
            if not db_path.exists():
                self.start_time = datetime.now()
                return

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM orchestrator_state WHERE key = 'orchestrator_start_time'")
            row = cursor.fetchone()
            conn.close()

            if row:
                self.start_time = datetime.fromisoformat(row[0])
            else:
                self.start_time = datetime.now()

        except Exception as e:
            logger.warning(f"Failed to load start time from database: {e}")
            self.start_time = datetime.now()

    def _make_system_overview(self) -> Panel:
        """Create system overview panel.

        Returns:
            Rich Panel with system metrics
        """
        # Calculate uptime (handle None case)
        if self.start_time:
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split(".")[0]  # Remove microseconds
        else:
            uptime_str = "Unknown"

        # Get active agents count (only running agents)
        active_result = self.agent_mgmt.execute(action="list_active_agents")
        active_count = active_result.get("result", {}).get("total", 0) if not active_result.get("error") else 0

        # Get ROADMAP stats
        roadmap_stats = self._get_roadmap_stats()

        # Build overview text
        overview = Text()
        overview.append("🤖 Orchestrator Status\n", style="bold cyan")
        overview.append(f"Uptime: {uptime_str}\n", style="white")
        overview.append(f"Running Agents: {active_count}\n", style="green" if active_count > 0 else "yellow")
        overview.append(f"ROADMAP Health: {roadmap_stats['health']}\n", style=roadmap_stats["health_style"])
        overview.append(f"Priorities: {roadmap_stats['completed']}/{roadmap_stats['total']} completed\n", style="white")

        return Panel(overview, title="System Overview", border_style="cyan")

    def _get_roadmap_stats(self) -> Dict[str, Any]:
        """Get ROADMAP statistics using roadmap-management skill.

        Returns:
            Dict with total, completed, in_progress, planned counts and health
        """
        try:
            # Load priorities from roadmap-management skill
            result = self.roadmap_mgmt.execute(operation="get_all_priorities")
            if result.get("error"):
                logger.error(f"Failed to load ROADMAP: {result['error']}")
                return {
                    "total": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "planned": 0,
                    "health": "Error",
                    "health_style": "red",
                }

            priorities = result.get("result", [])
            total = len(priorities)
            completed = len([p for p in priorities if p["status_emoji"] == "✅"])
            in_progress = len([p for p in priorities if p["status_emoji"] == "🔄"])
            planned = len([p for p in priorities if p["status_emoji"] == "📝"])

            # Calculate health
            if in_progress > 0:
                health = "Working"
                health_style = "green"
            elif planned > 0:
                health = "Idle (work available)"
                health_style = "yellow"
            else:
                health = "All complete!"
                health_style = "cyan"

            return {
                "total": total,
                "completed": completed,
                "in_progress": in_progress,
                "planned": planned,
                "health": health,
                "health_style": health_style,
            }
        except Exception as e:
            logger.error(f"Error getting ROADMAP stats: {e}")
            return {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planned": 0,
                "health": "Error",
                "health_style": "red",
            }

    def _make_agents_table(self) -> Table:
        """Create running agents table.

        Returns:
            Rich Table with agent details
        """
        table = Table(title="Running Agents", show_header=True, header_style="bold magenta")
        table.add_column("PID", style="cyan", width=8)
        table.add_column("Agent Type", style="yellow", width=18)
        table.add_column("Task ID", style="white", width=20)
        table.add_column("Status", style="green", width=12)
        table.add_column("Duration", style="blue", width=12)

        # Get active agents
        result = self.agent_mgmt.execute(action="list_active_agents")

        if result.get("error"):
            table.add_row("—", "Error", result["error"], "—", "—")
            return table

        active_agents = result.get("result", {}).get("active_agents", [])

        if not active_agents:
            table.add_row("—", "No running agents", "—", "—", "—")
            return table

        for agent in active_agents:
            # Format duration
            duration_seconds = agent.get("duration", 0)
            duration_str = str(timedelta(seconds=int(duration_seconds))).split(".")[0]

            # Status emoji
            status = agent.get("status", "unknown")
            status_display = "🟢 Running" if status == "running" else "✅ Complete" if status == "completed" else status

            table.add_row(
                str(agent["pid"]),
                agent["agent_type"],
                agent["task_id"],
                status_display,
                duration_str,
            )

        return table

    def _make_work_queue(self) -> Panel:
        """Create work queue panel showing pending priorities.

        Now shows TWO separate queues:
        1. architect queue (missing specs) - priorities need specs before implementation
        2. code_developer queue (have specs) - ready for implementation

        Returns:
            Rich Panel with both work queues
        """
        try:
            # Load priorities from roadmap-management skill
            result = self.roadmap_mgmt.execute(operation="get_all_priorities")
            if result.get("error"):
                return Panel(f"Error loading ROADMAP: {result['error']}", title="Work Queue", border_style="red")

            priorities = result.get("result", [])
            planned = [p for p in priorities if p["status_emoji"] == "📝"]  # All planned

            # Separate into two queues based on spec availability
            architect_queue = []  # Missing specs
            developer_queue = []  # Have specs

            for p in planned:
                has_spec = p.get("technical_spec") is not None and p.get("technical_spec") != ""
                if has_spec:
                    developer_queue.append(p)
                else:
                    architect_queue.append(p)

            if not architect_queue and not developer_queue:
                queue_text = Text("No pending work", style="green")
            else:
                queue_text = Text()

                # Show architect queue (missing specs)
                if architect_queue:
                    queue_text.append("🏗️  architect Queue (Missing Specs):\n", style="bold magenta")
                    for i, p in enumerate(architect_queue[:3], 1):  # Show first 3
                        us_id = p.get("us_id", f"PRIORITY {p['number']}")
                        title = p.get("title", "No title")
                        queue_text.append(f"  {i}. {us_id} ❌ {title}\n", style="magenta")
                    if len(architect_queue) > 3:
                        queue_text.append(f"  ... and {len(architect_queue) - 3} more\n", style="dim magenta")
                    queue_text.append("\n")

                # Show code_developer queue (have specs)
                if developer_queue:
                    queue_text.append("💻 code_developer Queue (Ready):\n", style="bold cyan")
                    for i, p in enumerate(developer_queue[:3], 1):  # Show first 3
                        us_id = p.get("us_id", f"PRIORITY {p['number']}")
                        title = p.get("title", "No title")
                        queue_text.append(f"  {i}. {us_id} 📄 {title}\n", style="cyan")
                    if len(developer_queue) > 3:
                        queue_text.append(f"  ... and {len(developer_queue) - 3} more\n", style="dim cyan")
                else:
                    queue_text.append("💻 code_developer Queue (Ready):\n", style="bold cyan")
                    queue_text.append("  (Waiting for architect to create specs)\n", style="dim cyan")

            return Panel(queue_text, title="Work Queues", border_style="yellow")

        except Exception as e:
            logger.error(f"Error creating work queue: {e}")
            return Panel(f"Error: {str(e)}", title="Work Queue", border_style="red")

    def _make_metrics_panel(self) -> Panel:
        """Create success metrics panel.

        Returns:
            Rich Panel with metrics
        """
        # Calculate metrics from ROADMAP
        stats = self._get_roadmap_stats()
        total = stats["total"]
        completed = stats["completed"]

        completion_pct = (completed / total * 100) if total > 0 else 0

        metrics = Text()
        metrics.append("📊 Success Metrics\n", style="bold cyan")
        metrics.append(f"Completion: {completion_pct:.1f}%\n", style="green")
        metrics.append(f"Completed: {completed}\n", style="white")
        metrics.append(f"In Progress: {stats['in_progress']}\n", style="yellow")
        metrics.append(f"Planned: {stats['planned']}\n", style="blue")

        return Panel(metrics, title="Metrics", border_style="cyan")

    def _make_dashboard_layout(self) -> Layout:
        """Create dashboard layout.

        Returns:
            Rich Layout with all panels
        """
        layout = Layout()

        # Split into header and body
        layout.split(
            Layout(name="header", size=8),
            Layout(name="body"),
        )

        # Split header into overview and metrics
        layout["header"].split_row(
            Layout(self._make_system_overview(), name="overview"),
            Layout(self._make_metrics_panel(), name="metrics"),
        )

        # Split body into agents table and work queue
        layout["body"].split(
            Layout(self._make_agents_table(), name="agents", ratio=2),
            Layout(self._make_work_queue(), name="queue", ratio=1),
        )

        return layout

    def run(self, refresh_interval: int = 3):
        """Run dashboard with live updates.

        Args:
            refresh_interval: Refresh interval in seconds (default: 3)
        """
        self.console.clear()
        self.console.print("[bold cyan]🚀 Orchestrator Dashboard[/bold cyan]")
        self.console.print(f"[dim]Refresh interval: {refresh_interval}s | Press Ctrl+C to exit[/dim]\n")

        try:
            with Live(self._make_dashboard_layout(), refresh_per_second=1 / refresh_interval, console=self.console):
                while True:
                    time.sleep(refresh_interval)
                    # ROADMAP data is loaded fresh on each render via roadmap-management skill

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped[/yellow]")
