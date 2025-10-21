"""Provider implementations for different AI services.

This package contains concrete implementations of the BaseAIProvider interface
for various AI services (Claude, OpenAI, Gemini, etc.).

Available Providers:
    - ClaudeProvider: Anthropic Claude (API or CLI mode)
    - OpenAIProvider: OpenAI GPT-4/GPT-4 Turbo/o1/o3
    - GeminiProvider: Google Gemini

Example:
    >>> from coffee_maker.ai_providers.providers import ClaudeProvider
    >>> config = {
    ...     'model': 'claude-sonnet-4-5-20250929',
    ...     'use_cli': True,
    ...     'max_tokens': 8000,
    ...     'temperature': 0.7,
    ...     'api_key_env': 'ANTHROPIC_API_KEY'
    ... }
    >>> provider = ClaudeProvider(config)
    >>> result = provider.execute_prompt("Write a Python function")
"""

from coffee_maker.ai_providers.providers.claude_provider import ClaudeProvider
from coffee_maker.ai_providers.providers.gemini_provider import GeminiProvider
from coffee_maker.ai_providers.providers.openai_provider import OpenAIProvider

__all__ = [
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
]
