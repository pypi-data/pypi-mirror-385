"""Database models for Langfuse export using native sqlite3.

This module replaces SQLAlchemy with native sqlite3 for the analytics module,
reducing dependencies while maintaining full functionality.

## Purpose

This schema is optimized for:
- **Langfuse Export**: Direct mapping from Langfuse API to local database
- **Basic Analytics**: LLM performance, costs, and usage analysis
- **Simplicity**: Minimal dependencies, stdlib only

## Tables

- **Trace**: Complete LLM execution traces
- **Generation**: Individual LLM API calls with metrics
- **Span**: Intermediate steps/operations within traces
- **PerformanceMetric**: Pre-aggregated performance metrics
- **RateLimitCounter**: Multi-process safe rate limit tracking

## Database Support

SQLite only (via stdlib sqlite3 module).

Example:
    Create tables:
    >>> from coffee_maker.langfuse_observe.analytics.models_sqlite import init_database
    >>>
    >>> conn = init_database("llm_metrics.db")
    >>> conn.close()

    Query recent generations:
    >>> import sqlite3
    >>> from coffee_maker.langfuse_observe.analytics.models_sqlite import Gener

ation
    >>>
    >>> conn = sqlite3.connect("llm_metrics.db")
    >>> cursor = conn.execute("SELECT * FROM generations ORDER BY created_at DESC LIMIT 10")
    >>> rows = cursor.fetchall()
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


# SQL Schema Definitions

CREATE_TRACES_TABLE = """
CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    name TEXT,
    user_id TEXT,
    session_id TEXT,
    trace_metadata TEXT,  -- JSON
    input TEXT,           -- JSON
    output TEXT,          -- JSON
    created_at TEXT NOT NULL,
    updated_at TEXT,
    release TEXT,
    tags TEXT             -- JSON array
);

CREATE INDEX IF NOT EXISTS idx_trace_created_at ON traces(created_at);
CREATE INDEX IF NOT EXISTS idx_trace_user_id ON traces(user_id);
CREATE INDEX IF NOT EXISTS idx_trace_session_id ON traces(session_id);
CREATE INDEX IF NOT EXISTS idx_trace_user_session ON traces(user_id, session_id);
"""

CREATE_GENERATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS generations (
    id TEXT PRIMARY KEY,
    trace_id TEXT,
    name TEXT,
    model TEXT,
    model_parameters TEXT,  -- JSON
    input TEXT,             -- JSON
    output TEXT,            -- JSON
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    input_cost REAL DEFAULT 0.0,
    output_cost REAL DEFAULT 0.0,
    total_cost REAL DEFAULT 0.0,
    latency_ms REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    metadata TEXT,          -- JSON
    level TEXT DEFAULT 'DEFAULT',
    status_message TEXT,
    completion_start_time TEXT,
    completion_end_time TEXT,
    FOREIGN KEY (trace_id) REFERENCES traces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_generation_trace_id ON generations(trace_id);
CREATE INDEX IF NOT EXISTS idx_generation_model ON generations(model);
CREATE INDEX IF NOT EXISTS idx_generation_created_at ON generations(created_at);
CREATE INDEX IF NOT EXISTS idx_generation_cost ON generations(total_cost);
"""

CREATE_SPANS_TABLE = """
CREATE TABLE IF NOT EXISTS spans (
    id TEXT PRIMARY KEY,
    trace_id TEXT,
    name TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    input TEXT,             -- JSON
    output TEXT,            -- JSON
    metadata TEXT,          -- JSON
    level TEXT DEFAULT 'DEFAULT',
    status_message TEXT,
    FOREIGN KEY (trace_id) REFERENCES traces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_span_trace_id ON spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_span_start_time ON spans(start_time);
"""

CREATE_PERFORMANCE_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    model TEXT,
    timeframe TEXT,  -- 'hour', 'day', 'week', 'month'
    timestamp TEXT NOT NULL,
    metadata TEXT    -- JSON
);

CREATE INDEX IF NOT EXISTS idx_perf_metric_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_perf_model ON performance_metrics(model);
CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp);
"""

CREATE_RATE_LIMIT_COUNTERS_TABLE = """
CREATE TABLE IF NOT EXISTS rate_limit_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    token_count INTEGER DEFAULT 0,
    UNIQUE(model, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_model ON rate_limit_counters(model);
CREATE INDEX IF NOT EXISTS idx_rate_limit_window ON rate_limit_counters(window_start, window_end);
"""


# Dataclass Models


@dataclass
class Trace:
    """Langfuse trace record."""

    id: str
    name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_metadata: Optional[Dict[str, Any]] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    release: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_db_row(self) -> tuple:
        """Convert to database row tuple."""
        return (
            self.id,
            self.name,
            self.user_id,
            self.session_id,
            json.dumps(self.trace_metadata) if self.trace_metadata else None,
            json.dumps(self.input) if self.input else None,
            json.dumps(self.output) if self.output else None,
            self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            self.updated_at.isoformat() if self.updated_at else None,
            self.release,
            json.dumps(self.tags) if self.tags else None,
        )

    @classmethod
    def from_db_row(cls, row: tuple) -> "Trace":
        """Create from database row."""
        return cls(
            id=row[0],
            name=row[1],
            user_id=row[2],
            session_id=row[3],
            trace_metadata=json.loads(row[4]) if row[4] else None,
            input=json.loads(row[5]) if row[5] else None,
            output=json.loads(row[6]) if row[6] else None,
            created_at=datetime.fromisoformat(row[7]) if row[7] else None,
            updated_at=datetime.fromisoformat(row[8]) if row[8] else None,
            release=row[9],
            tags=json.loads(row[10]) if row[10] else None,
        )


@dataclass
class Generation:
    """Langfuse generation record."""

    id: str
    trace_id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    model_parameters: Optional[Dict[str, Any]] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    latency_ms: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    level: str = "DEFAULT"
    status_message: Optional[str] = None
    completion_start_time: Optional[datetime] = None
    completion_end_time: Optional[datetime] = None

    def to_db_row(self) -> tuple:
        """Convert to database row tuple."""
        return (
            self.id,
            self.trace_id,
            self.name,
            self.model,
            json.dumps(self.model_parameters) if self.model_parameters else None,
            json.dumps(self.input) if self.input else None,
            json.dumps(self.output) if self.output else None,
            self.input_tokens,
            self.output_tokens,
            self.total_tokens,
            self.input_cost,
            self.output_cost,
            self.total_cost,
            self.latency_ms,
            self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            self.updated_at.isoformat() if self.updated_at else None,
            json.dumps(self.metadata) if self.metadata else None,
            self.level,
            self.status_message,
            self.completion_start_time.isoformat() if self.completion_start_time else None,
            self.completion_end_time.isoformat() if self.completion_end_time else None,
        )

    @classmethod
    def from_db_row(cls, row: tuple) -> "Generation":
        """Create from database row."""
        return cls(
            id=row[0],
            trace_id=row[1],
            name=row[2],
            model=row[3],
            model_parameters=json.loads(row[4]) if row[4] else None,
            input=json.loads(row[5]) if row[5] else None,
            output=json.loads(row[6]) if row[6] else None,
            input_tokens=row[7] or 0,
            output_tokens=row[8] or 0,
            total_tokens=row[9] or 0,
            input_cost=row[10] or 0.0,
            output_cost=row[11] or 0.0,
            total_cost=row[12] or 0.0,
            latency_ms=row[13],
            created_at=datetime.fromisoformat(row[14]) if row[14] else None,
            updated_at=datetime.fromisoformat(row[15]) if row[15] else None,
            metadata=json.loads(row[16]) if row[16] else None,
            level=row[17] or "DEFAULT",
            status_message=row[18],
            completion_start_time=datetime.fromisoformat(row[19]) if row[19] else None,
            completion_end_time=datetime.fromisoformat(row[20]) if row[20] else None,
        )


@dataclass
class Span:
    """Langfuse span record."""

    id: str
    trace_id: Optional[str] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    level: str = "DEFAULT"
    status_message: Optional[str] = None

    def to_db_row(self) -> tuple:
        """Convert to database row tuple."""
        return (
            self.id,
            self.trace_id,
            self.name,
            self.start_time.isoformat() if self.start_time else datetime.utcnow().isoformat(),
            self.end_time.isoformat() if self.end_time else None,
            json.dumps(self.input) if self.input else None,
            json.dumps(self.output) if self.output else None,
            json.dumps(self.metadata) if self.metadata else None,
            self.level,
            self.status_message,
        )

    @classmethod
    def from_db_row(cls, row: tuple) -> "Span":
        """Create from database row."""
        return cls(
            id=row[0],
            trace_id=row[1],
            name=row[2],
            start_time=datetime.fromisoformat(row[3]) if row[3] else None,
            end_time=datetime.fromisoformat(row[4]) if row[4] else None,
            input=json.loads(row[5]) if row[5] else None,
            output=json.loads(row[6]) if row[6] else None,
            metadata=json.loads(row[7]) if row[7] else None,
            level=row[8] or "DEFAULT",
            status_message=row[9],
        )


# Database Initialization


def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database with schema.

    Args:
        db_path: Path to SQLite database file

    Returns:
        sqlite3.Connection: Database connection

    Example:
        >>> conn = init_database("llm_metrics.db")
        >>> conn.close()
    """
    conn = sqlite3.connect(db_path)

    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")

    # Create tables
    conn.executescript(CREATE_TRACES_TABLE)
    conn.executescript(CREATE_GENERATIONS_TABLE)
    conn.executescript(CREATE_SPANS_TABLE)
    conn.executescript(CREATE_PERFORMANCE_METRICS_TABLE)
    conn.executescript(CREATE_RATE_LIMIT_COUNTERS_TABLE)

    conn.commit()
    return conn


# Helper Functions for Database Operations


def insert_trace(conn: sqlite3.Connection, trace: Trace) -> None:
    """Insert a trace record into the database."""
    conn.execute(
        """
        INSERT OR REPLACE INTO traces
        (id, name, user_id, session_id, trace_metadata, input, output,
         created_at, updated_at, release, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        trace.to_db_row(),
    )
    conn.commit()


def insert_generation(conn: sqlite3.Connection, generation: Generation) -> None:
    """Insert a generation record into the database."""
    conn.execute(
        """
        INSERT OR REPLACE INTO generations
        (id, trace_id, name, model, model_parameters, input, output,
         input_tokens, output_tokens, total_tokens, input_cost, output_cost, total_cost,
         latency_ms, created_at, updated_at, metadata, level, status_message,
         completion_start_time, completion_end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        generation.to_db_row(),
    )
    conn.commit()


def insert_span(conn: sqlite3.Connection, span: Span) -> None:
    """Insert a span record into the database."""
    conn.execute(
        """
        INSERT OR REPLACE INTO spans
        (id, trace_id, name, start_time, end_time, input, output, metadata, level, status_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        span.to_db_row(),
    )
    conn.commit()


def get_generation_by_id(conn: sqlite3.Connection, generation_id: str) -> Optional[Generation]:
    """Get a generation by ID."""
    cursor = conn.execute("SELECT * FROM generations WHERE id = ?", (generation_id,))
    row = cursor.fetchone()
    return Generation.from_db_row(row) if row else None


def get_recent_generations(conn: sqlite3.Connection, limit: int = 10) -> List[Generation]:
    """Get recent generations ordered by creation time."""
    cursor = conn.execute("SELECT * FROM generations ORDER BY created_at DESC LIMIT ?", (limit,))
    return [Generation.from_db_row(row) for row in cursor.fetchall()]


def get_generations_by_model(conn: sqlite3.Connection, model: str, limit: int = 100) -> List[Generation]:
    """Get generations for a specific model."""
    cursor = conn.execute("SELECT * FROM generations WHERE model = ? ORDER BY created_at DESC LIMIT ?", (model, limit))
    return [Generation.from_db_row(row) for row in cursor.fetchall()]
