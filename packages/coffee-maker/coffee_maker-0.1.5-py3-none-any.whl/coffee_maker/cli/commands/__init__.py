"""CLI command modules - Modularized commands for roadmap_cli.py.

SPEC-050: Refactor roadmap_cli.py Modularization

This package organizes the 17+ command functions from roadmap_cli.py into
focused, testable modules by command category.

Directory structure:
    commands/
    ├── __init__.py          # This file (exports all commands)
    ├── roadmap.py           # View commands (cmd_view, cmd_view_priority)
    ├── status.py            # Status commands (cmd_status, cmd_developer_status, etc.)
    ├── notifications.py     # Notification commands (cmd_notifications, cmd_respond)
    └── chat.py              # Chat commands (cmd_chat, cmd_assistant_*)

Module exports:
All command functions are imported here and re-exported for easy importing:
    from coffee_maker.cli.commands import roadmap, status, notifications, chat

Usage:
    # Import all modules
    from coffee_maker.cli.commands import roadmap, status, notifications, chat

    # Use in main CLI
    commands = {
        "view": roadmap.cmd_view,
        "status": status.cmd_status,
        # ... etc
    }

Migration Strategy (SPEC-050 Implementation Plan):
    Phase 1: Create package structure (this file + all submodules)
    Phase 2: Incrementally move command functions to submodules
    Phase 3: Update roadmap_cli.py to import from commands package
    Phase 4: Remove moved functions from roadmap_cli.py
    Phase 5: Test and validate all commands

Status: Phase 1 - Package structure created
Next: Phase 2 - Incrementally move commands

Reference:
    SPEC-050: docs/architecture/specs/SPEC-050-refactor-roadmap-cli-modularization.md
"""

# Command registry and helper functions for command lookup
from typing import Dict, List, Optional

from coffee_maker.cli.commands.base import BaseCommand

# Global command registry
_COMMAND_REGISTRY: Dict[str, BaseCommand] = {}
_REGISTRY_INITIALIZED = False


def register_command(command_class):
    """Decorator to register a command class.

    This decorator is used by command classes to automatically register themselves
    in the global registry.

    Args:
        command_class: The command class to register

    Returns:
        The command class (unchanged)
    """
    return command_class


def _initialize_registry():
    """Initialize the command registry with all available commands."""
    global _COMMAND_REGISTRY, _REGISTRY_INITIALIZED

    if _REGISTRY_INITIALIZED:
        return

    # Import here to avoid circular imports
    from coffee_maker.cli.commands.all_commands import ALL_COMMANDS

    for command_class in ALL_COMMANDS:
        cmd_instance = command_class()
        _COMMAND_REGISTRY[cmd_instance.name] = cmd_instance

    _REGISTRY_INITIALIZED = True


def get_command_handler(command_name: str) -> Optional[BaseCommand]:
    """Get a command handler by name.

    Args:
        command_name: Name of the command (without leading slash)

    Returns:
        BaseCommand instance if found, None otherwise
    """
    _initialize_registry()
    return _COMMAND_REGISTRY.get(command_name)


def list_commands() -> List[BaseCommand]:
    """Get list of all available commands.

    Returns:
        List of BaseCommand instances
    """
    _initialize_registry()
    return list(_COMMAND_REGISTRY.values())


__all__ = ["register_command", "get_command_handler", "list_commands"]
