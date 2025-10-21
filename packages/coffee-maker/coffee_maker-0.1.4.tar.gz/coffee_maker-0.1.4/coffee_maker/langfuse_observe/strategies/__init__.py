"""Pluggable strategies for LLM orchestration.

## Available Strategies

### Fallback Strategies
Handle model failover and redundancy:
- `SequentialFallback`: Try models in order
- `SmartFallback`: Intelligent selection based on error type
- `CostOptimizedFallback`: Choose based on cost/quality tradeoff

### Metrics Strategies
Collect and report usage metrics:
- `LocalMetrics`: In-memory collection
- `PrometheusMetrics`: Prometheus integration
- `NoOpMetrics`: Disabled for minimal overhead

### Scheduling Strategies
Manage rate limits proactively:
- `ProactiveRateLimitScheduler`: Stay N-2 under limits
- `SimpleScheduler`: Basic scheduling

### Retry Strategies
Handle transient failures:
- `ExponentialBackoffRetry`: Standard exponential backoff
- `ContextualRetry`: Retry based on error type

### Context Strategies
Manage context length limits:
- `LargeContextFallbackStrategy`: Automatic fallback to larger context models
- `NoContextCheckStrategy`: Disable context checking
- `ContextTruncation`: Smart truncation (planned)

## Example Usage

```python
from coffee_maker.langfuse_observe.strategies.fallback import SmartFallback
from coffee_maker.langfuse_observe.strategies.metrics import LocalMetrics
from coffee_maker.langfuse_observe.strategies.scheduling import ProactiveRateLimitScheduler

# Create strategies
fallback = SmartFallback(fallback_models=["openai/gpt-4o-mini"])
metrics = LocalMetrics()
scheduler = ProactiveRateLimitScheduler(tier="tier1")

# Use with LLM
llm = AutoPickerLLMRefactored(
    primary_llm=primary,
    primary_model_name="openai/gpt-4o",
    fallback_llms=fallbacks,
    fallback_strategy=fallback,
    metrics_strategy=metrics
)
```
"""

from coffee_maker.langfuse_observe.strategies.retry import (
    RetryStrategy,
    ExponentialBackoffRetry,
)
from coffee_maker.langfuse_observe.strategies.scheduling import (
    SchedulingStrategy,
    ProactiveRateLimitScheduler,
)
from coffee_maker.langfuse_observe.strategies.fallback import (
    FallbackStrategy,
    SequentialFallback,
    SmartFallback,
    CostOptimizedFallback,
)
from coffee_maker.langfuse_observe.strategies.metrics import (
    MetricsStrategy,
    LocalMetrics,
    PrometheusMetrics,
    NoOpMetrics,
    create_metrics_strategy,
)
from coffee_maker.langfuse_observe.strategies.context import (
    ContextStrategy,
    LargeContextFallbackStrategy,
    NoContextCheckStrategy,
)

from typing import List

__all__: List[str] = [
    # Retry
    "RetryStrategy",
    "ExponentialBackoffRetry",
    # Scheduling
    "SchedulingStrategy",
    "ProactiveRateLimitScheduler",
    # Fallback
    "FallbackStrategy",
    "SequentialFallback",
    "SmartFallback",
    "CostOptimizedFallback",
    # Metrics
    "MetricsStrategy",
    "LocalMetrics",
    "PrometheusMetrics",
    "NoOpMetrics",
    "create_metrics_strategy",
    # Context
    "ContextStrategy",
    "LargeContextFallbackStrategy",
    "NoContextCheckStrategy",
]
