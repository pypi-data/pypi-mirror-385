"""Custom exceptions for langfuse_observe module.

This module provides centralized exception definitions for the langfuse_observe
package, ensuring single source of truth for error handling.

Example:
    >>> from coffee_maker.langfuse_observe.exceptions import ContextLengthError
    >>>
    >>> raise ContextLengthError(
    ...     model="gpt-4o",
    ...     required=150000,
    ...     available=128000
    ... )
"""

from typing import Optional


class ContextLengthError(Exception):
    """Raised when input exceeds model's context length.

    This exception is raised when the tokenized input to a language model
    exceeds the model's maximum context window size.

    Attributes:
        model: Name of the model that rejected the input
        required: Number of tokens required for the input
        available: Maximum tokens available in model's context window
    """

    def __init__(self, model: str, required: int, available: int):
        """Initialize ContextLengthError.

        Args:
            model: Name of the model
            required: Number of tokens required
            available: Maximum tokens available in context window
        """
        self.model = model
        self.required = required
        self.available = available
        super().__init__(f"Context length exceeded for {model}: " f"required {required} tokens, available {available}")


class BudgetExceededError(Exception):
    """Raised when cost budget limit is exceeded.

    This exception is raised when an operation would cause the total
    cost to exceed a predefined budget limit.

    Attributes:
        limit: Budget limit in USD
        actual: Actual cost that would be incurred
    """

    def __init__(self, limit: float, actual: float):
        """Initialize BudgetExceededError.

        Args:
            limit: Budget limit in USD
            actual: Actual cost in USD
        """
        self.limit = limit
        self.actual = actual
        super().__init__(f"Budget exceeded: limit ${limit:.4f}, actual ${actual:.4f}")


class ModelNotAvailableError(Exception):
    """Raised when requested model is not available.

    This exception is raised when a requested model is not configured,
    not accessible, or temporarily unavailable.

    Attributes:
        model: Name of the requested model
        provider: Provider name (e.g., "openai", "anthropic")
        reason: Optional reason for unavailability
    """

    def __init__(self, model: str, provider: str, reason: Optional[str] = None):
        """Initialize ModelNotAvailableError.

        Args:
            model: Name of the model
            provider: Provider name
            reason: Optional reason for unavailability
        """
        self.model = model
        self.provider = provider
        self.reason = reason

        message = f"Model {model} not available from provider {provider}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded.

    This exception is raised when API rate limits are exceeded and
    retry logic has been exhausted.

    Attributes:
        provider: Provider name
        limit_type: Type of limit exceeded (e.g., "requests", "tokens")
        retry_after: Optional seconds to wait before retrying
    """

    def __init__(self, provider: str, limit_type: str, retry_after: Optional[int] = None):
        """Initialize RateLimitExceededError.

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
        super().__init__(message)


class QuotaExceededError(Exception):
    """Raised when API quota/budget is exceeded (ResourceExhausted errors).

    This exception is raised when API quota limits are exceeded, distinct from
    rate limits. Quota errors indicate the account has hit spending limits,
    free tier limits, or other budget-related constraints.

    Common scenarios:
    - Google Gemini: "You exceeded your current quota, please check your plan"
    - OpenAI: Monthly spending limit reached
    - Anthropic: Account credit exhausted

    Attributes:
        provider: Provider name (e.g., "gemini", "openai", "anthropic")
        model: Model that triggered the quota error
        quota_type: Type of quota exceeded (e.g., "free_tier", "monthly_budget", "tokens")
        message_detail: Detailed error message from the provider
        retry_after: Optional seconds to wait (if provided by API)
    """

    def __init__(
        self,
        provider: str,
        model: str,
        quota_type: str = "unknown",
        message_detail: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        """Initialize QuotaExceededError.

        Args:
            provider: Provider name
            model: Model name
            quota_type: Type of quota exceeded
            message_detail: Detailed error message from provider
            retry_after: Optional seconds to wait before retrying
        """
        self.provider = provider
        self.model = model
        self.quota_type = quota_type
        self.message_detail = message_detail
        self.retry_after = retry_after

        message = f"Quota exceeded for {provider}/{model}: {quota_type}"
        if message_detail:
            message += f" - {message_detail}"
        if retry_after:
            message += f". Please retry in {retry_after} seconds"

        super().__init__(message)
