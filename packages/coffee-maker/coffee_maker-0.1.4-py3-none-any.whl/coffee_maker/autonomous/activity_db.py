"""Activity tracking database for code_developer daemon.

This module provides comprehensive activity tracking for generating daily standups,
progress reports, and productivity metrics. All activities are logged to SQLite with
proper indexing and concurrent access handling (WAL mode).

Example:
    >>> db = ActivityDB()
    >>> db.log_activity(
    ...     activity_type=ACTIVITY_TYPE_COMMIT,
    ...     title="Implemented user authentication",
    ...     priority_number="2.5",
    ...     priority_name="CI Testing",
    ...     metadata={"files_changed": 5, "lines_added": 120}
    ... )
    >>> activities = db.get_activities(
    ...     start_date=date.today(),
    ...     end_date=date.today()
    ... )
"""

import json
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from coffee_maker.config import DATABASE_PATHS
from coffee_maker.langfuse_observe.retry import with_retry

# Activity types
ACTIVITY_TYPE_COMMIT = "commit"
ACTIVITY_TYPE_FILE_CHANGED = "file_changed"
ACTIVITY_TYPE_TEST_RUN = "test_run"
ACTIVITY_TYPE_PR_CREATED = "pr_created"
ACTIVITY_TYPE_BRANCH_CREATED = "branch_created"
ACTIVITY_TYPE_PRIORITY_STARTED = "priority_started"
ACTIVITY_TYPE_PRIORITY_COMPLETED = "priority_completed"
ACTIVITY_TYPE_ERROR_ENCOUNTERED = "error_encountered"
ACTIVITY_TYPE_DEPENDENCY_INSTALLED = "dependency_installed"
ACTIVITY_TYPE_DOCUMENTATION_UPDATED = "documentation_updated"

# Outcomes
OUTCOME_SUCCESS = "success"
OUTCOME_FAILURE = "failure"
OUTCOME_PARTIAL = "partial"
OUTCOME_BLOCKED = "blocked"

# Database schema SQL
CREATE_ACTIVITIES_TABLE = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    priority_number TEXT,
    priority_name TEXT,
    title TEXT NOT NULL,
    description TEXT,
    metadata TEXT,
    outcome TEXT NOT NULL DEFAULT 'success',
    created_at TEXT NOT NULL,
    session_id TEXT,
    CHECK(outcome IN ('success', 'failure', 'partial', 'blocked'))
);

CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(created_at);
CREATE INDEX IF NOT EXISTS idx_activities_priority ON activities(priority_number);
CREATE INDEX IF NOT EXISTS idx_activities_session ON activities(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_outcome ON activities(outcome);

CREATE TABLE IF NOT EXISTS daily_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    summary_text TEXT NOT NULL,
    metrics TEXT,
    generated_at TEXT NOT NULL,
    version INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_summaries_date ON daily_summaries(date);

CREATE TABLE IF NOT EXISTS activity_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    metadata TEXT,
    UNIQUE(date, activity_type)
);

CREATE INDEX IF NOT EXISTS idx_stats_date ON activity_stats(date);
CREATE INDEX IF NOT EXISTS idx_stats_type ON activity_stats(activity_type);
"""


@dataclass
class Activity:
    """Represents a single developer activity.

    Attributes:
        activity_type: Type of activity (use ACTIVITY_TYPE_* constants)
        title: Short description of the activity
        created_at: ISO 8601 timestamp when activity occurred
        description: Optional detailed description
        priority_number: Priority being worked on (e.g., "2.5")
        priority_name: Priority name (e.g., "CI Testing")
        metadata: Additional context as dict
        outcome: Activity outcome (success/failure/partial/blocked)
        session_id: Session ID to group related activities
        id: Database ID (set on retrieval)
    """

    activity_type: str
    title: str
    created_at: str
    description: Optional[str] = None
    priority_number: Optional[str] = None
    priority_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    outcome: str = OUTCOME_SUCCESS
    session_id: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class DailySummary:
    """Represents a daily standup summary.

    Attributes:
        date: ISO 8601 date string (YYYY-MM-DD)
        summary_text: Markdown-formatted summary text
        metrics: Dictionary of aggregated metrics
        activities: List of activities for the day
        generated_at: ISO 8601 timestamp when summary was generated
    """

    date: str
    summary_text: str
    metrics: Dict[str, Any]
    activities: List[Activity]
    generated_at: str


class ActivityDB:
    """Database for tracking all code_developer activities.

    This class provides comprehensive activity tracking for generating daily standups,
    progress reports, and productivity metrics. Uses SQLite with WAL mode for
    reliable concurrent access.

    Attributes:
        db_path: Path to the SQLite database file

    Example:
        >>> db = ActivityDB()
        >>> db.log_activity(
        ...     activity_type=ACTIVITY_TYPE_COMMIT,
        ...     title="Implemented feature X",
        ...     priority_number="2.5"
        ... )
        >>> activities = db.get_activities(activity_type=ACTIVITY_TYPE_COMMIT)
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize activity database.

        Args:
            db_path: Path to database file. Defaults to data/activity.db.

        Raises:
            OSError: If database directory cannot be created
        """
        if db_path is None:
            db_path = str(Path(DATABASE_PATHS["base"]) / "activity.db")

        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema with WAL mode for reliability."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")

        # Create schema
        conn.executescript(CREATE_ACTIVITIES_TABLE)
        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory.

        Returns:
            SQLite connection configured for row access

        Note:
            Connection should be closed after use via context manager
            or explicit close() call.
        """
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def log_activity(
        self,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        priority_number: Optional[str] = None,
        priority_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
        outcome: str = OUTCOME_SUCCESS,
        session_id: Optional[str] = None,
    ) -> int:
        """Log a developer activity.

        Args:
            activity_type: Type of activity (use ACTIVITY_TYPE_* constants)
            title: Short title (max 200 chars, e.g., "Fixed authentication bug")
            description: Detailed description
            priority_number: Priority being worked on (e.g., "2.5")
            priority_name: Priority name (e.g., "CI Testing")
            metadata: Additional context as dict
            outcome: Activity outcome (success/failure/partial/blocked)
            session_id: Session ID to group related activities

        Returns:
            Activity ID of the logged activity

        Raises:
            sqlite3.OperationalError: If database write fails after retries
            ValueError: If activity_type or outcome is invalid
        """
        # Validate inputs
        valid_types = {
            ACTIVITY_TYPE_COMMIT,
            ACTIVITY_TYPE_FILE_CHANGED,
            ACTIVITY_TYPE_TEST_RUN,
            ACTIVITY_TYPE_PR_CREATED,
            ACTIVITY_TYPE_BRANCH_CREATED,
            ACTIVITY_TYPE_PRIORITY_STARTED,
            ACTIVITY_TYPE_PRIORITY_COMPLETED,
            ACTIVITY_TYPE_ERROR_ENCOUNTERED,
            ACTIVITY_TYPE_DEPENDENCY_INSTALLED,
            ACTIVITY_TYPE_DOCUMENTATION_UPDATED,
        }

        if activity_type not in valid_types:
            raise ValueError(f"Invalid activity type: {activity_type}")

        valid_outcomes = {OUTCOME_SUCCESS, OUTCOME_FAILURE, OUTCOME_PARTIAL, OUTCOME_BLOCKED}
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome: {outcome}")

        # Truncate title if needed
        if len(title) > 200:
            title = title[:200]

        now = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO activities
                (activity_type, priority_number, priority_name, title,
                 description, metadata, outcome, created_at, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    activity_type,
                    priority_number,
                    priority_name,
                    title,
                    description,
                    metadata_json,
                    outcome,
                    now,
                    session_id,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_activities(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        activity_type: Optional[str] = None,
        priority_number: Optional[str] = None,
        limit: int = 100,
    ) -> List[Activity]:
        """Get activities with optional filtering.

        Args:
            start_date: Start date (inclusive). Defaults to None (no lower bound)
            end_date: End date (inclusive). Defaults to None (no upper bound)
            activity_type: Filter by activity type. Defaults to None (no filter)
            priority_number: Filter by priority. Defaults to None (no filter)
            limit: Max results to return. Defaults to 100

        Returns:
            List of Activity objects matching the criteria, ordered by most recent first

        Example:
            >>> yesterday = date.today() - timedelta(days=1)
            >>> activities = db.get_activities(
            ...     start_date=yesterday,
            ...     end_date=yesterday,
            ...     activity_type=ACTIVITY_TYPE_COMMIT
            ... )
        """
        query = "SELECT * FROM activities WHERE 1=1"
        params = []

        if start_date:
            query += " AND date(created_at) >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND date(created_at) <= ?"
            params.append(end_date.isoformat())

        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)

        if priority_number:
            query += " AND priority_number = ?"
            params.append(priority_number)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        return [self._row_to_activity(row) for row in rows]

    def get_activity(self, activity_id: int) -> Optional[Activity]:
        """Get a single activity by ID.

        Args:
            activity_id: ID of the activity to retrieve

        Returns:
            Activity object if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
            row = cursor.fetchone()

        return self._row_to_activity(row) if row else None

    def get_daily_metrics(self, target_date: date) -> Dict[str, Any]:
        """Get aggregated metrics for a specific day.

        Args:
            target_date: Date to get metrics for

        Returns:
            Dictionary with metrics like {commits: 5, tests_passed: 42, ...}
        """
        date_str = target_date.isoformat()
        query = """
            SELECT
                COUNT(*) as total_activities,
                SUM(CASE WHEN activity_type = ? THEN 1 ELSE 0 END) as commits,
                SUM(CASE WHEN activity_type = ? THEN 1 ELSE 0 END) as test_runs,
                SUM(CASE WHEN activity_type = ? THEN 1 ELSE 0 END) as prs_created,
                SUM(CASE WHEN activity_type = ? THEN 1 ELSE 0 END) as priorities_completed,
                SUM(CASE WHEN outcome = ? THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN outcome = ? THEN 1 ELSE 0 END) as failures
            FROM activities
            WHERE date(created_at) = ?
        """

        with self._get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    ACTIVITY_TYPE_COMMIT,
                    ACTIVITY_TYPE_TEST_RUN,
                    ACTIVITY_TYPE_PR_CREATED,
                    ACTIVITY_TYPE_PRIORITY_COMPLETED,
                    OUTCOME_SUCCESS,
                    OUTCOME_FAILURE,
                    date_str,
                ),
            )
            row = cursor.fetchone()

        if not row:
            return {
                "total_activities": 0,
                "commits": 0,
                "test_runs": 0,
                "prs_created": 0,
                "priorities_completed": 0,
                "successes": 0,
                "failures": 0,
            }

        return {
            "total_activities": row[0] or 0,
            "commits": row[1] or 0,
            "test_runs": row[2] or 0,
            "prs_created": row[3] or 0,
            "priorities_completed": row[4] or 0,
            "successes": row[5] or 0,
            "failures": row[6] or 0,
        }

    def _row_to_activity(self, row: sqlite3.Row) -> Activity:
        """Convert database row to Activity object.

        Args:
            row: SQLite row from query

        Returns:
            Activity object
        """
        data = dict(row)
        if data.get("metadata"):
            data["metadata"] = json.loads(data["metadata"])
        return Activity(**data)
