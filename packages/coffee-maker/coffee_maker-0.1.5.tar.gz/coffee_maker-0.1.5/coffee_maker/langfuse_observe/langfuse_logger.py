"""Langfuse logging utilities for LLM events."""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LangfuseLogger:
    """Helper for logging events to Langfuse."""

    def __init__(self, client: Optional[Any] = None):
        """Initialize with Langfuse client."""
        self.client = client

    def log_generation(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cost_info: Dict[str, float],
        is_primary: bool,
        latency: float,
    ) -> None:
        """Log LLM generation to Langfuse."""
        if not self.client:
            return

        try:
            self.client.generation(
                name=f"llm_call_{model_name.replace('/', '_')}",
                model=model_name,
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
                metadata={
                    "cost_usd": cost_info["total_cost"],
                    "input_cost_usd": cost_info["input_cost"],
                    "output_cost_usd": cost_info["output_cost"],
                    "is_primary": is_primary,
                    "latency_seconds": latency,
                },
            )
            logger.debug(f"Logged cost to Langfuse: ${cost_info['total_cost']:.4f}")
        except Exception as e:
            logger.warning(f"Failed to log cost to Langfuse: {e}")

    def log_fallback(self, original_model: str, fallback_model: str, reason: str) -> None:
        """Log fallback event to Langfuse."""
        if not self.client:
            return

        try:
            self.client.event(
                name="fallback_success",
                metadata={
                    "original_model": original_model,
                    "fallback_model": fallback_model,
                    "reason": reason,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to log fallback to Langfuse: {e}")

    def log_context_fallback(
        self,
        original_model: str,
        fallback_model: str,
        estimated_tokens: int,
        original_max_context: int,
        fallback_max_context: int,
    ) -> None:
        """Log context length fallback to Langfuse."""
        if not self.client:
            return

        try:
            self.client.event(
                name="context_length_fallback",
                metadata={
                    "original_model": original_model,
                    "fallback_model": fallback_model,
                    "estimated_tokens": estimated_tokens,
                    "original_max_context": original_max_context,
                    "fallback_max_context": fallback_max_context,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to log context fallback to Langfuse: {e}")

    def log_quota_error(self, model: str, quota_type: str, error_message: str, retry_after: int = 0) -> None:
        """Log quota exceeded error to Langfuse.

        Args:
            model: Model that hit quota limit
            quota_type: Type of quota ("free_tier", "monthly_budget", "account_credit", "unknown")
            error_message: Full error message from provider
            retry_after: Seconds to wait before retry (0 if not specified)
        """
        if not self.client:
            return

        try:
            self.client.event(
                name="quota_exceeded",
                level="ERROR",
                metadata={
                    "model": model,
                    "quota_type": quota_type,
                    "error_message": error_message,
                    "retry_after_seconds": retry_after,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to log quota error to Langfuse: {e}")
