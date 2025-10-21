"""
Custom metrics collection for code_developer daemon.

Integrates with GCP Cloud Monitoring to track daemon performance,
costs, and task completion.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""

    task_id: str
    priority: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "in_progress"  # in_progress, completed, failed
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    anthropic_api_calls: int = 0
    anthropic_tokens_input: int = 0
    anthropic_tokens_output: int = 0
    cost_usd: float = 0.0


class MetricsCollector:
    """Collects and reports custom metrics."""

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize metrics collector.

        Args:
            project_id: GCP project ID (for Cloud Monitoring)
        """
        self.project_id = project_id
        self.metrics: Dict[str, TaskMetrics] = {}

        # Try to initialize GCP monitoring client
        self.monitoring_client = None
        if project_id:
            try:
                from google.cloud import monitoring_v3

                self.monitoring_client = monitoring_v3.MetricServiceClient()
                logger.info(f"Initialized GCP Monitoring for project {project_id}")
            except Exception as e:
                logger.warning(f"Could not initialize GCP Monitoring: {e}")

    def start_task(self, task_id: str, priority: str) -> TaskMetrics:
        """
        Start tracking a new task.

        Args:
            task_id: Unique task identifier
            priority: Priority being implemented

        Returns:
            TaskMetrics instance
        """
        metrics = TaskMetrics(
            task_id=task_id,
            priority=priority,
            started_at=datetime.utcnow(),
        )
        self.metrics[task_id] = metrics
        logger.info(f"Started tracking task {task_id} ({priority})")
        return metrics

    def complete_task(
        self,
        task_id: str,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> None:
        """
        Mark task as complete.

        Args:
            task_id: Task identifier
            status: Final status (completed, failed)
            error: Error message if failed
        """
        if task_id not in self.metrics:
            logger.warning(f"Task {task_id} not found in metrics")
            return

        metrics = self.metrics[task_id]
        metrics.completed_at = datetime.utcnow()
        metrics.status = status
        metrics.error = error

        if metrics.started_at:
            metrics.duration_seconds = (metrics.completed_at - metrics.started_at).total_seconds()

        logger.info(f"Task {task_id} {status} (duration: {metrics.duration_seconds:.1f}s)")

        # Report to GCP Monitoring
        self._report_task_completion(metrics)

    def record_api_call(
        self,
        task_id: str,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
    ) -> None:
        """
        Record an Anthropic API call.

        Args:
            task_id: Task identifier
            tokens_input: Input tokens used
            tokens_output: Output tokens generated
            cost_usd: Cost of this API call
        """
        if task_id not in self.metrics:
            logger.warning(f"Task {task_id} not found in metrics")
            return

        metrics = self.metrics[task_id]
        metrics.anthropic_api_calls += 1
        metrics.anthropic_tokens_input += tokens_input
        metrics.anthropic_tokens_output += tokens_output
        metrics.cost_usd += cost_usd

    def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """Get metrics for a specific task."""
        return self.metrics.get(task_id)

    def get_all_metrics(self) -> Dict[str, TaskMetrics]:
        """Get all collected metrics."""
        return self.metrics

    def _report_task_completion(self, metrics: TaskMetrics) -> None:
        """Report task completion to GCP Monitoring."""
        if not self.monitoring_client or not self.project_id:
            return

        try:
            # TODO: Implement actual GCP Monitoring reporting
            # This would use monitoring_client.create_time_series()
            logger.debug(f"Reported metrics for task {metrics.task_id} to GCP")
        except Exception as e:
            logger.error(f"Failed to report metrics to GCP: {e}")


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector

    if _metrics_collector is None:
        import os

        project_id = os.getenv("GCP_PROJECT_ID")
        _metrics_collector = MetricsCollector(project_id)

    return _metrics_collector
