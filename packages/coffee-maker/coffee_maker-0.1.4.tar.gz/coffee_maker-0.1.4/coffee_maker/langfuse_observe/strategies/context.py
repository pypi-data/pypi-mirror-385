"""Context management strategies for LLM input length handling."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from coffee_maker.langfuse_observe.token_estimator import estimate_tokens

logger = logging.getLogger(__name__)


class ContextStrategy(ABC):
    """Base class for context length management."""

    @abstractmethod
    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits within model's context limit.

        Returns: (fits, estimated_tokens, max_context)
        """

    @abstractmethod
    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Get models that can handle the required token count."""


class LargeContextFallbackStrategy(ContextStrategy):
    """Finds models with larger context windows when needed."""

    def __init__(self, model_context_limits: Dict[str, int]):
        self.model_limits = model_context_limits

    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Check if input fits in model's context window."""
        estimated_tokens = estimate_tokens(input_data, model_name)
        max_context = self.model_limits.get(model_name, 10_000_000)
        fits = estimated_tokens <= max_context

        if not fits:
            logger.warning(
                f"Input ({estimated_tokens:,} tokens) exceeds {model_name} context limit ({max_context:,} tokens)"
            )

        return fits, estimated_tokens, max_context

    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Get models with sufficient context length, sorted by size."""
        suitable_models = [(model, limit) for model, limit in self.model_limits.items() if limit >= required_tokens]
        suitable_models.sort(key=lambda x: x[1])
        model_names = [model for model, _ in suitable_models]
        logger.info(f"Found {len(model_names)} models for {required_tokens:,} tokens: {model_names}")
        return model_names


class NoContextCheckStrategy(ContextStrategy):
    """Strategy that disables context checking (always returns fits=True)."""

    def check_fits(self, input_data: Any, model_name: str) -> Tuple[bool, int, int]:
        """Always return that input fits."""
        return True, 0, 10_000_000

    def get_larger_context_models(self, required_tokens: int) -> List[str]:
        """Return empty list (no alternatives needed)."""
        return []


def create_context_strategy(
    enable_context_check: bool = True,
    model_limits: Optional[Dict[str, int]] = None,
) -> ContextStrategy:
    """Factory to create context strategy."""
    if not enable_context_check:
        return NoContextCheckStrategy()

    if model_limits is None:
        try:
            from coffee_maker.langfuse_observe.llm_config import get_all_model_context_limits

            model_limits = get_all_model_context_limits()
        except ImportError:
            logger.warning("Could not import get_all_model_context_limits, using empty limits")
            model_limits = {}

    return LargeContextFallbackStrategy(model_context_limits=model_limits)
