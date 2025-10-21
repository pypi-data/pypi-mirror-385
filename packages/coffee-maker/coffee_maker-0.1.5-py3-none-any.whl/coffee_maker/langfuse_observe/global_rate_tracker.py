"""Global rate tracker singleton for sharing rate limits across all LLM instances."""

import logging
from typing import Optional

from coffee_maker.langfuse_observe.llm_config import get_rate_limits_for_tier
from coffee_maker.langfuse_observe.rate_limiter import RateLimitTracker

logger = logging.getLogger(__name__)

# Global rate tracker instance (singleton)
_global_rate_tracker: Optional[RateLimitTracker] = None
_current_tier: Optional[str] = None
_last_call_time: Optional[float] = None  # Global timestamp of last LLM call


def get_global_rate_tracker(tier: str = "tier1") -> RateLimitTracker:
    """Get or create the global rate tracker singleton.

    This ensures that all LLM instances share the same rate limit tracking,
    preventing rate limit violations when multiple tools use the same model.

    Args:
        tier: API tier for rate limiting

    Returns:
        Shared RateLimitTracker instance
    """
    global _global_rate_tracker, _current_tier

    # If tier changed, reset the tracker
    if _current_tier is not None and _current_tier != tier:
        logger.warning(f"Tier changed from {_current_tier} to {tier}. " f"Resetting global rate tracker.")
        _global_rate_tracker = None

    # Create tracker if it doesn't exist
    if _global_rate_tracker is None:
        logger.info(f"Creating global rate tracker for tier: {tier}")
        rate_limits = get_rate_limits_for_tier(tier)
        _global_rate_tracker = RateLimitTracker(rate_limits)
        _current_tier = tier

    return _global_rate_tracker


def get_global_last_call_time() -> Optional[float]:
    """Get the global last call timestamp.

    Returns:
        Timestamp of last LLM call, or None if no calls made yet
    """
    global _last_call_time
    return _last_call_time


def set_global_last_call_time(timestamp: float):
    """Set the global last call timestamp.

    Args:
        timestamp: Timestamp to set
    """
    global _last_call_time
    _last_call_time = timestamp


def reset_global_rate_tracker():
    """Reset the global rate tracker.

    Useful for testing or when you want to start fresh.
    """
    global _global_rate_tracker, _current_tier, _last_call_time
    logger.info("Resetting global rate tracker")
    _global_rate_tracker = None
    _current_tier = None
    _last_call_time = None


def get_global_rate_tracker_stats():
    """Get statistics from the global rate tracker.

    Returns:
        Dictionary with stats for all models, or None if tracker doesn't exist
    """
    if _global_rate_tracker is None:
        return None

    # Get stats for all configured models
    stats = {}
    for model_name in _global_rate_tracker.model_limits.keys():
        stats[model_name] = _global_rate_tracker.get_usage_stats(model_name)

    return stats
