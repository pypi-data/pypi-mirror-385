"""AutoPickerLLM Refactored: Simplified LLM orchestrator with fallback capabilities."""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult
from pydantic import ConfigDict

from coffee_maker.langfuse_observe.langfuse_logger import LangfuseLogger
from coffee_maker.langfuse_observe.response_parser import (
    extract_token_usage,
    is_quota_exceeded_error,
    is_rate_limit_error,
)
from coffee_maker.langfuse_observe.strategies.context import ContextStrategy, create_context_strategy
from coffee_maker.langfuse_observe.strategies.fallback import FallbackStrategy, SequentialFallback
from coffee_maker.langfuse_observe.strategies.metrics import MetricsStrategy, NoOpMetrics

logger = logging.getLogger(__name__)


class AutoPickerLLMRefactored(BaseLLM):
    """LLM orchestrator with fallback capabilities and cost tracking."""

    # Pydantic model fields
    primary_llm: Any  # Should be ScheduledLLM
    primary_model_name: str
    fallback_llms: List[Tuple[Any, str]]  # List of (ScheduledLLM, model_name)
    fallback_strategy: FallbackStrategy  # Strategy for selecting fallbacks
    metrics_strategy: MetricsStrategy  # Strategy for metrics collection
    context_strategy: ContextStrategy  # Strategy for context length management
    cost_calculator: Optional[Any] = None  # CostCalculator instance
    langfuse_client: Optional[Any] = None  # Langfuse client for logging
    enable_context_fallback: bool = True  # Enable automatic context length fallback
    stats: Dict[str, int] = {}
    _langfuse_logger: Optional[LangfuseLogger] = None  # Lazy-loaded logger

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        primary_llm: Any,
        primary_model_name: str,
        fallback_llms: List[Tuple[Any, str]],
        fallback_strategy: Optional[FallbackStrategy] = None,
        metrics_strategy: Optional[MetricsStrategy] = None,
        context_strategy: Optional[ContextStrategy] = None,
        cost_calculator: Optional[Any] = None,
        langfuse_client: Optional[Any] = None,
        enable_context_fallback: bool = True,
        **kwargs,
    ):
        """Initialize AutoPickerLLMRefactored."""
        # Initialize statistics
        stats = {
            "total_requests": 0,
            "primary_requests": 0,
            "fallback_requests": 0,
            "rate_limit_fallbacks": 0,
            "quota_fallbacks": 0,
            "context_fallbacks": 0,
        }

        # Use default fallback strategy if none provided
        if fallback_strategy is None:
            fallback_strategy = SequentialFallback()

        # Use default metrics strategy if none provided
        if metrics_strategy is None:
            metrics_strategy = NoOpMetrics()

        # Use default context strategy if none provided
        if context_strategy is None:
            context_strategy = create_context_strategy()

        # Create Langfuse logger if client provided
        langfuse_logger = LangfuseLogger(langfuse_client) if langfuse_client else None

        # Call parent init
        super().__init__(
            primary_llm=primary_llm,
            primary_model_name=primary_model_name,
            fallback_llms=fallback_llms,
            fallback_strategy=fallback_strategy,
            metrics_strategy=metrics_strategy,
            context_strategy=context_strategy,
            cost_calculator=cost_calculator,
            langfuse_client=langfuse_client,
            enable_context_fallback=enable_context_fallback,
            stats=stats,
            _langfuse_logger=langfuse_logger,
            **kwargs,
        )

    def invoke(self, input_data: dict, **kwargs) -> Any:
        """Invoke LLM with fallback orchestration."""
        self.stats["total_requests"] += 1

        # Try primary model first
        primary_error = None
        result = self._try_invoke_model_with_error(
            self.primary_llm, self.primary_model_name, input_data, is_primary=True, **kwargs
        )

        if result["success"]:
            return result["response"]

        primary_error = result["error"]

        # Try fallback models using strategy
        logger.info(f"Primary model {self.primary_model_name} failed, trying fallbacks")

        # Build available fallbacks list
        available_fallback_names = [name for _, name in self.fallback_llms]
        fallback_dict = {name: llm for llm, name in self.fallback_llms}

        # Estimate tokens for smart fallback (if needed)
        estimated_tokens = self._estimate_tokens(input_data, self.primary_model_name)
        metadata = {"estimated_tokens": estimated_tokens}

        while available_fallback_names:
            # Use strategy to select next fallback
            next_fallback_name = self.fallback_strategy.select_next_fallback(
                failed_model_name=self.primary_model_name if primary_error else "previous_fallback",
                available_fallbacks=available_fallback_names,
                error=primary_error if primary_error else Exception("Unknown error"),
                metadata=metadata,
            )

            if next_fallback_name is None:
                break

            # Remove selected fallback from available list
            available_fallback_names.remove(next_fallback_name)
            fallback_llm = fallback_dict[next_fallback_name]

            logger.info(f"Attempting fallback to {next_fallback_name}")
            result = self._try_invoke_model_with_error(
                fallback_llm, next_fallback_name, input_data, is_primary=False, **kwargs
            )

            if result["success"]:
                # Record fallback metrics
                self.metrics_strategy.record_fallback(
                    from_model=self.primary_model_name,
                    to_model=next_fallback_name,
                    reason=str(primary_error) if primary_error else "unknown",
                )

                # Log fallback to Langfuse
                if self._langfuse_logger:
                    self._langfuse_logger.log_fallback(
                        original_model=self.primary_model_name,
                        fallback_model=next_fallback_name,
                        reason=str(primary_error) if primary_error else "unknown",
                    )

                return result["response"]

        # All models failed
        raise RuntimeError(
            f"All LLM models failed. "
            f"Primary: {self.primary_model_name}, "
            f"Fallbacks: {[name for _, name in self.fallback_llms]}"
        )

    def _try_invoke_model_with_error(
        self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
    ) -> Dict[str, Any]:
        """Try to invoke a model and return success/error info."""
        try:
            response = self._try_invoke_model(llm, model_name, input_data, is_primary, **kwargs)
            if response is None:
                return {"success": False, "response": None, "error": Exception("Model returned None")}
            return {"success": True, "response": response, "error": None}
        except Exception as e:
            return {"success": False, "response": None, "error": e}

    def _try_invoke_model(
        self, llm: Any, model_name: str, input_data: dict, is_primary: bool, **kwargs
    ) -> Optional[Any]:
        """Try to invoke a specific model, handling context length."""
        # Check context length FIRST (before invoking) using ContextStrategy
        fits, estimated_tokens, max_context = self.context_strategy.check_fits(input_data, model_name)

        if not fits:
            logger.info(
                f"Input too large for {model_name} "
                f"({estimated_tokens:,} > {max_context:,} tokens), "
                f"searching for larger-context model"
            )

            # Try to find suitable large-context model using ContextStrategy
            large_model_names = self.context_strategy.get_larger_context_models(estimated_tokens)

            if large_model_names:
                # Find matching LLM instances from fallback_llms
                large_models = [(llm, name) for llm, name in self.fallback_llms if name in large_model_names]

                # Try each large-context model
                for large_llm, large_model_name in large_models:
                    logger.info(f"Trying large-context fallback: {large_model_name}")

                    # Recursively try the large-context model
                    result = self._try_invoke_model(large_llm, large_model_name, input_data, is_primary=False, **kwargs)

                    if result is not None:
                        self.stats["context_fallbacks"] += 1

                        # Log context fallback to Langfuse
                        if self._langfuse_logger:
                            from coffee_maker.langfuse_observe.llm_config import (
                                get_model_context_length_from_name,
                            )

                            self._langfuse_logger.log_context_fallback(
                                original_model=model_name,
                                fallback_model=large_model_name,
                                estimated_tokens=estimated_tokens,
                                original_max_context=max_context,
                                fallback_max_context=get_model_context_length_from_name(large_model_name),
                            )

                        return result

            # No suitable model found - raise error
            from coffee_maker.langfuse_observe.llm_config import get_all_model_context_limits

            all_limits = get_all_model_context_limits()
            max_available = max(all_limits.values(), default=max_context)

            raise ValueError(
                f"Input is too large ({estimated_tokens:,} tokens) for any available model. "
                f"Maximum supported context: {max_available:,} tokens. "
                f"Original model: {model_name} (limit: {max_context:,} tokens). "
                f"Please reduce input size."
            )

        # Invoke the LLM (scheduling/retry handled by ScheduledLLM)
        try:
            logger.debug(f"Invoking {model_name}")
            start_time = time.time()

            response = llm.invoke(input_data, **kwargs)
            latency = time.time() - start_time

            # Extract token counts from response
            input_tokens, output_tokens = extract_token_usage(response)

            # Calculate and log cost if cost_calculator is available
            cost_info = None
            if self.cost_calculator and input_tokens > 0:
                cost_info = self.cost_calculator.calculate_cost(model_name, input_tokens, output_tokens)
                logger.info(
                    f"{model_name} cost: ${cost_info['total_cost']:.4f} "
                    f"({input_tokens} in + {output_tokens} out tokens)"
                )

                # Log to Langfuse if logger is available
                if self._langfuse_logger:
                    self._langfuse_logger.log_generation(
                        model_name=model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_info=cost_info,
                        is_primary=is_primary,
                        latency=latency,
                    )

            # Record metrics
            total_tokens = input_tokens + output_tokens
            self.metrics_strategy.record_request(
                model=model_name,
                latency=latency,
                tokens=total_tokens,
                is_primary=is_primary,
                success=True,
            )

            # Record cost if available
            if cost_info:
                self.metrics_strategy.record_cost(model=model_name, cost=cost_info["total_cost"], tokens=total_tokens)

            # Update stats
            if is_primary:
                self.stats["primary_requests"] += 1
            else:
                self.stats["fallback_requests"] += 1

            logger.info(f"Successfully invoked {model_name} in {latency:.2f}s")
            return response

        except Exception as e:
            # ScheduledLLM already handled retries, so any error means this model exhausted
            logger.error(f"Model {model_name} failed after all retries: {e}")

            # Check for quota exceeded errors (distinct from rate limits)
            is_quota, quota_type, retry_after = is_quota_exceeded_error(e)

            # Determine error type for metrics and stats
            if is_quota:
                error_type = "quota_exceeded"
                self.stats["quota_fallbacks"] = self.stats.get("quota_fallbacks", 0) + 1
                logger.warning(
                    f"Quota exceeded for {model_name} ({quota_type}). "
                    f"Will try fallback models. Retry after: {retry_after}s"
                )
            elif is_rate_limit_error(e):
                error_type = "rate_limit"
                self.stats["rate_limit_fallbacks"] += 1
            else:
                error_type = "other"

            # Record error metrics
            self.metrics_strategy.record_error(model=model_name, error_type=error_type, error_message=str(e))

            # Log quota error to Langfuse if available
            if is_quota and self._langfuse_logger:
                self._langfuse_logger.log_quota_error(
                    model=model_name, quota_type=quota_type, error_message=str(e), retry_after=retry_after
                )

            # Return None to try next fallback
            return None

    def get_stats(self) -> Dict:
        """Get usage statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            **self.stats,
            "primary_usage_percent": (
                (self.stats["primary_requests"] / self.stats["total_requests"] * 100)
                if self.stats["total_requests"] > 0
                else 0
            ),
            "fallback_usage_percent": (
                (self.stats["fallback_requests"] / self.stats["total_requests"] * 100)
                if self.stats["total_requests"] > 0
                else 0
            ),
        }

    def bind(self, **kwargs):
        """Bind arguments to the primary LLM.

        Args:
            **kwargs: Arguments to bind

        Returns:
            Self (for chaining)
        """
        # Bind to primary LLM
        if hasattr(self.primary_llm, "bind"):
            self.primary_llm = self.primary_llm.bind(**kwargs)

        # Also bind to fallback LLMs
        bound_fallbacks = []
        for fallback_llm, model_name in self.fallback_llms:
            if hasattr(fallback_llm, "bind"):
                bound_fallback = fallback_llm.bind(**kwargs)
                bound_fallbacks.append((bound_fallback, model_name))
            else:
                bound_fallbacks.append((fallback_llm, model_name))

        self.fallback_llms = bound_fallbacks
        return self

    @property
    def _llm_type(self) -> str:
        """Return type of language model."""
        return "auto_picker_llm_refactored"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate responses for a list of prompts.

        Args:
            prompts: List of prompts to generate from
            stop: Stop sequences
            run_manager: Callback manager
            **kwargs: Additional arguments

        Returns:
            LLMResult with generations
        """
        generations = []
        for prompt in prompts:
            # Use invoke for each prompt
            response = self.invoke({"input": prompt}, **kwargs)

            # Convert response to Generation
            if hasattr(response, "content"):
                text = response.content
            else:
                text = str(response)

            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)

    def _estimate_tokens(self, input_data: Any, model_name: str) -> int:
        """Estimate token count for input data.

        Args:
            input_data: Input data (string or dict)
            model_name: Model name for estimation

        Returns:
            Estimated token count
        """
        # Convert input_data to string
        if isinstance(input_data, dict):
            text = str(input_data.get("input", ""))
        else:
            text = str(input_data)

        # Rough estimation: 4 characters per token
        return max(1, len(text) // 4)

    def _check_context_length(
        self, estimated_tokens: int, model_name: str, enable_fallback: bool = True
    ) -> Tuple[bool, Optional[int]]:
        """Check if input fits within model's context length.

        Args:
            estimated_tokens: Estimated token count
            model_name: Model name to check
            enable_fallback: Whether fallback is enabled

        Returns:
            Tuple of (fits_in_context, max_context_length)
        """
        from coffee_maker.langfuse_observe.llm_config import (
            get_model_context_length_from_name,
        )

        try:
            max_context = get_model_context_length_from_name(model_name)
            fits = estimated_tokens <= max_context
            return fits, max_context
        except Exception:
            # If we can't determine context length, assume it fits
            return True, None

    def _get_large_context_models(self) -> List[Tuple[Any, str]]:
        """Get fallback models that support larger context windows.

        Returns:
            List of (llm, model_name) tuples with larger context windows
        """
        from coffee_maker.langfuse_observe.llm_config import (
            get_model_context_length_from_name,
        )

        # Get primary model's context length
        try:
            primary_context = get_model_context_length_from_name(self.primary_model_name)
        except Exception:
            primary_context = 0

        # Filter fallback models that have larger context windows
        large_models = []
        for fallback_llm, model_name in self.fallback_llms:
            try:
                fallback_context = get_model_context_length_from_name(model_name)
                if fallback_context > primary_context:
                    large_models.append((fallback_llm, model_name))
            except Exception:
                # If we can't determine context length, include it as potential fallback
                large_models.append((fallback_llm, model_name))

        return large_models


def create_auto_picker_llm_refactored(
    primary_provider: str,
    primary_model: str,
    fallback_configs: List[Tuple[str, str]],
    tier: str = "tier1",
    cost_calculator: Optional[Any] = None,
    langfuse_client: Optional[Any] = None,
    enable_context_fallback: bool = True,
    max_wait_seconds: float = 300.0,
    fallback_strategy: Optional[FallbackStrategy] = None,
) -> AutoPickerLLMRefactored:
    """Helper function to create AutoPickerLLMRefactored with scheduled LLMs.

    This is a convenience function that creates all the ScheduledLLM instances
    and wires them together with AutoPickerLLMRefactored.

    Args:
        primary_provider: Primary LLM provider (openai, gemini, anthropic)
        primary_model: Primary model name
        fallback_configs: List of (provider, model) tuples for fallbacks
        tier: API tier for rate limiting (default: tier1)
        cost_calculator: Optional CostCalculator for cost tracking
        langfuse_client: Optional Langfuse client for logging
        enable_context_fallback: Enable automatic context length fallback
        max_wait_seconds: Maximum wait time for rate limits
        fallback_strategy: Optional FallbackStrategy (default: Sequential)

    Returns:
        Configured AutoPickerLLMRefactored instance

    Example:
        >>> from coffee_maker.langfuse_observe.cost_calculator import CostCalculator
        >>> import langfuse
        >>>
        >>> cost_calc = CostCalculator()
        >>> langfuse_client = langfuse.get_client()
        >>>
        >>> auto_picker = create_auto_picker_llm_refactored(
        ...     primary_provider="openai",
        ...     primary_model="gpt-4o-mini",
        ...     fallback_configs=[
        ...         ("gemini", "gemini-2.5-flash"),
        ...         ("anthropic", "claude-3-5-haiku-20241022"),
        ...     ],
        ...     tier="tier1",
        ...     cost_calculator=cost_calc,
        ...     langfuse_client=langfuse_client,
        ... )
        >>> response = auto_picker.invoke({"input": "Hello"})
    """
    from coffee_maker.langfuse_observe.llm import get_scheduled_llm

    # Create primary scheduled LLM
    primary_llm = get_scheduled_llm(
        langfuse_client=langfuse_client,
        provider=primary_provider,
        model=primary_model,
        tier=tier,
        max_wait_seconds=max_wait_seconds,
    )
    primary_model_name = f"{primary_provider}/{primary_model}"

    # Create fallback scheduled LLMs
    fallback_llms = []
    for fb_provider, fb_model in fallback_configs:
        fb_llm = get_scheduled_llm(
            langfuse_client=langfuse_client,
            provider=fb_provider,
            model=fb_model,
            tier=tier,
            max_wait_seconds=max_wait_seconds,
        )
        fb_model_name = f"{fb_provider}/{fb_model}"
        fallback_llms.append((fb_llm, fb_model_name))

    # Create AutoPickerLLMRefactored
    return AutoPickerLLMRefactored(
        primary_llm=primary_llm,
        primary_model_name=primary_model_name,
        fallback_llms=fallback_llms,
        fallback_strategy=fallback_strategy,
        cost_calculator=cost_calculator,
        langfuse_client=langfuse_client,
        enable_context_fallback=enable_context_fallback,
    )
