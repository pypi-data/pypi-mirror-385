"""Performance analysis and insights from LLM metrics using native sqlite3.

This module provides tools to analyze LLM performance, costs, and usage patterns
from the exported Langfuse data stored in the local SQLite database.

Example:
    Analyze LLM performance:
    >>> from coffee_maker.langfuse_observe.analytics.analyzer_sqlite import PerformanceAnalyzer
    >>>
    >>> analyzer = PerformanceAnalyzer("llm_metrics.db")
    >>> perf = analyzer.get_llm_performance(days=7, model="openai/gpt-4o")
    >>> print(f"Avg latency: {perf['avg_latency_ms']:.0f}ms")
    >>> print(f"Total cost: ${perf['total_cost_usd']:.2f}")
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from coffee_maker.langfuse_observe.retry import with_retry

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze LLM performance metrics using native sqlite3.

    This class provides methods to query and analyze LLM performance data
    including latency, cost, token usage, and error rates.

    Attributes:
        db_path: Path to SQLite database
        conn: SQLite connection

    Example:
        >>> analyzer = PerformanceAnalyzer("llm_metrics.db")
        >>> stats = analyzer.get_llm_performance(days=7)
    """

    def __init__(self, db_path: str):
        """Initialize analyzer with database path.

        Args:
            db_path: Path to SQLite database file
        """
        # Remove sqlite:/// prefix if present
        self.db_path = db_path.replace("sqlite:///", "")
        self.conn = sqlite3.connect(self.db_path)
        # Enable row factory for dict-like access
        self.conn.row_factory = sqlite3.Row
        logger.info(f"PerformanceAnalyzer initialized with database: {self.db_path}")

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_llm_performance(
        self,
        days: int = 7,
        model: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, float]:
        """Get LLM performance metrics.

        Args:
            days: Number of days to analyze
            model: Filter by specific model (None = all models)
            user_id: Filter by specific user (None = all users)

        Returns:
            Dictionary with performance metrics

        Example:
            >>> perf = analyzer.get_llm_performance(days=7, model="openai/gpt-4o")
            >>> print(perf['avg_latency_ms'], perf['total_cost_usd'])
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        # Build query
        query = """
            SELECT
                COUNT(*) as total_requests,
                AVG(latency_ms) as avg_latency_ms,
                SUM(input_tokens) as total_input_tokens,
                SUM(output_tokens) as total_output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(total_cost) as total_cost_usd,
                AVG(total_cost) as avg_cost_per_request
            FROM generations
            WHERE created_at >= ?
        """

        params = [cutoff_str]

        if model:
            query += " AND model = ?"
            params.append(model)

        if user_id:
            query += """ AND trace_id IN (
                SELECT id FROM traces WHERE user_id = ?
            )"""
            params.append(user_id)

        cursor = self.conn.execute(query, params)
        row = cursor.fetchone()

        return {
            "total_requests": row["total_requests"] or 0,
            "avg_latency_ms": row["avg_latency_ms"] or 0.0,
            "total_input_tokens": row["total_input_tokens"] or 0,
            "total_output_tokens": row["total_output_tokens"] or 0,
            "total_tokens": row["total_tokens"] or 0,
            "total_cost_usd": row["total_cost_usd"] or 0.0,
            "avg_cost_per_request": row["avg_cost_per_request"] or 0.0,
        }

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_cost_over_time(
        self,
        days: int = 30,
        model: Optional[str] = None,
        granularity: str = "day",
    ) -> List[Dict]:
        """Get cost breakdown over time.

        Args:
            days: Number of days to analyze
            model: Filter by specific model
            granularity: Time granularity ('hour' or 'day')

        Returns:
            List of dicts with timestamp and cost

        Example:
            >>> costs = analyzer.get_cost_over_time(days=7, granularity='day')
            >>> for entry in costs:
            ...     print(f"{entry['date']}: ${entry['cost']:.2f}")
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        # SQLite date formatting
        if granularity == "hour":
            date_format = "strftime('%Y-%m-%d %H:00', created_at)"
        else:  # day
            date_format = "strftime('%Y-%m-%d', created_at)"

        query = f"""
            SELECT
                {date_format} as period,
                SUM(total_cost) as total_cost,
                COUNT(*) as request_count
            FROM generations
            WHERE created_at >= ?
        """

        params = [cutoff_str]

        if model:
            query += " AND model = ?"
            params.append(model)

        query += " GROUP BY period ORDER BY period"

        cursor = self.conn.execute(query, params)

        return [
            {
                "date": row["period"],
                "cost": row["total_cost"] or 0.0,
                "requests": row["request_count"] or 0,
            }
            for row in cursor.fetchall()
        ]

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_most_expensive_prompts(self, limit: int = 10, days: int = 30) -> List[Dict]:
        """Get most expensive prompts by total cost.

        Args:
            limit: Number of prompts to return
            days: Number of days to analyze

        Returns:
            List of expensive prompts with details

        Example:
            >>> expensive = analyzer.get_most_expensive_prompts(limit=5)
            >>> for prompt in expensive:
            ...     print(f"${prompt['total_cost']:.4f} - {prompt['model']}")
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        query = """
            SELECT
                id,
                model,
                input,
                output,
                total_cost,
                total_tokens,
                latency_ms,
                created_at
            FROM generations
            WHERE created_at >= ?
            ORDER BY total_cost DESC
            LIMIT ?
        """

        cursor = self.conn.execute(query, [cutoff_str, limit])

        return [dict(row) for row in cursor.fetchall()]

    @with_retry(max_attempts=3, retriable_exceptions=(sqlite3.OperationalError,))
    def get_model_comparison(self, days: int = 7) -> List[Dict]:
        """Compare performance across different models.

        Args:
            days: Number of days to analyze

        Returns:
            List of model statistics

        Example:
            >>> models = analyzer.get_model_comparison(days=7)
            >>> for m in models:
            ...     print(f"{m['model']}: {m['requests']} requests, ${m['total_cost']:.2f}")
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        query = """
            SELECT
                model,
                COUNT(*) as requests,
                AVG(latency_ms) as avg_latency_ms,
                SUM(total_cost) as total_cost,
                SUM(total_tokens) as total_tokens,
                AVG(total_cost) as avg_cost_per_request
            FROM generations
            WHERE created_at >= ? AND model IS NOT NULL
            GROUP BY model
            ORDER BY total_cost DESC
        """

        cursor = self.conn.execute(query, [cutoff_str])

        return [
            {
                "model": row["model"],
                "requests": row["requests"],
                "avg_latency_ms": row["avg_latency_ms"] or 0.0,
                "total_cost": row["total_cost"] or 0.0,
                "total_tokens": row["total_tokens"] or 0,
                "avg_cost_per_request": row["avg_cost_per_request"] or 0.0,
            }
            for row in cursor.fetchall()
        ]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
