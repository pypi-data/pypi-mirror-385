"""Notifications command - List and respond to pending notifications.

Example:
    >>> from coffee_maker.cli.commands.notifications_command import NotificationsCommand
    >>> command = NotificationsCommand()
    >>> response = command.execute([], editor)  # List notifications
    >>> response = command.execute(["respond", "151", "yes"], editor)  # Respond
"""

import logging
from typing import List

from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.notifications import (
    NOTIF_PRIORITY_CRITICAL,
    NOTIF_PRIORITY_HIGH,
    NOTIF_STATUS_PENDING,
    NotificationDB,
)
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class NotificationsCommand(BaseCommand):
    """List and respond to pending notifications.

    Usage:
        /notifications                  - List pending notifications
        /notifications respond <id> <response> - Respond to a notification

    Example:
        /notifications
        /notifications respond 151 yes
        /notifications respond 152 "This is a test"
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "notifications"

    @property
    def description(self) -> str:
        """Command description."""
        return "List and respond to pending notifications"

    def get_usage(self) -> str:
        """Get usage string."""
        return (
            "Usage:\n"
            "  /notifications                  - List pending notifications\n"
            "  /notifications respond <id> <response> - Respond to a notification"
        )

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute notifications command.

        Args:
            args: Command arguments (empty for list, or "respond <id> <response>")
            editor: RoadmapEditor instance (unused but required by interface)

        Returns:
            Response message (formatted for console)
        """
        try:
            if not args:
                # List notifications
                return self._list_notifications()
            elif args[0] == "respond":
                # Respond to notification
                if len(args) < 3:
                    return self.format_error("Usage: /notifications respond <id> <response>")
                notif_id = int(args[1])
                response = " ".join(args[2:])
                return self._respond_to_notification(notif_id, response)
            else:
                return self.format_error(f"Unknown subcommand: {args[0]}. Use '/help' for usage.")

        except ValueError as e:
            logger.error(f"Invalid notification ID: {e}")
            return self.format_error("Notification ID must be a number")
        except Exception as e:
            logger.error(f"Failed to execute notifications command: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")

    def _list_notifications(self) -> str:
        """List pending notifications.

        Returns:
            Formatted notification list
        """
        db = NotificationDB()
        pending = db.get_pending_notifications()

        if not pending:
            return "✅ No pending notifications"

        # Group by priority
        critical = [n for n in pending if n["priority"] == NOTIF_PRIORITY_CRITICAL]
        high = [n for n in pending if n["priority"] == NOTIF_PRIORITY_HIGH]
        normal = [n for n in pending if n["priority"] not in [NOTIF_PRIORITY_CRITICAL, NOTIF_PRIORITY_HIGH]]

        # Build response
        lines = []
        lines.append("📋 Pending Notifications\n")

        # Critical notifications
        if critical:
            lines.append(f"🚨 CRITICAL ({len(critical)}):")
            for notif in critical:
                lines.append(f"  #{notif['id']}: {notif['title']}")
                lines.append(f"      {notif['message']}")
                lines.append(f"      Created: {notif['created_at']}\n")

        # High priority notifications
        if high:
            lines.append(f"⚠️  HIGH PRIORITY ({len(high)}):")
            for notif in high:
                lines.append(f"  #{notif['id']}: {notif['title']}")
                lines.append(f"      {notif['message']}")
                lines.append(f"      Created: {notif['created_at']}\n")

        # Normal notifications
        if normal:
            lines.append(f"📋 NORMAL ({len(normal)}):")
            for notif in normal:
                lines.append(f"  #{notif['id']}: {notif['title']}")
                lines.append(f"      {notif['message']}")
                lines.append(f"      Created: {notif['created_at']}\n")

        # Summary
        lines.append(f"\nTotal: {len(pending)} pending notification(s)")
        lines.append("💡 Tip: Use '/notifications respond <id> <response>' to respond")

        return "\n".join(lines)

    def _respond_to_notification(self, notif_id: int, response: str) -> str:
        """Respond to a notification.

        Args:
            notif_id: Notification ID
            response: User response

        Returns:
            Success or error message
        """
        db = NotificationDB()

        # Get notification
        notif = db.get_notification(notif_id)

        if not notif:
            return self.format_error(
                f"Notification {notif_id} not found. Use '/notifications' to see available notifications."
            )

        if notif["status"] != NOTIF_STATUS_PENDING:
            return self.format_warning(
                f"Notification {notif_id} is not pending (status: {notif['status']}). "
                "Only pending notifications can be responded to."
            )

        # Respond
        db.respond_to_notification(notif_id, response)

        return (
            f"✅ Responded to notification {notif_id}\n\n"
            f"Original Question: {notif['title']}\n"
            f"Your Response: {response}\n"
            f"Timestamp: {notif['created_at']}"
        )
