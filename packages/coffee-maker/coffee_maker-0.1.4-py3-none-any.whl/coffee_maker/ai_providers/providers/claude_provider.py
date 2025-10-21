"""Claude provider implementation.

This module provides Claude (Anthropic) support for the AI provider abstraction layer.
Supports both API mode (direct Anthropic API calls) and CLI mode (Claude CLI wrapper).

Example:
    >>> from coffee_maker.ai_providers.providers.claude_provider import ClaudeProvider
    >>> config = {
    ...     'model': 'claude-sonnet-4-5-20250929',
    ...     'use_cli': True,
    ...     'max_tokens': 8000
    ... }
    >>> provider = ClaudeProvider(config)
    >>> result = provider.execute_prompt("Implement feature X")
"""

import logging
import os
from typing import List, Optional

from anthropic import Anthropic

from coffee_maker.ai_providers.base import (
    BaseAIProvider,
    ProviderCapability,
    ProviderResult,
)
from coffee_maker.config.manager import ConfigManager

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Claude (Anthropic) provider implementation.

    Supports two modes:
    1. API mode: Direct Anthropic API calls (reliable, token tracking)
    2. CLI mode: Claude CLI wrapper (better for autonomous development with tool use)

    Attributes:
        use_cli: Whether to use Claude CLI instead of API
        client: Anthropic API client (None if using CLI)
        timeout: Request timeout in seconds
    """

    def __init__(self, config: dict):
        """Initialize Claude provider.

        Args:
            config: Provider configuration with keys:
                   - model: Model identifier
                   - use_cli: Use CLI mode (default: True)
                   - max_tokens: Max output tokens
                   - temperature: Sampling temperature
                   - api_key_env: Environment variable for API key
                   - cost_per_1m_input_tokens: Cost per 1M input tokens (USD)
                   - cost_per_1m_output_tokens: Cost per 1M output tokens (USD)
        """
        super().__init__(config)

        self.use_cli = config.get("use_cli", True)
        self.timeout = config.get("timeout", 3600)

        # Cost rates (USD per 1M tokens)
        self.cost_per_1m_input = config.get("cost_per_1m_input_tokens", 15.0)
        self.cost_per_1m_output = config.get("cost_per_1m_output_tokens", 75.0)

        if not self.use_cli:
            # Initialize API client using ConfigManager
            api_key = ConfigManager.get_anthropic_api_key(required=True)
            self.client = Anthropic(api_key=api_key)
        else:
            # CLI mode - import ClaudeCLIInterface
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            self.cli_interface = ClaudeCLIInterface(model=self.model)
            self.client = None

        logger.info(f"ClaudeProvider initialized: model={self.model}, mode={'CLI' if self.use_cli else 'API'}")

    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ProviderResult:
        """Execute a prompt using Claude.

        Args:
            prompt: User prompt/task description
            system_prompt: Optional system prompt
            working_dir: Working directory context
            timeout: Request timeout (None = use default)
            **kwargs: Additional parameters

        Returns:
            ProviderResult with response content and metadata
        """
        timeout = timeout or self.timeout

        if self.use_cli:
            return self._execute_cli(prompt, system_prompt, working_dir, timeout)
        else:
            return self._execute_api(prompt, system_prompt, working_dir, timeout)

    def _execute_api(
        self, prompt: str, system_prompt: Optional[str], working_dir: Optional[str], timeout: int
    ) -> ProviderResult:
        """Execute via Anthropic API.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            working_dir: Working directory
            timeout: Timeout in seconds

        Returns:
            ProviderResult
        """
        # Add working directory context
        if working_dir:
            prompt = f"Working directory: {working_dir}\n\n{prompt}"

        # Default system prompt for autonomous development
        if system_prompt is None:
            system_prompt = self._build_default_system_prompt(working_dir)

        logger.debug(f"Executing Claude API request: {prompt[:100]}...")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                timeout=timeout,
            )

            content = self._extract_content(message)
            logger.debug(f"API request completed: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

            return ProviderResult(
                content=content,
                model=message.model,
                usage={
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
                stop_reason=message.stop_reason,
                metadata={"mode": "api"},
            )

        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            return ProviderResult(
                content="",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                error=str(e),
                metadata={"mode": "api"},
            )

    def _execute_cli(
        self, prompt: str, system_prompt: Optional[str], working_dir: Optional[str], timeout: int
    ) -> ProviderResult:
        """Execute via Claude CLI.

        Args:
            prompt: User prompt
            system_prompt: System prompt (not used in CLI mode)
            working_dir: Working directory
            timeout: Timeout in seconds

        Returns:
            ProviderResult
        """
        logger.debug(f"Executing Claude CLI request: {prompt[:100]}...")

        try:
            # Use ClaudeCLIInterface for CLI execution
            result = self.cli_interface.execute_with_context(prompt=prompt, working_dir=working_dir or os.getcwd())

            # Convert ClaudeCLIInterface result to ProviderResult
            if result.success:
                return ProviderResult(
                    content=result.content,
                    model=self.model,
                    usage={"input_tokens": 0, "output_tokens": 0},  # CLI doesn't track tokens
                    stop_reason="end_turn",
                    metadata={"mode": "cli"},
                )
            else:
                return ProviderResult(
                    content="",
                    model=self.model,
                    usage={"input_tokens": 0, "output_tokens": 0},
                    stop_reason="error",
                    error=result.error,
                    metadata={"mode": "cli"},
                )

        except Exception as e:
            logger.error(f"Claude CLI request failed: {e}")
            return ProviderResult(
                content="",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                error=str(e),
                metadata={"mode": "cli"},
            )

    def check_available(self) -> bool:
        """Check if Claude is available.

        Returns:
            True if API key is set and Claude is accessible
        """
        if self.use_cli:
            # Check if claude CLI is in PATH
            import shutil

            return shutil.which("claude") is not None
        else:
            # Check if API key is set using ConfigManager
            if not ConfigManager.has_anthropic_api_key():
                logger.warning("ANTHROPIC_API_KEY not set")
                return False

            # Try a simple API call
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}],
                    timeout=5,
                )
                logger.info(f"Claude API available: {message.model}")
                return True
            except Exception as e:
                logger.error(f"Claude API not available: {e}")
                return False

    def estimate_cost(
        self, prompt: str, system_prompt: Optional[str] = None, max_output_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for Claude request.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_output_tokens: Expected output tokens

        Returns:
            Estimated cost in USD
        """
        # Estimate input tokens (rough approximation: 1 token ≈ 0.75 words)
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
        return "claude"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        """Supported capabilities."""
        return [
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.VISION,
            ProviderCapability.STREAMING,
            ProviderCapability.SYSTEM_PROMPTS,
            ProviderCapability.CONTEXT_CACHING,
        ]

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Uses Anthropic's token counting if available, otherwise
        uses rough approximation (1 token ≈ 0.75 words).

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not self.use_cli and self.client:
            try:
                # Use Anthropic's token counting
                from anthropic import count_tokens

                return count_tokens(text)
            except (ImportError, Exception):
                pass

        # Fallback: rough approximation
        words = len(text.split())
        return int(words / 0.75)

    def _extract_content(self, message) -> str:
        """Extract text content from API response.

        Args:
            message: Anthropic API message response

        Returns:
            Combined text content from all blocks
        """
        content_parts = []
        for block in message.content:
            if block.type == "text":
                content_parts.append(block.text)
        return "\n".join(content_parts)

    def _build_default_system_prompt(self, working_dir: Optional[str] = None) -> str:
        """Build default system prompt for autonomous development.

        Args:
            working_dir: Working directory path

        Returns:
            System prompt string
        """
        working_dir = working_dir or os.getcwd()

        prompt = f"""You are an autonomous development assistant working in: {working_dir}

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
