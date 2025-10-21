"""AI Provider abstraction layer for multi-AI support.

This package provides a unified interface for working with multiple AI providers
(Claude, OpenAI, Gemini, etc.) allowing the autonomous code-developer daemon to
seamlessly switch between providers or use fallback strategies when needed.

Key Components:
    - BaseAIProvider: Abstract base class all providers implement
    - ProviderConfig: Configuration management for providers
    - Provider implementations: ClaudeProvider, OpenAIProvider, GeminiProvider
    - ProviderFactory: Factory for creating provider instances
    - FallbackStrategy: Smart fallback and retry logic

Quick Start:
    >>> from coffee_maker.ai_providers import get_provider
    >>> provider = get_provider()  # Gets default provider from config
    >>> result = provider.execute_prompt("Implement feature X")
    >>> print(result.content)

Configuration:
    Providers are configured via config/ai_providers.yaml. You can:
    - Set default provider
    - Configure API keys (via environment variables)
    - Enable/disable specific providers
    - Set cost limits
    - Configure fallback order

Example config/ai_providers.yaml:
    default_provider: claude
    providers:
      claude:
        enabled: true
        api_key_env: ANTHROPIC_API_KEY
        model: claude-sonnet-4-5-20250929
      openai:
        enabled: true
        api_key_env: OPENAI_API_KEY
        model: gpt-4-turbo

For complete documentation, see: docs/PRIORITY_8_MULTI_AI_PROVIDER_GUIDE.md
"""

from coffee_maker.ai_providers.base import (
    BaseAIProvider,
    ProviderCapability,
    ProviderResult,
)
from coffee_maker.ai_providers.fallback_strategy import (
    AllProvidersFailedError,
    FallbackStrategy,
    ProviderUnavailableError,
    RateLimitError,
)
from coffee_maker.ai_providers.provider_config import (
    CostConfig,
    FallbackConfig,
    ProviderConfig,
    ProviderConfigError,
)
from coffee_maker.ai_providers.provider_factory import (
    get_provider,
    list_available_providers,
    list_enabled_providers,
)

__all__ = [
    # Base classes
    "BaseAIProvider",
    "ProviderCapability",
    "ProviderResult",
    # Configuration
    "ProviderConfig",
    "ProviderConfigError",
    "FallbackConfig",
    "CostConfig",
    # Factory
    "get_provider",
    "list_enabled_providers",
    "list_available_providers",
    # Fallback strategy
    "FallbackStrategy",
    "RateLimitError",
    "ProviderUnavailableError",
    "AllProvidersFailedError",
]

__version__ = "1.0.0"
