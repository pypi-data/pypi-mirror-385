"""Data models for ACE framework."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Execution:
    """Single execution within a trace.

    Attributes:
        execution_id: Unique execution identifier
        prompt: Prompt sent to agent
        input_data: Input data for execution
        output: Output from execution
        result_status: success, failure, or error
        duration_seconds: Execution duration
        metadata: Additional execution metadata
    """

    execution_id: str
    prompt: str
    input_data: Dict[str, Any]
    output: str
    result_status: str
    duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "execution_id": self.execution_id,
            "prompt": self.prompt,
            "input_data": self.input_data,
            "output": self.output,
            "result_status": self.result_status,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionTrace:
    """Complete execution trace for an agent task.

    Attributes:
        trace_id: Unique trace identifier
        timestamp: Trace creation time
        agent_identity: Agent identification info
        user_query: Original user query
        executions: List of executions in this trace
        context: Trace context information
    """

    trace_id: str
    timestamp: datetime
    agent_identity: Dict[str, Any]
    user_query: str
    executions: List[Execution]
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_identity": self.agent_identity,
            "user_query": self.user_query,
            "executions": [e.to_dict() for e in self.executions],
            "context": self.context,
        }


@dataclass
class PlaybookBullet:
    """Single playbook bullet item.

    Attributes:
        bullet_id: Unique bullet identifier
        content: Bullet content text
        category: Bullet category (e.g., error_handling, optimization)
        effectiveness: Effectiveness score (0.0-1.0)
        usage_count: Number of times applied
        added_date: Date bullet was added
        status: active, pending, or archived
        metadata: Additional bullet metadata
    """

    bullet_id: str
    content: str
    category: str
    effectiveness: float
    usage_count: int = 0
    added_date: Optional[datetime] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bullet_id": self.bullet_id,
            "content": self.content,
            "category": self.category,
            "effectiveness": self.effectiveness,
            "usage_count": self.usage_count,
            "added_date": self.added_date.isoformat() if self.added_date else None,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class Playbook:
    """Agent playbook containing learned behaviors.

    Attributes:
        agent_name: Agent this playbook belongs to
        bullets: List of playbook bullets
        total_bullets: Total number of bullets
        avg_effectiveness: Average effectiveness score
        last_updated: Last update timestamp
    """

    agent_name: str
    bullets: List[PlaybookBullet]
    total_bullets: int
    avg_effectiveness: float
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "bullets": [b.to_dict() for b in self.bullets],
            "total_bullets": self.total_bullets,
            "avg_effectiveness": self.avg_effectiveness,
            "last_updated": (self.last_updated.isoformat() if self.last_updated else None),
        }
