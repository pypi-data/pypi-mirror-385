"""Story Metrics Database - Track estimation accuracy and team velocity.

US-015: Estimation Metrics & Velocity Tracking

This module provides a SQLite-based storage system for tracking user story
estimation accuracy, measuring team velocity, and using historical data to
improve future estimates.

Database Schema:
    story_metrics table:
        - id: Primary key
        - story_id: Story identifier (e.g., "US-015")
        - story_title: Human-readable title
        - estimated_min_days: Lower bound of estimate
        - estimated_max_days: Upper bound of estimate
        - actual_days: Actual time taken
        - started_at: When work began
        - completed_at: When work completed
        - estimation_error: actual - avg(estimated)
        - estimation_accuracy_pct: 100 - abs(error/estimated × 100)
        - complexity: "low", "medium", "high"
        - category: "feature", "bug", "refactor", "docs"
        - story_points: Agile story points
        - spec_phase_metrics: JSON array of phase-level metrics
        - has_technical_spec: Boolean flag
        - technical_spec_path: Path to spec document

    velocity_snapshots table:
        - id: Primary key
        - period_start: Start of period (weekly/sprint)
        - period_end: End of period
        - stories_completed: Count of stories
        - story_points_completed: Total points
        - total_days_actual: Sum of actual days
        - avg_estimation_accuracy_pct: Average accuracy

Features:
    - Estimation error tracking
    - Velocity calculation (stories/week, points/week)
    - Accuracy trends over time
    - Category-specific metrics
    - Spec vs no-spec comparison
    - Historical learning for improved estimates

Example:
    >>> from coffee_maker.autonomous.story_metrics import StoryMetricsDB
    >>> metrics = StoryMetricsDB()
    >>>
    >>> # Start a story
    >>> metrics.start_story(
    ...     story_id="US-015",
    ...     story_title="Estimation Metrics & Velocity Tracking",
    ...     estimated_min_days=3.0,
    ...     estimated_max_days=4.0,
    ...     complexity="medium",
    ...     category="feature"
    ... )
    >>>
    >>> # Complete the story
    >>> metrics.complete_story(story_id="US-015", actual_days=3.5)
    >>>
    >>> # Get velocity
    >>> velocity = metrics.get_current_velocity(period_days=7)
    >>> print(f"Stories per week: {velocity['stories_per_week']}")
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StoryMetricsDB:
    """Database for tracking story-level estimation metrics and velocity.

    Attributes:
        db_path: Path to SQLite database file
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize metrics database.

        Args:
            db_path: Optional custom database path.
                    Defaults to ~/.coffee_maker/story_metrics.db
        """
        if db_path is None:
            db_path = Path.home() / ".coffee_maker" / "story_metrics.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"StoryMetricsDB initialized at {self.db_path}")

    def _init_database(self):
        """Initialize database schema with WAL mode."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")

        cursor = conn.cursor()

        # Create story_metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS story_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id TEXT NOT NULL UNIQUE,
                story_title TEXT NOT NULL,

                -- Time estimation
                estimated_min_days REAL,
                estimated_max_days REAL,
                actual_days REAL,

                -- Timestamps
                started_at TEXT,
                completed_at TEXT,

                -- Accuracy metrics
                estimation_error REAL,
                estimation_accuracy_pct REAL,

                -- Context
                complexity TEXT,
                category TEXT,
                story_points INTEGER,

                -- Technical spec integration (US-016)
                spec_phase_metrics TEXT,
                has_technical_spec INTEGER DEFAULT 0,
                technical_spec_path TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create velocity_snapshots table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS velocity_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                stories_completed INTEGER NOT NULL,
                story_points_completed INTEGER NOT NULL,
                total_days_actual REAL NOT NULL,
                avg_estimation_accuracy_pct REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for fast queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_story_id
            ON story_metrics(story_id)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_completed_at
            ON story_metrics(completed_at)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_category
            ON story_metrics(category)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_has_technical_spec
            ON story_metrics(has_technical_spec)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_velocity_period_start
            ON velocity_snapshots(period_start)
        """
        )

        conn.commit()
        conn.close()

        logger.debug("Story metrics database schema initialized")

    def start_story(
        self,
        story_id: str,
        story_title: str,
        estimated_min_days: float,
        estimated_max_days: float,
        complexity: str = "medium",
        category: str = "feature",
        story_points: Optional[int] = None,
        has_technical_spec: bool = False,
        technical_spec_path: Optional[str] = None,
    ) -> int:
        """Record the start of a user story.

        Args:
            story_id: Story identifier (e.g., "US-015")
            story_title: Human-readable title
            estimated_min_days: Lower bound estimate
            estimated_max_days: Upper bound estimate
            complexity: "low", "medium", or "high"
            category: "feature", "bug", "refactor", or "docs"
            story_points: Optional agile story points
            has_technical_spec: Whether story has detailed technical spec
            technical_spec_path: Path to technical spec document

        Returns:
            Database record ID

        Example:
            >>> metrics.start_story(
            ...     story_id="US-015",
            ...     story_title="Estimation Metrics",
            ...     estimated_min_days=3.0,
            ...     estimated_max_days=4.0,
            ...     complexity="medium",
            ...     category="feature",
            ...     has_technical_spec=True,
            ...     technical_spec_path="docs/US-015_TECHNICAL_SPEC.md"
            ... )
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        started_at = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO story_metrics (
                story_id,
                story_title,
                estimated_min_days,
                estimated_max_days,
                started_at,
                complexity,
                category,
                story_points,
                has_technical_spec,
                technical_spec_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                story_id,
                story_title,
                estimated_min_days,
                estimated_max_days,
                started_at,
                complexity,
                category,
                story_points,
                1 if has_technical_spec else 0,
                technical_spec_path,
            ),
        )

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(
            f"Started story {story_id}: {story_title} " f"(estimated {estimated_min_days}-{estimated_max_days} days)"
        )

        return record_id

    def complete_story(
        self,
        story_id: str,
        actual_days: Optional[float] = None,
        spec_phase_metrics: Optional[List[Dict]] = None,
    ):
        """Mark a story as complete and calculate metrics.

        Args:
            story_id: Story identifier
            actual_days: Actual time taken (if None, calculated from started_at)
            spec_phase_metrics: Optional list of phase-level metrics from spec

        Example:
            >>> metrics.complete_story(
            ...     story_id="US-015",
            ...     actual_days=3.5,
            ...     spec_phase_metrics=[
            ...         {"phase": "Phase 1", "estimated_hours": 6, "actual_hours": 8},
            ...         {"phase": "Phase 2", "estimated_hours": 8, "actual_hours": 7}
            ...     ]
            ... )
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get story record
        cursor.execute(
            """
            SELECT started_at, estimated_min_days, estimated_max_days
            FROM story_metrics
            WHERE story_id = ?
        """,
            (story_id,),
        )

        row = cursor.fetchone()
        if not row:
            logger.error(f"Story {story_id} not found in database")
            conn.close()
            return

        started_at_str, estimated_min, estimated_max = row

        # Calculate actual days if not provided
        if actual_days is None:
            started_at = datetime.fromisoformat(started_at_str)
            completed_at = datetime.now()
            actual_days = (completed_at - started_at).total_seconds() / (24 * 3600)
        else:
            completed_at = datetime.now()

        # Calculate metrics
        estimated_avg = (estimated_min + estimated_max) / 2
        estimation_error = actual_days - estimated_avg
        estimation_accuracy_pct = 100 - abs(estimation_error / estimated_avg * 100) if estimated_avg > 0 else 0

        # Serialize spec phase metrics if provided
        spec_phase_json = json.dumps(spec_phase_metrics) if spec_phase_metrics else None

        # Update record
        cursor.execute(
            """
            UPDATE story_metrics
            SET actual_days = ?,
                completed_at = ?,
                estimation_error = ?,
                estimation_accuracy_pct = ?,
                spec_phase_metrics = ?
            WHERE story_id = ?
        """,
            (
                actual_days,
                completed_at.isoformat(),
                estimation_error,
                estimation_accuracy_pct,
                spec_phase_json,
                story_id,
            ),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"Completed story {story_id}: {actual_days:.1f} days "
            f"(estimated {estimated_avg:.1f}, error {estimation_error:+.1f}, "
            f"accuracy {estimation_accuracy_pct:.1f}%)"
        )

    def get_story_metrics(self, story_id: str) -> Optional[Dict]:
        """Get metrics for a specific story.

        Args:
            story_id: Story identifier

        Returns:
            Dictionary with story metrics or None if not found
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM story_metrics WHERE story_id = ?
        """,
            (story_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        metrics = dict(row)

        # Parse JSON fields
        if metrics.get("spec_phase_metrics"):
            try:
                metrics["spec_phase_metrics"] = json.loads(metrics["spec_phase_metrics"])
            except json.JSONDecodeError:
                metrics["spec_phase_metrics"] = None

        return metrics

    def get_current_velocity(self, period_days: int = 7) -> Dict:
        """Calculate current velocity over specified period.

        Args:
            period_days: Number of days to look back (default: 7 for weekly)

        Returns:
            Dictionary with velocity metrics:
            - stories_per_week: Stories completed per week
            - points_per_week: Story points per week
            - avg_days_per_story: Average days per story
            - avg_accuracy_pct: Average estimation accuracy
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

        cursor.execute(
            """
            SELECT
                COUNT(*) as story_count,
                SUM(story_points) as total_points,
                SUM(actual_days) as total_days,
                AVG(estimation_accuracy_pct) as avg_accuracy
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            AND completed_at >= ?
        """,
            (cutoff_date,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row or row[0] == 0:
            return {
                "stories_per_week": 0,
                "points_per_week": 0,
                "avg_days_per_story": 0,
                "avg_accuracy_pct": 0,
                "period_days": period_days,
            }

        story_count, total_points, total_days, avg_accuracy = row

        # Calculate per-week metrics
        weeks = period_days / 7
        stories_per_week = story_count / weeks if weeks > 0 else 0
        points_per_week = (total_points or 0) / weeks if weeks > 0 else 0
        avg_days_per_story = total_days / story_count if story_count > 0 else 0

        return {
            "stories_per_week": round(stories_per_week, 2),
            "points_per_week": round(points_per_week, 2),
            "avg_days_per_story": round(avg_days_per_story, 2),
            "avg_accuracy_pct": round(avg_accuracy or 0, 2),
            "period_days": period_days,
        }

    def get_accuracy_trends(self, limit: int = 10) -> List[Dict]:
        """Get accuracy trends for recent stories.

        Args:
            limit: Number of recent stories to include

        Returns:
            List of story metrics with accuracy data
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                story_id,
                story_title,
                estimated_min_days,
                estimated_max_days,
                actual_days,
                estimation_error,
                estimation_accuracy_pct,
                completed_at
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_category_accuracy(self) -> List[Dict]:
        """Get accuracy metrics grouped by category.

        Returns:
            List of category metrics with average accuracy
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                category,
                COUNT(*) as story_count,
                AVG(estimation_accuracy_pct) as avg_accuracy,
                AVG(actual_days) as avg_actual_days,
                AVG((estimated_min_days + estimated_max_days) / 2.0) as avg_estimated_days
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            GROUP BY category
            ORDER BY avg_accuracy DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "category": row[0],
                "story_count": row[1],
                "avg_accuracy_pct": round(row[2] or 0, 2),
                "avg_actual_days": round(row[3] or 0, 2),
                "avg_estimated_days": round(row[4] or 0, 2),
            }
            for row in rows
        ]

    def get_spec_comparison(self) -> Dict:
        """Compare accuracy for stories with vs without technical specs.

        Returns:
            Dictionary comparing spec vs no-spec metrics
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Stories with specs
        cursor.execute(
            """
            SELECT
                COUNT(*) as count,
                AVG(estimation_accuracy_pct) as avg_accuracy,
                AVG(actual_days) as avg_actual_days
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            AND has_technical_spec = 1
        """
        )
        with_spec = cursor.fetchone()

        # Stories without specs
        cursor.execute(
            """
            SELECT
                COUNT(*) as count,
                AVG(estimation_accuracy_pct) as avg_accuracy,
                AVG(actual_days) as avg_actual_days
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            AND has_technical_spec = 0
        """
        )
        without_spec = cursor.fetchone()

        conn.close()

        return {
            "with_spec": {
                "count": with_spec[0] or 0,
                "avg_accuracy_pct": round(with_spec[1] or 0, 2),
                "avg_actual_days": round(with_spec[2] or 0, 2),
            },
            "without_spec": {
                "count": without_spec[0] or 0,
                "avg_accuracy_pct": round(without_spec[1] or 0, 2),
                "avg_actual_days": round(without_spec[2] or 0, 2),
            },
        }

    def create_velocity_snapshot(self, period_start: datetime, period_end: datetime) -> int:
        """Create a velocity snapshot for a time period.

        Args:
            period_start: Start of period
            period_end: End of period

        Returns:
            Snapshot record ID
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get metrics for period
        cursor.execute(
            """
            SELECT
                COUNT(*) as story_count,
                SUM(story_points) as total_points,
                SUM(actual_days) as total_days,
                AVG(estimation_accuracy_pct) as avg_accuracy
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            AND completed_at >= ?
            AND completed_at < ?
        """,
            (period_start.isoformat(), period_end.isoformat()),
        )

        row = cursor.fetchone()
        story_count, total_points, total_days, avg_accuracy = row

        # Insert snapshot
        cursor.execute(
            """
            INSERT INTO velocity_snapshots (
                period_start,
                period_end,
                stories_completed,
                story_points_completed,
                total_days_actual,
                avg_estimation_accuracy_pct
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                period_start.isoformat(),
                period_end.isoformat(),
                story_count or 0,
                total_points or 0,
                total_days or 0,
                avg_accuracy or 0,
            ),
        )

        snapshot_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(
            f"Created velocity snapshot: {story_count} stories, " f"{total_points} points, {avg_accuracy:.1f}% accuracy"
        )

        return snapshot_id

    def get_suggested_estimate(
        self, category: str, complexity: str, has_technical_spec: bool = False
    ) -> Optional[Dict]:
        """Get suggested estimate based on historical data.

        Args:
            category: Story category
            complexity: Story complexity
            has_technical_spec: Whether story has technical spec

        Returns:
            Dictionary with suggested min/max days or None if no data
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                AVG(actual_days) as avg_days,
                MIN(actual_days) as min_days,
                MAX(actual_days) as max_days,
                COUNT(*) as sample_count
            FROM story_metrics
            WHERE completed_at IS NOT NULL
            AND category = ?
            AND complexity = ?
            AND has_technical_spec = ?
        """,
            (category, complexity, 1 if has_technical_spec else 0),
        )

        row = cursor.fetchone()
        conn.close()

        if not row or row[3] == 0:  # No historical data
            return None

        avg_days, min_days, max_days, sample_count = row

        # Calculate suggested range with buffer
        suggested_min = avg_days * 0.8
        suggested_max = avg_days * 1.2

        return {
            "suggested_min_days": round(suggested_min, 1),
            "suggested_max_days": round(suggested_max, 1),
            "based_on_samples": sample_count,
            "historical_avg": round(avg_days, 1),
            "historical_range": (round(min_days, 1), round(max_days, 1)),
        }
