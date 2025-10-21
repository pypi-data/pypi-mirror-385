"""Fallback selection strategies for LLM orchestration.

This module provides strategies for selecting which fallback model to use
when the current model fails.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FallbackStrategy(ABC):
    """Abstract base class for fallback selection strategies.

    A fallback strategy determines which model to try next when a model fails.
    Different strategies can optimize for different goals (reliability, cost, performance).
    """

    @abstractmethod
    def select_next_fallback(
        self,
        failed_model_name: str,
        available_fallbacks: List[str],
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Select the next fallback model to try.

        Args:
            failed_model_name: Name of the model that just failed
            available_fallbacks: List of remaining fallback model names
            error: The exception that was raised
            metadata: Optional context (e.g., estimated_tokens, attempt_count)

        Returns:
            Model name to try next, or None if no suitable fallback
        """


class SequentialFallback(FallbackStrategy):
    """Sequential fallback strategy - tries fallbacks in order.

    This is the simplest strategy: just try each fallback in the order provided.
    This is the default behavior of the original AutoPickerLLM.
    """

    def select_next_fallback(
        self,
        failed_model_name: str,
        available_fallbacks: List[str],
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Select first available fallback.

        Args:
            failed_model_name: Failed model (unused)
            available_fallbacks: Remaining fallbacks
            error: Error that occurred (unused)
            metadata: Optional context (unused)

        Returns:
            First fallback in list, or None if list is empty
        """
        if not available_fallbacks:
            return None

        next_fallback = available_fallbacks[0]
        logger.info(f"Sequential fallback: {failed_model_name} → {next_fallback}")
        return next_fallback


class SmartFallback(FallbackStrategy):
    """Smart fallback strategy - selects based on error type and model characteristics.

    This strategy analyzes the error and chooses the most appropriate fallback:
    - ContextLengthError → Choose model with larger context
    - RateLimitError → Choose model from different provider
    - Other errors → Fall back to sequential
    """

    def __init__(self, model_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize smart fallback strategy.

        Args:
            model_configs: Dict mapping model names to their configs
                          (e.g., {"openai/gpt-4o": {"context_length": 128000, "provider": "openai"}})
        """
        self.model_configs = model_configs or {}

    def select_next_fallback(
        self,
        failed_model_name: str,
        available_fallbacks: List[str],
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Select fallback based on error type.

        Args:
            failed_model_name: Failed model name
            available_fallbacks: Remaining fallbacks
            error: Error that occurred
            metadata: Optional context (estimated_tokens, etc.)

        Returns:
            Best fallback for this error type
        """
        if not available_fallbacks:
            return None

        error_msg = str(error).lower()

        # Check error type
        if self._is_context_error(error, error_msg):
            return self._select_larger_context(failed_model_name, available_fallbacks, metadata)
        elif self._is_rate_limit_error(error_msg):
            return self._select_different_provider(failed_model_name, available_fallbacks)
        else:
            # Default to sequential
            return available_fallbacks[0]

    def _is_context_error(self, error: Exception, error_msg: str) -> bool:
        """Check if error is related to context length.

        Args:
            error: The exception
            error_msg: Error message (lowercase)

        Returns:
            True if context length error
        """
        context_keywords = [
            "context",
            "context length",
            "too large",
            "exceeds",
            "maximum context",
            "token limit",
        ]
        return any(keyword in error_msg for keyword in context_keywords)

    def _is_rate_limit_error(self, error_msg: str) -> bool:
        """Check if error is related to rate limiting.

        Args:
            error_msg: Error message (lowercase)

        Returns:
            True if rate limit error
        """
        rate_limit_keywords = [
            "rate limit",
            "ratelimit",
            "429",
            "quota",
            "too many requests",
            "resource_exhausted",
        ]
        return any(keyword in error_msg for keyword in rate_limit_keywords)

    def _select_larger_context(
        self,
        failed_model: str,
        available: List[str],
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Select fallback with larger context window.

        Args:
            failed_model: Model that failed
            available: Available fallbacks
            metadata: Context (may include estimated_tokens)

        Returns:
            Fallback with largest context
        """
        # Get required tokens from metadata
        required_tokens = metadata.get("estimated_tokens", 0) if metadata else 0

        # Find fallbacks with sufficient context
        suitable = []
        for model in available:
            config = self.model_configs.get(model, {})
            context_limit = config.get("context_length", float("inf"))
            if context_limit >= required_tokens:
                suitable.append((model, context_limit))

        if suitable:
            # Sort by context length (smallest sufficient)
            suitable.sort(key=lambda x: x[1])
            selected = suitable[0][0]
            logger.info(f"Smart fallback (context): {failed_model} → {selected} " f"(need {required_tokens:,} tokens)")
            return selected

        # No suitable model, just return first
        logger.warning(f"No model with sufficient context for {required_tokens:,} tokens")
        return available[0]

    def _select_different_provider(self, failed_model: str, available: List[str]) -> str:
        """Select fallback from different provider.

        Args:
            failed_model: Model that failed
            available: Available fallbacks

        Returns:
            Fallback from different provider, or first if none found
        """
        # Extract provider from failed model
        failed_provider = failed_model.split("/")[0] if "/" in failed_model else None

        # Try to find fallback from different provider
        for model in available:
            model_provider = model.split("/")[0] if "/" in model else None
            if model_provider != failed_provider:
                logger.info(f"Smart fallback (rate limit): {failed_model} → {model} (different provider)")
                return model

        # All same provider, just return first
        logger.info(f"Smart fallback (rate limit): {failed_model} → {available[0]} (same provider)")
        return available[0]


class CostOptimizedFallback(FallbackStrategy):
    """Cost-optimized fallback strategy - prefers cheaper models.

    This strategy selects the cheapest available fallback model.
    Useful for cost-sensitive applications.
    """

    def __init__(self, model_costs: Optional[Dict[str, float]] = None):
        """Initialize cost-optimized fallback.

        Args:
            model_costs: Dict mapping model names to cost per 1K tokens
                        (e.g., {"openai/gpt-4o-mini": 0.15})
        """
        self.model_costs = model_costs or {}

    def select_next_fallback(
        self,
        failed_model_name: str,
        available_fallbacks: List[str],
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Select cheapest available fallback.

        Args:
            failed_model_name: Failed model (unused)
            available_fallbacks: Remaining fallbacks
            error: Error (unused)
            metadata: Context (unused)

        Returns:
            Cheapest fallback model
        """
        if not available_fallbacks:
            return None

        # Sort by cost (cheapest first)
        sorted_fallbacks = sorted(
            available_fallbacks,
            key=lambda m: self.model_costs.get(m, float("inf")),
        )

        selected = sorted_fallbacks[0]
        cost = self.model_costs.get(selected, "unknown")
        logger.info(f"Cost-optimized fallback: {failed_model_name} → {selected} (cost: ${cost}/1K tokens)")
        return selected


def create_fallback_strategy(
    strategy_type: str = "sequential",
    model_configs: Optional[Dict[str, Dict[str, Any]]] = None,
    model_costs: Optional[Dict[str, float]] = None,
) -> FallbackStrategy:
    """Factory function to create fallback strategy.

    Args:
        strategy_type: Type of strategy ("sequential", "smart", "cost")
        model_configs: Model configurations (for smart strategy)
        model_costs: Model costs (for cost strategy)

    Returns:
        FallbackStrategy instance

    Example:
        >>> strategy = create_fallback_strategy("smart", model_configs={
        ...     "openai/gpt-4o-mini": {"context_length": 128000, "provider": "openai"},
        ...     "gemini/gemini-2.5-flash": {"context_length": 1000000, "provider": "gemini"},
        ... })
    """
    if strategy_type == "sequential":
        return SequentialFallback()
    elif strategy_type == "smart":
        return SmartFallback(model_configs=model_configs)
    elif strategy_type == "cost":
        return CostOptimizedFallback(model_costs=model_costs)
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
