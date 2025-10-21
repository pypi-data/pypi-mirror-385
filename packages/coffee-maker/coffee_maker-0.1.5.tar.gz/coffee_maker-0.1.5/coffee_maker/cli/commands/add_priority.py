"""Add priority command - Add new priority to roadmap.

Example:
    >>> from coffee_maker.cli.commands.add_priority import AddPriorityCommand
    >>> command = AddPriorityCommand()
    >>> response = command.execute(["User", "Authentication"], editor)
"""

import logging
from typing import List

from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class AddPriorityCommand(BaseCommand):
    """Add new priority to roadmap.

    Usage: /add <priority_title>

    Example:
        /add User Authentication
        /add Rate Limiting Feature
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "add"

    @property
    def description(self) -> str:
        """Command description."""
        return "Add new priority to roadmap"

    def get_usage(self) -> str:
        """Get usage string."""
        return "Usage: /add <priority_title>"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute add command.

        Args:
            args: Priority title words
            editor: RoadmapEditor instance

        Returns:
            Response message
        """
        if not self.validate_min_args(args, 1):
            return self.format_error(f"Priority title required\n{self.get_usage()}")

        try:
            # Join args to form title
            title = " ".join(args)

            # Get current summary to determine next priority number
            summary = editor.get_priority_summary()
            next_number = summary["total"] + 1

            # Create priority number
            priority_number = f"PRIORITY {next_number}"

            # Add priority with default values
            success = editor.add_priority(
                priority_number=priority_number,
                title=title,
                duration="TBD (define during planning)",
                impact="⭐⭐⭐",
                status="📝 Planned",
                description=f"Implementation of {title}.",
                deliverables=[
                    "Define technical specification",
                    "Implement core functionality",
                    "Add tests",
                    "Update documentation",
                ],
            )

            if success:
                return self.format_success(
                    f"Added {priority_number}: {title}\n\n"
                    f"**Next steps**:\n"
                    f"- Review and refine the priority details\n"
                    f"- Update duration estimate\n"
                    f"- Adjust impact level\n"
                    f"- Define specific deliverables\n\n"
                    f"Use `/view {next_number}` to see the full priority."
                )
            else:
                return self.format_error("Failed to add priority")

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return self.format_error(str(e))
        except Exception as e:
            logger.error(f"Failed to add priority: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")
