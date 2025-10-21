"""Notification management commands for project manager CLI.

SPEC-050: Modularized command modules - Phase 4

This module contains all notification commands extracted from roadmap_cli.py:
- cmd_notifications: List pending notifications
- cmd_respond: Respond to a notification

Module Pattern:
    setup_parser(subparsers): Configure command-line arguments
    execute(args): Route to appropriate command handler
    cmd_*(): Individual command implementations
"""

import argparse
import logging

from coffee_maker.cli.console_ui import (
    console,
    create_table,
    error,
    format_notification,
    info,
    warning,
)
from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_STATUS_PENDING,
    NotificationDB,
)

logger = logging.getLogger(__name__)


def cmd_notifications(args: argparse.Namespace) -> int:
    """List pending notifications from daemon.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success
    """
    from coffee_maker.cli.console_ui import section_header, success

    section_header("Pending Notifications", "Review and respond to daemon questions and updates")

    db = NotificationDB()

    # Get pending notifications
    pending = db.get_pending_notifications()

    if not pending:
        success("No pending notifications")
        console.print()
        return 0

    # Group by priority
    critical = [n for n in pending if n["priority"] == NOTIF_PRIORITY_CRITICAL]
    high = [n for n in pending if n["priority"] == NOTIF_PRIORITY_HIGH]
    normal = [n for n in pending if n["priority"] not in [NOTIF_PRIORITY_CRITICAL, NOTIF_PRIORITY_HIGH]]

    # Display critical notifications
    if critical:
        console.print(f"[bold red]🚨 CRITICAL ({len(critical)})[/bold red]")
        console.print()
        for notif in critical:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Display high priority notifications
    if high:
        console.print(f"[bold yellow]⚠️  HIGH PRIORITY ({len(high)})[/bold yellow]")
        console.print()
        for notif in high:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Display normal notifications
    if normal:
        console.print(f"[bold blue]📋 NORMAL ({len(normal)})[/bold blue]")
        console.print()
        for notif in normal:
            panel = format_notification(
                notif_type=notif["type"],
                title=f"[{notif['id']}] {notif['title']}",
                message=notif["message"],
                priority=notif["priority"],
                created_at=notif["created_at"],
            )
            console.print(panel)
            console.print()

    # Summary
    info(f"Total: {len(pending)} pending notification(s)")
    console.print()
    console.print("[dim]💡 Tip: Use 'project-manager respond <id> <response>' to respond[/dim]")
    console.print()

    return 0


def cmd_respond(args: argparse.Namespace) -> int:
    """Respond to a notification.

    Args:
        args: Parsed arguments with notif_id and response

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.cli.console_ui import success

    db = NotificationDB()

    # Get notification
    notif = db.get_notification(args.notif_id)

    if not notif:
        error(
            f"Notification {args.notif_id} not found",
            suggestion="Use 'project-manager notifications' to see available notifications",
        )
        return 1

    if notif["status"] != NOTIF_STATUS_PENDING:
        warning(
            f"Notification {args.notif_id} is not pending (status: {notif['status']})",
            suggestion="Only pending notifications can be responded to",
        )
        return 1

    # Respond
    db.respond_to_notification(args.notif_id, args.response)

    console.print()
    success(f"Responded to notification {args.notif_id}")
    console.print()

    # Show details in a table
    table = create_table(title="Response Details", show_header=False)
    table.add_column(style="bold cyan", justify="right")
    table.add_column()
    table.add_row("Original Question", notif["title"])
    table.add_row("Your Response", args.response)
    table.add_row("Timestamp", notif["created_at"])

    console.print(table)
    console.print()

    return 0


def setup_parser(subparsers):
    """Configure notification-related subcommands.

    Args:
        subparsers: argparse subparsers object
    """
    # Notifications command
    subparsers.add_parser("notifications", help="List pending notifications")

    # Respond command
    respond_parser = subparsers.add_parser("respond", help="Respond to notification")
    respond_parser.add_argument("notif_id", type=int, help="Notification ID")
    respond_parser.add_argument("response", help="Your response")


def execute(args: argparse.Namespace) -> int:
    """Execute notification commands based on args.command.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    commands = {
        "notifications": cmd_notifications,
        "respond": cmd_respond,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown notification command: {args.command}")
        return 1
