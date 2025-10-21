"""OpenAI provider implementation.

This module provides OpenAI GPT-4/GPT-4 Turbo/o1/o3 support for the AI provider abstraction layer.

Example:
    >>> from coffee_maker.ai_providers.providers.openai_provider import OpenAIProvider
    >>> config = {
    ...     'model': 'gpt-4-turbo',
    ...     'max_tokens': 8000,
    ...     'api_key_env': 'OPENAI_API_KEY'
    ... }
    >>> provider = OpenAIProvider(config)
    >>> result = provider.execute_prompt("Implement feature X")
"""

import logging
import os
from typing import List, Optional

import tiktoken
from openai import OpenAI

from coffee_maker.ai_providers.base import (
    BaseAIProvider,
    ProviderCapability,
    ProviderResult,
)
from coffee_maker.config.manager import ConfigManager

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 provider implementation.

    Supports GPT-4, GPT-4 Turbo, and o1/o3 models via OpenAI API.

    Attributes:
        client: OpenAI API client
        encoding: Tiktoken encoding for token counting
        fallback_models: List of fallback models if primary fails
    """

    def __init__(self, config: dict):
        """Initialize OpenAI provider.

        Args:
            config: Provider configuration with keys:
                   - model: Model identifier (e.g., 'gpt-4-turbo')
                   - fallback_models: List of fallback models
                   - max_tokens: Max output tokens
                   - temperature: Sampling temperature
                   - api_key_env: Environment variable for API key
                   - cost_per_1m_input_tokens: Cost per 1M input tokens (USD)
                   - cost_per_1m_output_tokens: Cost per 1M output tokens (USD)
        """
        super().__init__(config)

        # Initialize OpenAI client using ConfigManager
        api_key = ConfigManager.get_openai_api_key(required=True)
        self.client = OpenAI(api_key=api_key)

        # Fallback models
        self.fallback_models = config.get("fallback_models", [])

        # Cost rates (USD per 1M tokens)
        self.cost_per_1m_input = config.get("cost_per_1m_input_tokens", 10.0)
        self.cost_per_1m_output = config.get("cost_per_1m_output_tokens", 30.0)

        # Initialize tiktoken encoding for token counting
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")

        logger.info(f"OpenAIProvider initialized: model={self.model}")

    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ProviderResult:
        """Execute a prompt using OpenAI.

        Args:
            prompt: User prompt/task description
            system_prompt: Optional system prompt
            working_dir: Working directory context
            timeout: Request timeout (None = use default)
            **kwargs: Additional parameters

        Returns:
            ProviderResult with response content and metadata
        """
        # Add working directory context
        if working_dir:
            prompt = f"Working directory: {working_dir}\n\n{prompt}"

        # Default system prompt for autonomous development
        if system_prompt is None:
            system_prompt = self._build_default_system_prompt(working_dir)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

        logger.debug(f"Executing OpenAI request: {prompt[:100]}...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=timeout or 600,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage

            logger.debug(f"OpenAI request completed: {usage.prompt_tokens} in, {usage.completion_tokens} out")

            return ProviderResult(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                },
                stop_reason=response.choices[0].finish_reason,
                metadata={"provider": "openai", "system_fingerprint": response.system_fingerprint},
            )

        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            return ProviderResult(
                content="",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                error=str(e),
                metadata={"provider": "openai"},
            )

    def check_available(self) -> bool:
        """Check if OpenAI is available.

        Returns:
            True if API key is set and OpenAI is accessible
        """
        if not ConfigManager.has_openai_api_key():
            logger.warning("OPENAI_API_KEY not set")
            return False

        # Try a simple API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=5,
            )
            logger.info(f"OpenAI API available: {response.model}")
            return True
        except Exception as e:
            logger.error(f"OpenAI API not available: {e}")
            return False

    def estimate_cost(
        self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for OpenAI request.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_output_tokens: Expected output tokens

        Returns:
            Estimated cost in USD
        """
        # Count input tokens
        input_text = prompt
        if system_prompt:
            input_text += " " + system_prompt

        input_tokens = self.count_tokens(input_text)

        # Estimate output tokens
        output_tokens = max_output_tokens or (self.max_tokens // 2)

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * self.cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * self.cost_per_1m_output

        return input_cost + output_cost

    @property
    def name(self) -> str:
        """Provider name."""
        return "openai"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        """Supported capabilities."""
        return [
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.VISION,
            ProviderCapability.STREAMING,
            ProviderCapability.SYSTEM_PROMPTS,
        ]

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed, using approximation: {e}")
            # Fallback: rough approximation (1 token ≈ 0.75 words)
            words = len(text.split())
            return int(words / 0.75)

    def _build_default_system_prompt(self, working_dir: Optional[str] = None) -> str:
        """Build default system prompt for autonomous development.

        Args:
            working_dir: Working directory path

        Returns:
            System prompt string
        """
        working_dir = working_dir or os.getcwd()

        prompt = f"""You are an expert autonomous development assistant working in: {working_dir}

Your role:
- Read and implement tasks from the project ROADMAP
- Create, edit, and organize files
- Follow coding standards and best practices
- Write clear commit messages
- Update ROADMAP status as you work

Guidelines:
- Be concrete and specific, not abstract
- Create real, working code with actual examples
- Test your work before committing
- Update documentation as you go
- Use meaningful file and variable names
- Follow the project's existing patterns

File Operations:
- You can read files to understand context
- You should create new files for new features
- You should modify existing files to fix bugs or add features
- Always preserve existing functionality unless explicitly changing it

Communication:
- Explain your approach before implementing
- Report what you've done when complete
- Ask questions if requirements are unclear
- Be proactive about potential issues
"""
        return prompt
