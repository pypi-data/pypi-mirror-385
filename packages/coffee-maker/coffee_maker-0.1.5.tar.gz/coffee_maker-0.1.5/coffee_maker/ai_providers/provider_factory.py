"""Provider factory for creating AI provider instances.

This module provides factory functions for instantiating the correct provider
based on configuration. It handles provider selection, configuration loading,
and validation.

Example:
    >>> from coffee_maker.ai_providers.provider_factory import get_provider
    >>> provider = get_provider()  # Gets default provider
    >>> result = provider.execute_prompt("Write a function")

    >>> # Get specific provider
    >>> openai_provider = get_provider('openai')
    >>> result = openai_provider.execute_prompt("Write a function")
"""

import logging
from typing import List, Optional

from coffee_maker.ai_providers.base import BaseAIProvider
from coffee_maker.ai_providers.provider_config import ProviderConfig
from coffee_maker.ai_providers.providers.claude_provider import ClaudeProvider
from coffee_maker.ai_providers.providers.gemini_provider import GeminiProvider
from coffee_maker.ai_providers.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


# Provider registry - maps provider names to classes
PROVIDER_REGISTRY = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


class ProviderNotFoundError(Exception):
    """Raised when requested provider is not found."""


class ProviderNotEnabledError(Exception):
    """Raised when requested provider is not enabled in config."""


def get_provider(provider_name: Optional[str] = None, config: Optional[ProviderConfig] = None) -> BaseAIProvider:
    """Get an AI provider instance.

    This is the main factory function for creating provider instances.
    It handles loading configuration, validating provider availability,
    and instantiating the correct provider class.

    Args:
        provider_name: Name of provider to create (e.g., 'claude', 'openai', 'gemini').
                      If None, uses default provider from config.
        config: ProviderConfig instance. If None, loads from config/ai_providers.yaml.

    Returns:
        Instantiated provider (ClaudeProvider, OpenAIProvider, or GeminiProvider)

    Raises:
        ProviderNotFoundError: If provider name is not in registry
        ProviderNotEnabledError: If provider is not enabled in config
        ProviderConfigError: If configuration is invalid

    Example:
        >>> # Get default provider
        >>> provider = get_provider()
        >>> print(provider.name)  # 'claude'

        >>> # Get specific provider
        >>> openai = get_provider('openai')
        >>> print(openai.name)  # 'openai'

        >>> # Use custom config
        >>> custom_config = ProviderConfig('my_config.yaml')
        >>> provider = get_provider(config=custom_config)
    """
    # Load configuration if not provided
    if config is None:
        config = ProviderConfig()

    # Use default provider if none specified
    if provider_name is None:
        provider_name = config.default_provider
        logger.info(f"Using default provider: {provider_name}")

    # Validate provider exists in registry
    if provider_name not in PROVIDER_REGISTRY:
        available = list(PROVIDER_REGISTRY.keys())
        raise ProviderNotFoundError(f"Provider '{provider_name}' not found. " f"Available providers: {available}")

    # Check if provider is enabled
    if not config.is_provider_enabled(provider_name):
        raise ProviderNotEnabledError(
            f"Provider '{provider_name}' is not enabled in config. " f"Set 'enabled: true' in config/ai_providers.yaml"
        )

    # Get provider configuration
    provider_config = config.get_provider_config(provider_name)

    # Instantiate provider
    provider_class = PROVIDER_REGISTRY[provider_name]
    provider = provider_class(provider_config)

    logger.info(f"Created provider: {provider_name} (model={provider.model})")
    return provider


def list_enabled_providers(config: Optional[ProviderConfig] = None) -> List[str]:
    """Get list of enabled providers from configuration.

    Args:
        config: ProviderConfig instance. If None, loads from default location.

    Returns:
        List of enabled provider names

    Example:
        >>> providers = list_enabled_providers()
        >>> print(providers)  # ['claude', 'openai', 'gemini']
    """
    if config is None:
        config = ProviderConfig()

    return config.get_enabled_providers()


def list_available_providers(config: Optional[ProviderConfig] = None, check_connectivity: bool = False) -> List[str]:
    """Get list of available providers (enabled AND accessible).

    This function checks which providers are both enabled in config
    and actually accessible (API key set, service reachable).

    Args:
        config: ProviderConfig instance. If None, loads from default location.
        check_connectivity: If True, test connectivity to each provider.
                           If False, only check if API keys are set.

    Returns:
        List of available provider names

    Example:
        >>> # Quick check (API keys only)
        >>> providers = list_available_providers()
        >>> print(providers)  # ['claude', 'openai']

        >>> # Full check (including connectivity)
        >>> providers = list_available_providers(check_connectivity=True)
        >>> print(providers)  # ['claude', 'openai']  # gemini excluded if unreachable
    """
    if config is None:
        config = ProviderConfig()

    available = []

    for provider_name in config.get_enabled_providers():
        try:
            # Try to create provider instance
            provider = get_provider(provider_name, config)

            # If check_connectivity is True, test the provider
            if check_connectivity:
                if provider.check_available():
                    available.append(provider_name)
                    logger.info(f"Provider '{provider_name}' is available")
                else:
                    logger.warning(f"Provider '{provider_name}' is enabled but not accessible")
            else:
                # Just check if API key is set
                api_key = config.get_api_key(provider_name)
                if api_key:
                    available.append(provider_name)
                    logger.info(f"Provider '{provider_name}' API key is set")
                else:
                    logger.warning(f"Provider '{provider_name}' API key not set")

        except Exception as e:
            logger.warning(f"Provider '{provider_name}' not available: {e}")

    return available


def register_provider(provider_name: str, provider_class: type):
    """Register a new provider class.

    This allows adding custom providers at runtime without modifying
    the factory code. Useful for plugins or custom AI backends.

    Args:
        provider_name: Name to register provider under (e.g., 'my_custom_ai')
        provider_class: Provider class (must inherit from BaseAIProvider)

    Raises:
        TypeError: If provider_class doesn't inherit from BaseAIProvider

    Example:
        >>> class MyCustomProvider(BaseAIProvider):
        ...     # Implementation here
        ...     pass
        >>>
        >>> register_provider('my_ai', MyCustomProvider)
        >>> provider = get_provider('my_ai')
    """
    if not issubclass(provider_class, BaseAIProvider):
        raise TypeError(f"Provider class must inherit from BaseAIProvider, " f"got {provider_class.__name__}")

    PROVIDER_REGISTRY[provider_name] = provider_class
    logger.info(f"Registered provider: {provider_name} -> {provider_class.__name__}")


def get_provider_registry() -> dict:
    """Get the current provider registry.

    Returns:
        Dictionary mapping provider names to provider classes

    Example:
        >>> registry = get_provider_registry()
        >>> print(registry.keys())  # dict_keys(['claude', 'openai', 'gemini'])
    """
    return PROVIDER_REGISTRY.copy()
