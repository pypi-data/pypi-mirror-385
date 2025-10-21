"""Fallback and retry strategy for AI providers.

This module implements intelligent fallback logic when providers fail:
- Automatic retry with exponential backoff
- Fallback to alternative providers
- Cost limit checking before execution
- Comprehensive error handling

Example:
    >>> from coffee_maker.ai_providers import FallbackStrategy, get_provider
    >>> strategy = FallbackStrategy()
    >>> result = strategy.execute_with_fallback(
    ...     prompt="Implement feature X",
    ...     working_dir="/path/to/project"
    ... )
"""

import logging
import time
from typing import Dict, List, Optional

from coffee_maker.ai_providers.base import ProviderResult
from coffee_maker.ai_providers.provider_config import ProviderConfig
from coffee_maker.ai_providers.provider_factory import get_provider

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when provider rate limit is exceeded."""


class ProviderUnavailableError(Exception):
    """Raised when provider is temporarily unavailable."""


class CostLimitExceededError(Exception):
    """Raised when cost limit is exceeded."""


class AllProvidersFailedError(Exception):
    """Raised when all providers in fallback chain have failed."""


class FallbackStrategy:
    """Handles provider failures and automatic fallback.

    This class implements smart fallback logic:
    1. Try primary provider with retry
    2. If rate limited or unavailable, try next provider
    3. Check cost limits before execution
    4. Track which provider succeeded

    Attributes:
        config: ProviderConfig instance
        retry_attempts: Number of retry attempts per provider
        retry_delay: Initial retry delay in seconds
        max_retry_delay: Maximum retry delay for exponential backoff
        fallback_order: List of provider names to try in order
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        """Initialize fallback strategy.

        Args:
            config: ProviderConfig instance. If None, loads from default location.
        """
        self.config = config or ProviderConfig()

        # Load fallback configuration
        self.retry_attempts = self.config.fallback_config.retry_attempts
        self.retry_delay = self.config.fallback_config.retry_delay
        self.max_retry_delay = self.config.fallback_config.max_retry_delay
        self.fallback_order = self.config.fallback_config.fallback_order
        self.fallback_enabled = self.config.fallback_config.enabled

        logger.info(
            f"FallbackStrategy initialized: "
            f"enabled={self.fallback_enabled}, "
            f"order={self.fallback_order}, "
            f"retries={self.retry_attempts}"
        )

    def execute_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        providers: Optional[List[str]] = None,
        check_cost: bool = True,
        **kwargs,
    ) -> ProviderResult:
        """Execute prompt with automatic fallback on failure.

        Tries providers in sequence until one succeeds. Implements:
        - Retry with exponential backoff for transient errors
        - Cost checking before execution
        - Fallback to next provider on rate limits or unavailability

        Args:
            prompt: User prompt/task description
            system_prompt: Optional system prompt
            working_dir: Working directory context
            timeout: Request timeout in seconds
            providers: Custom provider order (default: use config fallback_order)
            check_cost: Whether to check cost limits (default: True)
            **kwargs: Additional parameters passed to provider

        Returns:
            ProviderResult from the first successful provider

        Raises:
            AllProvidersFailedError: If all providers in chain fail
            CostLimitExceededError: If cost limit would be exceeded

        Example:
            >>> strategy = FallbackStrategy()
            >>> result = strategy.execute_with_fallback(
            ...     prompt="Implement feature X",
            ...     working_dir="/path/to/project"
            ... )
            >>> print(result.content)
        """
        # Use custom provider list or default fallback order
        provider_list = providers or self.fallback_order

        # Filter to only enabled providers
        enabled_providers = [p for p in provider_list if self.config.is_provider_enabled(p)]

        if not enabled_providers:
            raise AllProvidersFailedError(
                "No enabled providers available. " "Enable at least one provider in config/ai_providers.yaml"
            )

        logger.info(f"Executing with fallback chain: {enabled_providers}")

        errors = []

        # Try each provider in sequence
        for provider_name in enabled_providers:
            try:
                logger.info(f"Trying provider: {provider_name}")

                # Get provider instance
                provider = get_provider(provider_name, self.config)

                # Check cost if enabled
                if check_cost:
                    estimated_cost = provider.estimate_cost(
                        prompt, system_prompt, self.config.cost_config.per_task_limit
                    )

                    if estimated_cost > self.config.cost_config.per_task_limit:
                        logger.warning(
                            f"{provider_name}: Estimated cost ${estimated_cost:.2f} "
                            f"exceeds per-task limit ${self.config.cost_config.per_task_limit:.2f}"
                        )
                        errors.append(f"{provider_name}: Cost limit exceeded")
                        continue

                # Try executing with retry
                result = self._execute_with_retry(provider, prompt, system_prompt, working_dir, timeout, **kwargs)

                if result.success:
                    logger.info(f"✅ Success with {provider_name}")
                    return result
                else:
                    logger.warning(f"{provider_name} returned error: {result.error}")
                    errors.append(f"{provider_name}: {result.error}")

            except RateLimitError:
                logger.warning(f"⚠️ {provider_name} rate limited, trying next provider...")
                errors.append(f"{provider_name}: Rate limited")

                # If this is the last provider, raise the error
                if provider_name == enabled_providers[-1]:
                    raise AllProvidersFailedError(f"All providers rate limited. Errors: {errors}")

            except ProviderUnavailableError:
                logger.warning(f"❌ {provider_name} unavailable, trying next provider...")
                errors.append(f"{provider_name}: Unavailable")

            except Exception as e:
                logger.error(f"❌ {provider_name} failed with error: {e}")
                errors.append(f"{provider_name}: {str(e)}")

        # All providers failed
        raise AllProvidersFailedError(
            f"All providers failed after {len(enabled_providers)} attempts. " f"Errors: {errors}"
        )

    def _execute_with_retry(
        self,
        provider,
        prompt: str,
        system_prompt: Optional[str],
        working_dir: Optional[str],
        timeout: Optional[int],
        **kwargs,
    ) -> ProviderResult:
        """Execute prompt with retry logic.

        Implements exponential backoff retry for transient failures.

        Args:
            provider: Provider instance
            prompt: User prompt
            system_prompt: System prompt
            working_dir: Working directory
            timeout: Timeout in seconds
            **kwargs: Additional parameters

        Returns:
            ProviderResult

        Raises:
            RateLimitError: On rate limit (no retry, fallback immediately)
            ProviderUnavailableError: On service unavailable
            Exception: On other errors after retries exhausted
        """
        last_error = None
        delay = self.retry_delay

        for attempt in range(self.retry_attempts):
            try:
                result = provider.execute_prompt(
                    prompt=prompt, system_prompt=system_prompt, working_dir=working_dir, timeout=timeout, **kwargs
                )

                # If we got a result, return it (even if it has an error)
                return result

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check for rate limit errors (don't retry, fallback immediately)
                if "rate" in error_str or "quota" in error_str or "429" in error_str:
                    logger.warning(f"Rate limit detected on attempt {attempt + 1}")
                    raise RateLimitError(str(e))

                # Check for unavailability (retry with backoff)
                if "unavailable" in error_str or "timeout" in error_str or "503" in error_str:
                    if attempt < self.retry_attempts - 1:
                        logger.warning(f"Provider unavailable on attempt {attempt + 1}, " f"retrying in {delay}s...")
                        time.sleep(delay)
                        delay = min(delay * 2, self.max_retry_delay)
                        continue
                    else:
                        raise ProviderUnavailableError(str(e))

                # Other errors - retry with backoff
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Request failed on attempt {attempt + 1}: {e}, " f"retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * 2, self.max_retry_delay)
                else:
                    logger.error(f"Request failed after {self.retry_attempts} attempts")
                    raise

        # Should never reach here, but just in case
        raise last_error if last_error else Exception("Unknown error")

    def get_provider_costs(self) -> Dict[str, float]:
        """Get estimated costs per provider.

        This is a placeholder for future cost tracking functionality.
        In a full implementation, this would read from a cost tracking
        database to return actual usage costs.

        Returns:
            Dictionary mapping provider names to total costs (USD)

        Example:
            >>> strategy = FallbackStrategy()
            >>> costs = strategy.get_provider_costs()
            >>> print(costs)  # {'claude': 23.50, 'openai': 8.20, 'gemini': 1.80}
        """
        # TODO: Implement cost tracking
        # This would read from data/cost_tracking.json
        # For now, return empty dict
        return {}

    def get_provider_stats(self) -> Dict[str, Dict[str, int]]:
        """Get usage statistics per provider.

        This is a placeholder for future statistics tracking.
        In a full implementation, this would track:
        - Total requests
        - Successful requests
        - Failed requests
        - Total tokens used

        Returns:
            Dictionary mapping provider names to stats

        Example:
            >>> strategy = FallbackStrategy()
            >>> stats = strategy.get_provider_stats()
            >>> print(stats['claude'])
            {'requests': 45, 'success': 43, 'failures': 2, 'tokens': 125000}
        """
        # TODO: Implement usage statistics tracking
        # For now, return empty dict
        return {}
