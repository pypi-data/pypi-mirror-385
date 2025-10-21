"""General-purpose retry utilities with Langfuse observability.

This module provides a retry decorator that can be applied to any function,
with automatic logging to both Python logger and Langfuse for full observability.

Example:
    >>> from coffee_maker.langfuse_observe.retry import with_retry
    >>>
    >>> @with_retry(max_attempts=3, backoff_base=2.0)
    >>> def flaky_api_call():
    >>>     # API call that might fail
    >>>     pass
"""

import functools
import logging
import time
from typing import Any, Callable, Optional, Tuple, Type

from langfuse import observe

logger = logging.getLogger(__name__)


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, original_error: Exception, attempts: int):
        self.original_error = original_error
        self.attempts = attempts
        super().__init__(
            f"Retry exhausted after {attempts} attempts. "
            f"Last error: {type(original_error).__name__}: {original_error}"
        )


class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including initial call)
        backoff_base: Base for exponential backoff (seconds)
        max_backoff: Maximum backoff time (seconds)
        retriable_exceptions: Tuple of exception types to retry
        should_retry_predicate: Optional function to determine if error is retriable
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_base: float = 2.0,
        max_backoff: float = 60.0,
        retriable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
        should_retry_predicate: Optional[Callable[[Exception], bool]] = None,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum attempts (default: 3)
            backoff_base: Exponential backoff base (default: 2.0)
            max_backoff: Maximum backoff time in seconds (default: 60.0)
            retriable_exceptions: Tuple of exception types to retry (default: Exception)
            should_retry_predicate: Function that takes exception and returns bool
        """
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.max_backoff = max_backoff
        self.retriable_exceptions = retriable_exceptions or (Exception,)
        self.should_retry_predicate = should_retry_predicate

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time for given attempt.

        Uses exponential backoff: min(backoff_base ^ attempt, max_backoff)

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Backoff time in seconds
        """
        backoff = self.backoff_base**attempt
        return min(backoff, self.max_backoff)

    def is_retriable(self, error: Exception) -> bool:
        """Determine if an error should trigger a retry.

        Args:
            error: Exception that occurred

        Returns:
            True if error is retriable, False otherwise
        """
        # Check exception type
        if not isinstance(error, self.retriable_exceptions):
            return False

        # Check custom predicate if provided
        if self.should_retry_predicate is not None:
            return self.should_retry_predicate(error)

        return True


@observe(capture_input=False, capture_output=False)
def _log_retry_attempt(
    function_name: str,
    attempt: int,
    max_attempts: int,
    error: Exception,
    backoff: float,
) -> None:
    """Log retry attempt to Langfuse and Python logger.

    This is a separate observed function so each retry attempt
    creates a Langfuse span with metadata.

    Args:
        function_name: Name of function being retried
        attempt: Current attempt number (1-indexed for display)
        max_attempts: Maximum attempts configured
        error: Exception that triggered retry
        backoff: Backoff time in seconds
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Log to Python logger
    logger.warning(
        f"Retry {attempt}/{max_attempts} for {function_name}: "
        f"{error_type}: {error_msg}. Waiting {backoff:.2f}s before retry."
    )

    # Langfuse will automatically capture this as a span with metadata
    # The observe decorator handles the Langfuse integration


@observe(capture_input=False, capture_output=False)
def _log_retry_exhausted(
    function_name: str,
    total_attempts: int,
    total_time: float,
    final_error: Exception,
) -> None:
    """Log retry exhaustion to Langfuse and Python logger.

    Args:
        function_name: Name of function that failed
        total_attempts: Total attempts made
        total_time: Total time spent retrying
        final_error: Final exception that caused failure
    """
    error_type = type(final_error).__name__
    error_msg = str(final_error)

    # Log to Python logger
    logger.error(
        f"Retry exhausted for {function_name} after {total_attempts} attempts "
        f"({total_time:.2f}s total). Final error: {error_type}: {error_msg}"
    )

    # Langfuse will automatically capture this as a span


@observe(capture_input=False, capture_output=False)
def _log_retry_success(
    function_name: str,
    attempt: int,
    total_time: float,
) -> None:
    """Log successful retry to Langfuse and Python logger.

    Args:
        function_name: Name of function that succeeded
        attempt: Attempt number that succeeded (1-indexed)
        total_time: Total time spent including retries
    """
    if attempt > 1:
        logger.info(f"Success for {function_name} on attempt {attempt} " f"after {total_time:.2f}s total")


def with_retry(
    max_attempts: int = 3,
    backoff_base: float = 2.0,
    max_backoff: float = 60.0,
    retriable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    should_retry_predicate: Optional[Callable[[Exception], bool]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """Decorator to add retry logic with Langfuse observability.

    This decorator will:
    - Retry the decorated function on failure
    - Use exponential backoff between retries
    - Log each retry attempt to both Python logger and Langfuse
    - Raise RetryExhausted if all attempts fail

    Args:
        max_attempts: Maximum attempts including initial call (default: 3)
        backoff_base: Base for exponential backoff (default: 2.0)
        max_backoff: Maximum backoff time in seconds (default: 60.0)
        retriable_exceptions: Tuple of exception types to retry (default: Exception)
        should_retry_predicate: Optional function(error) -> bool for custom retry logic
        on_retry: Optional callback(error, attempt) called before each retry

    Returns:
        Decorated function with retry logic

    Example:
        >>> @with_retry(max_attempts=5, backoff_base=2.0)
        >>> def fetch_data():
        >>>     # Flaky API call
        >>>     response = requests.get("https://api.example.com/data")
        >>>     return response.json()
        >>>
        >>> # With custom retry predicate
        >>> def is_rate_limit_error(error):
        >>>     return "rate limit" in str(error).lower()
        >>>
        >>> @with_retry(
        >>>     max_attempts=10,
        >>>     should_retry_predicate=is_rate_limit_error
        >>> )
        >>> def api_call():
        >>>     pass
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        max_backoff=max_backoff,
        retriable_exceptions=retriable_exceptions,
        should_retry_predicate=should_retry_predicate,
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            function_name = func.__name__
            start_time = time.time()
            last_error = None

            for attempt in range(config.max_attempts):
                try:
                    result = func(*args, **kwargs)

                    # Log success if we had previous failures
                    if attempt > 0:
                        total_time = time.time() - start_time
                        _log_retry_success(function_name, attempt + 1, total_time)

                    return result

                except Exception as error:
                    last_error = error

                    # Check if we should retry this error
                    if not config.is_retriable(error):
                        logger.debug(f"Non-retriable error in {function_name}: " f"{type(error).__name__}: {error}")
                        raise

                    # Check if we have attempts remaining
                    is_last_attempt = attempt == config.max_attempts - 1
                    if is_last_attempt:
                        break  # Don't backoff on last attempt

                    # Calculate backoff and log retry
                    backoff = config.calculate_backoff(attempt)
                    _log_retry_attempt(
                        function_name=function_name,
                        attempt=attempt + 1,
                        max_attempts=config.max_attempts,
                        error=error,
                        backoff=backoff,
                    )

                    # Call custom retry callback if provided
                    if on_retry is not None:
                        try:
                            on_retry(error, attempt + 1)
                        except Exception as callback_error:
                            logger.warning(f"Error in on_retry callback: {callback_error}")

                    # Wait before retry
                    time.sleep(backoff)

            # All attempts exhausted
            total_time = time.time() - start_time
            _log_retry_exhausted(
                function_name=function_name,
                total_attempts=config.max_attempts,
                total_time=total_time,
                final_error=last_error,
            )

            raise RetryExhausted(last_error, config.max_attempts) from last_error

        return wrapper

    return decorator


def with_conditional_retry(
    condition_check: Callable[[Exception], Tuple[bool, Optional[Callable]]],
    max_attempts: int = 3,
    backoff_base: float = 2.0,
) -> Callable:
    """Decorator for retry with conditional cleanup logic.

    This is useful when you need to perform cleanup before retrying,
    such as clearing pending reviews before posting a new comment.

    Args:
        condition_check: Function(error) -> (should_retry, cleanup_func)
            Returns tuple of (bool, Optional[Callable])
            If should_retry is True and cleanup_func is provided,
            cleanup_func will be called before retry
        max_attempts: Maximum attempts (default: 3)
        backoff_base: Exponential backoff base (default: 2.0)

    Returns:
        Decorated function with conditional retry logic

    Example:
        >>> def check_pending_review(error):
        >>>     if "pending review" in str(error).lower():
        >>>         # Return True and cleanup function
        >>>         return True, lambda: clear_pending_reviews()
        >>>     return False, None
        >>>
        >>> @with_conditional_retry(check_pending_review, max_attempts=2)
        >>> def post_comment():
        >>>     # API call that might fail due to pending review
        >>>     pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            function_name = func.__name__
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as error:
                    last_error = error
                    is_last_attempt = attempt == max_attempts - 1

                    # Check condition
                    should_retry, cleanup_func = condition_check(error)

                    if not should_retry or is_last_attempt:
                        raise

                    # Log retry
                    logger.info(
                        f"Conditional retry {attempt + 1}/{max_attempts} "
                        f"for {function_name}: {type(error).__name__}"
                    )

                    # Perform cleanup if provided
                    if cleanup_func is not None:
                        try:
                            cleanup_func()
                        except Exception as cleanup_error:
                            logger.warning(f"Cleanup failed before retry: {cleanup_error}")

                    # Wait before retry
                    if attempt < max_attempts - 1:
                        backoff = backoff_base**attempt
                        time.sleep(backoff)

            # Should never reach here, but just in case
            raise last_error

        return wrapper

    return decorator
