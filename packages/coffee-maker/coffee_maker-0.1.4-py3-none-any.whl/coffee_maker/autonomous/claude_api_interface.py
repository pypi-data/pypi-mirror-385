"""Direct Anthropic API interface for autonomous development.

This module provides a reliable alternative to ClaudeCLI by calling the
Anthropic API directly, avoiding subprocess and TTY issues.

Example:
    >>> from coffee_maker.autonomous.claude_api_interface import ClaudeAPI
    >>>
    >>> api = ClaudeAPI()
    >>> result = api.execute_prompt(
    ...     "Read docs/roadmap/ROADMAP.md and implement PRIORITY 2"
    ... )
    >>> print(result.content)
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic

from coffee_maker.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class APIResult:
    """Result from Anthropic API execution.

    Attributes:
        content: Response content from Claude
        model: Model used for the request
        usage: Token usage information (input_tokens, output_tokens)
        stop_reason: Reason the response ended
        success: Whether execution succeeded
    """

    content: str
    model: str
    usage: dict
    stop_reason: str
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if request succeeded."""
        return self.error is None


class ClaudeAPI:
    """Direct Anthropic API interface for autonomous development.

    This class provides a reliable alternative to ClaudeCLI by calling the
    Anthropic API directly, avoiding subprocess, TTY, and interactive prompt issues.

    Key advantages over CLI approach:
    - No subprocess issues
    - No interactive prompt issues
    - No TTY detection issues
    - Direct control over Claude's behavior
    - Better error handling
    - Token usage tracking built-in
    - Can use tool calling API

    Attributes:
        model: Claude model to use (default: claude-sonnet-4)
        max_tokens: Maximum tokens per response (default: 8000)
        timeout: Request timeout in seconds (default: 3600)

    Example:
        >>> api = ClaudeAPI()
        >>> result = api.execute_prompt("Implement feature X")
        >>> if result.success:
        ...     print("Feature implemented!")
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8000,
        timeout: int = 3600,
        api_key: Optional[str] = None,
    ):
        """Initialize Claude API interface.

        Args:
            model: Claude model to use (default: claude-sonnet-4-20250514)
            max_tokens: Maximum tokens per response (default: 8000)
            timeout: Request timeout in seconds (default: 3600)
            api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Initialize Anthropic client
        # Use provided key or get from ConfigManager
        if api_key is None:
            api_key = ConfigManager.get_anthropic_api_key()
        self.client = Anthropic(api_key=api_key)

        logger.debug(f"ClaudeAPI initialized with model: {model}")

    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> APIResult:
        """Execute a prompt using Anthropic API.

        Args:
            prompt: The prompt to send to Claude
            system_prompt: Optional system prompt for context
            working_dir: Working directory context (included in prompt)
            timeout: Timeout in seconds (None = use default)

        Returns:
            APIResult with content, model, usage, and success status

        Example:
            >>> api = ClaudeAPI()
            >>> result = api.execute_prompt(
            ...     "Read docs/roadmap/ROADMAP.md and implement PRIORITY 2"
            ... )
            >>> if result.success:
            ...     print("Implementation complete")
        """
        timeout = timeout or self.timeout

        # Add working directory context if provided
        if working_dir:
            prompt = f"Working directory: {working_dir}\n\n{prompt}"

        # Default system prompt for autonomous development
        if system_prompt is None:
            system_prompt = self._build_default_system_prompt(working_dir)

        logger.debug(f"Executing API request: {prompt[:100]}...")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )

            logger.debug(f"API request completed: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

            return APIResult(
                content=self._extract_content(message),
                model=message.model,
                usage={
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
                stop_reason=message.stop_reason,
            )

        except Exception as e:
            logger.error(f"API request failed: {e}")
            return APIResult(
                content="",
                model=self.model,
                usage={"input_tokens": 0, "output_tokens": 0},
                stop_reason="error",
                error=str(e),
            )

    def _extract_content(self, message) -> str:
        """Extract text content from API response.

        Args:
            message: Anthropic API message response

        Returns:
            Combined text content from all content blocks
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

    def check_available(self) -> bool:
        """Check if Anthropic API is available.

        Returns:
            True if API key is configured and accessible

        Example:
            >>> api = ClaudeAPI()
            >>> if api.check_available():
            ...     print("API is ready!")
        """
        try:
            # Try a simple API call
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
                timeout=5,
            )
            logger.info(f"Anthropic API available: {message.model}")
            return True

        except Exception as e:
            logger.error(f"Anthropic API not available: {e}")
            return False
