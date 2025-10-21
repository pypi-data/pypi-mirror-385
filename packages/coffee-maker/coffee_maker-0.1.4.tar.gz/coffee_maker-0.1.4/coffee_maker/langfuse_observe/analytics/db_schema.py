"""Comprehensive analytics warehouse schema for LLM metrics.

⚠️ DEPRECATED: This module uses SQLAlchemy and is deprecated as of Sprint 5 (2025-10-09).
The analytics module now uses native sqlite3 in models_sqlite.py with zero external dependencies.
This file will be removed in a future version.

This module defines a **full-featured schema** for comprehensive LLM analytics,
including prompt variant tracking, agent task results, and advanced features.
For a simpler schema focused on Langfuse export, see models.py.

## Purpose

This schema is designed for:
- **Analytics Warehouse**: Complete LLM usage tracking and analysis
- **Prompt Engineering**: A/B testing with prompt variants
- **Agent Monitoring**: Track agent task execution and results
- **Advanced Features**: Export metadata, scheduling, WAL mode

## Tables

### Core Tables
- **llm_generations**: Individual LLM API calls with detailed metrics
- **llm_traces**: Complete execution traces with full context
- **llm_events**: Fallback events, errors, and state changes

### Advanced Features
- **rate_limit_counters**: Multi-process safe rate limit tracking
- **scheduled_requests**: Request scheduling queue for rate limiting
- **agent_task_results**: Agent performance and output tracking
- **prompt_variants**: Prompt versions for A/B testing and optimization
- **prompt_executions**: Execution results for each prompt variant
- **export_metadata**: Track export runs and sync state

## When to Use This vs models.py

**Use db_schema.py when**:
- Building comprehensive analytics warehouse
- Need prompt variant tracking and A/B testing
- Require agent task result tracking
- Want export metadata and scheduling features
- Need advanced analytics capabilities

**Use models.py when**:
- Just exporting Langfuse traces (simpler schema)
- Running basic performance analysis only
- Need minimal, lightweight schema
- Don't need prompt variants or agent tracking

## Features

### Multi-Process Safety
Enable WAL mode for SQLite to support concurrent writes:
```python
enable_sqlite_wal(engine)
```

### Platform Independence
Custom type decorators (GUID, JSON) work on both SQLite and PostgreSQL.

## Database Support

Supports both SQLite (default, with WAL mode) and PostgreSQL backends.

Example:
    Create all tables:
    >>> from sqlalchemy import create_engine
    >>> from coffee_maker.langfuse_observe.analytics.db_schema import Base
    >>>
    >>> engine = create_engine("sqlite:///llm_warehouse.db")
    >>> Base.metadata.create_all(engine)

    Enable WAL mode for SQLite (multi-process safe):
    >>> from coffee_maker.langfuse_observe.analytics.db_schema import enable_sqlite_wal
    >>> enable_sqlite_wal(engine)

    Setup with PostgreSQL:
    >>> engine = create_engine("postgresql://user:pass@localhost/llm_warehouse")
    >>> Base.metadata.create_all(engine)

See Also:
    - models.py: Simplified schema for Langfuse export
    - setup_metrics_db.py: Script to initialize the database
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator

Base = declarative_base()


# Custom type for UUID that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses TEXT for SQLite.
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load dialect-specific implementation."""
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID

            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        """Convert UUID to string for SQLite."""
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        """Convert string to UUID for SQLite."""
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, str):
                return UUID(value) if value else None
            return value


# Custom type for JSON that works with both SQLite and PostgreSQL
class JSON(TypeDecorator):
    """Platform-independent JSON type."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load dialect-specific implementation."""
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB

            return dialect.type_descriptor(JSONB)
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        """Convert dict to JSON string for SQLite."""
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            import json

            return json.dumps(value) if value else None

    def process_result_value(self, value, dialect):
        """Convert JSON string to dict for SQLite."""
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        else:
            import json

            return json.loads(value) if value else None


class LLMGeneration(Base):
    """Individual LLM generation record.

    Stores all LLM API calls with their metrics, costs, and metadata.

    Attributes:
        id: Unique identifier (UUID)
        trace_id: Parent trace identifier
        observation_id: Langfuse observation ID
        parent_observation_id: Parent observation ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
        start_time: Generation start time
        end_time: Generation end time
        latency_seconds: Generation latency in seconds
        model: Model identifier (e.g., "openai/gpt-4o-mini")
        model_version: Model version
        provider: Provider name (openai, gemini, anthropic)
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens (input + output)
        cost_usd: Total cost in USD
        input_cost_usd: Input cost in USD
        output_cost_usd: Output cost in USD
        is_primary: Whether this was the primary model
        tier: Rate limiting tier
        prompt_text: Input prompt
        prompt_tokens_estimate: Estimated prompt tokens
        completion_text: Generated completion
        metadata: Additional metadata (JSON)
    """

    __tablename__ = "llm_generations"

    # Identifiers
    id = Column(GUID, primary_key=True, default=uuid4)
    trace_id = Column(GUID, nullable=False, index=True)
    observation_id = Column(GUID)
    parent_observation_id = Column(GUID)

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    latency_seconds = Column(Float)

    # Model
    model = Column(String(255), nullable=False, index=True)
    model_version = Column(String(100))
    provider = Column(String(50), index=True)

    # Tokens
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)

    # Costs
    cost_usd = Column(Float, index=True)
    input_cost_usd = Column(Float)
    output_cost_usd = Column(Float)

    # Context
    is_primary = Column(Boolean, default=True)
    tier = Column(String(50))

    # Content
    prompt_text = Column(Text)
    prompt_tokens_estimate = Column(Integer)
    completion_text = Column(Text)

    # Metadata
    metadata = Column(JSON)


class LLMTrace(Base):
    """Complete LLM execution trace.

    Represents a full execution trace with all its generations and events.

    Attributes:
        id: Unique identifier
        trace_id: Trace identifier (unique)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: User identifier
        session_id: Session identifier
        name: Trace name
        tags: List of tags (JSON array)
        total_cost_usd: Total cost for this trace
        total_tokens: Total tokens used
        total_generations: Number of generations
        total_events: Number of events
        metadata: Additional metadata (JSON)
    """

    __tablename__ = "llm_traces"

    # Identifiers
    id = Column(GUID, primary_key=True, default=uuid4)
    trace_id = Column(GUID, unique=True, nullable=False, index=True)

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Attribution
    user_id = Column(String(255))
    session_id = Column(String(255))

    # Context
    name = Column(String(255), index=True)
    tags = Column(JSON)  # Array of strings

    # Aggregate metrics
    total_cost_usd = Column(Float)
    total_tokens = Column(Integer)
    total_generations = Column(Integer)
    total_events = Column(Integer)

    # Metadata
    metadata = Column(JSON)


class LLMEvent(Base):
    """LLM event (fallback, error, etc.).

    Stores events like rate limit fallbacks, context length errors, etc.

    Attributes:
        id: Unique identifier
        trace_id: Parent trace identifier
        observation_id: Observation identifier
        created_at: Creation timestamp
        event_name: Event name (e.g., "rate_limit_fallback")
        event_type: Event type (e.g., "fallback", "error")
        original_model: Model that failed
        fallback_model: Model used as fallback
        fallback_reason: Reason for fallback
        estimated_tokens: Estimated tokens
        original_max_context: Original model's max context
        fallback_max_context: Fallback model's max context
        metadata: Additional metadata (JSON)
    """

    __tablename__ = "llm_events"

    # Identifiers
    id = Column(GUID, primary_key=True, default=uuid4)
    trace_id = Column(GUID, index=True)
    observation_id = Column(GUID)

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Type
    event_name = Column(String(100), nullable=False, index=True)
    event_type = Column(String(50))

    # Fallback context
    original_model = Column(String(255), index=True)
    fallback_model = Column(String(255))
    fallback_reason = Column(Text)

    # Context specific
    estimated_tokens = Column(Integer)
    original_max_context = Column(Integer)
    fallback_max_context = Column(Integer)

    # Metadata
    metadata = Column(JSON)


class RateLimitCounter(Base):
    """Rate limit counter for multi-process safe tracking.

    This table stores rate limit counters that can be safely shared
    across multiple processes using SQLite's WAL mode or PostgreSQL.

    Attributes:
        id: Auto-increment ID
        provider: Provider name (openai, gemini, anthropic)
        model: Model name
        tier: Rate limiting tier
        window_start: Window start timestamp
        window_end: Window end timestamp
        window_type: Window type (minute, hour, day)
        request_count: Current request count
        token_count: Current token count
        request_limit: Maximum requests allowed
        token_limit: Maximum tokens allowed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "rate_limit_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False)

    # Window
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    window_type = Column(String(20))  # minute, hour, day

    # Counters (updated atomically)
    request_count = Column(Integer, default=0)
    token_count = Column(Integer, default=0)

    # Limits
    request_limit = Column(Integer)
    token_limit = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "model",
            "tier",
            "window_type",
            "window_start",
            name="uq_rate_limit_window",
        ),
        Index(
            "idx_rate_limit_lookup",
            "provider",
            "model",
            "tier",
            "window_type",
            "window_start",
        ),
        Index("idx_rate_limit_window_end", "window_end"),
    )


class ScheduledRequest(Base):
    """Scheduled LLM request queue.

    Stores requests scheduled for future execution to respect rate limits.

    Attributes:
        id: Auto-increment ID
        request_id: Unique request identifier
        provider: Provider name
        model: Model name
        tier: Rate limiting tier
        scheduled_time: Time when request should execute
        actual_execution_time: Actual execution time
        created_at: Creation timestamp
        priority: Request priority (higher = more important)
        status: Request status (pending, executing, completed, failed)
        estimated_tokens: Estimated token count
        execution_result: Execution result (JSON)
        error_message: Error message if failed
    """

    __tablename__ = "scheduled_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), unique=True, nullable=False)

    # LLM target
    provider = Column(String(50), nullable=False)
    model = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False)

    # Timing
    scheduled_time = Column(DateTime, nullable=False, index=True)
    actual_execution_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Priority
    priority = Column(Integer, default=0)

    # Status
    status = Column(String(50), default="pending", index=True)

    # Estimation
    estimated_tokens = Column(Integer)

    # Result
    execution_result = Column(Text)
    error_message = Column(Text)

    __table_args__ = (Index("idx_scheduled_lookup", "provider", "model", "tier", "status", "scheduled_time"),)


class AgentTaskResult(Base):
    """Agent task execution result.

    Stores results of agent task executions for performance analysis.

    Attributes:
        id: Auto-increment ID
        task_id: Unique task identifier
        trace_id: Related trace identifier
        agent_name: Agent name
        agent_version: Agent version
        task_type: Type of task
        task_description: Task description
        started_at: Task start timestamp
        completed_at: Task completion timestamp
        duration_seconds: Task duration
        success: Whether task succeeded
        quality_score: Quality score (0-1)
        confidence_score: Confidence score (0-1)
        total_cost_usd: Total cost
        total_tokens: Total tokens used
        llm_calls_count: Number of LLM calls
        fallback_count: Number of fallbacks
        result_data: Result data (JSON)
        error_message: Error message if failed
        metadata: Additional metadata (JSON)
    """

    __tablename__ = "agent_task_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), unique=True, nullable=False)
    trace_id = Column(String(36))

    # Agent info
    agent_name = Column(String(255), nullable=False, index=True)
    agent_version = Column(String(50))

    # Task info
    task_type = Column(String(100), index=True)
    task_description = Column(Text)

    # Timing
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    # Performance
    success = Column(Boolean, index=True)
    quality_score = Column(Float)
    confidence_score = Column(Float)

    # Resources
    total_cost_usd = Column(Float)
    total_tokens = Column(Integer)
    llm_calls_count = Column(Integer)
    fallback_count = Column(Integer)

    # Result
    result_data = Column(Text)
    error_message = Column(Text)

    # Metadata
    metadata = Column(Text)

    __table_args__ = (Index("idx_agent_performance", "agent_name", "task_type", "success", "started_at"),)


class PromptVariant(Base):
    """Prompt variant for A/B testing.

    Stores different versions of prompts for experimentation.

    Attributes:
        id: Auto-increment ID
        prompt_id: Unique prompt identifier
        prompt_name: Prompt name
        variant_name: Variant name (e.g., "v1", "control")
        version: Version number
        prompt_template: Prompt template text
        prompt_variables: Variables used in template (JSON)
        created_at: Creation timestamp
        created_by: Creator identifier
        description: Description
        tags: Tags (JSON array)
        is_active: Whether variant is active
        is_default: Whether this is the default variant
    """

    __tablename__ = "prompt_variants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(String(36), unique=True, nullable=False)

    # Identification
    prompt_name = Column(String(255), nullable=False, index=True)
    variant_name = Column(String(100), index=True)
    version = Column(Integer)

    # Content
    prompt_template = Column(Text, nullable=False)
    prompt_variables = Column(Text)  # JSON

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))
    description = Column(Text)
    tags = Column(Text)  # JSON array

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)


class PromptExecution(Base):
    """Prompt execution result.

    Stores execution results for prompt variants to measure effectiveness.

    Attributes:
        id: Auto-increment ID
        execution_id: Unique execution identifier
        prompt_id: Related prompt variant ID
        trace_id: Related trace ID
        provider: Provider name
        model: Model name
        executed_at: Execution timestamp
        latency_seconds: Execution latency
        input_tokens: Input tokens
        output_tokens: Output tokens
        cost_usd: Execution cost
        success: Whether execution succeeded
        quality_score: Quality score (0-1)
        user_feedback: User feedback score
        output_text: Generated output
        metadata: Additional metadata (JSON)
    """

    __tablename__ = "prompt_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(36), unique=True, nullable=False)
    prompt_id = Column(String(36), nullable=False, index=True)
    trace_id = Column(String(36))

    # LLM used
    provider = Column(String(50))
    model = Column(String(255))

    # Timing
    executed_at = Column(DateTime, nullable=False, index=True)
    latency_seconds = Column(Float)

    # Tokens & Costs
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost_usd = Column(Float)

    # Performance
    success = Column(Boolean, index=True)
    quality_score = Column(Float)
    user_feedback = Column(Float)

    # Result
    output_text = Column(Text)
    metadata = Column(Text)  # JSON

    __table_args__ = (Index("idx_prompt_performance", "prompt_id", "success", "executed_at"),)


class ExportMetadata(Base):
    """Export run metadata.

    Tracks Langfuse export runs for audit and monitoring.

    Attributes:
        id: Auto-increment ID
        export_run_id: Unique export run identifier
        export_started_at: Export start timestamp
        export_completed_at: Export completion timestamp
        data_start_time: Start of exported data range
        data_end_time: End of exported data range
        generations_exported: Number of generations exported
        traces_exported: Number of traces exported
        events_exported: Number of events exported
        status: Export status (running, completed, failed)
        error_message: Error message if failed
        langfuse_project_id: Langfuse project ID
    """

    __tablename__ = "export_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    export_run_id = Column(String(36), unique=True, nullable=False, index=True)
    export_started_at = Column(DateTime, nullable=False, index=True)
    export_completed_at = Column(DateTime)

    # Period
    data_start_time = Column(DateTime)
    data_end_time = Column(DateTime)

    # Stats
    generations_exported = Column(Integer, default=0)
    traces_exported = Column(Integer, default=0)
    events_exported = Column(Integer, default=0)

    # Status
    status = Column(String(50))
    error_message = Column(Text)

    # Config
    langfuse_project_id = Column(String(255))


def enable_sqlite_wal(engine: Engine) -> None:
    """Enable SQLite WAL mode for better multi-process concurrency.

    WAL (Write-Ahead Logging) mode allows multiple processes to read and
    write to the database concurrently without blocking.

    Args:
        engine: SQLAlchemy engine instance

    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite:///llm_metrics.db")
        >>> enable_sqlite_wal(engine)
    """
    if engine.dialect.name == "sqlite":
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))
            conn.commit()
