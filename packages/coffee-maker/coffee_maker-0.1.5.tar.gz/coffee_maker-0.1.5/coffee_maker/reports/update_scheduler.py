"""Update Scheduler - Automatic and Smart Updates for STATUS_TRACKING.md.

This module provides functionality to:
- Schedule automatic updates every 3 days
- Detect significant estimate changes (>1 day)
- Track update timestamps
- Persist state across sessions

Example:
    >>> from coffee_maker.reports.update_scheduler import UpdateScheduler
    >>>
    >>> scheduler = UpdateScheduler()
    >>> if scheduler.should_update():
    ...     # Perform update
    ...     scheduler.record_update()
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from coffee_maker.autonomous.roadmap_parser import RoadmapParser

logger = logging.getLogger(__name__)


@dataclass
class UpdateState:
    """Represents the state of STATUS_TRACKING.md updates.

    Attributes:
        last_update: Datetime of last update
        update_count: Total number of updates performed
        last_manual_update: Datetime of last manual update (optional)

    Example:
        >>> state = UpdateState(
        ...     last_update=datetime.now(),
        ...     update_count=5,
        ...     last_manual_update=None
        ... )
    """

    last_update: datetime
    update_count: int
    last_manual_update: Optional[datetime] = None


@dataclass
class EstimateChange:
    """Represents a significant estimate change.

    Attributes:
        story_id: Story ID (e.g., "US-017")
        old_min_days: Previous minimum estimate
        old_max_days: Previous maximum estimate
        new_min_days: New minimum estimate
        new_max_days: New maximum estimate
        delta: Change in average estimate (days)

    Example:
        >>> change = EstimateChange(
        ...     story_id="US-017",
        ...     old_min_days=5.0,
        ...     old_max_days=7.0,
        ...     new_min_days=8.0,
        ...     new_max_days=10.0,
        ...     delta=3.0
        ... )
    """

    story_id: str
    old_min_days: float
    old_max_days: float
    new_min_days: float
    new_max_days: float
    delta: float


class UpdateScheduler:
    """Scheduler for automatic and smart STATUS_TRACKING.md updates.

    This class manages:
    - 3-day automatic update schedule
    - Smart detection of estimate changes (>1 day)
    - Timestamp persistence
    - Manual update triggers

    Attributes:
        update_interval_days: Days between automatic updates (default: 3)
        estimate_change_threshold: Threshold for significant changes (default: 1.0 day)
        state_file: Path to update state file
        estimates_file: Path to previous estimates file
        roadmap_path: Path to ROADMAP.md file

    Example:
        >>> scheduler = UpdateScheduler()
        >>> if scheduler.should_update():
        ...     print("Update needed!")
        ...     scheduler.record_update()
    """

    def __init__(
        self,
        roadmap_path: str = "docs/roadmap/ROADMAP.md",
        update_interval_days: int = 3,
        estimate_change_threshold: float = 1.0,
    ):
        """Initialize UpdateScheduler.

        Args:
            roadmap_path: Path to ROADMAP.md file
            update_interval_days: Days between automatic updates (default: 3)
            estimate_change_threshold: Threshold for significant changes in days (default: 1.0)

        Raises:
            FileNotFoundError: If ROADMAP.md does not exist
        """
        self.roadmap_path = Path(roadmap_path)
        self.update_interval_days = update_interval_days
        self.estimate_change_threshold = estimate_change_threshold

        # State files in ~/.coffee_maker/
        coffee_maker_dir = Path.home() / ".coffee_maker"
        coffee_maker_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = coffee_maker_dir / "last_summary_update.json"
        self.estimates_file = coffee_maker_dir / "previous_estimates.json"

        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        self.parser = RoadmapParser(str(roadmap_path))

        logger.info(
            f"UpdateScheduler initialized: interval={update_interval_days} days, "
            f"threshold={estimate_change_threshold} days"
        )

    def should_update(self, force: bool = False) -> bool:
        """Check if STATUS_TRACKING.md should be updated.

        Checks for:
        1. Force flag (manual update)
        2. Time since last update (>= update_interval_days)
        3. Significant estimate changes (>= estimate_change_threshold)

        Args:
            force: Force update regardless of schedule (default: False)

        Returns:
            True if update is needed, False otherwise

        Example:
            >>> scheduler = UpdateScheduler()
            >>> if scheduler.should_update():
            ...     print("Time to update!")
            >>> if scheduler.should_update(force=True):
            ...     print("Forced update!")
        """
        if force:
            logger.info("Update forced by user")
            return True

        # Check time since last update
        time_based_update = self._should_update_by_time()
        if time_based_update:
            logger.info(f"Update needed: {self.update_interval_days} days elapsed")
            return True

        # Check for estimate changes
        estimate_changes = self.check_estimate_changes()
        if estimate_changes:
            logger.info(f"Update needed: {len(estimate_changes)} significant estimate change(s)")
            return True

        logger.debug("No update needed")
        return False

    def _should_update_by_time(self) -> bool:
        """Check if update is needed based on time interval.

        Returns:
            True if >= update_interval_days elapsed, False otherwise
        """
        state = self._load_state()

        if not state:
            # No previous update - should update
            return True

        time_since_update = datetime.now() - state.last_update
        return time_since_update.days >= self.update_interval_days

    def get_time_since_last_update(self) -> Optional[timedelta]:
        """Get time elapsed since last update.

        Returns:
            Timedelta since last update, or None if never updated

        Example:
            >>> scheduler = UpdateScheduler()
            >>> time_since = scheduler.get_time_since_last_update()
            >>> if time_since:
            ...     print(f"Last updated {time_since.days} days ago")
        """
        state = self._load_state()

        if not state:
            return None

        return datetime.now() - state.last_update

    def check_estimate_changes(self) -> list[EstimateChange]:
        """Check for significant estimate changes in ROADMAP.

        Compares current estimates with previous estimates and returns
        changes that exceed the threshold.

        Returns:
            List of EstimateChange objects with significant changes

        Example:
            >>> scheduler = UpdateScheduler()
            >>> changes = scheduler.check_estimate_changes()
            >>> for change in changes:
            ...     print(f"{change.story_id}: {change.delta:+.1f} days")
        """
        # Load previous estimates
        previous_estimates = self._load_estimates()

        # Get current estimates from ROADMAP
        current_estimates = self._get_current_estimates()

        # Compare and find significant changes
        significant_changes = []

        for story_id, current in current_estimates.items():
            if story_id not in previous_estimates:
                # New story - not a change
                continue

            previous = previous_estimates[story_id]

            # Calculate average estimates
            prev_avg = (previous["min_days"] + previous["max_days"]) / 2
            curr_avg = (current["min_days"] + current["max_days"]) / 2

            # Check if change is significant
            delta = abs(curr_avg - prev_avg)

            if delta >= self.estimate_change_threshold:
                change = EstimateChange(
                    story_id=story_id,
                    old_min_days=previous["min_days"],
                    old_max_days=previous["max_days"],
                    new_min_days=current["min_days"],
                    new_max_days=current["max_days"],
                    delta=delta,
                )
                significant_changes.append(change)

                logger.info(
                    f"Significant estimate change detected: {story_id} " f"({prev_avg:.1f} → {curr_avg:.1f} days)"
                )

        return significant_changes

    def record_update(self, manual: bool = False) -> None:
        """Record that an update was performed.

        Updates:
        - Last update timestamp
        - Update count
        - Manual update timestamp (if manual=True)
        - Previous estimates snapshot

        Args:
            manual: Whether this was a manual update (default: False)

        Example:
            >>> scheduler = UpdateScheduler()
            >>> scheduler.record_update(manual=True)
        """
        now = datetime.now()

        # Load or create state
        state = self._load_state()

        if state:
            state.last_update = now
            state.update_count += 1
            if manual:
                state.last_manual_update = now
        else:
            state = UpdateState(last_update=now, update_count=1, last_manual_update=now if manual else None)

        # Save state
        self._save_state(state)

        # Save current estimates as "previous" for next comparison
        current_estimates = self._get_current_estimates()
        self._save_estimates(current_estimates)

        logger.info(f"Update recorded: manual={manual}, total_count={state.update_count}")

    def get_update_summary(self) -> dict:
        """Get summary of update state.

        Returns:
            Dictionary with update state information

        Example:
            >>> scheduler = UpdateScheduler()
            >>> summary = scheduler.get_update_summary()
            >>> print(f"Last updated: {summary['last_update']}")
        """
        state = self._load_state()

        if not state:
            return {
                "last_update": None,
                "update_count": 0,
                "last_manual_update": None,
                "time_since_update": None,
                "next_update_due": None,
            }

        time_since = self.get_time_since_last_update()
        next_update = state.last_update + timedelta(days=self.update_interval_days)

        return {
            "last_update": state.last_update.isoformat(),
            "update_count": state.update_count,
            "last_manual_update": state.last_manual_update.isoformat() if state.last_manual_update else None,
            "time_since_update": str(time_since) if time_since else None,
            "next_update_due": next_update.isoformat(),
        }

    # ==================== PRIVATE METHODS ====================

    def _load_state(self) -> Optional[UpdateState]:
        """Load update state from file.

        Returns:
            UpdateState object or None if file doesn't exist
        """
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)

            return UpdateState(
                last_update=datetime.fromisoformat(data["last_update"]),
                update_count=data["update_count"],
                last_manual_update=(
                    datetime.fromisoformat(data["last_manual_update"]) if data.get("last_manual_update") else None
                ),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load state file: {e}")
            return None

    def _save_state(self, state: UpdateState) -> None:
        """Save update state to file.

        Args:
            state: UpdateState object to save
        """
        try:
            data = {
                "last_update": state.last_update.isoformat(),
                "update_count": state.update_count,
                "last_manual_update": state.last_manual_update.isoformat() if state.last_manual_update else None,
            }

            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.debug(f"State saved to {self.state_file}")
        except IOError as e:
            logger.error(f"Failed to save state: {e}")

    def _load_estimates(self) -> Dict[str, dict]:
        """Load previous estimates from file.

        Returns:
            Dictionary mapping story_id to estimate dict
        """
        if not self.estimates_file.exists():
            return {}

        try:
            with open(self.estimates_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load estimates file: {e}")
            return {}

    def _save_estimates(self, estimates: Dict[str, dict]) -> None:
        """Save current estimates to file.

        Args:
            estimates: Dictionary mapping story_id to estimate dict
        """
        try:
            with open(self.estimates_file, "w") as f:
                json.dump(estimates, f, indent=2)

            logger.debug(f"Estimates saved to {self.estimates_file}")
        except IOError as e:
            logger.error(f"Failed to save estimates: {e}")

    def _get_current_estimates(self) -> Dict[str, dict]:
        """Get current estimates from ROADMAP.md.

        Returns:
            Dictionary mapping story_id to estimate dict with min_days, max_days
        """
        import re

        estimates = {}

        # Read ROADMAP content
        content = self.roadmap_path.read_text()

        # Pattern to match User Stories: ### 🎯 [US-XXX] Title
        us_pattern = r"### 🎯 \[(US-\d+)\] (.+?)(?:\n|$)"
        us_matches = re.finditer(us_pattern, content)

        for match in us_matches:
            story_id = match.group(1)

            # Extract story section
            section_start = match.start()
            next_section = re.search(r"\n##", content[section_start + 1 :])
            section_end = section_start + next_section.start() if next_section else len(content)
            section_content = content[section_start:section_end]

            # Extract estimated days
            estimated_days = self._extract_estimated_days(section_content)

            if estimated_days:
                estimates[story_id] = estimated_days

        # Also check PRIORITY sections
        priorities = self.parser.get_priorities()
        for priority in priorities:
            estimated_days = self._extract_estimated_days(priority["content"])

            if estimated_days:
                estimates[priority["name"]] = estimated_days

        return estimates

    def _extract_estimated_days(self, content: str) -> Optional[dict]:
        """Extract estimated days from section content.

        Args:
            content: Section content

        Returns:
            Dict with min_days, max_days, or None
        """
        import re

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

        return None
