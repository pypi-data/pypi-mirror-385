"""Status Report Generator - Generate delivery summaries and calendars from ROADMAP.

This module provides functionality to:
- Extract completed stories from ROADMAP (last N days)
- Extract upcoming priorities with estimates
- Format executive-style delivery summaries
- Generate calendar reports with estimated completion dates

Example:
    >>> from coffee_maker.reports.status_report_generator import StatusReportGenerator
    >>>
    >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
    >>> completions = generator.get_recent_completions(days=14)
    >>> summary = generator.format_delivery_summary(completions)
    >>> print(summary)
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from coffee_maker.autonomous.roadmap_parser import RoadmapParser

logger = logging.getLogger(__name__)


@dataclass
class StoryCompletion:
    """Represents a completed user story or priority.

    Attributes:
        story_id: Story ID (e.g., "US-015", "PRIORITY 4")
        title: Story title
        completion_date: Date when story was completed
        business_value: Business value description
        key_features: List of key features delivered
        estimated_days: Estimated days (if available)
        actual_days: Actual days taken (if available)

    Example:
        >>> completion = StoryCompletion(
        ...     story_id="US-016",
        ...     title="Technical Spec Generation",
        ...     completion_date=datetime(2025, 10, 15),
        ...     business_value="Accurate delivery estimates before coding starts",
        ...     key_features=["AI-assisted task breakdown", "100 tests passing"],
        ...     estimated_days=4.5,
        ...     actual_days=3.75
        ... )
    """

    story_id: str
    title: str
    completion_date: datetime
    business_value: str
    key_features: List[str]
    estimated_days: Optional[float] = None
    actual_days: Optional[float] = None


@dataclass
class UpcomingStory:
    """Represents an upcoming deliverable with estimates.

    Attributes:
        story_id: Story ID (e.g., "US-017", "PRIORITY 5")
        title: Story title
        estimated_min_days: Minimum estimated days
        estimated_max_days: Maximum estimated days
        estimated_completion_date: Estimated completion date
        what_description: "What" description from user story
        impact_statement: Impact/business value statement

    Example:
        >>> upcoming = UpcomingStory(
        ...     story_id="US-017",
        ...     title="Summary & Calendar",
        ...     estimated_min_days=5.0,
        ...     estimated_max_days=7.0,
        ...     estimated_completion_date=datetime(2025, 10, 27),
        ...     what_description="Proactive delivery summaries and calendar",
        ...     impact_statement="Better visibility, reduced status questions"
        ... )
    """

    story_id: str
    title: str
    estimated_min_days: float
    estimated_max_days: float
    estimated_completion_date: datetime
    what_description: str
    impact_statement: str


class StatusReportGenerator:
    """Generate status reports and delivery calendars from ROADMAP.md.

    This class provides methods to extract completed stories, upcoming priorities,
    and format them into executive-style summaries and calendar reports.

    Attributes:
        roadmap_path: Path to ROADMAP.md file
        parser: RoadmapParser instance
        velocity_days_per_story: Average days per story (for calendar estimates)

    Example:
        >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
        >>> completions = generator.get_recent_completions(days=14)
        >>> print(f"Found {len(completions)} recent completions")
        >>> summary = generator.format_delivery_summary(completions)
        >>> print(summary)
    """

    def __init__(self, roadmap_path: str, velocity_days_per_story: float = 3.5):
        """Initialize StatusReportGenerator.

        Args:
            roadmap_path: Path to ROADMAP.md file
            velocity_days_per_story: Average days per story for calendar estimates
                                    (default: 3.5 days, will be replaced with
                                    US-015 metrics in future)

        Raises:
            FileNotFoundError: If ROADMAP.md does not exist
        """
        self.roadmap_path = Path(roadmap_path)

        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        self.parser = RoadmapParser(str(roadmap_path))
        self.velocity_days_per_story = velocity_days_per_story

        logger.info(f"StatusReportGenerator initialized for {roadmap_path}")

    def get_recent_completions(self, days: int = 14) -> List[StoryCompletion]:
        """Get list of recently completed stories/priorities.

        Searches ROADMAP.md for entries marked as "Complete" or "✅" within
        the last N days. Extracts business value, key features, and estimates.

        Args:
            days: Number of days to look back (default: 14)

        Returns:
            List of StoryCompletion objects, sorted by completion_date (newest first)

        Example:
            >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
            >>> completions = generator.get_recent_completions(days=7)
            >>> for completion in completions:
            ...     print(f"{completion.story_id}: {completion.title}")
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        completions = []

        # Read full roadmap content
        content = self.roadmap_path.read_text()

        # Pattern to match User Stories: ### 🎯 [US-XXX] Title
        us_pattern = r"### 🎯 \[(US-\d+)\] (.+?)(?:\n|$)"
        us_matches = re.finditer(us_pattern, content)

        for match in us_matches:
            story_id = match.group(1)
            title = match.group(2).strip()

            # Extract story section
            section_start = match.start()
            # Find next section (either ### or ##)
            next_section = re.search(r"\n##", content[section_start + 1 :])
            section_end = section_start + next_section.start() if next_section else len(content)
            section_content = content[section_start:section_end]

            # Check if story is complete
            if not self._is_complete(section_content):
                continue

            # Extract completion date
            completion_date = self._extract_completion_date(section_content)
            if not completion_date:
                # Try to extract from status line (fallback)
                completion_date = self._extract_date_from_status(section_content)

            # Skip if no completion date or outside date range
            if not completion_date or completion_date < cutoff_date:
                continue

            # Extract business value
            business_value = self._extract_business_value(section_content)

            # Extract key features
            key_features = self._extract_key_features(section_content)

            # Extract estimates
            estimated_days_dict = self._extract_estimated_days(section_content)
            actual_days = self._extract_actual_days(section_content)

            # Convert estimated_days dict to average float
            estimated_days = None
            if estimated_days_dict:
                estimated_days = (estimated_days_dict["min_days"] + estimated_days_dict["max_days"]) / 2

            completion = StoryCompletion(
                story_id=story_id,
                title=title,
                completion_date=completion_date,
                business_value=business_value,
                key_features=key_features,
                estimated_days=estimated_days,
                actual_days=actual_days,
            )

            completions.append(completion)
            logger.debug(f"Found completion: {story_id} - {title}")

        # Also check PRIORITY sections for completions
        priorities = self.parser.get_priorities()
        for priority in priorities:
            if not self._is_complete(priority["content"]):
                continue

            # Extract completion date
            completion_date = self._extract_completion_date(priority["content"])
            if not completion_date:
                completion_date = self._extract_date_from_status(priority["content"])

            # Skip if no completion date or outside date range
            if not completion_date or completion_date < cutoff_date:
                continue

            # Extract data
            business_value = self._extract_business_value(priority["content"])
            key_features = self._extract_key_features(priority["content"])
            estimated_days_dict = self._extract_estimated_days(priority["content"])
            actual_days = self._extract_actual_days(priority["content"])

            # Convert estimated_days dict to average float
            estimated_days = None
            if estimated_days_dict:
                estimated_days = (estimated_days_dict["min_days"] + estimated_days_dict["max_days"]) / 2

            completion = StoryCompletion(
                story_id=priority["name"],
                title=priority["title"],
                completion_date=completion_date,
                business_value=business_value,
                key_features=key_features,
                estimated_days=estimated_days,
                actual_days=actual_days,
            )

            completions.append(completion)
            logger.debug(f"Found priority completion: {priority['name']} - {priority['title']}")

        # Sort by completion date (newest first)
        completions.sort(key=lambda x: x.completion_date, reverse=True)

        logger.info(f"Found {len(completions)} completions in last {days} days")
        return completions

    def get_upcoming_deliverables(self, limit: int = 3) -> List[UpcomingStory]:
        """Get list of upcoming priorities/stories with estimates.

        Searches ROADMAP.md for planned/in-progress stories that have estimates
        (not "TBD"). Returns top N stories with estimated completion dates.

        Args:
            limit: Maximum number of upcoming stories to return (default: 3)

        Returns:
            List of UpcomingStory objects with estimated completion dates

        Example:
            >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
            >>> upcoming = generator.get_upcoming_deliverables(limit=3)
            >>> for story in upcoming:
            ...     print(f"{story.story_id}: {story.estimated_min_days}-{story.estimated_max_days} days")
        """
        upcoming = []

        # Read full roadmap content
        content = self.roadmap_path.read_text()

        # Pattern to match User Stories: ### 🎯 [US-XXX] Title
        us_pattern = r"### 🎯 \[(US-\d+)\] (.+?)(?:\n|$)"
        us_matches = re.finditer(us_pattern, content)

        for match in us_matches:
            if len(upcoming) >= limit:
                break

            story_id = match.group(1)
            title = match.group(2).strip()

            # Extract story section
            section_start = match.start()
            next_section = re.search(r"\n##", content[section_start + 1 :])
            section_end = section_start + next_section.start() if next_section else len(content)
            section_content = content[section_start:section_end]

            # Check if story is complete (skip if complete)
            if self._is_complete(section_content):
                continue

            # Extract estimated days
            estimated_days = self._extract_estimated_days(section_content)
            if not estimated_days:
                continue  # Skip stories without estimates

            # Extract "What" description (from "I want" field)
            what_description = self._extract_what_description(section_content)

            # Extract impact statement
            impact_statement = self._extract_impact_statement(section_content)

            # Calculate estimated completion date
            avg_days = (estimated_days["min_days"] + estimated_days["max_days"]) / 2
            estimated_completion_date = datetime.now() + timedelta(days=avg_days)

            upcoming_story = UpcomingStory(
                story_id=story_id,
                title=title,
                estimated_min_days=estimated_days["min_days"],
                estimated_max_days=estimated_days["max_days"],
                estimated_completion_date=estimated_completion_date,
                what_description=what_description,
                impact_statement=impact_statement,
            )

            upcoming.append(upcoming_story)
            logger.debug(f"Found upcoming: {story_id} - {title}")

        # Also check PRIORITY sections
        priorities = self.parser.get_priorities()
        for priority in priorities:
            if len(upcoming) >= limit:
                break

            # Skip completed priorities
            if self._is_complete(priority["content"]):
                continue

            # Extract estimated days
            estimated_days = self._extract_estimated_days(priority["content"])
            if not estimated_days:
                continue

            # Extract descriptions
            what_description = self._extract_what_description(priority["content"])
            impact_statement = self._extract_impact_statement(priority["content"])

            # Calculate estimated completion date
            avg_days = (estimated_days["min_days"] + estimated_days["max_days"]) / 2
            estimated_completion_date = datetime.now() + timedelta(days=avg_days)

            upcoming_story = UpcomingStory(
                story_id=priority["name"],
                title=priority["title"],
                estimated_min_days=estimated_days["min_days"],
                estimated_max_days=estimated_days["max_days"],
                estimated_completion_date=estimated_completion_date,
                what_description=what_description,
                impact_statement=impact_statement,
            )

            upcoming.append(upcoming_story)
            logger.debug(f"Found upcoming priority: {priority['name']} - {priority['title']}")

        logger.info(f"Found {len(upcoming)} upcoming deliverables with estimates")
        return upcoming[:limit]

    def format_delivery_summary(self, completions: List[StoryCompletion]) -> str:
        """Format recent completions as executive summary.

        Creates a pretty, user-friendly summary of recent deliveries with:
        - Story ID and title
        - Completion date
        - Business value
        - Key features delivered
        - Estimation accuracy (if available)

        Args:
            completions: List of StoryCompletion objects

        Returns:
            Formatted summary string (markdown format)

        Example:
            >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
            >>> completions = generator.get_recent_completions(days=14)
            >>> summary = generator.format_delivery_summary(completions)
            >>> print(summary)
        """
        if not completions:
            return "No recent deliveries in the specified timeframe."

        lines = []
        lines.append("# Recent Deliveries Summary")
        lines.append("")
        lines.append(f"Period: Last {(datetime.now() - completions[-1].completion_date).days} days")
        lines.append(f"Total Deliveries: {len(completions)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for completion in completions:
            # Header
            lines.append(f"## {completion.story_id}: {completion.title}")
            lines.append("")

            # Completion date
            date_str = completion.completion_date.strftime("%Y-%m-%d")
            lines.append(f"**Completed**: {date_str}")
            lines.append("")

            # Business value
            if completion.business_value:
                lines.append(f"**Business Value**: {completion.business_value}")
                lines.append("")

            # Key features
            if completion.key_features:
                lines.append("**Key Features**:")
                for feature in completion.key_features:
                    lines.append(f"- {feature}")
                lines.append("")

            # Estimation accuracy (if available)
            if completion.estimated_days and completion.actual_days:
                accuracy_pct = (
                    100 - abs(completion.actual_days - completion.estimated_days) / completion.estimated_days * 100
                )
                lines.append(
                    f"**Estimation Accuracy**: {accuracy_pct:.1f}% "
                    f"(Estimated: {completion.estimated_days} days, "
                    f"Actual: {completion.actual_days} days)"
                )
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def format_calendar_report(self, deliverables: List[UpcomingStory]) -> str:
        """Format upcoming deliverables as calendar report.

        Creates a text-based prose report with:
        - Priority order (1, 2, 3...)
        - Estimated completion dates
        - What description
        - Impact statement

        Args:
            deliverables: List of UpcomingStory objects

        Returns:
            Formatted calendar report string

        Example:
            >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
            >>> upcoming = generator.get_upcoming_deliverables(limit=3)
            >>> calendar = generator.format_calendar_report(upcoming)
            >>> print(calendar)
        """
        if not deliverables:
            return "No upcoming deliverables with time estimates."

        lines = []
        lines.append("# Upcoming Deliverables Calendar")
        lines.append("")
        lines.append(f"Next {len(deliverables)} Priorities")
        lines.append("")
        lines.append("---")
        lines.append("")

        for idx, story in enumerate(deliverables, 1):
            # Priority number and title
            lines.append(f"## {idx}. {story.story_id}: {story.title}")
            lines.append("")

            # Estimated time range
            lines.append(
                f"**Estimated**: {story.estimated_min_days:.0f}-{story.estimated_max_days:.0f} days "
                f"(completing by {story.estimated_completion_date.strftime('%Y-%m-%d')})"
            )
            lines.append("")

            # What description
            if story.what_description:
                lines.append(f"**What**: {story.what_description}")
                lines.append("")

            # Impact statement
            if story.impact_statement:
                lines.append(f"**Impact**: {story.impact_statement}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    # ==================== HELPER METHODS ====================

    def _is_complete(self, content: str) -> bool:
        """Check if section is marked as complete.

        Args:
            content: Section content

        Returns:
            True if complete, False otherwise
        """
        status_lower = content.lower()
        return "✅" in content or ("complete" in status_lower and "status" in status_lower)

    def _extract_completion_date(self, content: str) -> Optional[datetime]:
        """Extract completion date from section content.

        Looks for patterns like:
        - **Completed**: 2025-10-15
        - Completed: 2025-10-15
        - (2025-10-15)

        Args:
            content: Section content

        Returns:
            Datetime object or None if not found
        """
        # Pattern: **Completed**: YYYY-MM-DD
        patterns = [
            r"\*\*Completed\*\*:\s*(\d{4}-\d{2}-\d{2})",
            r"Completed:\s*(\d{4}-\d{2}-\d{2})",
            r"\((\d{4}-\d{2}-\d{2})\)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    date_str = match.group(1)
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue

        return None

    def _extract_date_from_status(self, content: str) -> Optional[datetime]:
        """Extract date from status line (fallback method).

        Looks for patterns like:
        - Status: ✅ Complete (2025-10-15)
        - Status: Complete - 2025-10-15

        Args:
            content: Section content

        Returns:
            Datetime object or None if not found
        """
        # Pattern: Status: ... (YYYY-MM-DD)
        pattern = r"\*\*Status\*\*:.*?(\d{4}-\d{2}-\d{2})"
        match = re.search(pattern, content)

        if match:
            try:
                date_str = match.group(1)
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        # If no date found, use today as fallback for recent completions
        if "✅" in content or "complete" in content.lower():
            return datetime.now()

        return None

    def _extract_business_value(self, content: str) -> str:
        """Extract business value from section content.

        Looks for patterns like:
        - **Business Value**: description
        - **Value**: description

        Args:
            content: Section content

        Returns:
            Business value string or empty string
        """
        patterns = [
            r"\*\*Business Value\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)",
            r"\*\*Value\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                value = match.group(1).strip()
                # Remove star ratings
                value = re.sub(r"⭐+\s*", "", value)
                return value

        return "Improved system capabilities"

    def _extract_key_features(self, content: str) -> List[str]:
        """Extract key features from section content.

        Looks for sections like:
        - **Key Features**:
        - **Features Delivered**:
        - **Deliverables**:

        Args:
            content: Section content

        Returns:
            List of key features
        """
        features = []

        # Look for Key Features section
        patterns = [
            r"\*\*Key Features\*\*:\s*\n((?:- .+\n?)+)",
            r"\*\*Features Delivered\*\*:\s*\n((?:- .+\n?)+)",
            r"\*\*Deliverables\*\*:\s*\n((?:- .+\n?)+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                features_text = match.group(1)
                # Extract list items
                feature_items = re.findall(r"- (.+)", features_text)
                features.extend([f.strip() for f in feature_items])
                break

        # Limit to top 5 features for summary
        return features[:5]

    def _extract_estimated_days(self, content: str) -> Optional[dict]:
        """Extract estimated days from section content.

        Handles multiple formats:
        - **Estimated Effort**: 4-5 days
        - **Estimated Effort**: 3 story points (2-3 days)
        - **Total Estimated**: 1-2 days

        Args:
            content: Section content

        Returns:
            Dict with min_days, max_days, or None
        """
        # Pattern 1: Direct days format (X-Y days)
        direct_patterns = [
            r"\*\*Estimated Effort\*\*:\s*(\d+)-(\d+)\s*days?",
            r"\*\*Total Estimated\*\*:\s*(\d+)-(\d+)\s*days?",
            r"\*\*Estimated\*\*:\s*(\d+)-(\d+)\s*days?",
        ]

        for pattern in direct_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                min_days = float(match.group(1))
                max_days = float(match.group(2))
                return {
                    "min_days": min_days,
                    "max_days": max_days,
                }

        # Pattern 2: Story points format (X story points (Y-Z days))
        story_points_pattern = r"\*\*Estimated Effort\*\*:\s*\d+(?:-\d+)?\s*story points?\s*\((\d+)-(\d+)\s*days?\)"
        match = re.search(story_points_pattern, content, re.IGNORECASE)
        if match:
            min_days = float(match.group(1))
            max_days = float(match.group(2))
            return {
                "min_days": min_days,
                "max_days": max_days,
            }

        # Pattern 3: Story points with weeks (X story points (Y-Z weeks))
        weeks_pattern = r"\*\*Estimated Effort\*\*:\s*\d+(?:-\d+)?\s*story points?\s*\((\d+)-(\d+)\s*weeks?\)"
        match = re.search(weeks_pattern, content, re.IGNORECASE)
        if match:
            min_weeks = float(match.group(1))
            max_weeks = float(match.group(2))
            # Convert weeks to days (assuming 5 work days per week)
            return {
                "min_days": min_weeks * 5,
                "max_days": max_weeks * 5,
            }

        return None

    def _extract_actual_days(self, content: str) -> Optional[float]:
        """Extract actual days taken from section content.

        Looks for patterns like:
        - **Actual Effort**: X days
        - Actual: X days

        Args:
            content: Section content

        Returns:
            Actual days or None
        """
        patterns = [
            r"\*\*Actual Effort\*\*:\s*(\d+(?:\.\d+)?)\s*days?",
            r"Actual:\s*(\d+(?:\.\d+)?)\s*days?",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return None

    def _extract_what_description(self, content: str) -> str:
        """Extract 'What' description from user story.

        Looks for patterns like:
        - **I want**: description
        - I want to: description

        Args:
            content: Section content

        Returns:
            What description or empty string
        """
        patterns = [
            r"\*\*I want\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)",
            r"I want to\s+(.+?)(?:\n\n|\n\*\*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                description = match.group(1).strip()
                # Truncate if too long
                if len(description) > 150:
                    description = description[:147] + "..."
                return description

        return "Implementation details in ROADMAP"

    def _extract_impact_statement(self, content: str) -> str:
        """Extract impact statement from user story.

        Looks for patterns like:
        - **So that**: impact
        - **Impact**: impact

        Args:
            content: Section content

        Returns:
            Impact statement or empty string
        """
        patterns = [
            r"\*\*So that\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)",
            r"\*\*Impact\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                impact = match.group(1).strip()
                # Truncate if too long
                if len(impact) > 150:
                    impact = impact[:147] + "..."
                return impact

        return "Improved system functionality"

    def generate_status_tracking_document(self, days: int = 14, upcoming_count: int = 5) -> str:
        """Generate auto-maintained STATUS_TRACKING.md document.

        Creates a comprehensive internal tracking document with:
        - Recent completions (last N days) with technical details
        - Current work in progress with progress indicators
        - Next up priorities with estimates
        - Velocity and accuracy metrics
        - Last updated timestamp

        Args:
            days: Number of days to look back for completions (default: 14)
            upcoming_count: Number of upcoming items to show (default: 5)

        Returns:
            Formatted STATUS_TRACKING.md content (markdown)

        Example:
            >>> generator = StatusReportGenerator("docs/roadmap/ROADMAP.md")
            >>> document = generator.generate_status_tracking_document()
            >>> Path("docs/STATUS_TRACKING.md").write_text(document)
        """
        lines = []

        # Header
        lines.append("# STATUS TRACKING")
        lines.append("")
        lines.append("**Auto-Generated Internal Document** - For PM & code_developer")
        lines.append("")
        lines.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Recent Completions Section
        completions = self.get_recent_completions(days=days)
        lines.append(f"## Recent Completions (Last {days} Days)")
        lines.append("")

        if completions:
            for completion in completions:
                lines.append(f"### {completion.story_id}: {completion.title}")
                lines.append("")
                lines.append(f"- **Completed**: {completion.completion_date.strftime('%Y-%m-%d')}")

                # Technical details
                if completion.estimated_days and completion.actual_days:
                    accuracy_pct = (
                        100 - abs(completion.actual_days - completion.estimated_days) / completion.estimated_days * 100
                    )
                    accuracy_emoji = "✅" if accuracy_pct >= 90 else "⚠️" if accuracy_pct >= 70 else "❌"
                    lines.append(
                        f"- **Estimated**: {completion.estimated_days:.1f} days → "
                        f"**Actual**: {completion.actual_days:.1f} days "
                        f"({accuracy_emoji} {accuracy_pct:.0f}% accuracy)"
                    )
                elif completion.estimated_days:
                    lines.append(f"- **Estimated**: {completion.estimated_days:.1f} days")

                # Business value
                if completion.business_value:
                    lines.append(f"- **Impact**: {completion.business_value}")

                # Key features
                if completion.key_features:
                    lines.append("- **Key Features**:")
                    for feature in completion.key_features[:3]:  # Top 3 only
                        lines.append(f"  - {feature}")

                lines.append("")
        else:
            lines.append(f"*No completions in the last {days} days*")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Current Work Section
        lines.append("## Current Work (In Progress)")
        lines.append("")

        in_progress_stories = self._get_in_progress_stories()
        if in_progress_stories:
            for story in in_progress_stories:
                lines.append(f"### {story['story_id']}: {story['title']}")
                lines.append("")

                if story.get("phase"):
                    lines.append(f"- **Phase**: {story['phase']}")

                if story.get("progress_pct"):
                    lines.append(f"- **Progress**: {story['progress_pct']}%")

                if story.get("started_date"):
                    lines.append(f"- **Started**: {story['started_date']}")

                if story.get("estimated_days"):
                    lines.append(f"- **Estimated Remaining**: {story['estimated_days']} days")

                lines.append("")
        else:
            lines.append("*No work currently in progress*")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Next Up Section
        lines.append(f"## Next Up (Top {upcoming_count})")
        lines.append("")

        upcoming = self.get_upcoming_deliverables(limit=upcoming_count)
        if upcoming:
            for idx, story in enumerate(upcoming, 1):
                lines.append(f"{idx}. **{story.story_id}: {story.title}**")
                lines.append(f"   - Estimated: {story.estimated_min_days:.0f}-{story.estimated_max_days:.0f} days")
                if story.what_description:
                    lines.append(f"   - What: {story.what_description}")
                lines.append(f"   - Status: PLANNED")
                lines.append("")
        else:
            lines.append("*No upcoming priorities with estimates*")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Velocity & Accuracy Section
        lines.append("## Velocity & Accuracy Metrics")
        lines.append("")

        velocity_data = self._calculate_velocity_metrics(completions)

        lines.append(f"**Last {days} Days**:")
        lines.append(f"- Stories completed: {velocity_data['stories_completed']}")

        if velocity_data["stories_completed"] > 0:
            lines.append(f"- Average velocity: {velocity_data['avg_velocity']:.1f} stories/week")

            if velocity_data["avg_accuracy"] is not None:
                trend_emoji = (
                    "↑"
                    if velocity_data["trend"] == "improving"
                    else "↓" if velocity_data["trend"] == "declining" else "→"
                )
                lines.append(f"- Average accuracy: {velocity_data['avg_accuracy']:.0f}%")
                lines.append(f"- Trend: {trend_emoji} {velocity_data['trend'].capitalize()}")
        else:
            lines.append("- No velocity data available yet")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Footer
        lines.append(
            "*This document is auto-generated from ROADMAP.md. " "Do not edit manually - changes will be overwritten.*"
        )

        return "\n".join(lines)

    def _get_in_progress_stories(self) -> List[dict]:
        """Get list of stories currently in progress.

        Returns:
            List of dictionaries with story information
        """
        in_progress = []

        # Read full roadmap content
        content = self.roadmap_path.read_text()

        # Pattern to match User Stories: ### 🎯 [US-XXX] Title
        us_pattern = r"### 🎯 \[(US-\d+)\] (.+?)(?:\n|$)"
        us_matches = re.finditer(us_pattern, content)

        for match in us_matches:
            story_id = match.group(1)
            title = match.group(2).strip()

            # Extract story section
            section_start = match.start()
            next_section = re.search(r"\n##", content[section_start + 1 :])
            section_end = section_start + next_section.start() if next_section else len(content)
            section_content = content[section_start:section_end]

            # Check if in progress (not complete, has started or progress indicators)
            if self._is_in_progress(section_content):
                story_info = {
                    "story_id": story_id,
                    "title": title,
                    "phase": self._extract_phase(section_content),
                    "progress_pct": self._extract_progress_pct(section_content),
                    "started_date": self._extract_started_date(section_content),
                    "estimated_days": self._extract_estimated_remaining(section_content),
                }
                in_progress.append(story_info)

        return in_progress

    def _is_in_progress(self, content: str) -> bool:
        """Check if section is marked as in progress.

        Args:
            content: Section content

        Returns:
            True if in progress, False otherwise
        """
        # Don't include completed stories
        if self._is_complete(content):
            return False

        # Look for in-progress indicators
        status_lower = content.lower()
        return "in progress" in status_lower or "🔄" in content or "started:" in status_lower or "phase" in status_lower

    def _extract_phase(self, content: str) -> Optional[str]:
        """Extract phase information from story content."""
        pattern = r"[Pp]hase[:\s]+(\d+/\d+|\d+\s+of\s+\d+)"
        match = re.search(pattern, content)
        return match.group(1) if match else None

    def _extract_progress_pct(self, content: str) -> Optional[int]:
        """Extract progress percentage from story content."""
        pattern = r"[Pp]rogress[:\s]+(\d+)%"
        match = re.search(pattern, content)
        return int(match.group(1)) if match else None

    def _extract_started_date(self, content: str) -> Optional[str]:
        """Extract started date from story content."""
        patterns = [
            r"\*\*Started\*\*:\s*(\d{4}-\d{2}-\d{2})",
            r"Started:\s*(\d{4}-\d{2}-\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None

    def _extract_estimated_remaining(self, content: str) -> Optional[str]:
        """Extract estimated remaining time from story content."""
        patterns = [
            r"[Ee]stimated [Rr]emaining[:\s]+(\d+-?\d*\s*days?)",
            r"[Rr]emaining[:\s]+(\d+-?\d*\s*days?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None

    def _calculate_velocity_metrics(self, completions: List[StoryCompletion]) -> dict:
        """Calculate velocity and accuracy metrics from completions.

        Args:
            completions: List of StoryCompletion objects

        Returns:
            Dictionary with velocity metrics
        """
        stories_completed = len(completions)

        if stories_completed == 0:
            return {"stories_completed": 0, "avg_velocity": 0.0, "avg_accuracy": None, "trend": "unknown"}

        # Calculate average velocity (stories per week)
        days_range = (datetime.now() - completions[-1].completion_date).days
        weeks = max(days_range / 7, 1)  # At least 1 week
        avg_velocity = stories_completed / weeks

        # Calculate average accuracy
        accuracies = []
        for completion in completions:
            if completion.estimated_days and completion.actual_days:
                accuracy = (
                    100 - abs(completion.actual_days - completion.estimated_days) / completion.estimated_days * 100
                )
                accuracies.append(accuracy)

        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

        # Determine trend (compare first half vs second half)
        if len(accuracies) >= 4:
            mid = len(accuracies) // 2
            first_half = sum(accuracies[:mid]) / mid
            second_half = sum(accuracies[mid:]) / (len(accuracies) - mid)

            if second_half > first_half + 5:
                trend = "improving"
            elif second_half < first_half - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "stories_completed": stories_completed,
            "avg_velocity": avg_velocity,
            "avg_accuracy": avg_accuracy,
            "trend": trend,
        }
