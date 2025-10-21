"""Slack notification integration for status reports.

This module provides Slack integration for sending summary and calendar
notifications to Slack channels. Uses Slack Block Kit for rich formatting.

US-017 Phase 5: Multi-Channel Delivery

Example:
    >>> from coffee_maker.reports.slack_notifier import SlackNotifier
    >>> from coffee_maker.reports.status_report_generator import StatusReportGenerator
    >>>
    >>> # Generate report data
    >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
    >>> completions = generator.get_recent_completions(days=14)
    >>> deliverables = generator.get_upcoming_deliverables(limit=5)
    >>>
    >>> # Send to Slack
    >>> notifier = SlackNotifier(webhook_url="https://hooks.slack.com/...")
    >>> notifier.send_summary_to_slack(completions, period_days=14)
    >>> notifier.send_calendar_to_slack(deliverables, limit=5)
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack notification client for status reports.

    Sends formatted status updates to Slack using Block Kit for rich UI.
    Supports both summary (completions) and calendar (upcoming) notifications.

    Attributes:
        webhook_url: Slack webhook URL for posting messages
        enabled: Whether Slack notifications are enabled

    Example:
        >>> notifier = SlackNotifier(webhook_url="https://hooks.slack.com/...")
        >>> notifier.send_summary_to_slack(completions, period_days=14)
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL (defaults to SLACK_WEBHOOK_URL env var)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)

        if not self.enabled:
            logger.warning("Slack notifications disabled: No webhook URL configured")
        else:
            logger.info("Slack notifications enabled")

    def send_summary_to_slack(
        self,
        completions: List,
        period_days: int = 14,
        channel_override: Optional[str] = None,
    ) -> bool:
        """Send summary of completed work to Slack.

        Formats completion data as Slack blocks with rich formatting:
        - Header with period and summary
        - Section for each completion with story ID, title, business value
        - Footer with timestamp

        Args:
            completions: List of StoryCompletion objects
            period_days: Number of days covered by summary
            channel_override: Optional channel to post to (overrides default)

        Returns:
            True if sent successfully, False otherwise

        Example:
            >>> notifier = SlackNotifier()
            >>> completions = generator.get_recent_completions(days=14)
            >>> notifier.send_summary_to_slack(completions, period_days=14)
        """
        if not self.enabled:
            logger.debug("Slack disabled, skipping summary notification")
            return False

        try:
            blocks = self._build_summary_blocks(completions, period_days)
            return self._send_to_slack(blocks, channel_override)

        except Exception as e:
            logger.error(f"Failed to send summary to Slack: {e}")
            return False

    def send_calendar_to_slack(
        self, deliverables: List, limit: int = 5, channel_override: Optional[str] = None
    ) -> bool:
        """Send calendar of upcoming deliverables to Slack.

        Formats deliverable data as Slack blocks with:
        - Header with upcoming count
        - Section for each deliverable with story ID, title, estimate
        - Footer with timestamp

        Args:
            deliverables: List of UpcomingStory objects
            limit: Maximum number of deliverables to show
            channel_override: Optional channel to post to

        Returns:
            True if sent successfully, False otherwise

        Example:
            >>> notifier = SlackNotifier()
            >>> deliverables = generator.get_upcoming_deliverables(limit=5)
            >>> notifier.send_calendar_to_slack(deliverables, limit=5)
        """
        if not self.enabled:
            logger.debug("Slack disabled, skipping calendar notification")
            return False

        try:
            blocks = self._build_calendar_blocks(deliverables, limit)
            return self._send_to_slack(blocks, channel_override)

        except Exception as e:
            logger.error(f"Failed to send calendar to Slack: {e}")
            return False

    def _build_summary_blocks(self, completions: List, period_days: int) -> List[Dict]:
        """Build Slack blocks for summary notification.

        Args:
            completions: List of StoryCompletion objects
            period_days: Number of days covered

        Returns:
            List of Slack block dictionaries
        """
        blocks = []

        # Header
        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Summary - Last {period_days} Days",
                    "emoji": True,
                },
            }
        )

        # Summary section (note: story_points not in data class, calculate from estimated_days)
        total_estimated_days = sum(getattr(c, "estimated_days", 0) or 0 for c in completions)
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(completions)}* stories completed | *{total_estimated_days:.1f}* days estimated",
                },
            }
        )

        blocks.append({"type": "divider"})

        # Individual completions
        for completion in completions[:10]:  # Limit to 10 to avoid message size limits
            story_id = getattr(completion, "story_id", "Unknown")
            title = getattr(completion, "title", "Untitled")
            business_value = getattr(completion, "business_value", "N/A")
            completion_date = getattr(completion, "completion_date", None)

            date_str = ""
            if completion_date:
                if isinstance(completion_date, str):
                    date_str = f" • {completion_date}"
                else:
                    date_str = f" • {completion_date.strftime('%Y-%m-%d')}"

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{story_id}*: {title}{date_str}\n_{business_value}_",
                    },
                }
            )

        # Footer
        blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | MonolithicCoffeeMakerAgent_",
                    }
                ],
            }
        )

        return blocks

    def _build_calendar_blocks(self, deliverables: List, limit: int) -> List[Dict]:
        """Build Slack blocks for calendar notification.

        Args:
            deliverables: List of UpcomingStory objects
            limit: Maximum number to show

        Returns:
            List of Slack block dictionaries
        """
        blocks = []

        # Header
        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📅 Upcoming Deliverables - Next {limit}",
                    "emoji": True,
                },
            }
        )

        # Summary section
        total_estimate = sum(getattr(d, "estimate_days", 0) or 0 for d in deliverables)
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(deliverables)}* upcoming stories | *{total_estimate:.1f}* days estimated",
                },
            }
        )

        blocks.append({"type": "divider"})

        # Individual deliverables
        for idx, deliverable in enumerate(deliverables[:limit], 1):
            story_id = getattr(deliverable, "story_id", "Unknown")
            title = getattr(deliverable, "title", "Untitled")
            estimate_days = getattr(deliverable, "estimate_days", 0) or 0
            status = getattr(deliverable, "status", "planned")

            status_emoji = "📝" if status == "planned" else "🔄"
            estimate_str = f"{estimate_days:.1f}d" if estimate_days > 0 else "TBD"

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{status_emoji} *{idx}. {story_id}*: {title}\n_Estimate: {estimate_str}_",
                    },
                }
            )

        # Footer
        blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | MonolithicCoffeeMakerAgent_",
                    }
                ],
            }
        )

        return blocks

    def _send_to_slack(self, blocks: List[Dict], channel_override: Optional[str] = None) -> bool:
        """Send blocks to Slack webhook.

        Args:
            blocks: List of Slack block dictionaries
            channel_override: Optional channel to post to

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Cannot send to Slack: No webhook URL")
            return False

        try:
            import requests

            payload = {"blocks": blocks}

            if channel_override:
                payload["channel"] = channel_override

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False

        except ImportError:
            logger.error("requests library not available - cannot send to Slack")
            return False
        except Exception as e:
            logger.error(f"Failed to send to Slack: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Slack webhook connection.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Slack not configured")
            return False

        try:
            test_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ Test message from MonolithicCoffeeMakerAgent",
                    },
                }
            ]
            return self._send_to_slack(test_blocks)

        except Exception as e:
            logger.error(f"Slack connection test failed: {e}")
            return False
