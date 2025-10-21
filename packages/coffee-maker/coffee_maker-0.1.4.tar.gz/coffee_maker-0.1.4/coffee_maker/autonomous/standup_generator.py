"""Daily standup report generation using Claude API.

Generates professional, human-readable daily standup reports from activity data.
Uses Claude API to intelligently summarize activities into a compelling narrative
that highlights business value and accomplishments.

Example:
    >>> gen = StandupGenerator()
    >>> summary = gen.generate_daily_standup(date(2025, 10, 10))
    >>> print(summary.summary_text)
"""

import json
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any

from anthropic import Anthropic

from coffee_maker.autonomous.activity_db import ActivityDB, Activity, DailySummary
from coffee_maker.config import ConfigManager

logger = logging.getLogger(__name__)

# Standup prompt template - Claude will use this to generate professional reports
STANDUP_PROMPT_TEMPLATE = """You are generating a daily standup report for an AI software developer named "code_developer".

Yesterday's date: {date}

Activities completed yesterday:
{activities_json}

Current developer status:
{developer_status}

Generate a professional daily standup report in this format:

🤖 code_developer Daily Standup - {date}
================================================

📊 Yesterday's Accomplishments:
[List major accomplishments with metrics and business impact]

🔄 Current Status:
[What's currently in progress if applicable]

⚠️ Blockers/Issues:
[Any blockers or issues encountered, or "None at this time"]

📈 Metrics:
[Key metrics: commits, tests, files changed, etc.]

🎯 Next Steps:
[What will be worked on next]

Guidelines:
- Be concise but informative (200-300 words)
- Highlight business value of work done
- Use appropriate emojis
- Include specific numbers/metrics
- Professional but friendly tone
- Focus on impact, not just activity

Return ONLY the formatted markdown report, nothing else."""


class StandupGenerator:
    """Generates daily standup reports from activity data.

    Uses Claude API to create human-readable, professional standup reports
    from raw activity data. Caches summaries for performance.

    Attributes:
        db: ActivityDB instance for retrieving activities
        client: Anthropic API client

    Example:
        >>> gen = StandupGenerator()
        >>> summary = gen.generate_daily_standup(date(2025, 10, 10))
        >>> print(summary.summary_text)
    """

    def __init__(self, db: Optional[ActivityDB] = None):
        """Initialize standup generator.

        Args:
            db: ActivityDB instance. Creates new if None.

        Raises:
            ValueError: If Anthropic API key is not configured
        """
        self.db = db or ActivityDB()

        # Get API key from configuration
        config = ConfigManager()
        api_key = config.get_anthropic_api_key()

        self.client = Anthropic(api_key=api_key)

    def generate_daily_standup(self, target_date: date, force_regenerate: bool = False) -> DailySummary:
        """Generate daily standup report for a specific date.

        Generates a professional daily standup by:
        1. Retrieving all activities for the date
        2. Calculating metrics
        3. Using Claude API to generate summary
        4. Caching result for future retrievals

        Args:
            target_date: Date to generate report for
            force_regenerate: Regenerate even if cached. Defaults to False

        Returns:
            DailySummary object with formatted report and metrics

        Example:
            >>> yesterday = date.today() - timedelta(days=1)
            >>> summary = gen.generate_daily_standup(yesterday)
            >>> print(summary.summary_text)
        """
        # Get activities for the day
        activities = self.db.get_activities(start_date=target_date, end_date=target_date, limit=1000)

        if not activities:
            logger.info(f"No activities found for {target_date}")
            return self._generate_empty_summary(target_date)

        # Calculate metrics
        metrics = self.db.get_daily_metrics(target_date)

        # Get developer status
        developer_status = self._get_developer_status()

        # Generate summary using Claude
        try:
            summary_text = self._generate_with_claude(
                target_date=target_date, activities=activities, developer_status=developer_status
            )
        except Exception as e:
            logger.error(f"Failed to generate summary with Claude: {e}")
            summary_text = self._generate_fallback_summary(target_date, activities, metrics)

        # Create summary object
        summary = DailySummary(
            date=target_date.isoformat(),
            summary_text=summary_text,
            metrics=metrics,
            activities=activities,
            generated_at=datetime.utcnow().isoformat(),
        )

        return summary

    def _generate_with_claude(
        self,
        target_date: date,
        activities: List[Activity],
        developer_status: Dict,
    ) -> str:
        """Use Claude API to generate summary text.

        Args:
            target_date: Date of report
            activities: List of activities
            developer_status: Current developer status

        Returns:
            Formatted markdown summary
        """
        # Prepare activities JSON
        activities_json = self._format_activities_for_prompt(activities)

        # Create prompt
        prompt = STANDUP_PROMPT_TEMPLATE.format(
            date=target_date.isoformat(),
            activities_json=activities_json,
            developer_status=json.dumps(developer_status, indent=2),
        )

        # Call Claude API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
        )

        summary_text = response.content[0].text
        logger.info(f"Generated standup summary for {target_date}")
        return summary_text

    def _format_activities_for_prompt(self, activities: List[Activity]) -> str:
        """Format activities as JSON for Claude prompt.

        Args:
            activities: List of activities

        Returns:
            JSON string representation of activities
        """
        activities_data = []
        for activity in activities:
            activities_data.append(
                {
                    "type": activity.activity_type,
                    "title": activity.title,
                    "description": activity.description,
                    "priority": activity.priority_number,
                    "outcome": activity.outcome,
                    "timestamp": activity.created_at,
                    "metadata": activity.metadata,
                }
            )

        return json.dumps(activities_data, indent=2)

    def _generate_empty_summary(self, target_date: date) -> DailySummary:
        """Generate summary for a day with no activities.

        Args:
            target_date: Date with no activities

        Returns:
            DailySummary with empty day message
        """
        summary_text = f"""🤖 code_developer Daily Standup - {target_date.isoformat()}
================================================

📊 Yesterday's Accomplishments:
No development activities recorded for this date.

⚠️ Blockers/Issues:
None

📈 Metrics:
- Total activities: 0

🎯 Next Steps:
Waiting for next work session.
"""

        return DailySummary(
            date=target_date.isoformat(),
            summary_text=summary_text,
            metrics={
                "total_activities": 0,
                "commits": 0,
                "test_runs": 0,
                "prs_created": 0,
                "priorities_completed": 0,
                "successes": 0,
                "failures": 0,
            },
            activities=[],
            generated_at=datetime.utcnow().isoformat(),
        )

    def _generate_fallback_summary(
        self,
        target_date: date,
        activities: List[Activity],
        metrics: Dict[str, Any],
    ) -> str:
        """Generate template-based summary when Claude API fails.

        Provides basic metrics summary without AI-generated narrative.

        Args:
            target_date: Date of report
            activities: List of activities
            metrics: Calculated metrics

        Returns:
            Markdown summary with metrics
        """
        activity_summary = self._summarize_activities_basic(activities)

        return f"""🤖 code_developer Daily Standup - {target_date.isoformat()}
================================================

📊 Yesterday's Accomplishments:
{activity_summary}

📈 Metrics:
- Commits: {metrics.get('commits', 0)}
- Test runs: {metrics.get('test_runs', 0)}
- Tests passed: (check test run details)
- PRs created: {metrics.get('prs_created', 0)}
- Priorities completed: {metrics.get('priorities_completed', 0)}
- Success rate: {metrics.get('successes', 0)}/{metrics.get('total_activities', 0)}

Note: AI summary unavailable - showing basic metrics only.
"""

    def _summarize_activities_basic(self, activities: List[Activity]) -> str:
        """Create basic summary of activities.

        Args:
            activities: List of activities

        Returns:
            Bullet-point summary of activities
        """
        if not activities:
            return "No activities recorded."

        priority_work = {}
        for activity in activities:
            priority = activity.priority_number or "Uncategorized"
            if priority not in priority_work:
                priority_work[priority] = []
            priority_work[priority].append(activity.title)

        lines = []
        for priority, titles in priority_work.items():
            lines.append(f"- {priority}: {len(titles)} activities")
            for title in titles[:3]:  # Show first 3
                lines.append(f"  - {title}")
            if len(titles) > 3:
                lines.append(f"  ... and {len(titles) - 3} more")

        return "\n".join(lines)

    def _get_developer_status(self) -> Dict:
        """Get current developer status from developer_status.json.

        Returns:
            Dictionary with developer status info

        Note:
            Returns empty dict if file doesn't exist or can't be read.
        """
        try:
            from pathlib import Path

            status_file = Path("/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/data/developer_status.json")

            if status_file.exists():
                with open(status_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load developer status: {e}")

        return {}
