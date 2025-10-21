"""Import all command handlers to trigger registration.

This module imports all command handler modules to ensure they are
registered via the @register_command decorator.

Simply import this module to load all commands:
    >>> from coffee_maker.cli.commands import all_commands
"""

from typing import List, Type

# Import all command handlers to trigger @register_command decorator
from coffee_maker.cli.commands.add_priority import AddPriorityCommand
from coffee_maker.cli.commands.analyze_roadmap import AnalyzeRoadmapCommand
from coffee_maker.cli.commands.notifications_command import NotificationsCommand
from coffee_maker.cli.commands.update_priority import UpdatePriorityCommand
from coffee_maker.cli.commands.user_story import UserStoryCommand
from coffee_maker.cli.commands.view_roadmap import ViewRoadmapCommand
from coffee_maker.cli.commands.team import TeamStatusCommand, AgentsStatusCommand

# List of all command classes
ALL_COMMANDS: List[Type] = [
    AddPriorityCommand,
    UpdatePriorityCommand,
    ViewRoadmapCommand,
    AnalyzeRoadmapCommand,
    UserStoryCommand,
    NotificationsCommand,
    TeamStatusCommand,
    AgentsStatusCommand,
]

__all__ = ["ALL_COMMANDS"]
