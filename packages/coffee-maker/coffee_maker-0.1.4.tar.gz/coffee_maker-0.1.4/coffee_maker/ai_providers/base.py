"""Base classes and interfaces for AI provider abstraction.

This module defines the abstract base class that all AI providers must implement,
ensuring a consistent interface across different AI backends (Claude, OpenAI, Gemini, etc.).

Example:
    >>> from coffee_maker.ai_providers import get_provider
    >>> provider = get_provider()  # Gets default from config
    >>> result = provider.execute_prompt("Implement feature X")
    >>> print(result.content)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderCapability(Enum):
    """Provider capabilities.

    Used to advertise what features a provider supports, allowing
    the daemon to choose providers based on required capabilities.
    """

    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    STREAMING = "streaming"
    SYSTEM_PROMPTS = "system_prompts"
    CONTEXT_CACHING = "context_caching"


@dataclass
class ProviderResult:
    """Standardized result from any provider.

    This matches the existing APIResult format for backward compatibility
    with the daemon's current implementation.

    Attributes:
        content: Response text from the AI model
        model: Model identifier used for the request
        usage: Token usage dict with keys: input_tokens, output_tokens
        stop_reason: Why the model stopped (e.g., "end_turn", "max_tokens")
        error: Error message if request failed, None if successful
        metadata: Provider-specific metadata (e.g., safety ratings, tool calls)
    """

    content: str
    model: str
    usage: Dict[str, int]  # {"input_tokens": X, "output_tokens": Y}
    stop_reason: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if request succeeded."""
        return self.error is None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers.

    All provider implementations must inherit from this class and implement
    all abstract methods. This ensures consistent interface across providers
    (Claude, OpenAI, Gemini, etc.) allowing the daemon to swap providers
    without code changes.

    Attributes:
        config: Provider-specific configuration from ai_providers.yaml
        model: Model identifier (e.g., "claude-sonnet-4", "gpt-4-turbo")
        max_tokens: Maximum output tokens
        temperature: Sampling temperature (0.0-1.0)

    Example:
        >>> class MyProvider(BaseAIProvider):
        ...     def execute_prompt(self, prompt, **kwargs):
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration.

        Args:
            config: Provider configuration from ai_providers.yaml
                   Should include: model, max_tokens, temperature, api_key_env, etc.
        """
        self.config = config
        self.model = config.get("model")
        self.max_tokens = config.get("max_tokens", 8000)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ProviderResult:
        """Execute a prompt and return result.

        This is the core method that all providers must implement.
        It should handle API calls, error handling, and return a standardized result.

        Args:
            prompt: User prompt/task description
            system_prompt: Optional system prompt for context
            working_dir: Working directory context (for file operations)
            timeout: Request timeout in seconds
            **kwargs: Provider-specific parameters

        Returns:
            ProviderResult with content, usage, and metadata

        Raises:
            Exception: Provider-specific errors (rate limits, API errors, etc.)
        """

    @abstractmethod
    def check_available(self) -> bool:
        """Check if provider is available and configured.

        This should verify:
        - API key is set
        - Provider endpoint is reachable
        - Configuration is valid

        Returns:
            True if provider can be used, False otherwise
        """

    @abstractmethod
    def estimate_cost(
        self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for a request in USD.

        Used for budget tracking and cost optimization.
        Estimate should be based on current provider pricing.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_output_tokens: Expected output tokens (use provider default if None)

        Returns:
            Estimated cost in USD
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'claude', 'openai', 'gemini').

        Returns:
            Provider identifier (lowercase, alphanumeric)
        """

    @property
    @abstractmethod
    def capabilities(self) -> List[ProviderCapability]:
        """List of supported capabilities.

        Returns:
            List of ProviderCapability enums this provider supports
        """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text for this provider's tokenizer.

        Used for cost estimation and context window management.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """

    def __repr__(self) -> str:
        """String representation of provider."""
        return f"<{self.__class__.__name__}(model={self.model})>"
