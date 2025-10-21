"""Export Langfuse traces to local SQLite database for analytics.

This module provides the LangfuseExporter class which fetches traces from
Langfuse and stores them in a local SQLite database using native sqlite3
(no SQLAlchemy dependency).

Example:
    One-time export:
    >>> from coffee_maker.langfuse_observe.analytics.exporter_sqlite import LangfuseExporter
    >>> from coffee_maker.langfuse_observe.analytics.config import ExportConfig
    >>>
    >>> config = ExportConfig.from_env()
    >>> exporter = LangfuseExporter(config)
    >>> exporter.setup_database()
    >>> stats = exporter.export_traces(lookback_hours=24)
    >>> print(f"Exported {stats['generations']} generations from {stats['traces']} traces")
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from langfuse import Langfuse

from coffee_maker.langfuse_observe.analytics.config import ExportConfig
from coffee_maker.langfuse_observe.analytics.models_sqlite import (
    Generation,
    Span,
    Trace,
    init_database,
    insert_generation,
    insert_span,
    insert_trace,
)
from coffee_maker.langfuse_observe.retry import with_retry

logger = logging.getLogger(__name__)


class LangfuseExporter:
    """Export Langfuse traces to local SQLite database.

    This class handles:
    - Fetching traces from Langfuse API
    - Converting Langfuse data to dataclass models
    - Storing traces, generations, and spans in local database
    - Incremental sync to avoid re-exporting data

    Attributes:
        config: Export configuration
        langfuse: Langfuse client
        conn: SQLite database connection

    Example:
        >>> config = ExportConfig.from_env()
        >>> exporter = LangfuseExporter(config)
        >>> exporter.setup_database()
        >>> stats = exporter.export_traces()
    """

    def __init__(self, config: ExportConfig):
        """Initialize exporter with configuration.

        Args:
            config: Export configuration with Langfuse credentials and DB settings
        """
        self.config = config

        # Initialize Langfuse client
        self.langfuse = Langfuse(
            public_key=config.langfuse_public_key,
            secret_key=config.langfuse_secret_key,
            host=config.langfuse_host,
        )

        # Database connection (will be initialized in setup_database)
        self.conn: Optional[sqlite3.Connection] = None
        self.db_path = config.db_url.replace("sqlite:///", "")

        logger.info(f"LangfuseExporter initialized with database: {self.db_path}")

    def setup_database(self):
        """Create database tables if they don't exist."""
        self.conn = init_database(self.db_path)
        logger.info("Database schema initialized")

    @with_retry(max_attempts=3, backoff_base=2.0)
    def export_traces(
        self,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        lookback_hours: int = 24,
        limit: Optional[int] = None,
    ) -> Dict[str, int]:
        """Export traces from Langfuse to local database.

        Args:
            from_timestamp: Start time for export (defaults to lookback_hours ago)
            to_timestamp: End time for export (defaults to now)
            lookback_hours: Hours to look back if from_timestamp not provided
            limit: Maximum number of traces to export (None = all)

        Returns:
            Dict with export statistics (traces, generations, spans exported)

        Example:
            >>> stats = exporter.export_traces(lookback_hours=48)
            >>> print(f"Exported {stats['traces']} traces")
        """
        if not self.conn:
            self.setup_database()

        # Set time range
        if to_timestamp is None:
            to_timestamp = datetime.utcnow()
        if from_timestamp is None:
            from_timestamp = to_timestamp - timedelta(hours=lookback_hours)

        logger.info(f"Exporting traces from {from_timestamp} to {to_timestamp}")

        # Fetch traces from Langfuse
        traces = self._fetch_traces_from_langfuse(from_timestamp, to_timestamp)

        if limit:
            traces = traces[:limit]

        logger.info(f"Found {len(traces)} traces to export")

        # Export each trace
        stats = {"traces": 0, "generations": 0, "spans": 0, "errors": 0}

        for trace_data in traces:
            try:
                self._export_trace(trace_data)
                stats["traces"] += 1

                # Export observations (generations and spans)
                trace_id = trace_data.get("id")
                if trace_id:
                    gen_count, span_count = self._export_observations(trace_id)
                    stats["generations"] += gen_count
                    stats["spans"] += span_count

            except Exception as e:
                logger.error(f"Error exporting trace {trace_data.get('id')}: {e}")
                stats["errors"] += 1

        logger.info(
            f"Export complete: {stats['traces']} traces, " f"{stats['generations']} generations, {stats['spans']} spans"
        )

        return stats

    def _fetch_traces_from_langfuse(self, from_timestamp: datetime, to_timestamp: datetime) -> List[Dict]:
        """Fetch traces from Langfuse API.

        Args:
            from_timestamp: Start time
            to_timestamp: End time

        Returns:
            List of trace dictionaries from Langfuse
        """
        try:
            # Fetch traces using Langfuse client
            traces = self.langfuse.get_traces(
                from_timestamp=from_timestamp.isoformat(),
                to_timestamp=to_timestamp.isoformat(),
            )
            return traces.data if hasattr(traces, "data") else []
        except Exception as e:
            logger.error(f"Error fetching traces from Langfuse: {e}")
            return []

    def _export_trace(self, trace_data: Dict):
        """Export a single trace to database.

        Args:
            trace_data: Trace dictionary from Langfuse
        """
        trace = Trace(
            id=trace_data.get("id"),
            name=trace_data.get("name"),
            user_id=trace_data.get("userId"),
            session_id=trace_data.get("sessionId"),
            trace_metadata=trace_data.get("metadata"),
            input=trace_data.get("input"),
            output=trace_data.get("output"),
            created_at=self._parse_timestamp(trace_data.get("timestamp")),
            updated_at=self._parse_timestamp(trace_data.get("updatedAt")),
            release=trace_data.get("release"),
            tags=trace_data.get("tags"),
        )

        insert_trace(self.conn, trace)

    def _export_observations(self, trace_id: str) -> tuple[int, int]:
        """Export observations (generations and spans) for a trace.

        Args:
            trace_id: Trace ID

        Returns:
            Tuple of (generation_count, span_count)
        """
        gen_count = 0
        span_count = 0

        try:
            # Fetch observations from Langfuse
            observations = self.langfuse.get_observations(trace_id=trace_id)
            obs_data = observations.data if hasattr(observations, "data") else []

            for obs in obs_data:
                obs_type = obs.get("type", "").lower()

                if obs_type == "generation":
                    self._export_generation(trace_id, obs)
                    gen_count += 1
                elif obs_type == "span":
                    self._export_span(trace_id, obs)
                    span_count += 1

        except Exception as e:
            logger.error(f"Error exporting observations for trace {trace_id}: {e}")

        return gen_count, span_count

    def _export_generation(self, trace_id: str, gen_data: Dict):
        """Export a generation to database.

        Args:
            trace_id: Parent trace ID
            gen_data: Generation dictionary from Langfuse
        """
        # Extract usage/cost data
        usage = gen_data.get("usage", {}) or {}
        model_params = gen_data.get("modelParameters", {})

        generation = Generation(
            id=gen_data.get("id"),
            trace_id=trace_id,
            name=gen_data.get("name"),
            model=gen_data.get("model"),
            model_parameters=model_params if model_params else None,
            input=gen_data.get("input"),
            output=gen_data.get("output"),
            input_tokens=usage.get("input", 0) or usage.get("promptTokens", 0) or 0,
            output_tokens=usage.get("output", 0) or usage.get("completionTokens", 0) or 0,
            total_tokens=usage.get("total", 0) or usage.get("totalTokens", 0) or 0,
            input_cost=gen_data.get("calculatedInputCost", 0.0) or 0.0,
            output_cost=gen_data.get("calculatedOutputCost", 0.0) or 0.0,
            total_cost=gen_data.get("calculatedTotalCost", 0.0) or 0.0,
            latency_ms=gen_data.get("latency"),
            created_at=self._parse_timestamp(gen_data.get("startTime")),
            updated_at=self._parse_timestamp(gen_data.get("updatedAt")),
            metadata=gen_data.get("metadata"),
            level=gen_data.get("level", "DEFAULT"),
            status_message=gen_data.get("statusMessage"),
            completion_start_time=self._parse_timestamp(gen_data.get("completionStartTime")),
            completion_end_time=self._parse_timestamp(gen_data.get("endTime")),
        )

        insert_generation(self.conn, generation)

    def _export_span(self, trace_id: str, span_data: Dict):
        """Export a span to database.

        Args:
            trace_id: Parent trace ID
            span_data: Span dictionary from Langfuse
        """
        span = Span(
            id=span_data.get("id"),
            trace_id=trace_id,
            name=span_data.get("name"),
            start_time=self._parse_timestamp(span_data.get("startTime")),
            end_time=self._parse_timestamp(span_data.get("endTime")),
            input=span_data.get("input"),
            output=span_data.get("output"),
            metadata=span_data.get("metadata"),
            level=span_data.get("level", "DEFAULT"),
            status_message=span_data.get("statusMessage"),
        )

        insert_span(self.conn, span)

    def _parse_timestamp(self, ts_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime.

        Args:
            ts_str: ISO format timestamp string

        Returns:
            datetime object or None
        """
        if not ts_str:
            return None

        try:
            # Handle ISO format with timezone
            if "T" in ts_str:
                # Remove timezone info for simplicity
                ts_str = ts_str.split("+")[0].split("Z")[0]
            return datetime.fromisoformat(ts_str)
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse timestamp: {ts_str}")
            return None

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
