"""Performance analysis and insights from LLM metrics.

⚠️ DEPRECATED: This module uses SQLAlchemy and is deprecated as of Sprint 5 (2025-10-09).
Use analyzer_sqlite.py instead for native sqlite3 implementation with zero external dependencies.
This file will be removed in a future version.

This module provides tools to analyze LLM performance, costs, and usage patterns
from the exported Langfuse data stored in the local database.

Example:
    Analyze LLM performance:
    >>> from coffee_maker.langfuse_observe.analytics import PerformanceAnalyzer
    >>>
    >>> analyzer = PerformanceAnalyzer("sqlite:///llm_metrics.db")
    >>> perf = analyzer.get_llm_performance(days=7, model="openai/gpt-4o")
    >>> print(f"Avg latency: {perf['avg_latency_ms']:.0f}ms")
    >>> print(f"P95 latency: {perf['p95_latency_ms']:.0f}ms")
    >>> print(f"Total cost: ${perf['total_cost_usd']:.2f}")

    Find expensive prompts:
    >>> expensive = analyzer.get_most_expensive_prompts(limit=10)
    >>> for prompt in expensive:
    ...     print(f"{prompt['input'][:50]}... - ${prompt['total_cost']:.4f}")

    Analyze by user:
    >>> user_stats = analyzer.get_usage_by_user(days=30)
    >>> for user_id, stats in user_stats.items():
    ...     print(f"{user_id}: {stats['total_requests']} requests, ${stats['total_cost']:.2f}")
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from langfuse import observe
from sqlalchemy import create_engine, func
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from coffee_maker.langfuse_observe.analytics.models import Generation, Trace
from coffee_maker.langfuse_observe.retry import with_retry

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze LLM performance metrics.

    This class provides methods to query and analyze LLM performance data
    including latency, cost, token usage, and error rates.

    Attributes:
        engine: SQLAlchemy engine
        Session: SQLAlchemy session factory

    Example:
        >>> analyzer = PerformanceAnalyzer("sqlite:///llm_metrics.db")
        >>> stats = analyzer.get_llm_performance(days=7)
    """

    def __init__(self, db_url: str):
        """Initialize analyzer with database URL.

        Args:
            db_url: SQLAlchemy database URL (e.g., "sqlite:///llm_metrics.db")
        """
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"PerformanceAnalyzer initialized with database: {db_url}")

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_llm_performance(self, days: int = 7, model: Optional[str] = None, user_id: Optional[str] = None) -> Dict:
        """Get LLM performance metrics.

        Calculates aggregated performance metrics including latency percentiles,
        token usage, costs, and error rates.

        Args:
            days: Number of days to analyze (default: 7)
            model: Filter by specific model (optional)
            user_id: Filter by specific user (optional)

        Returns:
            Dictionary with performance metrics:
            {
                "total_requests": int,
                "avg_latency_ms": float,
                "p50_latency_ms": float,
                "p95_latency_ms": float,
                "p99_latency_ms": float,
                "total_tokens": int,
                "avg_tokens_per_request": float,
                "total_cost_usd": float,
                "avg_cost_per_request": float,
                "error_count": int,
                "error_rate": float,
                "time_range": {"from": datetime, "to": datetime}
            }

        Example:
            >>> perf = analyzer.get_llm_performance(days=7, model="openai/gpt-4o")
            >>> print(f"Avg latency: {perf['avg_latency_ms']:.0f}ms")
        """
        with self.Session() as session:
            # Calculate time range
            to_timestamp = datetime.utcnow()
            from_timestamp = to_timestamp - timedelta(days=days)

            # Build query
            query = (
                session.query(Generation)
                .join(Trace)
                .filter(Generation.created_at >= from_timestamp, Generation.created_at <= to_timestamp)
            )

            if model:
                query = query.filter(Generation.model == model)

            if user_id:
                query = query.filter(Trace.user_id == user_id)

            generations = query.all()

            if not generations:
                return {
                    "total_requests": 0,
                    "avg_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "p99_latency_ms": 0,
                    "total_tokens": 0,
                    "avg_tokens_per_request": 0,
                    "total_cost_usd": 0,
                    "avg_cost_per_request": 0,
                    "error_count": 0,
                    "error_rate": 0,
                    "time_range": {"from": from_timestamp, "to": to_timestamp},
                }

            # Calculate metrics
            latencies = [g.latency_ms for g in generations if g.latency_ms is not None]
            latencies.sort()

            total_requests = len(generations)
            total_tokens = sum(g.total_tokens or 0 for g in generations)
            total_cost = sum(g.total_cost or 0 for g in generations)
            error_count = sum(1 for g in generations if g.level == "ERROR")

            return {
                "total_requests": total_requests,
                "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
                "p50_latency_ms": self._percentile(latencies, 50),
                "p95_latency_ms": self._percentile(latencies, 95),
                "p99_latency_ms": self._percentile(latencies, 99),
                "total_tokens": total_tokens,
                "avg_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
                "total_cost_usd": total_cost,
                "avg_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
                "error_count": error_count,
                "error_rate": error_count / total_requests if total_requests > 0 else 0,
                "time_range": {"from": from_timestamp, "to": to_timestamp},
            }

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_performance_by_model(self, days: int = 7) -> Dict[str, Dict]:
        """Get performance breakdown by model.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary mapping model names to performance metrics

        Example:
            >>> by_model = analyzer.get_performance_by_model(days=7)
            >>> for model, metrics in by_model.items():
            ...     print(f"{model}: {metrics['total_requests']} requests, ${metrics['total_cost_usd']:.2f}")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            # Get all models
            models = session.query(Generation.model).filter(Generation.created_at >= from_timestamp).distinct().all()

            results = {}
            for (model_name,) in models:
                if model_name:
                    results[model_name] = self.get_llm_performance(days=days, model=model_name)

            return results

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_most_expensive_prompts(self, limit: int = 10, days: int = 7) -> List[Dict]:
        """Get most expensive prompts by total cost.

        Args:
            limit: Maximum number of prompts to return
            days: Number of days to analyze

        Returns:
            List of dictionaries with prompt details:
            [
                {
                    "generation_id": str,
                    "model": str,
                    "input": str,
                    "total_cost": float,
                    "total_tokens": int,
                    "created_at": datetime
                },
                ...
            ]

        Example:
            >>> expensive = analyzer.get_most_expensive_prompts(limit=5)
            >>> for prompt in expensive:
            ...     print(f"{prompt['input'][:50]}... - ${prompt['total_cost']:.4f}")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            generations = (
                session.query(Generation)
                .filter(Generation.created_at >= from_timestamp, Generation.total_cost.isnot(None))
                .order_by(Generation.total_cost.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "generation_id": g.id,
                    "model": g.model,
                    "input": g.input[:500] if g.input else "",  # Truncate long inputs
                    "total_cost": g.total_cost,
                    "total_tokens": g.total_tokens,
                    "created_at": g.created_at,
                }
                for g in generations
            ]

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_slowest_requests(self, limit: int = 10, days: int = 7) -> List[Dict]:
        """Get slowest requests by latency.

        Args:
            limit: Maximum number of requests to return
            days: Number of days to analyze

        Returns:
            List of dictionaries with request details

        Example:
            >>> slow = analyzer.get_slowest_requests(limit=5)
            >>> for req in slow:
            ...     print(f"{req['model']}: {req['latency_ms']:.0f}ms")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            generations = (
                session.query(Generation)
                .filter(Generation.created_at >= from_timestamp, Generation.latency_ms.isnot(None))
                .order_by(Generation.latency_ms.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "generation_id": g.id,
                    "model": g.model,
                    "input": g.input[:500] if g.input else "",
                    "latency_ms": g.latency_ms,
                    "total_tokens": g.total_tokens,
                    "created_at": g.created_at,
                }
                for g in generations
            ]

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_usage_by_user(self, days: int = 30) -> Dict[str, Dict]:
        """Get usage statistics by user.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary mapping user_id to usage statistics

        Example:
            >>> by_user = analyzer.get_usage_by_user(days=30)
            >>> for user_id, stats in by_user.items():
            ...     print(f"{user_id}: {stats['total_requests']} requests")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            # Get all users
            users = (
                session.query(Trace.user_id)
                .join(Generation)
                .filter(Generation.created_at >= from_timestamp, Trace.user_id.isnot(None))
                .distinct()
                .all()
            )

            results = {}
            for (user_id,) in users:
                if user_id:
                    results[user_id] = self.get_llm_performance(days=days, user_id=user_id)

            return results

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_cost_over_time(self, days: int = 30, bucket_hours: int = 24, model: Optional[str] = None) -> List[Dict]:
        """Get cost trend over time.

        Args:
            days: Number of days to analyze
            bucket_hours: Time bucket size in hours (default: 24 = daily)
            model: Filter by specific model (optional)

        Returns:
            List of dictionaries with time-bucketed costs:
            [
                {
                    "time_bucket": datetime,
                    "total_cost": float,
                    "total_requests": int,
                    "total_tokens": int
                },
                ...
            ]

        Example:
            >>> daily_cost = analyzer.get_cost_over_time(days=30, bucket_hours=24)
            >>> for bucket in daily_cost:
            ...     print(f"{bucket['time_bucket'].date()}: ${bucket['total_cost']:.2f}")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            query = session.query(Generation).filter(Generation.created_at >= from_timestamp)

            if model:
                query = query.filter(Generation.model == model)

            generations = query.all()

            # Bucket by time
            bucket_size = timedelta(hours=bucket_hours)
            buckets = {}

            for gen in generations:
                # Calculate bucket
                bucket_time = gen.created_at - timedelta(
                    hours=gen.created_at.hour % bucket_hours,
                    minutes=gen.created_at.minute,
                    seconds=gen.created_at.second,
                )

                if bucket_time not in buckets:
                    buckets[bucket_time] = {
                        "time_bucket": bucket_time,
                        "total_cost": 0,
                        "total_requests": 0,
                        "total_tokens": 0,
                    }

                buckets[bucket_time]["total_cost"] += gen.total_cost or 0
                buckets[bucket_time]["total_requests"] += 1
                buckets[bucket_time]["total_tokens"] += gen.total_tokens or 0

            # Sort by time
            return sorted(buckets.values(), key=lambda x: x["time_bucket"])

    @observe
    @with_retry(
        max_attempts=3,
        backoff_base=1.5,
        retriable_exceptions=(OperationalError, TimeoutError),
    )
    def get_error_analysis(self, days: int = 7) -> Dict:
        """Analyze errors and failures.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with error analysis:
            {
                "total_errors": int,
                "error_rate": float,
                "errors_by_model": Dict[str, int],
                "common_error_messages": List[Dict]
            }

        Example:
            >>> errors = analyzer.get_error_analysis(days=7)
            >>> print(f"Error rate: {errors['error_rate']:.2%}")
        """
        with self.Session() as session:
            from_timestamp = datetime.utcnow() - timedelta(days=days)

            # Get all generations
            total_generations = (
                session.query(func.count(Generation.id)).filter(Generation.created_at >= from_timestamp).scalar()
            )

            # Get errors
            errors = (
                session.query(Generation)
                .filter(Generation.created_at >= from_timestamp, Generation.level == "ERROR")
                .all()
            )

            # Count by model
            errors_by_model = {}
            error_messages = {}

            for error in errors:
                # Count by model
                model = error.model or "unknown"
                errors_by_model[model] = errors_by_model.get(model, 0) + 1

                # Count error messages
                msg = error.status_message or "No message"
                if msg not in error_messages:
                    error_messages[msg] = {"message": msg, "count": 0, "example_id": error.id}
                error_messages[msg]["count"] += 1

            # Sort error messages by count
            common_errors = sorted(error_messages.values(), key=lambda x: x["count"], reverse=True)[:10]

            return {
                "total_errors": len(errors),
                "error_rate": len(errors) / total_generations if total_generations > 0 else 0,
                "errors_by_model": errors_by_model,
                "common_error_messages": common_errors,
            }

    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile from sorted values.

        Args:
            sorted_values: Sorted list of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0

        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
