"""Project Manager CLI - Roadmap management tool.

SPEC-050: Modularized command modules - Phase 3/4 Integration

This module provides the main entry point for project manager CLI commands.
All individual commands have been extracted to command modules:

- commands/roadmap.py: View commands (cmd_view)
- commands/status.py: Status commands (cmd_status, cmd_developer_status, etc.)
- commands/notifications.py: Notification commands (cmd_notifications, cmd_respond)
- commands/utility.py: Chat and spec commands (cmd_chat, cmd_spec, etc.)

This main file now acts as a router that:
1. Parses command-line arguments
2. Delegates to appropriate command module
3. Manages singleton registration (US-035)
4. Initializes assistant manager (PRIORITY 5)

MVP Phase 1 (Complete):
    - View roadmap
    - Check daemon status
    - View notifications
    - Respond to daemon questions
    - Basic text output

Phase 2 (Current):
    - Claude AI integration
    - Rich terminal UI
    - Roadmap editing
    - Slack integration (future)
"""

import argparse
import logging
import sys

from coffee_maker.autonomous.agent_registry import AgentAlreadyRunningError, AgentRegistry, AgentType

# Configure logging BEFORE imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Import command modules for SPEC-050 Phase 3/4
from coffee_maker.cli.commands import roadmap, status, notifications, utility

# Import chat components for Phase 2
try:
    from coffee_maker.cli.assistant_manager import AssistantManager

    CHAT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chat features not available: {e}")
    CHAT_AVAILABLE = False


def main() -> int:
    """Main CLI entry point.

    US-035: Registers project_manager in singleton registry to prevent duplicate instances.
    PRIORITY 9: Shows daily report on first interaction of new day.

    Returns:
        0 on success, 1 on error
    """

    from coffee_maker.cli.daily_report_generator import should_show_report, show_daily_report

    parser = argparse.ArgumentParser(
        prog="project-manager",
        description="Coffee Maker Agent - Project Manager CLI with AI (Phase 2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive AI chat (Phase 2) ⭐ NEW
  project-manager chat

  # View full roadmap
  project-manager view

  # View specific priority
  project-manager view 1
  project-manager view PRIORITY-3

  # Check pending notifications
  project-manager notifications

  # Respond to notification
  project-manager respond 5 approve
  project-manager respond 10 "no, use option 2"

  # Check daemon status
  project-manager status

Phase 1 (Complete):
  ✅ View roadmap (read-only)
  ✅ List notifications
  ✅ Respond to notifications
  ✅ Basic CLI commands

Phase 2 (Current): ⭐ NEW
  ✅ Interactive AI chat session
  ✅ Natural language roadmap management
  ✅ Rich terminal UI
  ✅ Intelligent roadmap analysis
  ✅ Command handlers (/add, /update, /view, /analyze)

Use 'project-manager chat' for the best experience!
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register command subparsers from all modules (SPEC-050)
    roadmap.setup_parser(subparsers)
    status.setup_parser(subparsers)
    notifications.setup_parser(subparsers)
    utility.setup_parser(subparsers)

    args = parser.parse_args()

    # US-030: Default to chat when no command provided
    if not args.command:
        logger.info("No command provided - defaulting to chat interface (US-030)")
        args.command = "chat"

    # US-035: Register project_manager in singleton registry
    try:
        with AgentRegistry.register(AgentType.PROJECT_MANAGER):
            logger.info("✅ Agent registered in singleton registry")

            # PRIORITY 5: Initialize and start AssistantManager if chat features available
            if CHAT_AVAILABLE:
                try:
                    assistant_manager = AssistantManager()
                    assistant_manager.start_auto_refresh()

                    # Make manager available to command handlers via function attributes
                    utility.cmd_assistant_status.manager = assistant_manager
                    utility.cmd_assistant_refresh.manager = assistant_manager

                    logger.info("Assistant manager initialized and auto-refresh started")
                except Exception as e:
                    logger.warning(f"Failed to initialize assistant manager: {e}")

            # PRIORITY 9: Show daily report on first interaction of new day
            if should_show_report():
                show_daily_report()

            # Route to appropriate command module (SPEC-050 Phase 4)
            if args.command == "view":
                return roadmap.execute(args)
            elif args.command in ["status", "developer-status", "metrics", "summary", "calendar", "dev-report"]:
                return status.execute(args)
            elif args.command in ["notifications", "respond"]:
                return notifications.execute(args)
            elif args.command in [
                "sync",
                "spec",
                "chat",
                "assistant-status",
                "assistant-refresh",
                "spec-metrics",
                "spec-status",
                "spec-diff",
                "spec-review",
            ]:
                return utility.execute(args)
            else:
                print(f"❌ Unknown command: {args.command}")
                parser.print_help()
                return 1

    except AgentAlreadyRunningError as e:
        print(f"\n[red]Error: {e}[/]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
