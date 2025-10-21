"""Rate limiting tracker using sliding window algorithm for LLM API calls."""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limits of a specific model."""

    requests_per_minute: int
    tokens_per_minute: int
    requests_per_day: Optional[int] = None


@dataclass
class RequestRecord:
    """Record of a single API request."""

    timestamp: float
    tokens: int


class RateLimitTracker:
    """Thread-safe rate limit tracker with sliding window for multiple models."""

    def __init__(self, model_limits: Dict[str, RateLimitConfig]):
        """Initialize with model limits dictionary."""
        self.model_limits = model_limits
        self._request_history: Dict[str, deque] = {model: deque() for model in model_limits}
        self._daily_requests: Dict[str, int] = {model: 0 for model in model_limits}
        self._daily_reset_time: Dict[str, float] = {model: time.time() + 86400 for model in model_limits}
        self._lock = threading.Lock()
        self._last_call_time: Optional[float] = None  # Global timestamp of last LLM call attempt

    def can_make_request(self, model: str, estimated_tokens: int) -> bool:
        """Check if a request can be made without hitting rate limits.

        Args:
            model: Model name to check
            estimated_tokens: Estimated number of tokens for the request

        Returns:
            True if request can be made, False otherwise
        """
        if model not in self.model_limits:
            logger.warning(f"Model {model} not configured for rate limiting, allowing request")
            return True

        with self._lock:
            self._cleanup_old_requests(model)
            self._reset_daily_count_if_needed(model)

            limits = self.model_limits[model]
            history = self._request_history[model]

            # Check requests per minute
            current_rpm = len(history)
            if current_rpm >= limits.requests_per_minute:
                logger.debug(f"RPM limit reached for {model}: {current_rpm}/{limits.requests_per_minute}")
                return False

            # Check tokens per minute
            current_tpm = sum(record.tokens for record in history)
            if current_tpm + estimated_tokens > limits.tokens_per_minute:
                logger.debug(
                    f"TPM limit would be exceeded for {model}: "
                    f"{current_tpm + estimated_tokens}/{limits.tokens_per_minute}"
                )
                return False

            # Check requests per day if configured
            if limits.requests_per_day is not None:
                if self._daily_requests[model] >= limits.requests_per_day:
                    logger.debug(
                        f"Daily request limit reached for {model}: "
                        f"{self._daily_requests[model]}/{limits.requests_per_day}"
                    )
                    return False

            return True

    def record_request(self, model: str, tokens_used: int):
        """Record a completed request.

        Args:
            model: Model name
            tokens_used: Number of tokens used in the request
        """
        if model not in self.model_limits:
            logger.warning(f"Model {model} not configured for rate limiting")
            return

        with self._lock:
            record = RequestRecord(timestamp=time.time(), tokens=tokens_used)
            self._request_history[model].append(record)
            self._daily_requests[model] += 1

            logger.debug(f"Recorded request for {model}: {tokens_used} tokens")

    def get_wait_time(self, model: str, estimated_tokens: int) -> float:
        """Calculate how long to wait before a request can be made.

        Args:
            model: Model name
            estimated_tokens: Estimated tokens for the request

        Returns:
            Seconds to wait (0 if request can be made immediately)
        """
        if model not in self.model_limits:
            return 0.0

        with self._lock:
            self._cleanup_old_requests(model)

            limits = self.model_limits[model]
            history = self._request_history[model]

            if not history:
                return 0.0

            wait_times = []

            # Check if we need to wait for RPM limit
            if len(history) >= limits.requests_per_minute:
                oldest_request = history[0]
                time_since_oldest = time.time() - oldest_request.timestamp
                rpm_wait = max(0, 60 - time_since_oldest)
                wait_times.append(rpm_wait)

            # Check if we need to wait for TPM limit
            current_tpm = sum(record.tokens for record in history)
            if current_tpm + estimated_tokens > limits.tokens_per_minute:
                # Find when enough tokens will expire to make the request
                tokens_needed_to_expire = current_tpm + estimated_tokens - limits.tokens_per_minute
                tokens_expired = 0
                for record in history:
                    tokens_expired += record.tokens
                    if tokens_expired >= tokens_needed_to_expire:
                        time_since = time.time() - record.timestamp
                        tpm_wait = max(0, 60 - time_since)
                        wait_times.append(tpm_wait)
                        break

            return max(wait_times) if wait_times else 0.0

    def get_usage_stats(self, model: str) -> Dict:
        """Get current usage statistics for a model.

        Args:
            model: Model name

        Returns:
            Dictionary with usage statistics
        """
        if model not in self.model_limits:
            return {}

        with self._lock:
            self._cleanup_old_requests(model)
            self._reset_daily_count_if_needed(model)

            limits = self.model_limits[model]
            history = self._request_history[model]

            current_rpm = len(history)
            current_tpm = sum(record.tokens for record in history)

            return {
                "requests_per_minute": {
                    "current": current_rpm,
                    "limit": limits.requests_per_minute,
                    "usage_percent": (
                        (current_rpm / limits.requests_per_minute * 100) if limits.requests_per_minute > 0 else 0
                    ),
                },
                "tokens_per_minute": {
                    "current": current_tpm,
                    "limit": limits.tokens_per_minute,
                    "usage_percent": (
                        (current_tpm / limits.tokens_per_minute * 100) if limits.tokens_per_minute > 0 else 0
                    ),
                },
                "requests_today": self._daily_requests[model],
                "daily_limit": limits.requests_per_day,
            }

    def get_last_call_time(self) -> Optional[float]:
        """Get the timestamp of the last LLM call attempt.

        Returns:
            Timestamp of last call, or None if no calls made yet
        """
        with self._lock:
            return self._last_call_time

    def set_last_call_time(self, timestamp: float):
        """Set the timestamp of the last LLM call attempt.

        Args:
            timestamp: Timestamp to set
        """
        with self._lock:
            self._last_call_time = timestamp

    def _cleanup_old_requests(self, model: str):
        """Remove requests older than 1 minute from history.

        Args:
            model: Model name
        """
        cutoff_time = time.time() - 60  # 60 seconds = 1 minute
        history = self._request_history[model]

        while history and history[0].timestamp < cutoff_time:
            history.popleft()

    def _reset_daily_count_if_needed(self, model: str):
        """Reset daily request count if 24 hours have passed.

        Args:
            model: Model name
        """
        current_time = time.time()
        if current_time >= self._daily_reset_time[model]:
            logger.info(f"Resetting daily request count for {model}")
            self._daily_requests[model] = 0
            self._daily_reset_time[model] = current_time + 86400  # 24 hours
