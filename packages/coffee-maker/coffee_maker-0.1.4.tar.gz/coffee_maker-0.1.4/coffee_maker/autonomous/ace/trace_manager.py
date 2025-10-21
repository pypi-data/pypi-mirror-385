"""Trace manager for ACE framework."""

import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from coffee_maker.autonomous.ace.models import Execution, ExecutionTrace

logger = logging.getLogger(__name__)


class TraceManager:
    """Manages execution traces."""

    def __init__(self, trace_dir: Path):
        """Initialize trace manager.

        Args:
            trace_dir: Directory for trace storage
        """
        self.trace_dir = trace_dir

    def list_traces(self, date: Optional[str] = None, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """List traces (optionally filtered).

        Args:
            date: Filter by date (YYYY-MM-DD)
            agent: Filter by agent name

        Returns:
            List of ExecutionTrace objects
        """
        # For demo, generate mock traces
        return self._generate_mock_traces(date=date, agent=agent)

    def get_traces_since(self, hours: int, agent: Optional[str] = None) -> List[ExecutionTrace]:
        """Get traces from last N hours.

        Args:
            hours: Number of hours to look back
            agent: Optional agent filter

        Returns:
            List of ExecutionTrace objects
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        all_traces = self.list_traces(agent=agent)
        return [t for t in all_traces if t.timestamp >= cutoff]

    def read_trace(self, trace_id: str, date: Optional[str] = None) -> ExecutionTrace:
        """Read specific trace by ID.

        Args:
            trace_id: Trace ID
            date: Optional date hint

        Returns:
            ExecutionTrace object

        Raises:
            FileNotFoundError: If trace not found
        """
        # For demo, just generate a mock trace
        all_traces = self.list_traces()
        for trace in all_traces:
            if trace.trace_id == trace_id:
                return trace

        raise FileNotFoundError(f"Trace not found: {trace_id}")

    def _generate_mock_traces(
        self, date: Optional[str] = None, agent: Optional[str] = None, count: int = 50
    ) -> List[ExecutionTrace]:
        """Generate mock traces for demo.

        Args:
            date: Date filter
            agent: Agent filter
            count: Number of traces to generate

        Returns:
            List of mock ExecutionTrace objects
        """
        agents = [
            "user_interpret",
            "assistant",
            "code_searcher",
            "code_developer",
            "project_manager",
        ]
        if agent:
            agents = [agent]

        queries = [
            "Implement user authentication feature",
            "Fix bug in database connection pooling",
            "Add unit tests for API endpoints",
            "Optimize query performance",
            "Update documentation for new features",
            "Refactor legacy code module",
            "Add logging to critical operations",
            "Implement caching layer",
            "Fix security vulnerability in input validation",
            "Add error handling for edge cases",
        ]

        traces = []
        base_time = datetime.now() if not date else datetime.fromisoformat(date)

        for i in range(count):
            trace_id = f"trace_{i:04d}"
            agent_name = random.choice(agents)
            timestamp = base_time - timedelta(hours=random.randint(0, 72))
            user_query = random.choice(queries)

            # Generate 1-3 executions per trace
            num_executions = random.randint(1, 3)
            executions = []

            for j in range(num_executions):
                exec_id = f"{trace_id}_exec_{j}"
                result_status = random.choices(["success", "failure", "error"], weights=[0.85, 0.10, 0.05])[0]

                execution = Execution(
                    execution_id=exec_id,
                    prompt=f"Process: {user_query}",
                    input_data={"query": user_query, "context": {}},
                    output=(f"Completed {user_query}" if result_status == "success" else "Failed to complete"),
                    result_status=result_status,
                    duration_seconds=random.uniform(0.5, 15.0),
                    metadata={"iteration": j + 1},
                )
                executions.append(execution)

            trace = ExecutionTrace(
                trace_id=trace_id,
                timestamp=timestamp,
                agent_identity={"target_agent": agent_name, "version": "1.0"},
                user_query=user_query,
                executions=executions,
                context={"session_id": f"session_{i % 10}"},
            )
            traces.append(trace)

        return traces
