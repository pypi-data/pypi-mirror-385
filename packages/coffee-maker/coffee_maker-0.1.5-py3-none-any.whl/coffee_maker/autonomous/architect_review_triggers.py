"""Review trigger system for architect continuous improvement loop.

This module implements a simple file-based review trigger system that detects
when architect should perform reviews based on file modification times.

No external scheduler required - uses file mtimes for trigger detection.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ReviewTrigger:
    """Simple file-based review trigger system.

    Uses file modification times to determine when reviews are needed.
    No external scheduler required.
    """

    def __init__(self, data_dir: Path = Path("data")):
        """Initialize review trigger system.

        Args:
            data_dir: Directory for storing last review timestamps
        """
        self.data_dir = data_dir
        self.last_review_file = data_dir / "architect_last_review.json"
        self.last_review_file.parent.mkdir(parents=True, exist_ok=True)

    def should_run_daily_review(self) -> bool:
        """Check if daily quick review is needed.

        Triggers when:
        - ROADMAP.md has been modified since last daily review
        - OR last daily review was >24 hours ago

        Returns:
            True if daily review should run
        """
        roadmap_path = Path("docs/roadmap/ROADMAP.md")
        if not roadmap_path.exists():
            return False

        last_review_time = self._get_last_review_time("daily")
        roadmap_mtime = datetime.fromtimestamp(roadmap_path.stat().st_mtime)

        # Trigger if ROADMAP modified since last review
        if last_review_time is None or roadmap_mtime > last_review_time:
            return True

        # Trigger if >24 hours since last review
        if datetime.now() - last_review_time > timedelta(hours=24):
            return True

        return False

    def should_run_weekly_review(self) -> bool:
        """Check if weekly deep review is needed.

        Triggers when:
        - Last weekly review was >7 days ago

        Returns:
            True if weekly review should run
        """
        last_review_time = self._get_last_review_time("weekly")

        # No review yet, or >7 days since last review
        if last_review_time is None:
            return True

        if datetime.now() - last_review_time > timedelta(days=7):
            return True

        return False

    def mark_review_completed(self, review_type: str) -> None:
        """Record that a review was completed.

        Args:
            review_type: "daily" or "weekly"
        """
        reviews = self._load_reviews()
        reviews[review_type] = datetime.now().isoformat()
        self._save_reviews(reviews)

    def _get_last_review_time(self, review_type: str) -> Optional[datetime]:
        """Get timestamp of last review of given type.

        Args:
            review_type: "daily" or "weekly"

        Returns:
            Datetime of last review, or None if no review recorded
        """
        reviews = self._load_reviews()
        if review_type in reviews:
            return datetime.fromisoformat(reviews[review_type])
        return None

    def _load_reviews(self) -> dict:
        """Load review timestamps from JSON file.

        Returns:
            Dict with review timestamps
        """
        if not self.last_review_file.exists():
            return {}

        with open(self.last_review_file) as f:
            return json.load(f)

    def _save_reviews(self, reviews: dict) -> None:
        """Save review timestamps to JSON file.

        Args:
            reviews: Dict with review timestamps
        """
        with open(self.last_review_file, "w") as f:
            json.dump(reviews, f, indent=2)
