"""Retry strategies for handling failed LLM requests.

This module provides strategies for retrying failed requests with
exponential backoff and intelligent fallback logic.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class RetryStrategy(ABC):
    """Abstract base class for retry strategies.

    A retry strategy determines:
    - Whether to retry a failed request
    - How long to wait before retrying (backoff)
    - When to give up and use fallback
    """

    @abstractmethod
    def should_retry(self, attempt: int, elapsed_time: float, error: Optional[Exception] = None) -> bool:
        """Determine if we should retry the request.

        Args:
            attempt: Current attempt number (0-indexed)
            elapsed_time: Time elapsed since first attempt (seconds)
            error: Optional exception that caused the failure

        Returns:
            True if should retry, False if should fallback
        """

    @abstractmethod
    def get_backoff_time(self, attempt: int) -> float:
        """Calculate how long to wait before next retry.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Seconds to wait before next retry
        """

    @abstractmethod
    def should_fallback(self, attempt: int, elapsed_time: float, time_since_last_call: float) -> bool:
        """Determine if we should fallback to alternative model.

        Args:
            attempt: Current attempt number
            elapsed_time: Total time spent retrying (seconds)
            time_since_last_call: Time since last global LLM call (seconds)

        Returns:
            True if should fallback, False if should keep trying
        """


class ExponentialBackoffRetry(RetryStrategy):
    """Retry strategy with exponential backoff.

    This strategy:
    - Retries up to max_retries times
    - Waits exponentially longer between retries (base^attempt)
    - Gives up if total wait exceeds max_wait_seconds
    - Requires minimum time since last call before fallback

    Example:
        >>> retry = ExponentialBackoffRetry(
        ...     max_retries=3,
        ...     backoff_base=2.0,
        ...     max_wait_seconds=300.0,
        ...     min_wait_before_fallback=90.0
        ... )
        >>> # Attempt 0: wait 1s (2^0)
        >>> # Attempt 1: wait 2s (2^1)
        >>> # Attempt 2: wait 4s (2^2)
        >>> # Attempt 3: fallback or final attempt
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        max_wait_seconds: float = 300.0,
        min_wait_before_fallback: float = 90.0,
    ):
        """Initialize exponential backoff retry strategy.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_base: Exponential backoff multiplier (default: 2.0)
            max_wait_seconds: Maximum total wait time before fallback (default: 300s = 5min)
            min_wait_before_fallback: Minimum seconds since last call before fallback (default: 90s)
        """
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.max_wait_seconds = max_wait_seconds
        self.min_wait_before_fallback = min_wait_before_fallback

    def should_retry(self, attempt: int, elapsed_time: float, error: Optional[Exception] = None) -> bool:
        """Check if we should retry based on attempt count and elapsed time.

        Retries if:
        - Haven't exceeded max_retries
        - Haven't exceeded max_wait_seconds

        Args:
            attempt: Current attempt number (0-indexed)
            elapsed_time: Time elapsed since first attempt
            error: Optional exception (not currently used)

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            logger.debug(f"Max retries ({self.max_retries}) exceeded")
            return False

        if elapsed_time >= self.max_wait_seconds:
            logger.debug(f"Max wait time ({self.max_wait_seconds}s) exceeded")
            return False

        return True

    def get_backoff_time(self, attempt: int) -> float:
        """Calculate exponential backoff time.

        Formula: base^attempt

        Examples (base=2.0):
        - Attempt 0: 2^0 = 1 second
        - Attempt 1: 2^1 = 2 seconds
        - Attempt 2: 2^2 = 4 seconds
        - Attempt 3: 2^3 = 8 seconds

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Seconds to wait before next retry
        """
        backoff = self.backoff_base**attempt
        logger.debug(f"Attempt {attempt}: calculated backoff = {backoff}s")
        return backoff

    def should_fallback(self, attempt: int, elapsed_time: float, time_since_last_call: float) -> bool:
        """Determine if we should fallback to alternative model.

        Fallback conditions:
        1. Retries exhausted OR wait time exceeded
        2. AND minimum time since last call has passed

        The min_wait_before_fallback ensures we don't immediately fallback
        if we just made a call. This prevents rapid model switching.

        Args:
            attempt: Current attempt number
            elapsed_time: Total time spent retrying
            time_since_last_call: Time since last global LLM call

        Returns:
            True if should fallback to alternative model
        """
        # Check if we've exhausted retries or exceeded max wait
        retries_exhausted = attempt >= self.max_retries
        wait_exceeded = elapsed_time >= self.max_wait_seconds

        if not (retries_exhausted or wait_exceeded):
            # Haven't reached limits yet, keep trying primary
            return False

        # Check if enough time has passed since last call
        if time_since_last_call < self.min_wait_before_fallback:
            logger.debug(
                f"Not enough time since last call ({time_since_last_call:.1f}s < "
                f"{self.min_wait_before_fallback}s), waiting before fallback"
            )
            return False

        logger.info(
            f"Fallback conditions met: retries={attempt}/{self.max_retries}, "
            f"elapsed={elapsed_time:.1f}s, since_last_call={time_since_last_call:.1f}s"
        )
        return True

    def wait_remaining_time(self, time_since_last_call: float) -> float:
        """Calculate remaining wait time before fallback is allowed.

        Args:
            time_since_last_call: Time since last global LLM call (seconds)

        Returns:
            Seconds to wait before fallback is allowed (0 if can fallback now)
        """
        if time_since_last_call >= self.min_wait_before_fallback:
            return 0.0

        remaining = self.min_wait_before_fallback - time_since_last_call
        return remaining

    def enforce_min_wait(self, time_since_last_call: float) -> None:
        """Wait until minimum time has passed since last call.

        This ensures we respect the min_wait_before_fallback rule.
        Sleeps if necessary.

        Args:
            time_since_last_call: Time since last global LLM call (seconds)
        """
        remaining = self.wait_remaining_time(time_since_last_call)
        if remaining > 0:
            logger.info(f"Waiting {remaining:.1f}s to reach min_wait_before_fallback")
            time.sleep(remaining)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ExponentialBackoffRetry(max_retries={self.max_retries}, "
            f"backoff_base={self.backoff_base}, max_wait_seconds={self.max_wait_seconds}, "
            f"min_wait_before_fallback={self.min_wait_before_fallback})"
        )
