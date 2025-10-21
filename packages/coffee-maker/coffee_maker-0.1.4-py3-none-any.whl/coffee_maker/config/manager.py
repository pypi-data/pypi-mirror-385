"""Centralized configuration management for Coffee Maker Agent.

This module provides a single source of truth for all configuration needs:
- API key loading with consistent validation
- Environment variable access with fallbacks
- Configuration caching and validation

Example:
    >>> from coffee_maker.config import ConfigManager
    >>> api_key = ConfigManager.get_anthropic_api_key()
    >>> # Raises ConfigurationError if not found
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration or environment variable errors."""


class APIKeyMissingError(ConfigurationError):
    """Specific API key not found in environment."""

    def __init__(self, key_name: str, suggested_names: Optional[List[str]] = None):
        """Initialize with key name and optional suggestions.

        Args:
            key_name: Primary environment variable name
            suggested_names: Alternative names to check
        """
        self.key_name = key_name
        self.suggested_names = suggested_names or []
        message = f"API key '{key_name}' not found in environment"
        if self.suggested_names:
            message += f". Also checked: {', '.join(self.suggested_names)}"
        super().__init__(message)


class ConfigManager:
    """Centralized configuration management for all API keys and environment variables.

    This class provides static methods for accessing configuration with consistent
    validation, error handling, and fallback behavior.

    All methods follow the pattern:
    - Check environment variables
    - Apply fallbacks if configured
    - Raise appropriate errors if required and not found
    - Log access for debugging

    Example:
        >>> # Required API key (raises if not found)
        >>> api_key = ConfigManager.get_anthropic_api_key()
        >>>
        >>> # Optional API key (returns None if not found)
        >>> api_key = ConfigManager.get_anthropic_api_key(required=False)
        >>>
        >>> # With fallback names
        >>> gemini_key = ConfigManager.get_gemini_api_key()
        >>> # Checks GEMINI_API_KEY, GOOGLE_API_KEY, COFFEE_MAKER_GEMINI_API_KEY
    """

    # Cache for loaded configuration (avoids repeated env var access)
    _cache: Dict[str, Optional[str]] = {}

    @staticmethod
    def clear_cache() -> None:
        """Clear the configuration cache.

        Useful for testing or when environment variables change at runtime.

        Example:
            >>> import os
            >>> os.environ["ANTHROPIC_API_KEY"] = "new-key"
            >>> ConfigManager.clear_cache()
            >>> key = ConfigManager.get_anthropic_api_key()  # Will reload from env
        """
        ConfigManager._cache.clear()

    @staticmethod
    def _get_env_with_fallbacks(
        primary_name: str, fallback_names: Optional[List[str]] = None, cache_key: Optional[str] = None
    ) -> Optional[str]:
        """Get environment variable with fallback names.

        Args:
            primary_name: Primary environment variable name
            fallback_names: List of fallback names to check
            cache_key: Key for caching (defaults to primary_name)

        Returns:
            Value if found, None otherwise

        Example:
            >>> value = ConfigManager._get_env_with_fallbacks(
            ...     "GEMINI_API_KEY",
            ...     ["GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]
            ... )
        """
        cache_key = cache_key or primary_name

        # Check cache first
        if cache_key in ConfigManager._cache:
            return ConfigManager._cache[cache_key]

        # Try primary name
        value = os.getenv(primary_name)
        if value:
            ConfigManager._cache[cache_key] = value
            return value

        # Try fallbacks
        if fallback_names:
            for fallback in fallback_names:
                value = os.getenv(fallback)
                if value:
                    logger.debug(f"Found {primary_name} using fallback name: {fallback}")
                    # Normalize: set primary name for consistency
                    os.environ.setdefault(primary_name, value)
                    ConfigManager._cache[cache_key] = value
                    return value

        # Not found
        ConfigManager._cache[cache_key] = None
        return None

    @staticmethod
    def get_anthropic_api_key(required: bool = True) -> Optional[str]:
        """Get ANTHROPIC_API_KEY with consistent validation.

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            API key string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and key not found

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> api_key = ConfigManager.get_anthropic_api_key()
            >>> # Use with Claude API
            >>> from anthropic import Anthropic
            >>> client = Anthropic(api_key=api_key)
        """
        value = ConfigManager._get_env_with_fallbacks("ANTHROPIC_API_KEY")

        if not value and required:
            raise APIKeyMissingError("ANTHROPIC_API_KEY")

        return value

    @staticmethod
    def get_openai_api_key(required: bool = True) -> Optional[str]:
        """Get OPENAI_API_KEY with consistent validation.

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            API key string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and key not found

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> api_key = ConfigManager.get_openai_api_key()
            >>> # Use with OpenAI API
            >>> from openai import OpenAI
            >>> client = OpenAI(api_key=api_key)
        """
        value = ConfigManager._get_env_with_fallbacks("OPENAI_API_KEY")

        if not value and required:
            raise APIKeyMissingError("OPENAI_API_KEY")

        return value

    @staticmethod
    def get_gemini_api_key(required: bool = True) -> Optional[str]:
        """Resolve Gemini API key from multiple possible environment variable names.

        Checks for API key in multiple environment variable names and ensures
        GEMINI_API_KEY is set for consistent access. Supports three variable names:
        - GEMINI_API_KEY (primary)
        - GOOGLE_API_KEY (alternative)
        - COFFEE_MAKER_GEMINI_API_KEY (project-specific)

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            API key string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and key not found in any location

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> api_key = ConfigManager.get_gemini_api_key()
            >>> # Use with Google Generative AI
            >>> import google.generativeai as genai
            >>> genai.configure(api_key=api_key)
        """
        value = ConfigManager._get_env_with_fallbacks(
            "GEMINI_API_KEY", fallback_names=["GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]
        )

        if not value and required:
            raise APIKeyMissingError(
                "GEMINI_API_KEY", suggested_names=["GOOGLE_API_KEY", "COFFEE_MAKER_GEMINI_API_KEY"]
            )

        return value

    @staticmethod
    def get_github_token(required: bool = True) -> Optional[str]:
        """Get GITHUB_TOKEN with consistent validation.

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            Token string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and token not found

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> token = ConfigManager.get_github_token()
            >>> # Use with PyGithub
            >>> from github import Github, Auth
            >>> auth = Auth.Token(token)
            >>> client = Github(auth=auth)
        """
        value = ConfigManager._get_env_with_fallbacks("GITHUB_TOKEN")

        if not value and required:
            raise APIKeyMissingError("GITHUB_TOKEN")

        return value

    @staticmethod
    def has_anthropic_api_key() -> bool:
        """Check if ANTHROPIC_API_KEY is set.

        Returns:
            True if API key is set, False otherwise

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> if ConfigManager.has_anthropic_api_key():
            ...     print("Claude API available")
        """
        return ConfigManager.get_anthropic_api_key(required=False) is not None

    @staticmethod
    def has_openai_api_key() -> bool:
        """Check if OPENAI_API_KEY is set.

        Returns:
            True if API key is set, False otherwise

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> if ConfigManager.has_openai_api_key():
            ...     print("OpenAI API available")
        """
        return ConfigManager.get_openai_api_key(required=False) is not None

    @staticmethod
    def has_gemini_api_key() -> bool:
        """Check if any Gemini API key is set.

        Returns:
            True if API key is set, False otherwise

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> if ConfigManager.has_gemini_api_key():
            ...     print("Gemini API available")
        """
        return ConfigManager.get_gemini_api_key(required=False) is not None

    @staticmethod
    def has_github_token() -> bool:
        """Check if GITHUB_TOKEN is set.

        Returns:
            True if token is set, False otherwise

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> if ConfigManager.has_github_token():
            ...     print("GitHub API available")
        """
        return ConfigManager.get_github_token(required=False) is not None

    @staticmethod
    def get_langfuse_public_key(required: bool = True) -> Optional[str]:
        """Get LANGFUSE_PUBLIC_KEY with consistent validation.

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            Public key string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and key not found

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> public_key = ConfigManager.get_langfuse_public_key()
            >>> # Use with Langfuse client
            >>> import langfuse
            >>> client = langfuse.Langfuse(public_key=public_key, secret_key=...)
        """
        value = ConfigManager._get_env_with_fallbacks("LANGFUSE_PUBLIC_KEY")

        if not value and required:
            raise APIKeyMissingError("LANGFUSE_PUBLIC_KEY")

        return value

    @staticmethod
    def get_langfuse_secret_key(required: bool = True) -> Optional[str]:
        """Get LANGFUSE_SECRET_KEY with consistent validation.

        Args:
            required: If True, raise APIKeyMissingError if not found

        Returns:
            Secret key string if found, None if not required and not found

        Raises:
            APIKeyMissingError: If required=True and key not found

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> secret_key = ConfigManager.get_langfuse_secret_key()
            >>> # Use with Langfuse client
            >>> import langfuse
            >>> client = langfuse.Langfuse(public_key=..., secret_key=secret_key)
        """
        value = ConfigManager._get_env_with_fallbacks("LANGFUSE_SECRET_KEY")

        if not value and required:
            raise APIKeyMissingError("LANGFUSE_SECRET_KEY")

        return value

    @staticmethod
    def has_langfuse_keys() -> bool:
        """Check if both Langfuse keys are set.

        Returns:
            True if both public and secret keys are set, False otherwise

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> if ConfigManager.has_langfuse_keys():
            ...     print("Langfuse observability available")
        """
        return (
            ConfigManager.get_langfuse_public_key(required=False) is not None
            and ConfigManager.get_langfuse_secret_key(required=False) is not None
        )

    @staticmethod
    def get_all_api_keys() -> Dict[str, Optional[str]]:
        """Get all configured API keys.

        Returns:
            Dictionary mapping key names to their values (or None if not set)

        Example:
            >>> from coffee_maker.config import ConfigManager
            >>> keys = ConfigManager.get_all_api_keys()
            >>> for name, value in keys.items():
            ...     status = "✓" if value else "✗"
            ...     print(f"{status} {name}")
        """
        return {
            "ANTHROPIC_API_KEY": ConfigManager.get_anthropic_api_key(required=False),
            "OPENAI_API_KEY": ConfigManager.get_openai_api_key(required=False),
            "GEMINI_API_KEY": ConfigManager.get_gemini_api_key(required=False),
            "GITHUB_TOKEN": ConfigManager.get_github_token(required=False),
            "LANGFUSE_PUBLIC_KEY": ConfigManager.get_langfuse_public_key(required=False),
            "LANGFUSE_SECRET_KEY": ConfigManager.get_langfuse_secret_key(required=False),
        }
