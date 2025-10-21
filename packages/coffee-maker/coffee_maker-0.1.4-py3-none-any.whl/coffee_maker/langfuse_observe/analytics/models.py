"""Database models for Langfuse export and basic analytics.

⚠️ DEPRECATED: This module uses SQLAlchemy and is deprecated as of Sprint 5 (2025-10-09).
Use models_sqlite.py instead for native sqlite3 implementation with zero external dependencies.
This file will be removed in a future version.

This module defines a **simplified schema** focused on Langfuse trace export
and basic performance analysis. For a more comprehensive analytics warehouse
with additional features, see db_schema.py.

## Purpose

This schema is optimized for:
- **Langfuse Export**: Direct mapping from Langfuse API to local database
- **Basic Analytics**: LLM performance, costs, and usage analysis
- **Simplicity**: Minimal tables focused on core use cases

## Tables

- **Trace**: Complete LLM execution traces
- **Generation**: Individual LLM API calls with metrics
- **Span**: Intermediate steps/operations within traces
- **PerformanceMetric**: Pre-aggregated performance metrics
- **RateLimitCounter**: Multi-process safe rate limit tracking

## When to Use This vs db_schema.py

**Use models.py when**:
- Exporting Langfuse traces to local database
- Running basic performance analysis (PerformanceAnalyzer)
- Need simple, lightweight schema

**Use db_schema.py when**:
- Building comprehensive analytics warehouse
- Need prompt variant tracking and A/B testing
- Require agent task result tracking
- Want export metadata and scheduling features

## Database Support

Supports both SQLite (default) and PostgreSQL backends.

Example:
    Create tables in SQLite:
    >>> from sqlalchemy import create_engine
    >>> from coffee_maker.langfuse_observe.analytics.models import Base
    >>>
    >>> engine = create_engine("sqlite:///llm_metrics.db")
    >>> Base.metadata.create_all(engine)

    Query recent generations:
    >>> from sqlalchemy.orm import Session
    >>> from coffee_maker.langfuse_observe.analytics.models import Generation
    >>>
    >>> with Session(engine) as session:
    ...     recent = session.query(Generation).order_by(Generation.created_at.desc()).limit(10).all()

See Also:
    - db_schema.py: Comprehensive analytics warehouse schema
    - exporter.py: LangfuseExporter for populating this schema
    - analyzer.py: PerformanceAnalyzer for querying this schema
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Trace(Base):
    """Langfuse trace record.

    A trace represents a complete LLM interaction session, which may contain
    multiple generations (LLM calls) and spans (intermediate steps).

    Attributes:
        id: Unique trace ID from Langfuse
        name: Human-readable trace name
        user_id: Optional user identifier
        session_id: Optional session identifier
        metadata: Additional trace metadata (JSON)
        input: Trace input data (JSON)
        output: Trace output data (JSON)
        created_at: Trace creation timestamp
        updated_at: Last update timestamp
        release: Release/version tag
        tags: List of tags (JSON array)
    """

    __tablename__ = "traces"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    trace_metadata = Column(JSON, nullable=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    release = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)

    # Relationships
    generations = relationship("Generation", back_populates="trace", cascade="all, delete-orphan")
    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_trace_created_at", "created_at"),
        Index("idx_trace_user_session", "user_id", "session_id"),
    )


class Generation(Base):
    """Langfuse generation record.

    A generation represents a single LLM API call with its input, output,
    and associated metrics (tokens, cost, latency).

    Attributes:
        id: Unique generation ID from Langfuse
        trace_id: Parent trace ID
        name: Generation name (often the model name)
        model: Model identifier (e.g., "openai/gpt-4o")
        model_parameters: Model parameters (temperature, max_tokens, etc.)
        input: Generation input/prompt
        output: Generation output/completion
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens (input + output)
        input_cost: Cost of input tokens (USD)
        output_cost: Cost of output tokens (USD)
        total_cost: Total cost (USD)
        latency_ms: Generation latency in milliseconds
        created_at: Generation creation timestamp
        updated_at: Last update timestamp
        metadata: Additional metadata (JSON)
        level: Generation level (e.g., "DEFAULT", "ERROR")
        status_message: Status or error message
        completion_start_time: When completion generation started
        completion_end_time: When completion generation ended
    """

    __tablename__ = "generations"

    id = Column(String(255), primary_key=True)
    trace_id = Column(String(255), ForeignKey("traces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True, index=True)
    model_parameters = Column(JSON, nullable=True)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)

    # Token counts
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    # Costs
    input_cost = Column(Float, nullable=True)
    output_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)

    # Performance
    latency_ms = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    completion_start_time = Column(DateTime, nullable=True)
    completion_end_time = Column(DateTime, nullable=True)

    # Additional fields
    generation_metadata = Column(JSON, nullable=True)
    level = Column(String(50), nullable=True)
    status_message = Column(Text, nullable=True)

    # Relationships
    trace = relationship("Trace", back_populates="generations")

    __table_args__ = (
        Index("idx_generation_created_at", "created_at"),
        Index("idx_generation_model", "model"),
        Index("idx_generation_trace_created", "trace_id", "created_at"),
    )


class Span(Base):
    """Langfuse span record.

    A span represents an intermediate step or operation within a trace,
    such as retrieval, tool use, or sub-agent calls.

    Attributes:
        id: Unique span ID from Langfuse
        trace_id: Parent trace ID
        parent_observation_id: Parent span/generation ID
        name: Span name (operation type)
        input: Span input data (JSON)
        output: Span output data (JSON)
        metadata: Additional metadata (JSON)
        level: Span level
        status_message: Status or error message
        created_at: Span creation timestamp
        updated_at: Last update timestamp
        start_time: Span start time
        end_time: Span end time
    """

    __tablename__ = "spans"

    id = Column(String(255), primary_key=True)
    trace_id = Column(String(255), ForeignKey("traces.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_observation_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    span_metadata = Column(JSON, nullable=True)
    level = Column(String(50), nullable=True)
    status_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    # Relationships
    trace = relationship("Trace", back_populates="spans")

    __table_args__ = (Index("idx_span_trace_created", "trace_id", "created_at"),)


class PerformanceMetric(Base):
    """Aggregated performance metrics.

    This table stores pre-calculated performance metrics for faster querying
    and analysis. Metrics are aggregated by model, time period, and other dimensions.

    Attributes:
        id: Auto-increment primary key
        metric_type: Type of metric (e.g., "llm_latency", "prompt_performance")
        model: Model name
        dimension: Metric dimension (e.g., "prompt_template", "user_id")
        dimension_value: Value of the dimension
        time_bucket: Time bucket for aggregation
        avg_latency_ms: Average latency in milliseconds
        p50_latency_ms: 50th percentile latency
        p95_latency_ms: 95th percentile latency
        p99_latency_ms: 99th percentile latency
        total_requests: Total number of requests
        total_tokens: Total tokens used
        total_cost: Total cost (USD)
        avg_tokens_per_request: Average tokens per request
        avg_cost_per_request: Average cost per request
        error_count: Number of errors
        error_rate: Error rate (0.0 to 1.0)
        created_at: Metric creation timestamp
    """

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(100), nullable=False, index=True)
    model = Column(String(255), nullable=True, index=True)
    dimension = Column(String(100), nullable=True)
    dimension_value = Column(String(255), nullable=True)
    time_bucket = Column(DateTime, nullable=False, index=True)

    # Latency metrics
    avg_latency_ms = Column(Float, nullable=True)
    p50_latency_ms = Column(Float, nullable=True)
    p95_latency_ms = Column(Float, nullable=True)
    p99_latency_ms = Column(Float, nullable=True)

    # Usage metrics
    total_requests = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    total_cost = Column(Float, nullable=True)
    avg_tokens_per_request = Column(Float, nullable=True)
    avg_cost_per_request = Column(Float, nullable=True)

    # Error metrics
    error_count = Column(Integer, nullable=True)
    error_rate = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_perf_metric_model_time", "metric_type", "model", "time_bucket"),
        Index("idx_perf_metric_dimension", "dimension", "dimension_value"),
    )


class RateLimitCounter(Base):
    """Multi-process safe rate limit counter.

    This table provides process-safe rate limiting by storing request counts
    in the database. It's used to coordinate rate limits across multiple workers.

    Attributes:
        id: Auto-increment primary key
        model: Model name
        tier: Rate limit tier
        window_start: Time window start
        window_end: Time window end
        request_count: Number of requests in window
        token_count: Number of tokens in window
        last_updated: Last update timestamp
    """

    __tablename__ = "rate_limit_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(255), nullable=False, index=True)
    tier = Column(String(50), nullable=False, index=True)
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False)
    request_count = Column(Integer, nullable=False, default=0)
    token_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_rate_limit_model_tier_window", "model", "tier", "window_start"),)
