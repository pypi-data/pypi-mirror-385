"""Scheduling strategies for proactive rate limit management.

This module provides strategies for intelligently scheduling LLM requests
to prevent rate limit errors before they occur.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SchedulingStrategy(ABC):
    """Abstract base class for request scheduling strategies.

    A scheduling strategy determines:
    - When it's safe to make a request (proactive rate limiting)
    - How long to wait before making the next request
    - How to handle rate limit errors reactively (exponential backoff)
    - When to give up and signal fallback
    """

    @abstractmethod
    def can_proceed(self, model_name: str, estimated_tokens: int) -> Tuple[bool, float]:
        """Check if we can proceed with a request now.

        Args:
            model_name: Name of the model to invoke
            estimated_tokens: Estimated tokens for the request

        Returns:
            (can_proceed, wait_time_seconds)
            - can_proceed: True if safe to proceed now
            - wait_time_seconds: Seconds to wait if can't proceed (0 if can proceed)
        """

    @abstractmethod
    def record_request(self, model_name: str, actual_tokens: int) -> None:
        """Record that a request was made successfully.

        Args:
            model_name: Name of the model invoked
            actual_tokens: Actual tokens used in the request
        """

    @abstractmethod
    def record_error(self, model_name: str, error: Exception) -> None:
        """Record that a request failed.

        Args:
            model_name: Name of the model that failed
            error: The exception that occurred
        """

    @abstractmethod
    def should_retry_after_error(self, model_name: str) -> Tuple[bool, float]:
        """Determine if we should retry after a rate limit error.

        Uses exponential backoff and 90s rule:
        - Wait with exponential backoff from last call
        - After 90s from last FAILED call, make one final attempt
        - If that fails too, signal fallback

        Args:
            model_name: Name of the model that failed

        Returns:
            (should_retry, wait_time_seconds)
            - should_retry: True if should retry, False if should fallback
            - wait_time_seconds: How long to wait before retry (if should_retry=True)
        """

    @abstractmethod
    def get_status(self, model_name: str) -> dict:
        """Get current status for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with status information (requests made, tokens used, etc.)
        """


class ProactiveRateLimitScheduler(SchedulingStrategy):
    """Proactive scheduler that prevents rate limit errors.

    This strategy implements smart scheduling rules:
    1. NEVER reach N-1 of the limit (maintain N-2 safety margin)
    2. Space requests evenly: wait (60/RPM) seconds between requests
    3. Account for time already elapsed since last request

    Example:
        >>> scheduler = ProactiveRateLimitScheduler(
        ...     rate_tracker=global_tracker,
        ...     safety_margin=2  # Stop at N-2 of limit
        ... )
        >>> can_proceed, wait_time = scheduler.can_proceed("openai/gpt-4o-mini", 1000)
        >>> if not can_proceed:
        ...     time.sleep(wait_time)
        >>> # Now safe to proceed
        >>> response = llm.invoke(...)
        >>> scheduler.record_request("openai/gpt-4o-mini", actual_tokens=1234)
    """

    def __init__(self, rate_tracker, safety_margin: int = 2, max_retries: int = 3, backoff_base: float = 2.0):
        """Initialize proactive rate limit scheduler.

        Args:
            rate_tracker: RateLimitTracker instance to query current usage
            safety_margin: How many requests to stay below limit (default: 2 for N-2)
            max_retries: Maximum retry attempts after errors (default: 3)
            backoff_base: Exponential backoff multiplier (default: 2.0)
        """
        from coffee_maker.langfuse_observe.rate_limiter import RateLimitTracker

        if not isinstance(rate_tracker, RateLimitTracker):
            raise TypeError(f"rate_tracker must be RateLimitTracker, got {type(rate_tracker)}")

        self.rate_tracker = rate_tracker
        self.safety_margin = safety_margin
        self.max_retries = max_retries
        self.backoff_base = backoff_base

        # Track errors per model
        self._error_history: Dict[str, List[Tuple[float, Exception, int]]] = (
            {}
        )  # {model_name: [(timestamp, error, retry_count), ...]}
        self._last_failed_call: Dict[str, float] = {}  # {model_name: timestamp}
        self._final_attempt_made: Dict[str, bool] = {}  # {model_name: bool}

    def can_proceed(self, model_name: str, estimated_tokens: int) -> Tuple[bool, float]:
        """Check if we can safely proceed with a request.

        Implements the scheduling rules:
        1. Check if we're at N-2 of request limit (safety margin)
        2. Check if we're at N-2 of token limit (safety margin)
        3. Calculate minimum wait time based on RPM (60/RPM spacing)
        4. Account for time already elapsed since last call

        Args:
            model_name: Name of the model to invoke
            estimated_tokens: Estimated tokens for the request

        Returns:
            (can_proceed, wait_time_seconds)
        """
        # Get current limits and usage
        if model_name not in self.rate_tracker.model_limits:
            logger.warning(f"Model {model_name} not found in rate tracker, allowing request")
            return True, 0.0

        limits = self.rate_tracker.model_limits[model_name]
        rpm = limits.requests_per_minute
        tpm = limits.tokens_per_minute

        # Get current usage in the last minute
        usage_stats = self.rate_tracker.get_usage_stats(model_name)
        requests_in_window = usage_stats.get("requests_per_minute", {}).get("current", 0)
        tokens_in_window = usage_stats.get("tokens_per_minute", {}).get("current", 0)

        # Calculate safe limits (N - safety_margin)
        safe_request_limit = rpm - self.safety_margin if rpm != float("inf") else float("inf")
        safe_token_limit = tpm - self.safety_margin if tpm != float("inf") else float("inf")

        # Check 1: Would this request exceed our safety margin?
        would_exceed_requests = requests_in_window >= safe_request_limit
        would_exceed_tokens = (tokens_in_window + estimated_tokens) >= safe_token_limit

        if would_exceed_requests or would_exceed_tokens:
            # We're at safety margin, need to wait for window to slide
            wait_time = self._calculate_wait_for_capacity(
                model_name, estimated_tokens, safe_request_limit, safe_token_limit
            )
            logger.info(
                f"At safety margin for {model_name} "
                f"({requests_in_window}/{safe_request_limit} requests, "
                f"{tokens_in_window}/{safe_token_limit} tokens). "
                f"Waiting {wait_time:.1f}s for capacity."
            )
            return False, wait_time

        # Check 2: Minimum spacing between requests (60/RPM)
        last_call_time = self.rate_tracker.get_last_call_time()
        if last_call_time is not None and rpm != float("inf"):
            time_since_last_call = time.time() - last_call_time
            min_spacing = 60.0 / rpm  # seconds between requests

            if time_since_last_call < min_spacing:
                remaining_wait = min_spacing - time_since_last_call
                logger.debug(
                    f"Enforcing {min_spacing:.2f}s spacing for {model_name} "
                    f"(RPM={rpm}). Waiting {remaining_wait:.2f}s more."
                )
                return False, remaining_wait

        # Safe to proceed
        return True, 0.0

    def _calculate_wait_for_capacity(
        self, model_name: str, estimated_tokens: int, safe_request_limit: float, safe_token_limit: float
    ) -> float:
        """Calculate how long to wait for sufficient capacity.

        Looks at the sliding window to determine when the oldest requests/tokens
        will expire, freeing up capacity.

        Args:
            model_name: Name of the model
            estimated_tokens: Tokens needed for the request
            safe_request_limit: Safe request limit (with margin)
            safe_token_limit: Safe token limit (with margin)

        Returns:
            Seconds to wait for capacity
        """
        # Get the request history for this model
        if model_name not in self.rate_tracker._request_history:
            return 0.0

        history = self.rate_tracker._request_history[model_name]
        if not history:
            return 0.0

        current_time = time.time()
        window_start = current_time - 60  # 1 minute sliding window

        # Find the oldest request that would need to expire
        # to free up capacity for our request
        requests_to_free = 1  # We need space for 1 more request
        tokens_to_free = estimated_tokens  # We need space for these tokens

        # Sort history by timestamp
        sorted_history = sorted(history, key=lambda x: x.timestamp)

        # Filter to only requests in current window
        requests_in_window = [r for r in sorted_history if r.timestamp >= window_start]

        if not requests_in_window:
            # No requests in window, shouldn't be at capacity
            return 0.0

        # Calculate current counts
        current_requests = len(requests_in_window)
        current_tokens = sum(r.tokens for r in requests_in_window)

        # Find when we'll have enough capacity
        for record in requests_in_window:
            # If this request expires, will we have enough capacity?
            future_requests = current_requests - 1
            future_tokens = current_tokens - record.tokens

            if future_requests < safe_request_limit and (future_tokens + estimated_tokens) < safe_token_limit:
                # This request expiring gives us enough capacity
                wait_time = (record.timestamp + 60) - current_time
                return max(0.0, wait_time)

        # Fallback: wait until oldest request in window expires
        oldest_timestamp = requests_in_window[0].timestamp
        wait_time = (oldest_timestamp + 60) - current_time
        return max(0.0, wait_time)

    def record_request(self, model_name: str, actual_tokens: int) -> None:
        """Record that a request was made successfully.

        Clears error history for this model since request succeeded.

        Args:
            model_name: Name of the model invoked
            actual_tokens: Actual tokens used in the request
        """
        self.rate_tracker.record_request(model_name, actual_tokens)
        self.rate_tracker.set_last_call_time(time.time())

        # Clear error history on success
        if model_name in self._error_history:
            del self._error_history[model_name]
        if model_name in self._last_failed_call:
            del self._last_failed_call[model_name]
        if model_name in self._final_attempt_made:
            del self._final_attempt_made[model_name]

    def record_error(self, model_name: str, error: Exception) -> None:
        """Record that a request failed.

        Args:
            model_name: Name of the model that failed
            error: The exception that occurred
        """
        current_time = time.time()

        # Initialize error history for this model if needed
        if model_name not in self._error_history:
            self._error_history[model_name] = []

        # Get current retry count
        retry_count = len(self._error_history[model_name])

        # Record this error
        self._error_history[model_name].append((current_time, error, retry_count))
        self._last_failed_call[model_name] = current_time

        logger.warning(f"Rate limit error for {model_name} (attempt {retry_count + 1}/{self.max_retries}): {error}")

    def should_retry_after_error(self, model_name: str) -> Tuple[bool, float]:
        """Determine if we should retry after a rate limit error.

        Implements the 90s rule:
        1. Retry with exponential backoff up to max_retries
        2. After max_retries, check if 90s have passed since last FAILED call
        3. If yes: make ONE FINAL ATTEMPT
        4. If that final attempt also fails: return (False, 0) to signal fallback

        Args:
            model_name: Name of the model that failed

        Returns:
            (should_retry, wait_time_seconds)
            - should_retry: True if should retry, False if should give up/fallback
            - wait_time_seconds: How long to wait before retry
        """
        if model_name not in self._error_history:
            # No errors recorded, shouldn't be here
            return True, 0.0

        error_count = len(self._error_history[model_name])
        last_failed_time = self._last_failed_call.get(model_name, 0)
        time_since_last_failure = time.time() - last_failed_time

        # Check if we've already made the final attempt
        if self._final_attempt_made.get(model_name, False):
            logger.error(f"Final attempt for {model_name} also failed after 90s rule. Signaling fallback.")
            return False, 0.0  # Give up, signal fallback

        # Still within max_retries: use exponential backoff
        if error_count < self.max_retries:
            # Exponential backoff: base^retry_count seconds
            # retry 0: 2^0 = 1s
            # retry 1: 2^1 = 2s
            # retry 2: 2^2 = 4s
            wait_time = 60 * (self.backoff_base**error_count)  # Start at 60s base

            logger.info(
                f"Retry {error_count + 1}/{self.max_retries} for {model_name} "
                f"with exponential backoff: {wait_time:.1f}s"
            )
            return True, wait_time

        # Exhausted max_retries: apply 90s rule
        MIN_WAIT_BEFORE_FINAL_ATTEMPT = 90.0

        if time_since_last_failure < MIN_WAIT_BEFORE_FINAL_ATTEMPT:
            # Need to wait until 90s have passed
            remaining_wait = MIN_WAIT_BEFORE_FINAL_ATTEMPT - time_since_last_failure
            logger.info(
                f"Max retries exhausted for {model_name}. "
                f"Waiting {remaining_wait:.1f}s more to reach 90s since last failure, "
                f"then making ONE FINAL ATTEMPT."
            )
            return True, remaining_wait

        # 90s have passed, make final attempt
        logger.info(
            f"90s have passed since last failure for {model_name}. " f"Making ONE FINAL ATTEMPT before fallback."
        )
        self._final_attempt_made[model_name] = True
        return True, 0.0  # Proceed immediately with final attempt

    def get_status(self, model_name: str) -> dict:
        """Get current scheduling status for a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with current usage and limits
        """
        if model_name not in self.rate_tracker.model_limits:
            return {"error": f"Model {model_name} not found"}

        limits = self.rate_tracker.model_limits[model_name]
        current_usage = self.rate_tracker.get_current_usage(model_name)

        rpm = limits.get("requests_per_minute", float("inf"))
        tpm = limits.get("tokens_per_minute", float("inf"))

        safe_request_limit = rpm - self.safety_margin if rpm != float("inf") else float("inf")
        safe_token_limit = tpm - self.safety_margin if tpm != float("inf") else float("inf")

        return {
            "model": model_name,
            "current_requests": current_usage["requests"],
            "safe_request_limit": safe_request_limit,
            "total_request_limit": rpm,
            "current_tokens": current_usage["tokens"],
            "safe_token_limit": safe_token_limit,
            "total_token_limit": tpm,
            "at_capacity": current_usage["requests"] >= safe_request_limit,
            "last_call_time": self.rate_tracker.get_last_call_time(),
        }

    def wait_until_ready(self, model_name: str, estimated_tokens: int, max_wait: float = 300.0) -> bool:
        """Wait until it's safe to make a request.

        Args:
            model_name: Name of the model
            estimated_tokens: Estimated tokens for the request
            max_wait: Maximum seconds to wait (default: 300s = 5min)

        Returns:
            True if ready to proceed, False if max_wait exceeded
        """
        start_time = time.time()

        while True:
            can_proceed, wait_time = self.can_proceed(model_name, estimated_tokens)

            if can_proceed:
                return True

            # Check if waiting would exceed max_wait
            elapsed = time.time() - start_time
            if elapsed + wait_time > max_wait:
                logger.warning(
                    f"Would exceed max_wait ({max_wait}s) waiting for {model_name}. "
                    f"Elapsed: {elapsed:.1f}s, Need: {wait_time:.1f}s more"
                )
                return False

            # Wait and check again
            logger.info(f"Waiting {wait_time:.1f}s for {model_name} scheduling...")
            time.sleep(wait_time)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ProactiveRateLimitScheduler(safety_margin={self.safety_margin})"
