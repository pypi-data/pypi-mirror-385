"""Centralized exception hierarchy for Coffee Maker Agent.

This module provides a unified exception hierarchy for the entire application,
making error handling consistent and improving debuggability.

Exception Hierarchy:
    CoffeeMakerError (base)
    ├── ConfigError
    │   ├── ConfigurationError (from config.manager)
    │   └── APIKeyMissingError (from config.manager)
    ├── ProviderError
    │   ├── ProviderNotFoundError (from ai_providers.provider_factory)
    │   ├── ProviderNotEnabledError (from ai_providers.provider_factory)
    │   ├── ProviderConfigError (from ai_providers.provider_config)
    │   ├── ProviderUnavailableError (from ai_providers.fallback_strategy)
    │   └── AllProvidersFailedError (from ai_providers.fallback_strategy)
    ├── ResourceError
    │   ├── RateLimitError
    │   ├── QuotaExceededError (from langfuse_observe.exceptions)
    │   ├── CostLimitExceededError (from ai_providers.fallback_strategy)
    │   └── BudgetExceededError (from langfuse_observe.exceptions)
    ├── ModelError
    │   ├── ModelNotAvailableError (from langfuse_observe.exceptions)
    │   └── ContextLengthError (from langfuse_observe.exceptions)
    ├── FileError
    │   └── FileOperationError (from utils.file_io)
    └── DaemonError
        ├── DaemonCrashError
        └── DaemonStateError

Usage:
    >>> from coffee_maker.exceptions import CoffeeMakerError, ProviderError
    >>>
    >>> try:
    ...     # Some operation
    ...     pass
    ... except ProviderError as e:
    ...     print(f"Provider failed: {e}")
    ... except CoffeeMakerError as e:
    ...     print(f"Application error: {e}")

Design Principles:
    1. All custom exceptions inherit from CoffeeMakerError
    2. Domain-specific base exceptions (ConfigError, ProviderError, etc.)
    3. Specific exceptions inherit from domain base
    4. Re-export existing well-structured exceptions for backward compatibility
    5. Rich error messages with context
    6. Type hints for better IDE support

Migration Strategy:
    Phase 1: Create hierarchy, re-export existing exceptions
    Phase 2: Gradually migrate code to use new hierarchy
    Phase 3: Deprecate scattered exception definitions
"""

from typing import Optional

# ============================================================================
# BASE EXCEPTIONS
# ============================================================================


class CoffeeMakerError(Exception):
    """Base exception for all Coffee Maker Agent errors.

    All custom exceptions in the application should inherit from this class.
    This allows catching all application-specific errors with a single except clause.

    Attributes:
        message: Error message
        details: Optional dict with additional error context
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize CoffeeMakerError.

        Args:
            message: Human-readable error message
            details: Optional dict with additional context (for logging/debugging)
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================


class ConfigError(CoffeeMakerError):
    """Base exception for configuration-related errors.

    Use this for issues with configuration files, environment variables,
    or application settings.
    """


# Re-export existing config exceptions for backward compatibility
# These are imported here so they're part of the unified hierarchy
from coffee_maker.config.manager import (  # noqa: E402
    APIKeyMissingError,
    ConfigurationError,
)

# Make ConfigurationError inherit from ConfigError conceptually
# (They're already defined, so we just re-export them)


# ============================================================================
# PROVIDER ERRORS
# ============================================================================


class ProviderError(CoffeeMakerError):
    """Base exception for AI provider-related errors.

    Use this for issues with AI provider configuration, availability,
    or provider-specific failures.
    """


# Re-export existing provider exceptions
from coffee_maker.ai_providers.fallback_strategy import (  # noqa: E402
    AllProvidersFailedError,
    CostLimitExceededError,
    ProviderUnavailableError,
    RateLimitError as FallbackRateLimitError,  # Avoid name collision
)
from coffee_maker.ai_providers.provider_config import (  # noqa: E402
    ProviderConfigError,
)
from coffee_maker.ai_providers.provider_factory import (  # noqa: E402
    ProviderNotEnabledError,
    ProviderNotFoundError,
)


# ============================================================================
# RESOURCE ERRORS
# ============================================================================


class ResourceError(CoffeeMakerError):
    """Base exception for resource limit errors.

    Use this for rate limits, quota exceeded, budget limits, etc.
    """


# Re-export resource-related exceptions from langfuse_observe
from coffee_maker.langfuse_observe.exceptions import (  # noqa: E402
    BudgetExceededError,
    QuotaExceededError,
    RateLimitExceededError,
)


# Unified RateLimitError (combines FallbackRateLimitError and RateLimitExceededError)
class RateLimitError(ResourceError):
    """Raised when API rate limits are exceeded.

    This is a unified exception that consolidates rate limit handling
    across the application.

    Attributes:
        provider: Provider name
        limit_type: Type of limit exceeded (e.g., "requests", "tokens")
        retry_after: Optional seconds to wait before retrying
    """

    def __init__(self, provider: str, limit_type: str = "requests", retry_after: Optional[int] = None):
        """Initialize RateLimitError.

        Args:
            provider: Provider name
            limit_type: Type of limit exceeded
            retry_after: Optional seconds to wait before retrying
        """
        self.provider = provider
        self.limit_type = limit_type
        self.retry_after = retry_after

        message = f"Rate limit exceeded for {provider}: {limit_type}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"

        super().__init__(message, details={"provider": provider, "limit_type": limit_type, "retry_after": retry_after})


# ============================================================================
# MODEL ERRORS
# ============================================================================


class ModelError(CoffeeMakerError):
    """Base exception for model-related errors.

    Use this for issues with model availability, context length,
    or model-specific failures.
    """


# Re-export model exceptions
from coffee_maker.langfuse_observe.exceptions import (  # noqa: E402
    ContextLengthError,
    ModelNotAvailableError,
)


# ============================================================================
# FILE ERRORS
# ============================================================================


class FileError(CoffeeMakerError):
    """Base exception for file operation errors.

    Use this for issues with reading, writing, or processing files.
    """


# Re-export file exception
from coffee_maker.utils.file_io import FileOperationError  # noqa: E402


# ============================================================================
# DAEMON ERRORS
# ============================================================================


class DaemonError(CoffeeMakerError):
    """Base exception for daemon-related errors.

    Use this for issues with daemon lifecycle, state management,
    or daemon-specific failures.
    """


class DaemonCrashError(DaemonError):
    """Raised when daemon crashes unexpectedly.

    Attributes:
        crash_count: Number of crashes so far
        max_crashes: Maximum crashes before stopping
        last_exception: The exception that caused the crash
    """

    def __init__(self, crash_count: int, max_crashes: int, last_exception: Optional[Exception] = None):
        """Initialize DaemonCrashError.

        Args:
            crash_count: Current crash count
            max_crashes: Maximum allowed crashes
            last_exception: The exception that caused the crash
        """
        self.crash_count = crash_count
        self.max_crashes = max_crashes
        self.last_exception = last_exception

        message = f"Daemon crashed {crash_count}/{max_crashes} times"
        if last_exception:
            message += f": {type(last_exception).__name__}: {last_exception}"

        super().__init__(
            message,
            details={"crash_count": crash_count, "max_crashes": max_crashes, "exception": str(last_exception)},
        )


class DaemonStateError(DaemonError):
    """Raised when daemon is in an invalid state for requested operation.

    Attributes:
        current_state: Current daemon state
        required_state: Required state for operation
        operation: Operation that was attempted
    """

    def __init__(self, current_state: str, required_state: str, operation: str):
        """Initialize DaemonStateError.

        Args:
            current_state: Current state of daemon
            required_state: State required for operation
            operation: Operation that was attempted
        """
        self.current_state = current_state
        self.required_state = required_state
        self.operation = operation

        message = f"Cannot {operation}: daemon is {current_state}, requires {required_state}"

        super().__init__(
            message,
            details={"current_state": current_state, "required_state": required_state, "operation": operation},
        )


# ============================================================================
# EXPORTED SYMBOLS
# ============================================================================

__all__ = [
    # Base exceptions
    "CoffeeMakerError",
    # Domain bases
    "ConfigError",
    "ProviderError",
    "ResourceError",
    "ModelError",
    "FileError",
    "DaemonError",
    # Config exceptions
    "ConfigurationError",
    "APIKeyMissingError",
    # Provider exceptions
    "ProviderNotFoundError",
    "ProviderNotEnabledError",
    "ProviderConfigError",
    "ProviderUnavailableError",
    "AllProvidersFailedError",
    # Resource exceptions
    "RateLimitError",
    "RateLimitExceededError",  # langfuse_observe version
    "FallbackRateLimitError",  # ai_providers version
    "QuotaExceededError",
    "CostLimitExceededError",
    "BudgetExceededError",
    # Model exceptions
    "ModelNotAvailableError",
    "ContextLengthError",
    # File exceptions
    "FileOperationError",
    # Daemon exceptions
    "DaemonCrashError",
    "DaemonStateError",
]
