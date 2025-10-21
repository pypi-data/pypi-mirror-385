"""View roadmap command - Display roadmap or specific priority.

Example:
    >>> from coffee_maker.cli.commands.view_roadmap import ViewRoadmapCommand
    >>> command = ViewRoadmapCommand()
    >>> response = command.execute([], editor)  # View summary
    >>> response = command.execute(["3"], editor)  # View PRIORITY 3
"""

import logging
from typing import List


from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class ViewRoadmapCommand(BaseCommand):
    """View roadmap or specific priority.

    Usage:
        /view              - View roadmap summary
        /view <priority>   - View specific priority

    Example:
        /view
        /view 3
        /view PRIORITY 5
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "view"

    @property
    def description(self) -> str:
        """Command description."""
        return "View roadmap summary or specific priority"

    def get_usage(self) -> str:
        """Get usage string."""
        return (
            "Usage:\n" "  /view              - View roadmap summary\n" "  /view <priority>   - View specific priority"
        )

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute view command.

        Args:
            args: Optional priority number
            editor: RoadmapEditor instance

        Returns:
            Response message (markdown formatted)
        """
        try:
            if args:
                # View specific priority
                return self._view_priority(args[0], editor)
            else:
                # View summary
                return self._view_summary(editor)

        except Exception as e:
            logger.error(f"Failed to view roadmap: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")

    def _view_summary(self, editor: RoadmapEditor) -> str:
        """View roadmap summary.

        Args:
            editor: RoadmapEditor instance

        Returns:
            Formatted summary
        """
        summary = editor.get_priority_summary()

        if summary["total"] == 0:
            return "No priorities found in roadmap."

        # Build markdown table
        output = "## 📋 Roadmap Summary\n\n"

        # Progress bar
        total = summary["total"]
        completed = summary["completed"]
        progress_pct = (completed / total * 100) if total > 0 else 0

        output += f"**Overall Progress**: {progress_pct:.0f}% ({completed}/{total} completed)\n\n"

        # Status breakdown
        output += "**Status Breakdown**:\n"
        output += f"- ✅ Completed: {summary['completed']}\n"
        output += f"- 🔄 In Progress: {summary['in_progress']}\n"
        output += f"- 📝 Planned: {summary['planned']}\n\n"

        # Priority table
        output += "| Priority | Title | Status |\n"
        output += "|----------|-------|--------|\n"

        for p in summary["priorities"]:
            output += f"| {p['number']} | {p['title']} | {p['status']} |\n"

        output += "\n**Tip**: Use `/view <priority>` to see detailed information about a specific priority.\n"

        return output

    def _view_priority(self, priority: str, editor: RoadmapEditor) -> str:
        """View specific priority.

        Args:
            priority: Priority number
            editor: RoadmapEditor instance

        Returns:
            Formatted priority content
        """
        # Normalize priority number
        if not priority.upper().startswith("PRIORITY"):
            priority = f"PRIORITY {priority}"

        content = editor.get_priority_content(priority)

        if not content:
            return self.format_error(f"{priority} not found in roadmap\n" f"Use `/view` to see all priorities.")

        return f"## {priority}\n\n{content}"
