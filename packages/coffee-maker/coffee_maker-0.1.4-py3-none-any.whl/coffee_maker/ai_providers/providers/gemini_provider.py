"""Google Gemini provider implementation.

This module provides Google Gemini support for the AI provider abstraction layer.
Supports Gemini 1.5 Pro and other Gemini models via Google's Generative AI API.

Example:
    >>> from coffee_maker.ai_providers.providers.gemini_provider import GeminiProvider
    >>> config = {
    ...     'model': 'gemini-1.5-pro',
    ...     'max_tokens': 8000,
    ...     'temperature': 0.7,
    ...     'api_key_env': 'GOOGLE_API_KEY'
    ... }
    >>> provider = GeminiProvider(config)
    >>> result = provider.execute_prompt("Implement feature X")
"""

import logging
import os
from typing import List, Optional

import google.generativeai as genai

from coffee_maker.ai_providers.base import (
    BaseAIProvider,
    ProviderCapability,
    ProviderResult,
)
from coffee_maker.config.manager import ConfigManager

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider implementation.

    Supports Gemini 1.5 Pro and other Gemini models via Google's Generative AI API.
    Offers cost-effective pricing with large context windows (up to 1M tokens).

    Attributes:
        model: GenerativeModel instance
        generation_config: Configuration for generation parameters
    """

    def __init__(self, config: dict):
        """Initialize Gemini provider.

        Args:
            config: Provider configuration with keys:
                   - model: Model identifier (e.g., 'gemini-1.5-pro')
                   - max_tokens: Max output tokens
                   - temperature: Sampling temperature
                   - api_key_env: Environment variable for API key
                   - cost_per_1m_input_tokens: Cost per 1M input tokens (USD)
                   - cost_per_1m_output_tokens: Cost per 1M output tokens (USD)
        """
        super().__init__(config)

        # Configure API key using ConfigManager
        api_key = ConfigManager.get_gemini_api_key(required=True)
        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel(self.config["model"])

        # Generation configuration
        self.generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }

        # Cost rates (USD per 1M tokens)
        self.cost_per_1m_input = config.get("cost_per_1m_input_tokens", 7.0)
        self.cost_per_1m_output = config.get("cost_per_1m_output_tokens", 21.0)

        logger.info(f"GeminiProvider initialized: model={self.config['model']}")

    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ProviderResult:
        """Execute a prompt using Gemini.

        Args:
            prompt: User prompt/task description
            system_prompt: Optional system prompt (combined with user prompt for Gemini)
            working_dir: Working directory context
            timeout: Request timeout (not used by Gemini API)
            **kwargs: Additional parameters

        Returns:
            ProviderResult with response content and metadata
        """
        # Add working directory context
        if working_dir:
            prompt = f"Working directory: {working_dir}\n\n{prompt}"

        # Gemini doesn't have a separate system prompt, so prepend it to user prompt
        if system_prompt is None:
            system_prompt = self._build_default_system_prompt(working_dir)

        full_prompt = f"{system_prompt}\n\nTask:\n{prompt}"

        logger.debug(f"Executing Gemini request: {prompt[:100]}...")

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
            )

            # Extract content
            content = response.text if response.text else ""

            # Gemini doesn't provide detailed token usage in the response
            # We'll estimate based on the prompt and response
            input_tokens = self.count_tokens(full_prompt)
            output_tokens = self.count_tokens(content)

            logger.debug(f"Gemini request completed: ~{input_tokens} in, ~{output_tokens} out")

            return ProviderResult(
                content=content,
                model=self.config["model"],
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                stop_reason=self._get_stop_reason(response),
                metadata={"provider": "gemini", "safety_ratings": self._extract_safety_ratings(response)},
            )

        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return ProviderResult(
                content="",
                model=self.config["model"],
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                error=str(e),
                metadata={"provider": "gemini"},
            )

    def check_available(self) -> bool:
        """Check if Gemini is available.

        Returns:
            True if API key is set and Gemini is accessible
        """
        if not ConfigManager.has_gemini_api_key():
            logger.warning("GOOGLE_API_KEY not set")
            return False

        # Try a simple API call
        try:
            response = self.model.generate_content("Hello", generation_config={"max_output_tokens": 10})
            logger.info(f"Gemini API available: {self.config['model']}")
            return True
        except Exception as e:
            logger.error(f"Gemini API not available: {e}")
            return False

    def estimate_cost(
        self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for Gemini request.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_output_tokens: Expected output tokens

        Returns:
            Estimated cost in USD
        """
        # Combine prompts for token counting
        input_text = prompt
        if system_prompt:
            input_text = f"{system_prompt}\n\n{prompt}"

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
        return "gemini"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        """Supported capabilities."""
        return [
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.VISION,
            ProviderCapability.STREAMING,
            # Note: Gemini doesn't have separate system prompts,
            # but we can simulate them by prepending to user prompt
        ]

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Gemini API provides a count_tokens method, but we'll use a simple
        approximation for reliability (1 token ≈ 0.75 words).

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        try:
            # Try using Gemini's token counting
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            logger.warning(f"Token counting failed, using approximation: {e}")
            # Fallback: rough approximation (1 token ≈ 0.75 words)
            words = len(text.split())
            return int(words / 0.75)

    def _get_stop_reason(self, response) -> str:
        """Extract stop reason from Gemini response.

        Args:
            response: Gemini response object

        Returns:
            Stop reason string
        """
        try:
            # Check if response has candidates
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason"):
                    return str(candidate.finish_reason)
            return "end_turn"
        except Exception:
            return "end_turn"

    def _extract_safety_ratings(self, response) -> dict:
        """Extract safety ratings from Gemini response.

        Args:
            response: Gemini response object

        Returns:
            Dictionary of safety ratings
        """
        try:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "safety_ratings"):
                    return {rating.category: rating.probability for rating in candidate.safety_ratings}
        except Exception:
            pass
        return {}

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
