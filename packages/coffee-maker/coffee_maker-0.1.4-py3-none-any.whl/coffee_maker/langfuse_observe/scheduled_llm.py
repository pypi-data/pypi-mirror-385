"""ScheduledLLM: Wrapper that adds proactive rate limiting to any LLM.

This module provides a lightweight wrapper around LangChain LLMs to add
intelligent scheduling without the overhead of fallback logic.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseLLM, BaseChatModel
from langchain_core.outputs import LLMResult
from pydantic import ConfigDict

from coffee_maker.langfuse_observe.strategies.scheduling import SchedulingStrategy

logger = logging.getLogger(__name__)


class ScheduledLLM(BaseLLM):
    """Wrapper that adds proactive scheduling to any LLM.

    This wrapper intercepts LLM calls and ensures they respect rate limits
    using the ProactiveRateLimitScheduler strategy:
    - Stays at N-2 of rate limits (safety margin)
    - Enforces 60/RPM spacing between requests
    - Waits intelligently based on actual usage

    Example:
        >>> base_llm = ChatOpenAI(model="gpt-4o-mini")
        >>> scheduled_llm = ScheduledLLM(
        ...     llm=base_llm,
        ...     model_name="openai/gpt-4o-mini",
        ...     scheduling_strategy=scheduler
        ... )
        >>> response = scheduled_llm.invoke("Hello")  # Automatically scheduled
    """

    # Pydantic model fields
    llm: Any  # The wrapped LLM instance
    model_name: str  # Full model name (e.g., "openai/gpt-4o-mini")
    scheduling_strategy: SchedulingStrategy  # Proactive scheduler
    max_wait_seconds: float = 300.0  # Max wait before giving up
    stats: Dict[str, int] = {}  # Usage statistics

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        llm: Any,
        model_name: str,
        scheduling_strategy: SchedulingStrategy,
        max_wait_seconds: float = 300.0,
        **kwargs,
    ):
        """Initialize ScheduledLLM wrapper.

        Args:
            llm: Base LLM instance to wrap
            model_name: Full model name (e.g., "openai/gpt-4o-mini")
            scheduling_strategy: Scheduling strategy for rate limiting
            max_wait_seconds: Maximum seconds to wait (default: 300s = 5min)
            **kwargs: Additional arguments
        """
        # Initialize statistics
        stats = {
            "total_requests": 0,
            "scheduled_waits": 0,
            "wait_timeouts": 0,
        }

        # Call parent init
        super().__init__(
            llm=llm,
            model_name=model_name,
            scheduling_strategy=scheduling_strategy,
            max_wait_seconds=max_wait_seconds,
            stats=stats,
            **kwargs,
        )

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return f"scheduled_{self.llm._llm_type}"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate responses with proactive scheduling.

        Args:
            prompts: List of prompts
            stop: Stop sequences
            run_manager: Callback manager
            **kwargs: Additional arguments

        Returns:
            LLM result

        Raises:
            RuntimeError: If scheduling wait exceeds max_wait_seconds
        """
        # Estimate tokens for scheduling decision
        estimated_tokens = self._estimate_tokens(prompts)

        # Use scheduling strategy to wait until safe to proceed
        can_proceed, wait_time = self.scheduling_strategy.can_proceed(self.model_name, estimated_tokens)

        if not can_proceed:
            if wait_time > self.max_wait_seconds:
                # Wait would exceed max, reject request
                self.stats["wait_timeouts"] += 1
                raise RuntimeError(
                    f"Scheduling strategy requires {wait_time:.1f}s wait for {self.model_name}, "
                    f"exceeds max {self.max_wait_seconds}s. Rate limit capacity exhausted."
                )

            # Wait as instructed by scheduling strategy
            logger.info(f"Proactive scheduling: waiting {wait_time:.1f}s for {self.model_name}")
            time.sleep(wait_time)
            self.stats["scheduled_waits"] += 1

        # Now safe to make the request
        self.stats["total_requests"] += 1

        # Invoke the wrapped LLM with error handling
        while True:
            try:
                result = self.llm._generate(prompts, stop=stop, run_manager=run_manager, **kwargs)

                # Success! Record the request for rate tracking
                actual_tokens = self._extract_token_usage(result, estimated_tokens)
                self.scheduling_strategy.record_request(self.model_name, actual_tokens)

                return result

            except Exception as e:
                # Check if this is a rate limit error
                if self._is_rate_limit_error(e):
                    # Record the error
                    self.scheduling_strategy.record_error(self.model_name, e)

                    # Ask strategy if we should retry
                    should_retry, wait_time = self.scheduling_strategy.should_retry_after_error(self.model_name)

                    if not should_retry:
                        # Strategy says give up, raise for fallback
                        logger.error(f"Scheduling strategy exhausted for {self.model_name}, raising error for fallback")
                        raise

                    # Wait and retry
                    if wait_time > 0:
                        logger.info(f"Waiting {wait_time:.1f}s before retry for {self.model_name}")
                        time.sleep(wait_time)
                        self.stats["scheduled_waits"] += 1

                    # Loop will retry
                    continue
                else:
                    # Not a rate limit error, raise immediately
                    raise

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error.

        Args:
            error: The exception to check

        Returns:
            True if it's a rate limit error
        """
        error_msg = str(error).lower()
        rate_limit_keywords = [
            "rate limit",
            "ratelimit",
            "429",
            "quota",
            "too many requests",
            "resource_exhausted",
        ]
        return any(keyword in error_msg for keyword in rate_limit_keywords)

    def _estimate_tokens(self, prompts: List[str]) -> int:
        """Estimate total tokens for all prompts.

        Args:
            prompts: List of prompt strings

        Returns:
            Estimated token count
        """
        # Rough estimation: 4 characters per token
        total_chars = sum(len(prompt) for prompt in prompts)
        return total_chars // 4

    def _extract_token_usage(self, result: LLMResult, estimated_tokens: int) -> int:
        """Extract actual token usage from LLM result.

        Args:
            result: LLM result
            estimated_tokens: Fallback if actual usage not available

        Returns:
            Actual or estimated token count
        """
        # Try to extract actual usage from result metadata
        if hasattr(result, "llm_output") and result.llm_output:
            usage = result.llm_output.get("token_usage", {})
            total = usage.get("total_tokens", 0)
            if total > 0:
                return total

        # Fallback to estimate
        return estimated_tokens

    def invoke(self, input_data: Any, **kwargs) -> Any:
        """Invoke with scheduling (for chat models).

        Args:
            input_data: Input for the LLM
            **kwargs: Additional arguments

        Returns:
            LLM response
        """
        # For chat models, delegate to their invoke method
        if hasattr(self.llm, "invoke"):
            # Estimate tokens
            if isinstance(input_data, dict):
                text = str(input_data.get("input", input_data))
            else:
                text = str(input_data)

            estimated_tokens = len(text) // 4

            # Schedule the request
            can_proceed, wait_time = self.scheduling_strategy.can_proceed(self.model_name, estimated_tokens)

            if not can_proceed:
                if wait_time > self.max_wait_seconds:
                    self.stats["wait_timeouts"] += 1
                    raise RuntimeError(
                        f"Scheduling strategy requires {wait_time:.1f}s wait for {self.model_name}, "
                        f"exceeds max {self.max_wait_seconds}s. Rate limit capacity exhausted."
                    )

                logger.info(f"Proactive scheduling: waiting {wait_time:.1f}s for {self.model_name}")
                time.sleep(wait_time)
                self.stats["scheduled_waits"] += 1

            # Make the request with error handling
            self.stats["total_requests"] += 1

            while True:
                try:
                    response = self.llm.invoke(input_data, **kwargs)

                    # Success! Extract and record usage
                    actual_tokens = estimated_tokens
                    if hasattr(response, "response_metadata"):
                        usage = response.response_metadata.get("usage", {})
                        total = usage.get("total_tokens", 0)
                        if total > 0:
                            actual_tokens = total
                    elif hasattr(response, "usage_metadata"):
                        input_tokens = getattr(response.usage_metadata, "input_tokens", 0)
                        output_tokens = getattr(response.usage_metadata, "output_tokens", 0)
                        if input_tokens + output_tokens > 0:
                            actual_tokens = input_tokens + output_tokens

                    self.scheduling_strategy.record_request(self.model_name, actual_tokens)

                    return response

                except Exception as e:
                    # Check if this is a rate limit error
                    if self._is_rate_limit_error(e):
                        # Record the error
                        self.scheduling_strategy.record_error(self.model_name, e)

                        # Ask strategy if we should retry
                        should_retry, wait_time = self.scheduling_strategy.should_retry_after_error(self.model_name)

                        if not should_retry:
                            # Strategy says give up, raise for fallback
                            logger.error(
                                f"Scheduling strategy exhausted for {self.model_name}, raising error for fallback"
                            )
                            raise

                        # Wait and retry
                        if wait_time > 0:
                            logger.info(f"Waiting {wait_time:.1f}s before retry for {self.model_name}")
                            time.sleep(wait_time)
                            self.stats["scheduled_waits"] += 1

                        # Loop will retry
                        continue
                    else:
                        # Not a rate limit error, raise immediately
                        raise
        else:
            # Fallback to _generate for non-chat models
            prompts = [str(input_data)]
            result = self._generate(prompts, **kwargs)
            return result.generations[0][0].text if result.generations else ""

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "scheduling_status": self.scheduling_strategy.get_status(self.model_name),
        }


class ScheduledChatModel(BaseChatModel):
    """Scheduled wrapper specifically for chat models.

    This is a specialized version of ScheduledLLM for ChatModels,
    maintaining full compatibility with LangChain's chat interface.
    """

    # Pydantic model fields
    llm: Any
    model_name: str
    scheduling_strategy: SchedulingStrategy
    max_wait_seconds: float = 300.0
    stats: Dict[str, int] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        llm: Any,
        model_name: str,
        scheduling_strategy: SchedulingStrategy,
        max_wait_seconds: float = 300.0,
        **kwargs,
    ):
        """Initialize ScheduledChatModel wrapper."""
        stats = {
            "total_requests": 0,
            "scheduled_waits": 0,
            "wait_timeouts": 0,
        }

        super().__init__(
            llm=llm,
            model_name=model_name,
            scheduling_strategy=scheduling_strategy,
            max_wait_seconds=max_wait_seconds,
            stats=stats,
            **kwargs,
        )

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return f"scheduled_{self.llm._llm_type}"

    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """Generate chat response with scheduling."""
        # Estimate tokens from messages
        estimated_tokens = sum(len(str(msg.content)) // 4 for msg in messages)

        # Schedule
        can_proceed, wait_time = self.scheduling_strategy.can_proceed(self.model_name, estimated_tokens)

        if not can_proceed:
            if wait_time > self.max_wait_seconds:
                self.stats["wait_timeouts"] += 1
                raise RuntimeError(
                    f"Scheduling strategy requires {wait_time:.1f}s wait, " f"exceeds max {self.max_wait_seconds}s"
                )

            logger.info(f"Proactive scheduling: waiting {wait_time:.1f}s for {self.model_name}")
            time.sleep(wait_time)
            self.stats["scheduled_waits"] += 1

        # Make request with error handling
        self.stats["total_requests"] += 1

        while True:
            try:
                result = self.llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

                # Success! Record usage
                actual_tokens = estimated_tokens
                if hasattr(result, "llm_output") and result.llm_output:
                    usage = result.llm_output.get("usage", {})
                    total = usage.get("total_tokens", 0)
                    if total > 0:
                        actual_tokens = total

                self.scheduling_strategy.record_request(self.model_name, actual_tokens)

                return result

            except Exception as e:
                # Check if this is a rate limit error
                if self._is_rate_limit_error(e):
                    # Record the error
                    self.scheduling_strategy.record_error(self.model_name, e)

                    # Ask strategy if we should retry
                    should_retry, wait_time = self.scheduling_strategy.should_retry_after_error(self.model_name)

                    if not should_retry:
                        # Strategy says give up, raise for fallback
                        logger.error(f"Scheduling strategy exhausted for {self.model_name}, raising error for fallback")
                        raise

                    # Wait and retry
                    if wait_time > 0:
                        logger.info(f"Waiting {wait_time:.1f}s before retry for {self.model_name}")
                        time.sleep(wait_time)
                        self.stats["scheduled_waits"] += 1

                    # Loop will retry
                    continue
                else:
                    # Not a rate limit error, raise immediately
                    raise

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error.

        Args:
            error: The exception to check

        Returns:
            True if it's a rate limit error
        """
        error_msg = str(error).lower()
        rate_limit_keywords = [
            "rate limit",
            "ratelimit",
            "429",
            "quota",
            "too many requests",
            "resource_exhausted",
        ]
        return any(keyword in error_msg for keyword in rate_limit_keywords)
