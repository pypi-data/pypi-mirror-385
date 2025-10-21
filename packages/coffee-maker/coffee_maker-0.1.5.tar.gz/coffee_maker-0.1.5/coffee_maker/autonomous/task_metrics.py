"""Task Metrics Database - Store and analyze subtask performance metrics.

This module provides a SQLite-based storage system for tracking subtask
execution times, comparing them with estimates, and learning from historical
data to improve future estimations.

Example:
    >>> metrics = TaskMetricsDB()
    >>> metrics.record_subtask(
    ...     priority_name="PRIORITY 9",
    ...     subtask_name="Creating feature branch",
    ...     estimated_seconds=10,
    ...     actual_seconds=8,
    ...     status="completed"
    ... )
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskMetricsDB:
    """Database for storing and analyzing task performance metrics.

    This class manages a SQLite database that tracks:
    - Subtask execution times (actual vs estimated)
    - Success/failure rates
    - Performance trends over time
    - Priority-specific metrics

    Attributes:
        db_path: Path to SQLite database file
        conn: Database connection

    Example:
        >>> metrics = TaskMetricsDB()
        >>> metrics.record_subtask(
        ...     priority_name="PRIORITY 9",
        ...     subtask_name="Executing Claude API",
        ...     estimated_seconds=300,
        ...     actual_seconds=245,
        ...     status="completed"
        ... )
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize metrics database.

        Args:
            db_path: Optional custom database path.
                    Defaults to ~/.coffee_maker/task_metrics.db
        """
        if db_path is None:
            db_path = Path.home() / ".coffee_maker" / "task_metrics.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"TaskMetricsDB initialized at {self.db_path}")

    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Create subtask_metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subtask_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                priority_name TEXT NOT NULL,
                priority_title TEXT,
                subtask_name TEXT NOT NULL,
                estimated_seconds INTEGER NOT NULL,
                actual_seconds INTEGER NOT NULL,
                status TEXT NOT NULL,
                deviation_seconds INTEGER,
                deviation_percent REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create index for faster queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_subtask_name
            ON subtask_metrics(subtask_name)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_priority_name
            ON subtask_metrics(priority_name)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON subtask_metrics(timestamp)
        """
        )

        conn.commit()
        conn.close()

        logger.debug("Database schema initialized")

    def record_subtask(
        self,
        priority_name: str,
        subtask_name: str,
        estimated_seconds: int,
        actual_seconds: int,
        status: str,
        priority_title: str = None,
    ) -> int:
        """Record a subtask execution metric.

        Args:
            priority_name: Name of the priority (e.g., "PRIORITY 9")
            subtask_name: Name of the subtask (e.g., "Creating feature branch")
            estimated_seconds: Estimated duration in seconds
            actual_seconds: Actual duration in seconds
            status: Status of subtask ("completed", "failed", "in_progress")
            priority_title: Optional title of the priority

        Returns:
            ID of the inserted record

        Example:
            >>> metrics.record_subtask(
            ...     priority_name="PRIORITY 9",
            ...     subtask_name="Pushing to remote",
            ...     estimated_seconds=30,
            ...     actual_seconds=25,
            ...     status="completed",
            ...     priority_title="Enhanced Communication"
            ... )
            42
        """
        # Calculate deviation
        deviation_seconds = actual_seconds - estimated_seconds
        deviation_percent = (deviation_seconds / estimated_seconds * 100) if estimated_seconds > 0 else 0

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO subtask_metrics (
                timestamp,
                priority_name,
                priority_title,
                subtask_name,
                estimated_seconds,
                actual_seconds,
                status,
                deviation_seconds,
                deviation_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                priority_name,
                priority_title,
                subtask_name,
                estimated_seconds,
                actual_seconds,
                status,
                deviation_seconds,
                deviation_percent,
            ),
        )

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(
            f"Recorded metric: {subtask_name} - {actual_seconds}s vs {estimated_seconds}s "
            f"({deviation_percent:+.1f}%)"
        )

        return record_id

    def get_average_duration(self, subtask_name: str, limit: int = 10) -> Optional[float]:
        """Get average actual duration for a subtask based on historical data.

        Args:
            subtask_name: Name of the subtask
            limit: Number of recent records to consider (default: 10)

        Returns:
            Average duration in seconds, or None if no data

        Example:
            >>> avg = metrics.get_average_duration("Executing Claude API", limit=5)
            >>> print(f"Average: {avg}s")
            Average: 278.4s
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT AVG(actual_seconds)
            FROM (
                SELECT actual_seconds
                FROM subtask_metrics
                WHERE subtask_name = ? AND status = 'completed'
                ORDER BY timestamp DESC
                LIMIT ?
            )
        """,
            (subtask_name, limit),
        )

        result = cursor.fetchone()
        conn.close()

        return result[0] if result and result[0] is not None else None

    def get_suggested_estimate(self, subtask_name: str) -> Optional[int]:
        """Get suggested estimate for a subtask based on historical performance.

        Uses average of recent successful completions, with a 20% buffer.

        Args:
            subtask_name: Name of the subtask

        Returns:
            Suggested estimate in seconds, or None if no historical data

        Example:
            >>> estimate = metrics.get_suggested_estimate("Committing changes")
            >>> print(f"Suggested: {estimate}s")
            Suggested: 24s
        """
        avg = self.get_average_duration(subtask_name, limit=10)

        if avg is None:
            return None

        # Add 20% buffer to average
        suggested = int(avg * 1.2)

        return suggested

    def get_subtask_statistics(self, subtask_name: str) -> Dict:
        """Get comprehensive statistics for a subtask.

        Args:
            subtask_name: Name of the subtask

        Returns:
            Dictionary with statistics:
            - count: Total number of executions
            - avg_actual: Average actual duration
            - avg_estimated: Average estimated duration
            - avg_deviation_percent: Average deviation percentage
            - success_rate: Percentage of successful completions

        Example:
            >>> stats = metrics.get_subtask_statistics("Executing Claude API")
            >>> print(f"Success rate: {stats['success_rate']}%")
            Success rate: 95.2%
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) as count,
                AVG(actual_seconds) as avg_actual,
                AVG(estimated_seconds) as avg_estimated,
                AVG(deviation_percent) as avg_deviation_percent,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM subtask_metrics
            WHERE subtask_name = ?
        """,
            (subtask_name,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row or row[0] == 0:
            return {
                "count": 0,
                "avg_actual": 0,
                "avg_estimated": 0,
                "avg_deviation_percent": 0,
                "success_rate": 0,
            }

        return {
            "count": row[0],
            "avg_actual": row[1] or 0,
            "avg_estimated": row[2] or 0,
            "avg_deviation_percent": row[3] or 0,
            "success_rate": row[4] or 0,
        }

    def get_all_subtask_stats(self) -> List[Dict]:
        """Get statistics for all subtasks.

        Returns:
            List of dictionaries with subtask statistics

        Example:
            >>> all_stats = metrics.get_all_subtask_stats()
            >>> for stat in all_stats:
            ...     print(f"{stat['subtask_name']}: {stat['count']} executions")
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                subtask_name,
                COUNT(*) as count,
                AVG(actual_seconds) as avg_actual,
                AVG(estimated_seconds) as avg_estimated,
                AVG(deviation_percent) as avg_deviation_percent,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM subtask_metrics
            GROUP BY subtask_name
            ORDER BY count DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "subtask_name": row[0],
                "count": row[1],
                "avg_actual": row[2] or 0,
                "avg_estimated": row[3] or 0,
                "avg_deviation_percent": row[4] or 0,
                "success_rate": row[5] or 0,
            }
            for row in rows
        ]

    def get_priority_metrics(self, priority_name: str) -> Dict:
        """Get metrics for a specific priority.

        Args:
            priority_name: Name of the priority

        Returns:
            Dictionary with priority-level metrics

        Example:
            >>> metrics.get_priority_metrics("PRIORITY 9")
            {'total_time': 365, 'subtask_count': 5, ...}
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                SUM(actual_seconds) as total_time,
                COUNT(*) as subtask_count,
                AVG(deviation_percent) as avg_deviation_percent
            FROM subtask_metrics
            WHERE priority_name = ?
        """,
            (priority_name,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row or row[1] == 0:
            return {"total_time": 0, "subtask_count": 0, "avg_deviation_percent": 0}

        return {
            "total_time": row[0] or 0,
            "subtask_count": row[1],
            "avg_deviation_percent": row[2] or 0,
        }
