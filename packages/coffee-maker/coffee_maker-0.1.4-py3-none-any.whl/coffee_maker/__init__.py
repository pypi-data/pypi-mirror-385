"""Coffee Maker Agent - Production-Ready LLM Orchestration Framework.

Coffee Maker Agent is a comprehensive framework for building, deploying, and monitoring
AI-powered applications with multiple LLM providers. It provides:

- **Multi-Provider Support**: Seamlessly work with Claude, GPT, Gemini, and more
- **Intelligent Fallback**: Automatic failover between providers and models
- **Cost Optimization**: Built-in cost tracking and optimization
- **Rate Limiting**: Robust rate limit handling and quotas
- **Observability**: Deep integration with Langfuse for monitoring
- **Production-Ready**: Error handling, retries, and reliability features

## Quick Start

```python
from coffee_maker.auto_picker_llm_refactored import AutoPickerLLM

# Initialize with automatic model selection
llm = AutoPickerLLM(
    model_list=["claude-sonnet-4", "gpt-4-turbo"],
    fallback_strategy="cost_optimized"
)

# Generate text
response = llm.generate("Explain quantum computing")
print(response)

# Streaming support
for chunk in llm.generate_stream("Write a story"):
    print(chunk, end="", flush=True)
```

## Key Components

### AutoPickerLLM
The main entry point for LLM interactions. Automatically selects the best model
based on your strategy (cost, performance, reliability).

```python
from coffee_maker.auto_picker_llm_refactored import AutoPickerLLM

llm = AutoPickerLLM(
    model_list=["claude-sonnet-4", "gpt-4-turbo", "gemini-pro"],
    fallback_strategy="intelligent",  # or "cost_optimized", "reliability_first"
    max_retries=3
)
```

### Fallback Strategies
Intelligent strategies for handling failures and optimizing performance:

- **Intelligent**: Learns from past performance and adapts
- **Cost Optimized**: Prioritizes cheaper models when quality is acceptable
- **Reliability First**: Prioritizes most reliable models
- **Round Robin**: Distributes load evenly

```python
from coffee_maker.strategies.fallback import IntelligentFallbackStrategy

strategy = IntelligentFallbackStrategy(
    primary_models=["claude-sonnet-4"],
    fallback_models=["gpt-4-turbo", "gpt-3.5-turbo"],
    success_threshold=0.95
)
```

### Cost Calculator
Track and optimize LLM usage costs:

```python
from coffee_maker.cost_calculator import CostCalculator

calculator = CostCalculator()

# Get cost for a completion
cost = calculator.calculate_cost(
    model="claude-sonnet-4",
    input_tokens=1000,
    output_tokens=500
)

print(f"Cost: ${cost:.4f}")
```

### Langfuse Integration
Built-in observability and monitoring:

```python
from coffee_maker.langfuse_observe import LangfuseObserver

observer = LangfuseObserver(
    project_name="my-project",
    environment="production"
)

# Automatically tracks all LLM calls
observer.start()
```

## Architecture

```
coffee_maker/
├── auto_picker_llm_refactored.py   # Main LLM interface
├── builder.py                      # LLM instance builder
├── strategies/                     # Fallback strategies
│   ├── fallback.py                # Strategy implementations
│   └── cost_optimizer.py          # Cost optimization
├── llm.py                          # Base LLM abstractions
├── cost_calculator.py              # Cost tracking
├── scheduled_llm.py                # Rate limiting and quotas
├── langfuse_observe/              # Observability
│   ├── analytics/                  # Analytics and reporting
│   └── exporters/                  # Data export utilities
├── autonomous/                     # Autonomous development daemon
│   ├── daemon.py                  # Main daemon loop
│   ├── roadmap_parser.py          # Roadmap parsing
│   └── git_manager.py             # Git operations
├── cli/                           # Command-line interfaces
│   ├── roadmap_cli.py            # Project manager CLI
│   └── notifications.py           # Notification system
└── streamlit_apps/                # Web interfaces
    └── agent_interface/           # Chat interface
```

## Features

### Multi-Provider Support
Work with multiple LLM providers seamlessly:

- **Anthropic Claude**: claude-3, claude-sonnet-4, claude-opus-4
- **OpenAI GPT**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Google Gemini**: gemini-pro, gemini-ultra
- **More**: Easily add custom providers

### Intelligent Fallback
Automatic failover when models fail:

1. Primary model fails → Try next model in list
2. All models in tier fail → Fall back to cheaper tier
3. Learn from failures → Adjust strategy dynamically

### Cost Optimization
Built-in cost tracking and optimization:

- Real-time cost calculation
- Cost-based model selection
- Budget limits and quotas
- Usage analytics

### Observability
Deep integration with Langfuse:

- Trace all LLM calls
- Track performance metrics
- Analyze costs over time
- Debug issues easily

### Production-Ready
Built for production use:

- Automatic retries with exponential backoff
- Rate limit handling
- Quota management
- Error recovery
- Comprehensive logging

## Advanced Usage

### Custom Fallback Strategy

```python
from coffee_maker.strategies.fallback import BaseFallbackStrategy

class MyStrategy(BaseFallbackStrategy):
    def select_model(self, context):
        # Custom logic here
        return "claude-sonnet-4"

    def handle_failure(self, model, error):
        # Custom failure handling
        pass
```

### Cost Budgets

```python
from coffee_maker.scheduled_llm import ScheduledLLM

llm = ScheduledLLM(
    model="claude-sonnet-4",
    daily_budget=10.00,  # $10/day limit
    quota_per_hour=1000   # Max 1000 tokens/hour
)
```

### Streaming with Observability

```python
from coffee_maker.auto_picker_llm_refactored import AutoPickerLLM
from coffee_maker.langfuse_observe import trace

@trace(name="story-generator")
def generate_story(prompt):
    llm = AutoPickerLLM()
    for chunk in llm.generate_stream(prompt):
        yield chunk

# Automatically traced in Langfuse
for chunk in generate_story("Write a sci-fi story"):
    print(chunk, end="")
```

## Configuration

### Environment Variables

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Langfuse (optional)
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."

# Custom settings
export COFFEE_MAKER_DEFAULT_MODEL="claude-sonnet-4"
export COFFEE_MAKER_MAX_RETRIES="3"
export COFFEE_MAKER_TIMEOUT="30"
```

### Configuration File

Create `coffee_maker.yaml`:

```yaml
models:
  primary:
    - claude-sonnet-4
    - gpt-4-turbo
  fallback:
    - gpt-3.5-turbo

strategies:
  default: intelligent
  cost_threshold: 0.01

observability:
  langfuse:
    enabled: true
    project: my-project

rate_limits:
  claude: 100000  # tokens/hour
  openai: 150000
```

## Examples

See `examples/` directory for complete examples:

- `examples/basic_usage.py` - Getting started
- `examples/streaming.py` - Streaming responses
- `examples/fallback.py` - Fallback strategies
- `examples/cost_optimization.py` - Cost tracking
- `examples/observability.py` - Langfuse integration

## Documentation

- **API Docs**: https://bobain.github.io/MonolithicCoffeeMakerAgent/
- **User Guide**: `docs/USER_GUIDE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Contributing**: `CONTRIBUTING.md`

## Support

- **Issues**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/issues
- **Discussions**: https://github.com/Bobain/MonolithicCoffeeMakerAgent/discussions

## License

See `LICENSE` file.

---

**Built with coffee by the Coffee Maker Agent team**
"""

from typing import List

__version__: str = "1.0.0"
__author__: str = "Coffee Maker Agent Team"
__license__: str = "MIT"

# Public API exports
__all__: List[str] = [
    # Core LLM interface
    "AutoPickerLLM",
    # Strategies
    "IntelligentFallbackStrategy",
    "CostOptimizedStrategy",
    # Cost tracking
    "CostCalculator",
    # Observability
    "LangfuseObserver",
    # Version info
    "__version__",
]

# Note: Actual imports would go here in a production setup
# For now, we keep the package lightweight and allow explicit imports
