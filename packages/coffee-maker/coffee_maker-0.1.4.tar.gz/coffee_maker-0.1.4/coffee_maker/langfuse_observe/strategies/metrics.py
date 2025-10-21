"""Metrics collection strategies for LLM monitoring.

This module provides pluggable metrics strategies for collecting and reporting
LLM usage metrics to various backends (Prometheus, Datadog, local, etc.).
"""

import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class MetricRecord:
    """Record of a single metric event."""

    timestamp: float
    model: str
    metric_type: str  # "request", "error", "cost", "latency"
    value: float
    labels: Dict[str, str]


class MetricsStrategy(ABC):
    """Abstract base class for metrics collection strategies."""

    @abstractmethod
    def record_request(
        self,
        model: str,
        latency: float,
        tokens: int,
        is_primary: bool = True,
        success: bool = True,
    ) -> None:
        """Record an LLM request."""

    @abstractmethod
    def record_error(self, model: str, error_type: str, error_message: str) -> None:
        """Record an error."""

    @abstractmethod
    def record_cost(self, model: str, cost: float, tokens: int) -> None:
        """Record cost."""

    @abstractmethod
    def record_fallback(self, from_model: str, to_model: str, reason: str) -> None:
        """Record a fallback event."""

    @abstractmethod
    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""


class LocalMetrics(MetricsStrategy):
    """In-memory metrics collection (current behavior).

    Stores metrics in memory for local analysis and reporting.
    Suitable for development and testing.
    """

    def __init__(self):
        """Initialize local metrics collector."""
        self._records: List[MetricRecord] = []
        self._request_count = defaultdict(int)
        self._error_count = defaultdict(int)
        self._total_cost = defaultdict(float)
        self._total_latency = defaultdict(float)
        self._total_tokens = defaultdict(int)
        self._fallback_count = defaultdict(int)

    def record_request(
        self,
        model: str,
        latency: float,
        tokens: int,
        is_primary: bool = True,
        success: bool = True,
    ) -> None:
        """Record an LLM request."""
        self._request_count[model] += 1
        self._total_latency[model] += latency
        self._total_tokens[model] += tokens

        self._records.append(
            MetricRecord(
                timestamp=time.time(),
                model=model,
                metric_type="request",
                value=1.0,
                labels={
                    "is_primary": str(is_primary),
                    "success": str(success),
                    "latency": str(latency),
                    "tokens": str(tokens),
                },
            )
        )

    def record_error(self, model: str, error_type: str, error_message: str) -> None:
        """Record an error."""
        self._error_count[f"{model}:{error_type}"] += 1

        self._records.append(
            MetricRecord(
                timestamp=time.time(),
                model=model,
                metric_type="error",
                value=1.0,
                labels={"error_type": error_type, "message": error_message[:100]},
            )
        )

    def record_cost(self, model: str, cost: float, tokens: int) -> None:
        """Record cost."""
        self._total_cost[model] += cost

        self._records.append(
            MetricRecord(
                timestamp=time.time(),
                model=model,
                metric_type="cost",
                value=cost,
                labels={"tokens": str(tokens)},
            )
        )

    def record_fallback(self, from_model: str, to_model: str, reason: str) -> None:
        """Record a fallback event."""
        self._fallback_count[f"{from_model}->{to_model}"] += 1

        self._records.append(
            MetricRecord(
                timestamp=time.time(),
                model=from_model,
                metric_type="fallback",
                value=1.0,
                labels={"to_model": to_model, "reason": reason},
            )
        )

    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            "requests": dict(self._request_count),
            "errors": dict(self._error_count),
            "costs": dict(self._total_cost),
            "latencies": dict(self._total_latency),
            "tokens": dict(self._total_tokens),
            "fallbacks": dict(self._fallback_count),
            "total_records": len(self._records),
        }

    def get_average_latency(self, model: str) -> float:
        """Get average latency for a model."""
        if self._request_count[model] == 0:
            return 0.0
        return self._total_latency[model] / self._request_count[model]

    def get_total_cost(self) -> float:
        """Get total cost across all models."""
        return sum(self._total_cost.values())

    def reset(self) -> None:
        """Reset all metrics."""
        self._records.clear()
        self._request_count.clear()
        self._error_count.clear()
        self._total_cost.clear()
        self._total_latency.clear()
        self._total_tokens.clear()
        self._fallback_count.clear()


class PrometheusMetrics(MetricsStrategy):
    """Prometheus metrics collector.

    Exports metrics in Prometheus format for scraping.
    Requires prometheus_client library.
    """

    def __init__(self, registry=None):
        """Initialize Prometheus metrics."""
        try:
            from prometheus_client import Counter, Histogram, Gauge

            self.Counter = Counter
            self.Histogram = Histogram
            self.Gauge = Gauge
            self.registry = registry

            # Define metrics
            self.request_counter = Counter(
                "llm_requests_total",
                "Total LLM requests",
                ["model", "is_primary", "success"],
                registry=registry,
            )

            self.error_counter = Counter(
                "llm_errors_total",
                "Total LLM errors",
                ["model", "error_type"],
                registry=registry,
            )

            self.latency_histogram = Histogram(
                "llm_latency_seconds",
                "LLM request latency",
                ["model"],
                registry=registry,
            )

            self.cost_counter = Counter(
                "llm_cost_usd_total",
                "Total LLM cost in USD",
                ["model"],
                registry=registry,
            )

            self.tokens_counter = Counter(
                "llm_tokens_total",
                "Total tokens processed",
                ["model"],
                registry=registry,
            )

            self.fallback_counter = Counter(
                "llm_fallbacks_total",
                "Total fallback events",
                ["from_model", "to_model", "reason"],
                registry=registry,
            )

            logger.info("Prometheus metrics initialized")

        except ImportError:
            logger.warning("prometheus_client not installed, metrics will be no-op")
            self._enabled = False
        else:
            self._enabled = True

    def record_request(
        self,
        model: str,
        latency: float,
        tokens: int,
        is_primary: bool = True,
        success: bool = True,
    ) -> None:
        """Record an LLM request."""
        if not self._enabled:
            return

        self.request_counter.labels(model=model, is_primary=str(is_primary), success=str(success)).inc()
        self.latency_histogram.labels(model=model).observe(latency)
        self.tokens_counter.labels(model=model).inc(tokens)

    def record_error(self, model: str, error_type: str, error_message: str) -> None:
        """Record an error."""
        if not self._enabled:
            return

        self.error_counter.labels(model=model, error_type=error_type).inc()

    def record_cost(self, model: str, cost: float, tokens: int) -> None:
        """Record cost."""
        if not self._enabled:
            return

        self.cost_counter.labels(model=model).inc(cost)

    def record_fallback(self, from_model: str, to_model: str, reason: str) -> None:
        """Record a fallback event."""
        if not self._enabled:
            return

        self.fallback_counter.labels(from_model=from_model, to_model=to_model, reason=reason).inc()

    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {"type": "prometheus", "enabled": self._enabled}


class NoOpMetrics(MetricsStrategy):
    """No-op metrics strategy that does nothing.

    Useful for disabling metrics collection entirely.
    """

    def record_request(
        self,
        model: str,
        latency: float,
        tokens: int,
        is_primary: bool = True,
        success: bool = True,
    ) -> None:
        """No-op."""

    def record_error(self, model: str, error_type: str, error_message: str) -> None:
        """No-op."""

    def record_cost(self, model: str, cost: float, tokens: int) -> None:
        """No-op."""

    def record_fallback(self, from_model: str, to_model: str, reason: str) -> None:
        """No-op."""

    def get_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {"type": "noop"}


def create_metrics_strategy(strategy_type: str = "local", **kwargs) -> MetricsStrategy:
    """Factory function to create metrics strategy.

    Args:
        strategy_type: Type of strategy ("local", "prometheus", "noop")
        **kwargs: Additional arguments for strategy initialization

    Returns:
        MetricsStrategy instance

    Example:
        >>> metrics = create_metrics_strategy("local")
        >>> metrics = create_metrics_strategy("prometheus")
        >>> metrics = create_metrics_strategy("noop")
    """
    if strategy_type == "local":
        return LocalMetrics()
    elif strategy_type == "prometheus":
        return PrometheusMetrics(**kwargs)
    elif strategy_type == "noop":
        return NoOpMetrics()
    else:
        logger.warning(f"Unknown metrics strategy: {strategy_type}, using local")
        return LocalMetrics()
