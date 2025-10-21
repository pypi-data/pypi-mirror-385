"""Utilities for parsing LLM responses."""

from typing import Any, Tuple


def extract_token_usage(response: Any) -> Tuple[int, int]:
    """Extract token usage from LLM response.

    Args:
        response: LLM response object

    Returns:
        Tuple of (input_tokens, output_tokens)
    """
    input_tokens = 0
    output_tokens = 0

    # Try to extract actual usage from response metadata
    if hasattr(response, "response_metadata") and response.response_metadata:
        usage = response.response_metadata.get("usage", {})
        input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
        output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
    elif hasattr(response, "usage_metadata") and response.usage_metadata:
        # LangChain format
        input_tokens = getattr(response.usage_metadata, "input_tokens", 0)
        output_tokens = getattr(response.usage_metadata, "output_tokens", 0)

    return input_tokens, output_tokens


def is_rate_limit_error(error: Exception) -> bool:
    """Check if an error is a rate limit error (temporary throttling).

    Rate limit errors are temporary and indicate too many requests in a short time.
    These are distinct from quota errors which indicate budget/spending limits.

    Args:
        error: Exception to check

    Returns:
        True if it's a rate limit error (429, throttling, etc.)
    """
    error_msg = str(error).lower()
    rate_limit_keywords = [
        "rate limit",
        "ratelimit",
        "429",
        "too many requests",
        "throttl",  # throttle, throttling
        "requests per",  # requests per minute/second/etc
    ]
    return any(keyword in error_msg for keyword in rate_limit_keywords)


def is_quota_exceeded_error(error: Exception) -> Tuple[bool, str, int]:
    """Check if an error is a quota/budget exceeded error (ResourceExhausted).

    Quota errors indicate spending limits, free tier exhaustion, or account budget limits.
    These are distinct from rate limits and usually require different handling (fallback to
    different model or manual intervention).

    Args:
        error: Exception to check

    Returns:
        Tuple of (is_quota_error, quota_type, retry_after_seconds)
        - is_quota_error: True if it's a quota exceeded error
        - quota_type: Type of quota ("free_tier", "monthly_budget", "unknown")
        - retry_after_seconds: Seconds to wait if specified in error (0 if not specified)
    """
    error_msg = str(error).lower()

    # Quota-specific keywords (distinct from rate limiting)
    quota_keywords = [
        "quota",
        "resource_exhausted",  # gRPC error code
        "resourceexhausted",
        "exceeded your current quota",
        "quota exceeded",
        "spending limit",
        "budget",
        "credit",
        "insufficient funds",
        "free tier",
    ]

    is_quota = any(keyword in error_msg for keyword in quota_keywords)

    if not is_quota:
        return False, "unknown", 0

    # Determine quota type
    quota_type = "unknown"
    if "free tier" in error_msg or "free_tier" in error_msg:
        quota_type = "free_tier"
    elif "monthly" in error_msg or "spending limit" in error_msg:
        quota_type = "monthly_budget"
    elif "credit" in error_msg or "insufficient funds" in error_msg:
        quota_type = "account_credit"

    # Try to extract retry_after from error message
    # Example: "Please retry in 31.940768649s"
    retry_after = 0
    if "retry" in error_msg:
        import re

        # Look for patterns like "31.94s" or "31 seconds"
        match = re.search(r"(\d+\.?\d*)\s*s(?:ec(?:ond)?s?)?", error_msg)
        if match:
            try:
                retry_after = int(float(match.group(1)))
            except ValueError:
                pass

    return True, quota_type, retry_after
