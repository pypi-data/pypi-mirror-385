"""Base command class for project manager CLI commands.

This module provides the abstract base class for all command handlers.

Example:
    >>> from coffee_maker.cli.commands.base import BaseCommand
    >>>
    >>> class MyCommand(BaseCommand):
    ...     @property
    ...     def name(self):
    ...         return "mycommand"
    ...
    ...     @property
    ...     def description(self):
    ...         return "Does something cool"
    ...
    ...     def execute(self, args, editor):
    ...         return "Done!"
"""

from abc import ABC, abstractmethod
from typing import List

from coffee_maker.cli.roadmap_editor import RoadmapEditor


class BaseCommand(ABC):
    """Abstract base class for all commands.

    All command handlers must inherit from this class and implement
    the required properties and methods.

    Attributes:
        name: Command name (used for /name)
        description: Short description of what the command does

    Example:
        >>> class AddCommand(BaseCommand):
        ...     @property
        ...     def name(self):
        ...         return "add"
        ...
        ...     @property
        ...     def description(self):
        ...         return "Add new priority to roadmap"
        ...
        ...     def execute(self, args, editor):
        ...         # Implementation
        ...         return "Priority added!"
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (without slash).

        Returns:
            Command name string

        Example:
            >>> command.name
            'add'
        """

    @property
    @abstractmethod
    def description(self) -> str:
        """Command description for help text.

        Returns:
            Description string

        Example:
            >>> command.description
            'Add new priority to roadmap'
        """

    @abstractmethod
    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute the command.

        Args:
            args: Command arguments (words after command name)
            editor: RoadmapEditor instance for roadmap manipulation

        Returns:
            Response message to display to user

        Example:
            >>> response = command.execute(
            ...     ["User", "Authentication"],
            ...     editor
            ... )
            >>> print(response)
            'Added PRIORITY 10: User Authentication'
        """

    def validate_args(self, args: List[str], expected_count: int) -> bool:
        """Validate argument count.

        Helper method to check if the correct number of arguments
        was provided.

        Args:
            args: Command arguments
            expected_count: Expected number of arguments

        Returns:
            True if argument count matches

        Example:
            >>> if not self.validate_args(args, 2):
            ...     return "Error: Expected 2 arguments"
        """
        return len(args) == expected_count

    def validate_min_args(self, args: List[str], min_count: int) -> bool:
        """Validate minimum argument count.

        Args:
            args: Command arguments
            min_count: Minimum required arguments

        Returns:
            True if enough arguments provided

        Example:
            >>> if not self.validate_min_args(args, 1):
            ...     return "Error: At least 1 argument required"
        """
        return len(args) >= min_count

    def format_error(self, message: str) -> str:
        """Format error message.

        Args:
            message: Error message

        Returns:
            Formatted error message

        Example:
            >>> return self.format_error("Invalid priority number")
            '❌ Error: Invalid priority number'
        """
        return f"❌ Error: {message}"

    def format_success(self, message: str) -> str:
        """Format success message.

        Args:
            message: Success message

        Returns:
            Formatted success message

        Example:
            >>> return self.format_success("Priority added")
            '✅ Success: Priority added'
        """
        return f"✅ {message}"

    def format_warning(self, message: str) -> str:
        """Format warning message.

        Args:
            message: Warning message

        Returns:
            Formatted warning message

        Example:
            >>> return self.format_warning("Priority already exists")
            '⚠️  Warning: Priority already exists'
        """
        return f"⚠️  Warning: {message}"

    def get_usage(self) -> str:
        """Get usage string for this command.

        Override this method to provide custom usage information.

        Returns:
            Usage string

        Example:
            >>> print(command.get_usage())
            'Usage: /add <priority_name>'
        """
        return f"Usage: /{self.name} [args]"
