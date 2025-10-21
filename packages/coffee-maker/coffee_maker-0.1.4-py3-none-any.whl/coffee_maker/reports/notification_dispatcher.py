"""Multi-channel notification dispatcher for status reports.

This module provides a unified interface for dispatching status reports to
multiple channels (console, Slack, email). Handles channel configuration,
graceful fallback, and error recovery.

US-017 Phase 5: Multi-Channel Delivery

Example:
    >>> from coffee_maker.reports.notification_dispatcher import NotificationDispatcher
    >>> from coffee_maker.reports.status_report_generator import StatusReportGenerator
    >>>
    >>> # Generate report data
    >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
    >>> completions = generator.get_recent_completions(days=14)
    >>> deliverables = generator.get_upcoming_deliverables(limit=5)
    >>>
    >>> # Dispatch to all enabled channels
    >>> dispatcher = NotificationDispatcher()
    >>> result = dispatcher.dispatch_summary(completions, period_days=14)
    >>> result = dispatcher.dispatch_calendar(deliverables, limit=5)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.reports.slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)

# Default configuration path
DEFAULT_CONFIG_PATH = Path.home() / ".coffee_maker" / "notification_preferences.json"

# Default configuration
DEFAULT_CONFIG = {
    "channels": ["console"],
    "slack_enabled": False,
    "email_enabled": False,
    "auto_update_enabled": True,
    "update_interval_days": 3,
    "slack_webhook_url": None,
    "email_recipients": [],
}


class NotificationDispatcher:
    """Multi-channel notification dispatcher for status reports.

    Dispatches status reports to multiple channels based on configuration.
    Provides graceful fallback if a channel fails.

    Channels:
        - console: Print to stdout
        - slack: Send to Slack via webhook
        - email: Send via email (stub implementation)

    Attributes:
        config: Configuration dictionary
        config_path: Path to configuration file
        slack_notifier: Slack notification client (if enabled)

    Example:
        >>> dispatcher = NotificationDispatcher()
        >>> dispatcher.dispatch_summary(completions, period_days=14)
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize notification dispatcher.

        Loads configuration from file or creates default if not exists.

        Args:
            config_path: Path to configuration file (defaults to ~/.coffee_maker/notification_preferences.json)
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config = self._load_config()

        # Initialize channel clients
        self.slack_notifier = None
        if self.config.get("slack_enabled", False):
            webhook_url = self.config.get("slack_webhook_url")
            self.slack_notifier = SlackNotifier(webhook_url=webhook_url)

        logger.info(
            f"NotificationDispatcher initialized: "
            f"channels={self.config.get('channels', [])}, "
            f"slack={self.config.get('slack_enabled', False)}, "
            f"email={self.config.get('email_enabled', False)}"
        )

    def _load_config(self) -> Dict:
        """Load configuration from file or create default.

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                logger.info(f"Loaded notification config: {self.config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            # Create default config
            self._save_config(DEFAULT_CONFIG)
            logger.info(f"Created default notification config: {self.config_path}")
            return DEFAULT_CONFIG.copy()

    def _save_config(self, config: Dict):
        """Save configuration to file.

        Args:
            config: Configuration dictionary
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved notification config: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def dispatch_summary(self, completions: List, period_days: int = 14) -> Dict[str, bool]:
        """Dispatch summary notification to all enabled channels.

        Args:
            completions: List of StoryCompletion objects
            period_days: Number of days covered by summary

        Returns:
            Dictionary mapping channel name to success status

        Example:
            >>> dispatcher = NotificationDispatcher()
            >>> results = dispatcher.dispatch_summary(completions, period_days=14)
            >>> print(results)  # {'console': True, 'slack': True, 'email': False}
        """
        results = {}

        # Console output (always enabled)
        if "console" in self.config.get("channels", []):
            try:
                self._print_summary_to_console(completions, period_days)
                results["console"] = True
            except Exception as e:
                logger.error(f"Console summary failed: {e}")
                results["console"] = False

        # Slack
        if self.config.get("slack_enabled", False) and self.slack_notifier:
            try:
                success = self.slack_notifier.send_summary_to_slack(completions, period_days)
                results["slack"] = success
            except Exception as e:
                logger.error(f"Slack summary failed: {e}")
                results["slack"] = False

        # Email (stub)
        if self.config.get("email_enabled", False):
            try:
                success = self._send_summary_email(completions, period_days)
                results["email"] = success
            except Exception as e:
                logger.error(f"Email summary failed: {e}")
                results["email"] = False

        logger.info(f"Summary dispatched: {results}")
        return results

    def dispatch_calendar(self, deliverables: List, limit: int = 5) -> Dict[str, bool]:
        """Dispatch calendar notification to all enabled channels.

        Args:
            deliverables: List of UpcomingStory objects
            limit: Maximum number of deliverables to show

        Returns:
            Dictionary mapping channel name to success status

        Example:
            >>> dispatcher = NotificationDispatcher()
            >>> results = dispatcher.dispatch_calendar(deliverables, limit=5)
            >>> print(results)  # {'console': True, 'slack': True}
        """
        results = {}

        # Console output (always enabled)
        if "console" in self.config.get("channels", []):
            try:
                self._print_calendar_to_console(deliverables, limit)
                results["console"] = True
            except Exception as e:
                logger.error(f"Console calendar failed: {e}")
                results["console"] = False

        # Slack
        if self.config.get("slack_enabled", False) and self.slack_notifier:
            try:
                success = self.slack_notifier.send_calendar_to_slack(deliverables, limit)
                results["slack"] = success
            except Exception as e:
                logger.error(f"Slack calendar failed: {e}")
                results["slack"] = False

        # Email (stub)
        if self.config.get("email_enabled", False):
            try:
                success = self._send_calendar_email(deliverables, limit)
                results["email"] = success
            except Exception as e:
                logger.error(f"Email calendar failed: {e}")
                results["email"] = False

        logger.info(f"Calendar dispatched: {results}")
        return results

    def dispatch_update(self, summary_data: Dict, calendar_data: Dict) -> Dict[str, Dict[str, bool]]:
        """Dispatch both summary and calendar notifications.

        Convenience method for dispatching both summary and calendar in one call.

        Args:
            summary_data: Dictionary with 'completions' and 'period_days'
            calendar_data: Dictionary with 'deliverables' and 'limit'

        Returns:
            Dictionary with 'summary' and 'calendar' dispatch results

        Example:
            >>> dispatcher = NotificationDispatcher()
            >>> results = dispatcher.dispatch_update(
            ...     summary_data={'completions': completions, 'period_days': 14},
            ...     calendar_data={'deliverables': deliverables, 'limit': 5}
            ... )
        """
        summary_results = self.dispatch_summary(summary_data["completions"], summary_data.get("period_days", 14))

        calendar_results = self.dispatch_calendar(calendar_data["deliverables"], calendar_data.get("limit", 5))

        return {"summary": summary_results, "calendar": calendar_results}

    def _print_summary_to_console(self, completions: List, period_days: int):
        """Print summary to console.

        Args:
            completions: List of StoryCompletion objects
            period_days: Number of days covered
        """
        print("\n" + "=" * 80)
        print(f"📊 SUMMARY - Last {period_days} Days")
        print("=" * 80)

        total_estimated_days = sum(getattr(c, "estimated_days", 0) or 0 for c in completions)
        print(f"\n{len(completions)} stories completed | {total_estimated_days:.1f} days estimated\n")

        for completion in completions:
            story_id = getattr(completion, "story_id", "Unknown")
            title = getattr(completion, "title", "Untitled")
            business_value = getattr(completion, "business_value", "N/A")
            completion_date = getattr(completion, "completion_date", None)

            date_str = ""
            if completion_date:
                if isinstance(completion_date, str):
                    date_str = f" | {completion_date}"
                else:
                    date_str = f" | {completion_date.strftime('%Y-%m-%d')}"

            print(f"  {story_id}: {title}{date_str}")
            print(f"    Business Value: {business_value}")
            print()

        print("=" * 80 + "\n")

    def _print_calendar_to_console(self, deliverables: List, limit: int):
        """Print calendar to console.

        Args:
            deliverables: List of UpcomingStory objects
            limit: Maximum number to show
        """
        print("\n" + "=" * 80)
        print(f"📅 UPCOMING DELIVERABLES - Next {limit}")
        print("=" * 80)

        total_estimate = sum(getattr(d, "estimate_days", 0) or 0 for d in deliverables)
        print(f"\n{len(deliverables)} upcoming stories | {total_estimate:.1f} days estimated\n")

        for idx, deliverable in enumerate(deliverables[:limit], 1):
            story_id = getattr(deliverable, "story_id", "Unknown")
            title = getattr(deliverable, "title", "Untitled")
            estimate_days = getattr(deliverable, "estimate_days", 0) or 0
            status = getattr(deliverable, "status", "planned")

            status_emoji = "📝" if status == "planned" else "🔄"
            estimate_str = f"{estimate_days:.1f}d" if estimate_days > 0 else "TBD"

            print(f"  {status_emoji} {idx}. {story_id}: {title}")
            print(f"     Estimate: {estimate_str}")
            print()

        print("=" * 80 + "\n")

    def _send_summary_email(self, completions: List, period_days: int) -> bool:
        """Send summary via email (stub implementation).

        Args:
            completions: List of StoryCompletion objects
            period_days: Number of days covered

        Returns:
            True if sent successfully, False otherwise
        """
        logger.warning("Email notifications not yet implemented (stub)")
        # TODO: Implement email sending when email system is available
        # - Use SMTP or email service API
        # - Format as HTML email with professional styling
        # - Include links to GitHub PRs
        return False

    def _send_calendar_email(self, deliverables: List, limit: int) -> bool:
        """Send calendar via email (stub implementation).

        Args:
            deliverables: List of UpcomingStory objects
            limit: Maximum number to show

        Returns:
            True if sent successfully, False otherwise
        """
        logger.warning("Email notifications not yet implemented (stub)")
        # TODO: Implement email sending when email system is available
        return False

    def update_config(self, **kwargs):
        """Update configuration and save to file.

        Args:
            **kwargs: Configuration keys to update

        Example:
            >>> dispatcher = NotificationDispatcher()
            >>> dispatcher.update_config(slack_enabled=True, slack_webhook_url="https://...")
        """
        self.config.update(kwargs)
        self._save_config(self.config)

        # Re-initialize Slack client if needed
        if kwargs.get("slack_enabled") or kwargs.get("slack_webhook_url"):
            if self.config.get("slack_enabled"):
                webhook_url = self.config.get("slack_webhook_url")
                self.slack_notifier = SlackNotifier(webhook_url=webhook_url)
            else:
                self.slack_notifier = None

        logger.info(f"Configuration updated: {kwargs}")

    def get_config(self) -> Dict:
        """Get current configuration.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def test_channels(self) -> Dict[str, bool]:
        """Test all enabled channels.

        Returns:
            Dictionary mapping channel name to test result
        """
        results = {}

        # Console always works
        if "console" in self.config.get("channels", []):
            results["console"] = True

        # Test Slack
        if self.config.get("slack_enabled", False) and self.slack_notifier:
            results["slack"] = self.slack_notifier.test_connection()

        # Email stub always fails
        if self.config.get("email_enabled", False):
            results["email"] = False

        logger.info(f"Channel test results: {results}")
        return results
