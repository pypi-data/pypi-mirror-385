"""Update priority command - Update existing priority fields.

Example:
    >>> from coffee_maker.cli.commands.update_priority import UpdatePriorityCommand
    >>> command = UpdatePriorityCommand()
    >>> response = command.execute(["3", "status", "✅ Complete"], editor)
"""

import logging
from typing import List

from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class UpdatePriorityCommand(BaseCommand):
    """Update existing priority field.

    Usage: /update <priority> <field> <value>

    Supported fields:
    - status: Update priority status
    - duration: Update duration estimate
    - impact: Update impact level

    Example:
        /update 3 status ✅ Complete
        /update PRIORITY 5 duration 2-3 weeks
        /update 2 impact ⭐⭐⭐⭐⭐
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "update"

    @property
    def description(self) -> str:
        """Command description."""
        return "Update existing priority field (status, duration, impact)"

    def get_usage(self) -> str:
        """Get usage string."""
        return (
            "Usage: /update <priority> <field> <value>\n"
            "Fields: status, duration, impact\n"
            "Example: /update 3 status ✅ Complete"
        )

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute update command.

        Args:
            args: [priority_number, field, value...]
            editor: RoadmapEditor instance

        Returns:
            Response message
        """
        if not self.validate_min_args(args, 3):
            return self.format_error(f"Insufficient arguments\n{self.get_usage()}")

        try:
            # Parse arguments
            priority = args[0]
            field = args[1]
            value = " ".join(args[2:])  # Value can be multiple words

            # Validate field
            valid_fields = ["status", "duration", "impact"]
            if field.lower() not in valid_fields:
                return self.format_error(f"Invalid field: {field}\n" f"Valid fields: {', '.join(valid_fields)}")

            # Normalize priority number
            if not priority.upper().startswith("PRIORITY"):
                priority = f"PRIORITY {priority}"

            # Update priority
            success = editor.update_priority(priority_number=priority, field=field, value=value)

            if success:
                return self.format_success(
                    f"Updated {priority}\n"
                    f"**{field.title()}**: {value}\n\n"
                    f"Use `/view {priority.split()[-1]}` to see the updated priority."
                )
            else:
                return self.format_error("Failed to update priority")

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return self.format_error(str(e))
        except Exception as e:
            logger.error(f"Failed to update priority: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")
