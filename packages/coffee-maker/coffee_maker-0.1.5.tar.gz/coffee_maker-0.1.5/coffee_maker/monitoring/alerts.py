"""
Alert rules and notifications for code_developer daemon.

Monitors daemon health and sends alerts when issues are detected.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert instance."""

    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metadata: dict


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self):
        """Initialize alert manager."""
        self.alerts: List[Alert] = []
        self.alert_channels = self._initialize_channels()

    def _initialize_channels(self) -> List:
        """Initialize notification channels (email, Slack, etc.)."""
        channels = []

        # Email channel
        email = os.getenv("ALERT_EMAIL")
        if email:
            channels.append({"type": "email", "address": email})

        # Slack channel
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            channels.append({"type": "slack", "webhook_url": slack_webhook})

        return channels

    def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.ERROR,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Send an alert.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            metadata: Additional metadata
        """
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )

        self.alerts.append(alert)
        logger.info(f"Alert: [{severity.value.upper()}] {title}")

        # Send to notification channels
        self._send_to_channels(alert)

    def _send_to_channels(self, alert: Alert) -> None:
        """Send alert to configured notification channels."""
        for channel in self.alert_channels:
            try:
                if channel["type"] == "email":
                    self._send_email(alert, channel["address"])
                elif channel["type"] == "slack":
                    self._send_slack(alert, channel["webhook_url"])
            except Exception as e:
                logger.error(f"Failed to send alert via {channel['type']}: {e}")

    def _send_email(self, alert: Alert, email: str) -> None:
        """Send alert via email."""
        # TODO: Implement email sending
        logger.info(f"Would send email alert to {email}")

    def _send_slack(self, alert: Alert, webhook_url: str) -> None:
        """Send alert to Slack."""
        import requests

        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9900",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#990000",
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(alert.severity, "#cccccc"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value, "short": True},
                        {"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
                    ],
                }
            ]
        }

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Sent alert to Slack")

    def get_alerts(self, severity: Optional[AlertSeverity] = None, limit: int = 100) -> List[Alert]:
        """
        Get recent alerts.

        Args:
            severity: Filter by severity
            limit: Maximum number of alerts to return

        Returns:
            List of alerts
        """
        alerts = self.alerts
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts[-limit:]


# Predefined alert rules
class AlertRules:
    """Common alert rules."""

    @staticmethod
    def daemon_crashed(error: str) -> Alert:
        """Alert when daemon crashes."""
        return Alert(
            title="Daemon Crashed",
            message=f"The code_developer daemon has crashed: {error}",
            severity=AlertSeverity.CRITICAL,
            timestamp=datetime.utcnow(),
            metadata={"error": error},
        )

    @staticmethod
    def high_error_rate(error_rate: float) -> Alert:
        """Alert when error rate is high."""
        return Alert(
            title="High Error Rate",
            message=f"Error rate is {error_rate:.1%} (threshold: 10%)",
            severity=AlertSeverity.ERROR,
            timestamp=datetime.utcnow(),
            metadata={"error_rate": error_rate},
        )

    @staticmethod
    def cost_threshold_exceeded(cost: float, limit: float) -> Alert:
        """Alert when cost threshold is exceeded."""
        return Alert(
            title="Cost Threshold Exceeded",
            message=f"Daily cost ${cost:.2f} exceeds limit ${limit:.2f}",
            severity=AlertSeverity.WARNING,
            timestamp=datetime.utcnow(),
            metadata={"cost": cost, "limit": limit},
        )

    @staticmethod
    def disk_space_low(usage_percent: float) -> Alert:
        """Alert when disk space is low."""
        return Alert(
            title="Low Disk Space",
            message=f"Disk usage is {usage_percent:.1f}% (threshold: 90%)",
            severity=AlertSeverity.WARNING,
            timestamp=datetime.utcnow(),
            metadata={"usage_percent": usage_percent},
        )


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get or create global alert manager."""
    global _alert_manager

    if _alert_manager is None:
        _alert_manager = AlertManager()

    return _alert_manager
