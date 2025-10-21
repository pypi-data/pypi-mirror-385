"""LangChain Observe - Production-ready LLM orchestration framework.

This module provides a comprehensive framework for managing LLM interactions with:

- **Intelligent Fallbacks**: Automatic failover between models
- **Rate Limiting**: Proactive scheduling to avoid API limits
- **Cost Tracking**: Monitor and budget LLM usage costs
- **Metrics Collection**: Pluggable metrics backends (Prometheus, local)
- **HTTP Pooling**: Efficient connection reuse
- **Context Management**: Automatic handling of context length limits

## Quick Start

```python
from coffee_maker.langfuse_observe import create_auto_picker_llm_refactored

# Create LLM with fallback support
llm = create_auto_picker_llm_refactored(
    provider="openai",
    model="gpt-4o",
    tier="tier1"
)

# Use it
response = llm.invoke("Your prompt here")
```

## Main Components

- `AutoPickerLLMRefactored`: Smart LLM with fallback orchestration
- `ScheduledLLM`: Rate-limited LLM wrapper
- `LLMBuilder` / `SmartLLM`: Fluent builder pattern for LLM construction
- `strategies`: Pluggable strategies for fallback, metrics, scheduling, context

## Strategies

### Fallback Strategies
- `SequentialFallback`: Try fallbacks in order
- `SmartFallback`: Intelligent selection based on error type
- `CostOptimizedFallback`: Cost-aware fallback selection

### Metrics Strategies
- `LocalMetrics`: In-memory metrics collection
- `PrometheusMetrics`: Prometheus integration
- `NoOpMetrics`: Disabled metrics for minimal overhead

### Scheduling Strategies
- `ProactiveRateLimitScheduler`: Stay under rate limits proactively
- `SimpleScheduler`: Basic scheduling

## Advanced Usage

```python
from coffee_maker.langfuse_observe.strategies.metrics import LocalMetrics
from coffee_maker.langfuse_observe.cost_budget import create_budget_enforcer
from coffee_maker.langfuse_observe.http_pool import get_http_client

# Setup metrics and budgets
metrics = LocalMetrics()
budget = create_budget_enforcer(daily_budget=10.0)
http_client = get_http_client()

# Create LLM with all features
llm = create_auto_picker_llm_refactored(
    provider="openai",
    model="gpt-4o",
    tier="tier1",
    metrics_strategy=metrics
)

# Monitor usage
print(metrics.get_metrics())
print(budget.get_budget_status())
```

## Documentation

Full API documentation available at: https://bobain.github.io/MonolithicCoffeeMakerAgent/
"""

from typing import List

from coffee_maker.langfuse_observe.auto_picker_llm_refactored import (
    AutoPickerLLMRefactored,
    create_auto_picker_llm_refactored,
)
from coffee_maker.langfuse_observe.builder import LLMBuilder, SmartLLM
from coffee_maker.langfuse_observe.scheduled_llm import ScheduledLLM
from coffee_maker.langfuse_observe.cost_calculator import CostCalculator
from coffee_maker.langfuse_observe.cost_budget import (
    CostBudgetEnforcer,
    create_budget_enforcer,
)
from coffee_maker.langfuse_observe.http_pool import (
    get_http_client,
    get_async_http_client,
)

__all__: List[str] = [
    "AutoPickerLLMRefactored",
    "create_auto_picker_llm_refactored",
    "LLMBuilder",
    "SmartLLM",
    "ScheduledLLM",
    "CostCalculator",
    "CostBudgetEnforcer",
    "create_budget_enforcer",
    "get_http_client",
    "get_async_http_client",
]
