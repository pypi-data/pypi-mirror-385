"""Roadmap viewing commands for project manager CLI.

SPEC-050: Modularized command modules - Phase 2

This module contains all roadmap view commands extracted from roadmap_cli.py:
- cmd_view: Display ROADMAP.md (full or specific priority)

Module Pattern:
    setup_parser(subparsers): Configure command-line arguments
    execute(args): Route to appropriate command handler
    cmd_*(): Individual command implementations

Related Commands:
- cmd_status, cmd_developer_status, cmd_metrics (see status.py)
- cmd_notifications, cmd_respond (see notifications.py)
- cmd_chat, cmd_assistant_* (see chat.py)
"""

import argparse

from coffee_maker.config import ROADMAP_PATH


def cmd_view(args: argparse.Namespace) -> int:
    """View roadmap or specific priority.

    Args:
        args: Parsed command-line arguments with priority field

    Returns:
        0 on success, 1 on error
    """
    if not ROADMAP_PATH.exists():
        print(f"❌ ROADMAP not found: {ROADMAP_PATH}")
        return 1

    print("\n" + "=" * 80)
    print("Coffee Maker Agent - ROADMAP")
    print("=" * 80 + "\n")

    with open(ROADMAP_PATH, "r") as f:
        content = f.read()

    if args.priority:
        # Show specific priority
        priority_name = args.priority.upper().replace("-", " ")
        if not priority_name.startswith("PRIORITY"):
            priority_name = f"PRIORITY {priority_name}"

        lines = content.split("\n")
        in_priority = False
        priority_lines = []

        for line in lines:
            if priority_name in line and line.startswith("###"):
                in_priority = True
                priority_lines.append(line)
            elif in_priority:
                if line.startswith("###") and "PRIORITY" in line:
                    # Next priority section started
                    break
                priority_lines.append(line)

        if priority_lines:
            print("\n".join(priority_lines))
        else:
            print(f"❌ {priority_name} not found in ROADMAP")
            return 1

    else:
        # Show full roadmap (first 100 lines for MVP)
        lines = content.split("\n")
        print("\n".join(lines[:100]))

        if len(lines) > 100:
            print(f"\n... ({len(lines) - 100} more lines)")
            print("\nTip: Use 'project-manager view <priority>' to see specific priority")

    return 0


def setup_parser(subparsers):
    """Configure roadmap-related subcommands.

    Args:
        subparsers: argparse subparsers object
    """
    view_parser = subparsers.add_parser("view", help="View roadmap")
    view_parser.add_argument("priority", nargs="?", help="Specific priority to view (optional)")


def execute(args: argparse.Namespace) -> int:
    """Execute roadmap commands based on args.command.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    if args.command == "view":
        return cmd_view(args)
    else:
        print(f"❌ Unknown roadmap command: {args.command}")
        return 1
