"""Export Langfuse traces to local database for analytics.

⚠️ DEPRECATED: This module uses SQLAlchemy and is deprecated as of Sprint 5 (2025-10-09).
Use exporter_sqlite.py instead for native sqlite3 implementation with zero external dependencies.
This file will be removed in a future version.

This module provides the LangfuseExporter class which fetches traces from
Langfuse and stores them in a local SQLite or PostgreSQL database for
offline analysis, reporting, and visualization.

Example:
    One-time export:
    >>> from coffee_maker.langfuse_observe.analytics import LangfuseExporter
    >>> from coffee_maker.langfuse_observe.analytics.config import ExportConfig
    >>>
    >>> config = ExportConfig.from_env()
    >>> exporter = LangfuseExporter(config)
    >>> exporter.setup_database()
    >>> stats = exporter.export_traces(lookback_hours=24)
    >>> print(f"Exported {stats['generations']} generations from {stats['traces']} traces")

    Continuous export (daemon mode):
    >>> exporter.start_continuous_export(interval_minutes=30)
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from langfuse import Langfuse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from coffee_maker.langfuse_observe.analytics.config import ExportConfig
from coffee_maker.langfuse_observe.analytics.models import Base, Generation, Span, Trace
from coffee_maker.langfuse_observe.retry import RetryExhausted, with_retry

logger = logging.getLogger(__name__)


class LangfuseExporter:
    """Export Langfuse traces to local database.

    This class handles:
    - Fetching traces from Langfuse API
    - Converting Langfuse data to SQLAlchemy models
    - Storing traces, generations, and spans in local database
    - Incremental sync to avoid re-exporting data
    - Continuous export mode for real-time analytics

    Attributes:
        config: Export configuration
        langfuse: Langfuse client
        engine: SQLAlchemy engine
        Session: SQLAlchemy session factory

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

        # Initialize database
        self.engine = create_engine(config.db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

        logger.info(f"LangfuseExporter initialized with database: {config.db_url}")

    def setup_database(self):
        """Create database tables if they don't exist.

        This creates all tables defined in models.py using SQLAlchemy's
        metadata.create_all(), which is idempotent (safe to call multiple times).

        Example:
            >>> exporter = LangfuseExporter(config)
            >>> exporter.setup_database()
        """
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created/verified")

    def export_traces(
        self,
        lookback_hours: Optional[int] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Export traces from Langfuse to local database.

        Fetches traces from Langfuse within the specified time range and
        stores them in the local database. Handles upserts to avoid duplicates.

        Args:
            lookback_hours: Export traces from last N hours (default: from config)
            from_timestamp: Start of time range (overrides lookback_hours)
            to_timestamp: End of time range (default: now)

        Returns:
            Dictionary with export statistics:
            {
                "traces": int,  # Number of traces exported
                "generations": int,  # Number of generations exported
                "spans": int,  # Number of spans exported
                "errors": int,  # Number of errors encountered
            }

        Example:
            >>> # Export last 24 hours
            >>> stats = exporter.export_traces(lookback_hours=24)
            >>>
            >>> # Export specific date range
            >>> from datetime import datetime
            >>> stats = exporter.export_traces(
            ...     from_timestamp=datetime(2025, 1, 1),
            ...     to_timestamp=datetime(2025, 1, 7)
            ... )
        """
        # Calculate time range
        if from_timestamp is None:
            hours = lookback_hours or self.config.lookback_hours
            from_timestamp = datetime.utcnow() - timedelta(hours=hours)

        if to_timestamp is None:
            to_timestamp = datetime.utcnow()

        logger.info(f"Exporting traces from {from_timestamp} to {to_timestamp}")

        stats = {"traces": 0, "generations": 0, "spans": 0, "errors": 0}

        try:
            # Fetch traces from Langfuse with automatic retry
            # Will retry up to 3 times on network failures
            traces_list = self._fetch_traces_from_langfuse(from_timestamp, to_timestamp)

            with self.Session() as session:
                for trace_data in traces_list:
                    try:
                        self._export_trace(session, trace_data)
                        stats["traces"] += 1
                    except RetryExhausted as e:
                        logger.error(
                            f"Failed to export trace {trace_data.get('id')} after all retries: {e.original_error}"
                        )
                        stats["errors"] += 1
                    except Exception as e:
                        logger.error(f"Error exporting trace {trace_data.get('id')}: {e}")
                        stats["errors"] += 1

                session.commit()

            # Get generation and span counts
            with self.Session() as session:
                stats["generations"] = session.query(Generation).count()
                stats["spans"] = session.query(Span).count()

            logger.info(
                f"Export complete: {stats['traces']} traces, "
                f"{stats['generations']} generations, "
                f"{stats['spans']} spans, "
                f"{stats['errors']} errors"
            )

        except RetryExhausted as e:
            logger.error(f"Export failed after all retries: {e.original_error}")
            stats["errors"] += 1
        except Exception as e:
            logger.error(f"Export failed: {e}")
            stats["errors"] += 1

        return stats

    @with_retry(
        max_attempts=3,
        backoff_base=2.0,
        retriable_exceptions=(ConnectionError, TimeoutError, Exception),
    )
    def _fetch_traces_from_langfuse(self, from_timestamp: datetime, to_timestamp: datetime) -> List[Dict]:
        """Fetch traces from Langfuse API with automatic retry on failures.

        This method is wrapped with retry logic to handle transient network failures
        when communicating with the Langfuse API. Will retry up to 3 times with
        exponential backoff (1s, 2s, 4s).

        Args:
            from_timestamp: Start of time range
            to_timestamp: End of time range

        Returns:
            List of trace dictionaries from Langfuse

        Raises:
            RetryExhausted: If all retry attempts fail after network errors
        """
        logger.debug(f"Fetching traces from Langfuse: {from_timestamp.isoformat()} to {to_timestamp.isoformat()}")

        # Fetch traces using Langfuse client
        # The Langfuse client handles pagination automatically
        trace_list = self.langfuse.get_traces(
            from_timestamp=from_timestamp.isoformat(),
            to_timestamp=to_timestamp.isoformat(),
            limit=self.config.export_batch_size,
        )

        traces = [trace.dict() for trace in trace_list.data]

        logger.info(f"Successfully fetched {len(traces)} traces from Langfuse")
        return traces

    def _export_trace(self, session: Session, trace_data: Dict):
        """Export a single trace with its generations and spans.

        Args:
            session: SQLAlchemy session
            trace_data: Trace data from Langfuse
        """
        trace_id = trace_data.get("id")

        # Upsert trace
        trace = session.query(Trace).filter_by(id=trace_id).first()
        if trace is None:
            trace = Trace(
                id=trace_id,
                name=trace_data.get("name"),
                user_id=trace_data.get("userId"),
                session_id=trace_data.get("sessionId"),
                trace_metadata=trace_data.get("metadata"),
                input=trace_data.get("input"),
                output=trace_data.get("output"),
                created_at=self._parse_timestamp(trace_data.get("timestamp")),
                release=trace_data.get("release"),
                tags=trace_data.get("tags"),
            )
            session.add(trace)
        else:
            # Update existing trace
            trace.name = trace_data.get("name") or trace.name
            trace.trace_metadata = trace_data.get("metadata") or trace.trace_metadata
            trace.output = trace_data.get("output") or trace.output
            trace.updated_at = datetime.utcnow()

        # Fetch and export observations (generations and spans)
        self._export_observations(session, trace_id)

    def _export_observations(self, session: Session, trace_id: str):
        """Export generations and spans for a trace.

        Args:
            session: SQLAlchemy session
            trace_id: Trace ID
        """
        # Fetch observations from Langfuse with retry
        trace = self._fetch_trace_details(trace_id)

        # Export generations and spans
        for obs in trace.observations:
            if obs.type == "GENERATION":
                self._export_generation(session, trace_id, obs.dict())
            elif obs.type == "SPAN":
                self._export_span(session, trace_id, obs.dict())

    @with_retry(
        max_attempts=3,
        backoff_base=2.0,
        retriable_exceptions=(ConnectionError, TimeoutError, Exception),
    )
    def _fetch_trace_details(self, trace_id: str):
        """Fetch detailed trace information from Langfuse with retry.

        Args:
            trace_id: Trace ID to fetch

        Returns:
            Trace object with observations

        Raises:
            RetryExhausted: If all retry attempts fail
        """
        logger.debug(f"Fetching trace details for {trace_id}")
        trace = self.langfuse.get_trace(trace_id)
        logger.debug(f"Successfully fetched trace {trace_id} with {len(trace.observations)} observations")
        return trace

    def _export_generation(self, session: Session, trace_id: str, gen_data: Dict):
        """Export a single generation.

        Args:
            session: SQLAlchemy session
            trace_id: Parent trace ID
            gen_data: Generation data from Langfuse
        """
        gen_id = gen_data.get("id")

        # Calculate latency if timestamps available
        latency_ms = None
        start_time = self._parse_timestamp(gen_data.get("startTime"))
        end_time = self._parse_timestamp(gen_data.get("endTime"))
        if start_time and end_time:
            latency_ms = (end_time - start_time).total_seconds() * 1000

        # Upsert generation
        generation = session.query(Generation).filter_by(id=gen_id).first()
        if generation is None:
            usage = gen_data.get("usage", {}) or {}
            generation = Generation(
                id=gen_id,
                trace_id=trace_id,
                name=gen_data.get("name"),
                model=gen_data.get("model"),
                model_parameters=gen_data.get("modelParameters"),
                input=str(gen_data.get("input")),
                output=str(gen_data.get("output")),
                input_tokens=usage.get("input"),
                output_tokens=usage.get("output"),
                total_tokens=usage.get("total"),
                input_cost=gen_data.get("inputCost"),
                output_cost=gen_data.get("outputCost"),
                total_cost=gen_data.get("totalCost"),
                latency_ms=latency_ms,
                created_at=self._parse_timestamp(gen_data.get("timestamp")),
                completion_start_time=start_time,
                completion_end_time=end_time,
                generation_metadata=gen_data.get("metadata"),
                level=gen_data.get("level"),
                status_message=gen_data.get("statusMessage"),
            )
            session.add(generation)

    def _export_span(self, session: Session, trace_id: str, span_data: Dict):
        """Export a single span.

        Args:
            session: SQLAlchemy session
            trace_id: Parent trace ID
            span_data: Span data from Langfuse
        """
        span_id = span_data.get("id")

        # Upsert span
        span = session.query(Span).filter_by(id=span_id).first()
        if span is None:
            span = Span(
                id=span_id,
                trace_id=trace_id,
                parent_observation_id=span_data.get("parentObservationId"),
                name=span_data.get("name"),
                input=span_data.get("input"),
                output=span_data.get("output"),
                span_metadata=span_data.get("metadata"),
                level=span_data.get("level"),
                status_message=span_data.get("statusMessage"),
                created_at=self._parse_timestamp(span_data.get("timestamp")),
                start_time=self._parse_timestamp(span_data.get("startTime")),
                end_time=self._parse_timestamp(span_data.get("endTime")),
            )
            session.add(span)

    def _parse_timestamp(self, ts_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO timestamp string to datetime.

        Args:
            ts_str: ISO timestamp string

        Returns:
            datetime object or None if parsing fails
        """
        if not ts_str:
            return None

        try:
            # Handle ISO format with timezone
            if "+" in ts_str or ts_str.endswith("Z"):
                return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(ts_str)
        except Exception as e:
            logger.warning(f"Failed to parse timestamp {ts_str}: {e}")
            return None

    def start_continuous_export(self, interval_minutes: Optional[int] = None):
        """Start continuous export daemon.

        Runs export at regular intervals in a loop. Useful for real-time
        analytics and monitoring.

        Args:
            interval_minutes: Export interval in minutes (default: from config)

        Example:
            >>> # Run in background thread
            >>> import threading
            >>> thread = threading.Thread(
            ...     target=exporter.start_continuous_export,
            ...     args=(30,)
            ... )
            >>> thread.daemon = True
            >>> thread.start()
        """
        interval = interval_minutes or self.config.export_interval_minutes
        logger.info(f"Starting continuous export with {interval} minute interval")

        last_export_time = datetime.utcnow()

        while True:
            try:
                # Export traces since last export
                now = datetime.utcnow()
                stats = self.export_traces(from_timestamp=last_export_time, to_timestamp=now)

                logger.info(
                    f"Continuous export: {stats['traces']} traces, "
                    f"{stats['generations']} generations, "
                    f"{stats['errors']} errors"
                )

                last_export_time = now

                # Sleep until next interval
                time.sleep(interval * 60)

            except KeyboardInterrupt:
                logger.info("Continuous export stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous export: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
