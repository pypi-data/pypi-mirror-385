"""Logging utilities for consistent log messages across the application.

This module provides utilities for standardized logging with:
- Consistent message formatting
- Structured logging context
- Log level helpers
- Error tracking integration
- Performance measurement

Usage:
    >>> from coffee_maker.utils.logging import get_logger, log_error
    >>> logger = get_logger(__name__)
    >>> logger.info("Starting process", extra={"priority": "US-021"})
    >>>
    >>> # Error with context
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     log_error(logger, "Operation failed", e, context={"user": "bob"})

Logging Conventions:
    1. Use get_logger(__name__) for module loggers
    2. Include context via extra={} parameter
    3. Use log_* helpers for consistent formatting
    4. Errors should include exception info
    5. Performance metrics use log_duration
    6. User-facing messages avoid technical jargon
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

# ============================================================================
# LOGGER CREATION
# ============================================================================


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a logger with standardized configuration.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


# ============================================================================
# STRUCTURED LOGGING HELPERS
# ============================================================================


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """Log message with structured context.

    Args:
        logger: Logger instance
        level: Log level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        context: Optional dictionary with additional context
        **kwargs: Additional keyword arguments for logger

    Example:
        >>> log_with_context(
        ...     logger, logging.INFO, "Task completed",
        ...     context={"task_id": "US-021", "duration": 5.2}
        ... )
    """
    extra = kwargs.get("extra", {})
    if context:
        extra.update(context)

    kwargs["extra"] = extra
    logger.log(level, message, **kwargs)


def log_error(
    logger: logging.Logger,
    message: str,
    exception: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log error with exception info and context.

    Args:
        logger: Logger instance
        message: Error message
        exception: Optional exception object
        context: Optional context dictionary

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_error(logger, "Operation failed", e, {"op": "risky"})
    """
    extra = {}
    if context:
        extra.update(context)

    if exception:
        extra["exception_type"] = type(exception).__name__
        extra["exception_msg"] = str(exception)
        logger.error(message, exc_info=True, extra=extra)
    else:
        logger.error(message, extra=extra)


def log_warning(
    logger: logging.Logger,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log warning with context.

    Args:
        logger: Logger instance
        message: Warning message
        context: Optional context dictionary

    Example:
        >>> log_warning(logger, "Fallback used", {"provider": "openai"})
    """
    extra = context or {}
    logger.warning(message, extra=extra)


# ============================================================================
# PERFORMANCE MEASUREMENT
# ============================================================================


@contextmanager
def log_duration(logger: logging.Logger, operation: str, level: int = logging.INFO):
    """Context manager to log operation duration.

    Args:
        logger: Logger instance
        operation: Operation description
        level: Log level (default: INFO)

    Yields:
        Dictionary that can be updated with additional context

    Example:
        >>> with log_duration(logger, "API call") as ctx:
        ...     result = expensive_operation()
        ...     ctx["result_count"] = len(result)
        >>> # Logs: "API call completed in 1.23s (result_count=5)"
    """
    start = time.time()
    context = {}

    try:
        yield context
    finally:
        duration = time.time() - start
        ctx_str = ", ".join(f"{k}={v}" for k, v in context.items())
        ctx_suffix = f" ({ctx_str})" if ctx_str else ""

        logger.log(level, f"{operation} completed in {duration:.2f}s{ctx_suffix}")


# ============================================================================
# MESSAGE FORMATTING
# ============================================================================


class LogFormatter:
    """Standardized log message formatting.

    Provides consistent formatting for common log message types.
    """

    # Emoji prefixes for visual scanning (optional, can be disabled)
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    DEBUG = "🔍"
    IN_PROGRESS = "🔄"
    SKIP = "⏭️"
    BLOCKED = "🚫"

    @staticmethod
    def success(message: str, use_emoji: bool = True) -> str:
        """Format success message.

        Args:
            message: Message text
            use_emoji: Whether to include emoji prefix

        Returns:
            Formatted message

        Example:
            >>> LogFormatter.success("Task complete")
            '✅ Task complete'
        """
        prefix = f"{LogFormatter.SUCCESS} " if use_emoji else ""
        return f"{prefix}{message}"

    @staticmethod
    def error(message: str, use_emoji: bool = True) -> str:
        """Format error message.

        Args:
            message: Message text
            use_emoji: Whether to include emoji prefix

        Returns:
            Formatted message

        Example:
            >>> LogFormatter.error("Operation failed")
            '❌ Operation failed'
        """
        prefix = f"{LogFormatter.ERROR} " if use_emoji else ""
        return f"{prefix}{message}"

    @staticmethod
    def warning(message: str, use_emoji: bool = True) -> str:
        """Format warning message.

        Args:
            message: Message text
            use_emoji: Whether to include emoji prefix

        Returns:
            Formatted message

        Example:
            >>> LogFormatter.warning("Fallback used")
            '⚠️ Fallback used'
        """
        prefix = f"{LogFormatter.WARNING} " if use_emoji else ""
        return f"{prefix}{message}"

    @staticmethod
    def in_progress(message: str, use_emoji: bool = True) -> str:
        """Format in-progress message.

        Args:
            message: Message text
            use_emoji: Whether to include emoji prefix

        Returns:
            Formatted message

        Example:
            >>> LogFormatter.in_progress("Processing...")
            '🔄 Processing...'
        """
        prefix = f"{LogFormatter.IN_PROGRESS} " if use_emoji else ""
        return f"{prefix}{message}"


# ============================================================================
# ERROR MESSAGE TEMPLATES
# ============================================================================


class ErrorMessages:
    """Standardized error message templates.

    Provides consistent error messages for common failure scenarios.
    """

    @staticmethod
    def file_not_found(path: str) -> str:
        """Error message for file not found.

        Args:
            path: File path

        Returns:
            Error message

        Example:
            >>> ErrorMessages.file_not_found("config.json")
            'File not found: config.json'
        """
        return f"File not found: {path}"

    @staticmethod
    def invalid_config(field: str, expected: str, actual: str) -> str:
        """Error message for invalid configuration.

        Args:
            field: Configuration field name
            expected: Expected value/type
            actual: Actual value/type

        Returns:
            Error message

        Example:
            >>> ErrorMessages.invalid_config("port", "integer", "string")
            'Invalid configuration for port: expected integer, got string'
        """
        return f"Invalid configuration for {field}: expected {expected}, got {actual}"

    @staticmethod
    def api_error(provider: str, status: int, message: str) -> str:
        """Error message for API failures.

        Args:
            provider: Provider name (e.g., "OpenAI", "Anthropic")
            status: HTTP status code
            message: Error message from provider

        Returns:
            Error message

        Example:
            >>> ErrorMessages.api_error("OpenAI", 429, "Rate limit exceeded")
            'OpenAI API error (429): Rate limit exceeded'
        """
        return f"{provider} API error ({status}): {message}"

    @staticmethod
    def resource_exhausted(resource: str, limit: Any, actual: Any) -> str:
        """Error message for resource limits.

        Args:
            resource: Resource name (e.g., "tokens", "budget")
            limit: Resource limit
            actual: Actual usage

        Returns:
            Error message

        Example:
            >>> ErrorMessages.resource_exhausted("tokens", 100000, 150000)
            'Resource exhausted for tokens: limit 100000, actual 150000'
        """
        return f"Resource exhausted for {resource}: limit {limit}, actual {actual}"

    @staticmethod
    def dependency_missing(dependency: str, install_cmd: Optional[str] = None) -> str:
        """Error message for missing dependencies.

        Args:
            dependency: Dependency name
            install_cmd: Optional installation command

        Returns:
            Error message

        Example:
            >>> ErrorMessages.dependency_missing("pandas", "pip install pandas")
            'Missing dependency: pandas. Install with: pip install pandas'
        """
        msg = f"Missing dependency: {dependency}"
        if install_cmd:
            msg += f". Install with: {install_cmd}"
        return msg


# ============================================================================
# LOGGING GUIDELINES
# ============================================================================

"""
LOGGING GUIDELINES FOR COFFEE MAKER AGENT

1. LOG LEVELS:
   - DEBUG: Detailed diagnostic information for troubleshooting
   - INFO: General informational messages about application progress
   - WARNING: Recoverable issues that don't prevent operation
   - ERROR: Error conditions that prevent specific operations
   - CRITICAL: Severe errors that may cause application failure

2. WHEN TO LOG:
   - INFO: Major state transitions, task completions, API calls
   - WARNING: Fallback usage, deprecated features, config issues
   - ERROR: Exception handling, failed operations, validation errors
   - CRITICAL: Unrecoverable failures, data corruption

3. WHAT TO INCLUDE:
   - Context: User ID, task ID, priority name, etc.
   - Timing: Duration for slow operations
   - Errors: Exception type, message, stack trace (via exc_info=True)
   - Resources: Token counts, API calls, costs

4. WHAT TO AVOID:
   - Sensitive data: API keys, passwords, PII
   - Excessive logging: Don't log in tight loops
   - Generic messages: "Error occurred" (be specific!)
   - User-unfriendly jargon: Explain what went wrong

5. STRUCTURED LOGGING:
   - Use extra={} for structured data
   - Keep messages human-readable
   - Add context for debugging
   - Enable log aggregation tools

6. PERFORMANCE:
   - Use lazy evaluation for expensive formatting
   - Guard debug logs: if logger.isEnabledFor(logging.DEBUG):
   - Don't log inside hot loops
   - Use sampling for high-frequency events

Examples:
    # Good: Specific, contextual, actionable
    logger.info("ConfigManager initialized", extra={"api_keys": 4})
    logger.error("Failed to load config", exc_info=True, extra={"path": path})
    logger.warning("Fallback to default", extra={"config": "timeout"})

    # Bad: Generic, no context, not actionable
    logger.info("Done")
    logger.error("Error")
    logger.warning("Issue detected")
"""

__all__ = [
    "get_logger",
    "log_with_context",
    "log_error",
    "log_warning",
    "log_duration",
    "LogFormatter",
    "ErrorMessages",
]
