"""Configuration management for AI providers.

This module handles loading and validating provider configuration from:
1. config/ai_providers.yaml (primary config file)
2. Environment variables (overrides)
3. Default values (fallback)

Example:
    >>> from coffee_maker.ai_providers.provider_config import ProviderConfig
    >>> config = ProviderConfig()
    >>> print(config.default_provider)  # 'claude'
    >>> print(config.get_provider_config('openai'))  # OpenAI config dict
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class FallbackConfig:
    """Fallback configuration.

    Attributes:
        enabled: Whether fallback is enabled
        retry_attempts: Number of retry attempts per provider
        fallback_order: List of provider names to try in order
        retry_delay: Initial retry delay in seconds
        max_retry_delay: Maximum retry delay in seconds (for exponential backoff)
    """

    enabled: bool = True
    retry_attempts: int = 3
    fallback_order: List[str] = field(default_factory=lambda: ["claude", "openai", "gemini"])
    retry_delay: float = 1.0
    max_retry_delay: float = 60.0


@dataclass
class CostConfig:
    """Cost control configuration.

    Attributes:
        daily_limit: Maximum USD per day across all providers
        per_task_limit: Maximum USD per single task
        warn_threshold: Warn when reaching this fraction of limits (0.0-1.0)
        tracking_file: Path to cost tracking JSON file
    """

    daily_limit: float = 50.0
    per_task_limit: float = 5.0
    warn_threshold: float = 0.8
    tracking_file: str = "data/cost_tracking.json"


class ProviderConfigError(Exception):
    """Raised when provider configuration is invalid."""


class ProviderConfig:
    """Manages AI provider configuration.

    Loads configuration from config/ai_providers.yaml and validates it.
    Supports environment variable overrides for API keys and default provider.

    Attributes:
        config_file: Path to ai_providers.yaml
        data: Loaded configuration data
        default_provider: Default provider name
        fallback_config: Fallback configuration
        cost_config: Cost control configuration

    Example:
        >>> config = ProviderConfig()
        >>> if config.is_provider_enabled('claude'):
        ...     claude_cfg = config.get_provider_config('claude')
        ...     print(f"Model: {claude_cfg['model']}")
    """

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_file: Path to ai_providers.yaml (default: config/ai_providers.yaml)

        Raises:
            ProviderConfigError: If config file is missing or invalid
        """
        if config_file is None:
            # Find config file relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config" / "ai_providers.yaml"

        self.config_file = Path(config_file)
        self.data = self._load_config()
        self._validate_config()

        # Extract key configurations
        self.default_provider = self._get_default_provider()
        self.fallback_config = self._load_fallback_config()
        self.cost_config = self._load_cost_config()

        logger.info(f"Provider config loaded: default={self.default_provider}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            ProviderConfigError: If file doesn't exist or can't be parsed
        """
        if not self.config_file.exists():
            raise ProviderConfigError(
                f"Configuration file not found: {self.config_file}\n"
                f"Please create config/ai_providers.yaml from the example in docs/"
            )

        try:
            with open(self.config_file, "r") as f:
                data = yaml.safe_load(f)
                if not data:
                    raise ProviderConfigError("Configuration file is empty")
                return data
        except yaml.YAMLError as e:
            raise ProviderConfigError(f"Invalid YAML in {self.config_file}: {e}")

    def _validate_config(self):
        """Validate configuration structure.

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        if "providers" not in self.data:
            raise ProviderConfigError("Missing 'providers' section in config")

        if not self.data["providers"]:
            raise ProviderConfigError("No providers configured")

        # Validate each provider has required fields
        for provider_name, provider_config in self.data["providers"].items():
            required_fields = ["enabled", "model", "api_key_env"]
            missing = [f for f in required_fields if f not in provider_config]
            if missing:
                raise ProviderConfigError(f"Provider '{provider_name}' missing required fields: {missing}")

    def _get_default_provider(self) -> str:
        """Get default provider from config or environment.

        Environment variable DEFAULT_AI_PROVIDER overrides config file.

        Returns:
            Provider name

        Raises:
            ProviderConfigError: If default provider is not configured
        """
        # Check environment variable first
        env_provider = os.getenv("DEFAULT_AI_PROVIDER")
        if env_provider:
            if env_provider not in self.data["providers"]:
                raise ProviderConfigError(f"DEFAULT_AI_PROVIDER={env_provider} not in configured providers")
            return env_provider

        # Fall back to config file
        default = self.data.get("default_provider", "claude")
        if default not in self.data["providers"]:
            raise ProviderConfigError(f"default_provider={default} not in configured providers")
        return default

    def _load_fallback_config(self) -> FallbackConfig:
        """Load fallback configuration.

        Returns:
            FallbackConfig instance
        """
        fallback_data = self.data.get("fallback", {})
        return FallbackConfig(
            enabled=fallback_data.get("enabled", True),
            retry_attempts=fallback_data.get("retry_attempts", 3),
            fallback_order=fallback_data.get("fallback_order", ["claude", "openai", "gemini"]),
            retry_delay=fallback_data.get("retry_delay", 1.0),
            max_retry_delay=fallback_data.get("max_retry_delay", 60.0),
        )

    def _load_cost_config(self) -> CostConfig:
        """Load cost control configuration.

        Returns:
            CostConfig instance
        """
        cost_data = self.data.get("cost_controls", {})
        return CostConfig(
            daily_limit=cost_data.get("daily_limit", 50.0),
            per_task_limit=cost_data.get("per_task_limit", 5.0),
            warn_threshold=cost_data.get("warn_threshold", 0.8),
            tracking_file=cost_data.get("tracking_file", "data/cost_tracking.json"),
        )

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider.

        Args:
            provider_name: Provider name (e.g., 'claude', 'openai')

        Returns:
            Provider configuration dictionary

        Raises:
            ProviderConfigError: If provider is not configured
        """
        if provider_name not in self.data["providers"]:
            raise ProviderConfigError(f"Provider '{provider_name}' not configured")

        return self.data["providers"][provider_name]

    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a provider is enabled.

        Args:
            provider_name: Provider name

        Returns:
            True if provider is enabled and configured
        """
        try:
            config = self.get_provider_config(provider_name)
            return config.get("enabled", False)
        except ProviderConfigError:
            return False

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers.

        Returns:
            List of provider names that are enabled
        """
        return [name for name, config in self.data["providers"].items() if config.get("enabled", False)]

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider from environment.

        Args:
            provider_name: Provider name

        Returns:
            API key string or None if not set
        """
        config = self.get_provider_config(provider_name)
        env_var = config["api_key_env"]
        return os.getenv(env_var)

    def __repr__(self) -> str:
        """String representation."""
        enabled = self.get_enabled_providers()
        return f"<ProviderConfig(default={self.default_provider}, enabled={enabled})>"
