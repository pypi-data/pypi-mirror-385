"""SQLite-based inter-agent communication queue with persistence and metrics.

This module provides a message queue for coordinating work between autonomous agents.
It uses SQLite for persistence, enabling messages to survive daemon crashes and providing
built-in analytics through SQL queries.

Features:
- Priority queuing (SQL ORDER BY priority)
- Persistence (messages survive daemon crashes)
- Duration tracking (start/completion timestamps)
- Bottleneck analysis (SQL queries on duration_ms)
- Historical metrics (aggregated performance data)
- Zero external dependencies (sqlite3 is Python stdlib)
- Thread-safe (WAL mode enables concurrent reads/writes)

Example:
    >>> queue = MessageQueue(db_path="data/orchestrator.db")
    >>> queue.send(Message(
    ...     sender="architect",
    ...     recipient="code_developer",
    ...     type="spec_created",
    ...     payload={"spec_id": "SPEC-072"},
    ...     priority=2,
    ... ))
    >>> message = queue.get("code_developer")
    >>> queue.mark_started(message.task_id, agent="code_developer")
    >>> # ... do work ...
    >>> queue.mark_completed(message.task_id, duration_ms=1500)
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class MessageType(Enum):
    """Types of inter-agent messages.

    IMPORTANT: ALL inter-agent communication goes through orchestrator.
    Agents send messages TO orchestrator with suggested_recipient.
    Orchestrator routes to best available agent.
    """

    # User interaction messages (from/to user_listener)
    USER_REQUEST = "user_request"  # User input → orchestrator (suggests recipient)
    USER_RESPONSE = "user_response"  # Agent → orchestrator → user_listener

    # Inter-agent task delegation (ALL go through orchestrator)
    TASK_REQUEST = "task_request"  # Agent → orchestrator (suggests recipient + reason)
    TASK_RESPONSE = "task_response"  # Agent → orchestrator → requesting agent
    TASK_COMPLETE = "task_complete"  # Agent finished task → orchestrator → requester

    # Legacy (deprecated - use TASK_REQUEST instead)
    SPEC_CREATED = "spec_created"  # Deprecated: use TASK_COMPLETE
    IMPLEMENTATION_REQUEST = "implementation_request"  # Deprecated: use TASK_REQUEST
    IMPLEMENTATION_COMPLETE = "implementation_complete"  # Deprecated: use TASK_COMPLETE
    BUG_REPORT = "bug_report"  # Keep for assistant → project_manager
    DEMO_REQUEST = "demo_request"  # Keep for specific demo requests
    DEMO_COMPLETE = "demo_complete"  # Keep for demo completion

    # Coordination (system messages)
    STATUS_UPDATE = "status_update"  # Progress updates
    HEARTBEAT = "heartbeat"  # Health check
    TASK_DELEGATE = "task_delegate"  # Deprecated: use TASK_REQUEST


class AgentType(Enum):
    """Types of autonomous agents."""

    USER_LISTENER = "user_listener"  # UI agent - handles user interaction
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    ASSISTANT = "assistant"
    CODE_SEARCHER = "code_searcher"
    UX_DESIGN_EXPERT = "ux_design_expert"


@dataclass
class Message:
    """Inter-agent message for queue communication.

    ARCHITECTURAL PRINCIPLE: ALL messages go TO orchestrator for routing.

    For inter-agent communication:
    - recipient: Should ALWAYS be "orchestrator"
    - payload["suggested_recipient"]: Agent you want to handle the task
    - Orchestrator will route to best available agent (may override suggestion)

    For responses to user:
    - recipient: "user_listener" (orchestrator routes directly)

    Attributes:
        sender: Agent sending the message (AgentType.value)
        recipient: Target for this message ("orchestrator" or "user_listener")
        type: Type of message (MessageType.value)
        payload: Message payload (dict, will be JSON-encoded)
            - For TASK_REQUEST: {"suggested_recipient": "agent_name", "task": "...", "reason": "..."}
            - For USER_REQUEST: {"user_input": "...", "suggested_recipient": "agent_name"}
            - For USER_RESPONSE: {"response": "...", "original_task_id": "..."}
        priority: Message priority (1=highest, 10=lowest)
        timestamp: ISO8601 timestamp of message creation
        task_id: Unique task identifier
    """

    sender: str  # AgentType.value
    recipient: str  # "orchestrator" or "user_listener" or specific agent
    type: str  # MessageType.value
    payload: dict
    priority: int = 5  # 1=highest, 10=lowest
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class MessageQueue:
    """SQLite-based inter-agent communication queue with persistence and metrics.

    This class implements a thread-safe message queue backed by SQLite database.
    Each message goes through lifecycle: queued -> running -> completed/failed.

    The database includes views for analytics:
    - bottlenecks: top 100 slowest tasks
    - agent_performance: aggregated stats per agent
    - queue_depth: current queue depth by agent and priority

    Thread Safety:
    - SQLite WAL mode enables concurrent reads/writes
    - No external locking needed (WAL handles it)

    Persistence:
    - Messages written to disk immediately
    - Survives daemon crashes and restarts
    - Historical data retained for 30 days
    """

    def __init__(self, db_path: str = "data/orchestrator.db"):
        """Initialize SQLite message queue.

        Args:
            db_path: Path to SQLite database file. Directory will be created if needed.

        Raises:
            sqlite3.Error: If database initialization fails
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database and schema
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema with tables, indexes, and views.

        Creates:
        - tasks table (message queue + history)
        - agent_metrics table (performance tracking)
        - bottlenecks view (top 100 slowest tasks)
        - agent_performance view (aggregated stats)
        - queue_depth view (current queue by agent/priority)
        - Various indexes for fast queries
        """
        schema_sql = """
        -- Enable WAL mode (Write-Ahead Logging) for concurrent access
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;

        -- Tasks table (message queue + historical data)
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            type TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 5,
            status TEXT NOT NULL DEFAULT 'queued',
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            duration_ms INTEGER,
            error_message TEXT
        );

        -- Indexes for fast queries
        CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority, created_at);
        CREATE INDEX IF NOT EXISTS idx_duration ON tasks(duration_ms DESC);
        CREATE INDEX IF NOT EXISTS idx_recipient_status ON tasks(recipient, status);
        CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);

        -- Agent metrics table (performance tracking)
        CREATE TABLE IF NOT EXISTS agent_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TEXT NOT NULL
        );

        -- Index for metrics queries
        CREATE INDEX IF NOT EXISTS idx_agent_metric ON agent_metrics(agent, metric_name, timestamp);

        -- View: Top 100 slowest tasks (bottleneck analysis)
        CREATE VIEW IF NOT EXISTS bottlenecks AS
        SELECT task_id, recipient AS agent, type, duration_ms, created_at, started_at, completed_at
        FROM tasks
        WHERE status = 'completed' AND duration_ms IS NOT NULL
        ORDER BY duration_ms DESC
        LIMIT 100;

        -- View: Agent performance aggregates
        CREATE VIEW IF NOT EXISTS agent_performance AS
        SELECT
            recipient AS agent,
            COUNT(*) AS total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_tasks,
            AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms,
            MAX(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS max_duration_ms,
            MIN(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS min_duration_ms
        FROM tasks
        GROUP BY recipient;

        -- View: Queue depth by agent (current queued tasks)
        CREATE VIEW IF NOT EXISTS queue_depth AS
        SELECT
            recipient AS agent,
            COUNT(*) AS queued_tasks,
            SUM(CASE WHEN priority <= 2 THEN 1 ELSE 0 END) AS high_priority,
            SUM(CASE WHEN priority BETWEEN 3 AND 7 THEN 1 ELSE 0 END) AS normal_priority,
            SUM(CASE WHEN priority >= 8 THEN 1 ELSE 0 END) AS low_priority
        FROM tasks
        WHERE status = 'queued'
        GROUP BY recipient;
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to initialize message queue schema: {e}")

    def send(self, message: Message) -> None:
        """Send message to recipient's queue with priority.

        Args:
            message: Message to send

        Raises:
            sqlite3.Error: If database write fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (task_id, sender, recipient, type, priority,
                                       payload, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'queued')
                    """,
                    (
                        message.task_id,
                        message.sender,
                        message.recipient,
                        message.type,
                        message.priority,
                        json.dumps(message.payload),
                        message.timestamp,
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to send message: {e}")

    def get(self, recipient: str, timeout: float = 1.0) -> Optional[Message]:
        """Get next message for recipient (highest priority first).

        Args:
            recipient: Agent to get messages for
            timeout: Not used (kept for API compatibility)

        Returns:
            Next message or None if no messages available

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT task_id, sender, recipient, type, priority, payload, created_at
                    FROM tasks
                    WHERE recipient = ? AND status = 'queued'
                    ORDER BY priority ASC, created_at ASC
                    LIMIT 1
                    """,
                    (recipient,),
                )

                row = cursor.fetchone()
                if row:
                    return Message(
                        task_id=row["task_id"],
                        sender=row["sender"],
                        recipient=row["recipient"],
                        type=row["type"],
                        priority=row["priority"],
                        payload=json.loads(row["payload"]),
                        timestamp=row["created_at"],
                    )
                return None
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get message: {e}")

    def mark_started(self, task_id: str, agent: str) -> None:
        """Mark task as started, record start time.

        Args:
            task_id: Task identifier
            agent: Agent starting the task

        Raises:
            sqlite3.Error: If database update fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'running', started_at = ?
                    WHERE task_id = ?
                    """,
                    (datetime.now().isoformat(), task_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to mark task started: {e}")

    def mark_completed(self, task_id: str, duration_ms: int) -> None:
        """Mark task as completed, record duration.

        Args:
            task_id: Task identifier
            duration_ms: Task duration in milliseconds

        Raises:
            sqlite3.Error: If database update fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'completed', completed_at = ?, duration_ms = ?
                    WHERE task_id = ?
                    """,
                    (datetime.now().isoformat(), duration_ms, task_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to mark task completed: {e}")

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark task as failed, record error message.

        Args:
            task_id: Task identifier
            error_message: Error details

        Raises:
            sqlite3.Error: If database update fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'failed', completed_at = ?, error_message = ?
                    WHERE task_id = ?
                    """,
                    (datetime.now().isoformat(), error_message, task_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to mark task failed: {e}")

    def get_slowest_tasks(self, limit: int = 10) -> List[dict]:
        """Get slowest tasks for bottleneck analysis.

        Args:
            limit: Number of slowest tasks to return

        Returns:
            List of task metadata sorted by duration (slowest first)

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM bottlenecks LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get slowest tasks: {e}")

    def get_agent_performance(self) -> List[dict]:
        """Get aggregated performance metrics per agent.

        Returns:
            List of agent performance stats

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM agent_performance")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get agent performance: {e}")

    def get_queue_depth(self) -> List[dict]:
        """Get current queue depth by agent and priority.

        Returns:
            List of queue depth stats by agent

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM queue_depth")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get queue depth: {e}")

    def record_metric(self, agent: str, metric_name: str, metric_value: float) -> None:
        """Record performance metric for agent.

        Args:
            agent: Agent name
            metric_name: Metric name (e.g., "cpu_percent", "memory_mb")
            metric_value: Metric value

        Raises:
            sqlite3.Error: If database write fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO agent_metrics (agent, metric_name, metric_value, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (agent, metric_name, metric_value, datetime.now().isoformat()),
                )
                conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to record metric: {e}")

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """Clean up completed tasks older than N days.

        Args:
            days: Number of days to retain

        Returns:
            Number of tasks deleted

        Raises:
            sqlite3.Error: If database cleanup fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    f"""
                    DELETE FROM tasks
                    WHERE status IN ('completed', 'failed')
                      AND completed_at < datetime('now', '-{days} days')
                    """
                )
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to cleanup old tasks: {e}")

    def has_messages(self, recipient: Optional[str] = None) -> bool:
        """Check if queue has messages.

        Args:
            recipient: Optional agent filter

        Returns:
            True if messages exist

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if recipient:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM tasks WHERE recipient = ? AND status = 'queued'",
                        (recipient,),
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'queued'")
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to check for messages: {e}")

    def size(self, recipient: Optional[str] = None) -> int:
        """Get queue size.

        Args:
            recipient: Optional agent filter

        Returns:
            Number of queued messages

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if recipient:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM tasks WHERE recipient = ? AND status = 'queued'",
                        (recipient,),
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'queued'")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get queue size: {e}")

    def get_task_metrics(self) -> dict:
        """Get overall task completion metrics.

        Returns:
            Dictionary with task statistics

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total_tasks,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
                        SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued_tasks,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_tasks,
                        AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) as avg_duration_ms
                    FROM tasks
                    """
                )
                row = cursor.fetchone()
                return {
                    "total_tasks": row[0] or 0,
                    "completed_tasks": row[1] or 0,
                    "failed_tasks": row[2] or 0,
                    "queued_tasks": row[3] or 0,
                    "running_tasks": row[4] or 0,
                    "avg_duration_ms": row[5] or 0,
                }
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get task metrics: {e}")

    def stop(self) -> None:
        """Stop message queue (cleanup, vacuum database).

        This should be called when shutting down the daemon to clean up old
        tasks and optimize the database.
        """
        try:
            # Clean up completed tasks older than 30 days
            self.cleanup_old_tasks(days=30)

            # Vacuum database to reclaim space
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
                conn.commit()
        except sqlite3.Error as e:
            # Log but don't raise - cleanup is not critical
            print(f"Warning: Failed to cleanup message queue: {e}")

    def get_percentiles(self, percentiles: List[int] = None) -> Dict[int, Optional[int]]:
        """Calculate duration percentiles for all completed tasks.

        Args:
            percentiles: List of percentiles to calculate (default: [50, 95, 99])

        Returns:
            Dictionary mapping percentile to duration_ms (e.g., {50: 1200, 95: 8500})

        Raises:
            sqlite3.Error: If database query fails
        """
        if percentiles is None:
            percentiles = [50, 95, 99]

        try:
            with sqlite3.connect(self.db_path) as conn:
                result = {}
                for p in percentiles:
                    cursor = conn.execute(
                        f"""
                        SELECT duration_ms
                        FROM tasks
                        WHERE status = 'completed' AND duration_ms IS NOT NULL
                        ORDER BY duration_ms
                        LIMIT 1 OFFSET (
                            SELECT CAST(COUNT(*) * {p} / 100 AS INTEGER)
                            FROM tasks
                            WHERE status = 'completed' AND duration_ms IS NOT NULL
                        )
                        """
                    )
                    row = cursor.fetchone()
                    result[p] = row[0] if row else None
                return result
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to calculate percentiles: {e}")
