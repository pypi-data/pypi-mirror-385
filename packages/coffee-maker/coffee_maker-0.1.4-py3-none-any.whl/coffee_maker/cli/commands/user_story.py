"""User Story command - Manage User Stories in roadmap backlog.

Example:
    >>> from coffee_maker.cli.commands.user_story import UserStoryCommand
    >>> command = UserStoryCommand()
    >>> response = command.execute(["list"], editor)  # List all User Stories
    >>> response = command.execute(["view", "US-001"], editor)  # View specific story
"""

import logging
from typing import List

from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class UserStoryCommand(BaseCommand):
    """Manage User Stories in roadmap backlog.

    Usage:
        /user-story list                   - List all User Stories
        /user-story view <id>              - View specific User Story
        /user-story add                    - Guided User Story creation (interactive)
        /user-story update <id> <field> <value>  - Update User Story field
        /user-story assign <id> <priority> - Assign story to priority

    Example:
        /user-story list
        /user-story view US-001
        /user-story add
        /user-story update US-001 status "🔄 In Discussion"
        /user-story assign US-001 "PRIORITY 4"
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "user-story"

    @property
    def description(self) -> str:
        """Command description."""
        return "Manage User Stories in backlog"

    def get_usage(self) -> str:
        """Get usage string."""
        return (
            "Usage:\n"
            "  /user-story list                   - List all User Stories\n"
            "  /user-story view <id>              - View specific User Story\n"
            "  /user-story add                    - Guided creation (interactive)\n"
            "  /user-story update <id> <field> <value> - Update field\n"
            "  /user-story assign <id> <priority> - Assign to priority"
        )

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute user-story command.

        Args:
            args: Subcommand and arguments
            editor: RoadmapEditor instance

        Returns:
            Response message (markdown formatted)
        """
        if not args:
            return self.get_usage()

        subcommand = args[0].lower()

        try:
            if subcommand == "list":
                return self._list_user_stories(editor)

            elif subcommand == "view":
                if len(args) < 2:
                    return self.format_error("Missing story ID\n" + self.get_usage())
                return self._view_user_story(args[1], editor)

            elif subcommand == "add":
                return self._add_user_story_interactive(editor)

            elif subcommand == "update":
                if len(args) < 4:
                    return self.format_error("Missing arguments\n" "Usage: /user-story update <id> <field> <value>")
                return self._update_user_story(args[1], args[2], " ".join(args[3:]), editor)

            elif subcommand == "assign":
                if len(args) < 3:
                    return self.format_error("Missing arguments\n" "Usage: /user-story assign <id> <priority>")
                return self._assign_user_story(args[1], " ".join(args[2:]), editor)

            else:
                return self.format_error(f"Unknown subcommand: {subcommand}\n" + self.get_usage())

        except Exception as e:
            logger.error(f"Failed to execute user-story command: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")

    def _list_user_stories(self, editor: RoadmapEditor) -> str:
        """List all User Stories with summary.

        Args:
            editor: RoadmapEditor instance

        Returns:
            Formatted list of User Stories
        """
        summary = editor.get_user_story_summary()

        if summary["total"] == 0:
            return "No User Stories found in backlog.\n\n" "Use `/user-story add` to create your first User Story."

        # Build markdown table
        output = "## 📋 User Story Backlog\n\n"

        # Statistics
        output += "**Statistics**:\n"
        output += f"- Total: {summary['total']}\n"
        output += f"- 📝 Backlog: {summary['backlog']}\n"
        output += f"- 🔄 In Discussion: {summary['in_discussion']}\n"
        output += f"- 📋 Ready: {summary['ready']}\n"
        output += f"- ✅ Assigned: {summary['assigned']}\n"
        output += f"- ✅ Complete: {summary['complete']}\n\n"

        # Story table
        output += "| ID | Title | Status |\n"
        output += "|----|-------|--------|\n"

        for story in summary["stories"]:
            output += f"| {story['id']} | {story['title']} | {story['status']} |\n"

        output += "\n**Tip**: Use `/user-story view <id>` to see detailed information about a specific User Story.\n"

        return output

    def _view_user_story(self, story_id: str, editor: RoadmapEditor) -> str:
        """View specific User Story details.

        Args:
            story_id: User Story ID (e.g., "US-001")
            editor: RoadmapEditor instance

        Returns:
            Formatted User Story content
        """
        # Normalize story ID
        if not story_id.upper().startswith("US-"):
            story_id = f"US-{story_id}"

        content = editor.get_user_story_content(story_id)

        if not content:
            return self.format_error(
                f"{story_id} not found in roadmap\n" f"Use `/user-story list` to see all User Stories."
            )

        return f"## User Story Details\n\n{content}"

    def _add_user_story_interactive(self, editor: RoadmapEditor) -> str:
        """Interactive User Story creation wizard.

        Args:
            editor: RoadmapEditor instance

        Returns:
            Instructions for guided creation
        """
        # NOTE: Interactive prompts should be handled by ChatSession
        # This command just provides the structure

        return (
            "## 📝 Create User Story\n\n"
            "To create a User Story, use natural language in chat:\n\n"
            "**Examples**:\n"
            '- "As a developer, I want to deploy on GCP so that it runs 24/7"\n'
            '- "I need CSV export functionality so I can analyze data in Excel"\n'
            '- "I want email notifications when tasks complete"\n\n'
            "The AI will extract your User Story and guide you through:\n"
            "1. Confirming the story details\n"
            "2. Defining acceptance criteria\n"
            "3. Estimating effort\n"
            "4. Analyzing roadmap impact\n"
            "5. Prioritizing against existing stories\n\n"
            "**Alternative**: Describe your need naturally, and I'll help you create a User Story!"
        )

    def _update_user_story(self, story_id: str, field: str, value: str, editor: RoadmapEditor) -> str:
        """Update User Story field.

        Args:
            story_id: User Story ID
            field: Field to update (status, business_value, etc.)
            value: New value
            editor: RoadmapEditor instance

        Returns:
            Success or error message
        """
        # Normalize story ID
        if not story_id.upper().startswith("US-"):
            story_id = f"US-{story_id}"

        try:
            editor.update_user_story(story_id, field, value)
            return self.format_success(f"Updated {story_id} {field} to: {value}")

        except ValueError as e:
            return self.format_error(str(e))
        except Exception as e:
            logger.error(f"Failed to update User Story: {e}", exc_info=True)
            return self.format_error(f"Update failed: {str(e)}")

    def _assign_user_story(self, story_id: str, priority_number: str, editor: RoadmapEditor) -> str:
        """Assign User Story to a priority.

        Args:
            story_id: User Story ID
            priority_number: Priority to assign to (e.g., "PRIORITY 4" or "4")
            editor: RoadmapEditor instance

        Returns:
            Success or error message
        """
        # Normalize story ID
        if not story_id.upper().startswith("US-"):
            story_id = f"US-{story_id}"

        # Normalize priority number
        if not priority_number.upper().startswith("PRIORITY"):
            priority_number = f"PRIORITY {priority_number}"

        try:
            editor.assign_user_story_to_priority(story_id, priority_number)
            return self.format_success(
                f"Assigned {story_id} to {priority_number}\n\n" f"Story status updated to: ✅ Assigned"
            )

        except ValueError as e:
            return self.format_error(str(e))
        except Exception as e:
            logger.error(f"Failed to assign User Story: {e}", exc_info=True)
            return self.format_error(f"Assignment failed: {str(e)}")
