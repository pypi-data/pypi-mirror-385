"""Centralized prompt loader for multi-AI provider support.

This module provides a centralized system for loading prompts from .claude/commands/
directory, making it easy to:
1. Manage prompts in a single location
2. Migrate prompts to Gemini, OpenAI, or other LLM providers
3. Version control prompts separately from code
4. Share prompts across different agents

Usage:
    >>> from coffee_maker.autonomous.prompt_loader import load_prompt
    >>> prompt = load_prompt("implement-feature", {
    ...     "PRIORITY_NAME": "US-021",
    ...     "PRIORITY_TITLE": "Refactoring",
    ...     "PRIORITY_CONTENT": "Split large files..."
    ... })

Related to:
- User Story: "As a code_developer or project_manager, I want all prompts
  stored in .claude/commands for easier migration to Gemini/OpenAI"
- PRIORITY 8: Multi-AI Provider Support
- PRIORITY 4.1: Puppeteer MCP Integration
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Default prompts directory
PROMPTS_DIR = Path(".claude/commands")


class PromptLoader:
    """Load and manage prompts from .claude/commands/ directory.

    This class provides centralized prompt management, allowing prompts
    to be stored separately from code for easy migration between
    AI providers (Claude, Gemini, OpenAI, etc.).

    Example:
        >>> loader = PromptLoader()
        >>> prompt = loader.load("implement-feature", {
        ...     "PRIORITY_NAME": "US-021",
        ...     "PRIORITY_TITLE": "Refactoring"
        ... })
        >>> print(prompt)
        "Read docs/roadmap/ROADMAP.md and implement US-021: Refactoring..."
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize prompt loader.

        Args:
            prompts_dir: Path to prompts directory (default: .claude/commands)
        """
        self.prompts_dir = prompts_dir or PROMPTS_DIR

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            logger.warning("Creating directory...")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def load(self, prompt_name: str, variables: Optional[Dict[str, str]] = None) -> str:
        """Load a prompt from file and substitute variables.

        Args:
            prompt_name: Name of prompt file (without .md extension)
            variables: Dictionary of variables to substitute ($VAR_NAME format)

        Returns:
            Processed prompt string with variables substituted

        Raises:
            FileNotFoundError: If prompt file doesn't exist

        Example:
            >>> loader = PromptLoader()
            >>> prompt = loader.load("create-technical-spec", {
            ...     "PRIORITY_NAME": "US-021",
            ...     "SPEC_FILENAME": "US_021_TECHNICAL_SPEC.md",
            ...     "PRIORITY_CONTEXT": "Split daemon.py..."
            ... })
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.md"

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}\n" f"Available prompts: {self.list_prompts()}"
            )

        # Read prompt template
        prompt_template = prompt_file.read_text()

        # Substitute variables
        if variables:
            for var_name, var_value in variables.items():
                placeholder = f"${var_name}"
                prompt_template = prompt_template.replace(placeholder, str(var_value))

        return prompt_template

    def list_prompts(self) -> list[str]:
        """List all available prompts.

        Returns:
            List of prompt names (without .md extension)

        Example:
            >>> loader = PromptLoader()
            >>> loader.list_prompts()
            ['implement-feature', 'implement-documentation', 'create-technical-spec', ...]
        """
        if not self.prompts_dir.exists():
            return []

        prompts = []
        for prompt_file in self.prompts_dir.glob("*.md"):
            prompts.append(prompt_file.stem)  # Get filename without extension

        return sorted(prompts)

    def prompt_exists(self, prompt_name: str) -> bool:
        """Check if a prompt file exists.

        Args:
            prompt_name: Name of prompt (without .md extension)

        Returns:
            True if prompt exists

        Example:
            >>> loader = PromptLoader()
            >>> loader.prompt_exists("implement-feature")
            True
            >>> loader.prompt_exists("nonexistent")
            False
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.md"
        return prompt_file.exists()

    def get_prompt_path(self, prompt_name: str) -> Path:
        """Get full path to a prompt file.

        Args:
            prompt_name: Name of prompt (without .md extension)

        Returns:
            Path to prompt file

        Example:
            >>> loader = PromptLoader()
            >>> path = loader.get_prompt_path("implement-feature")
            >>> print(path)
            .claude/commands/implement-feature.md
        """
        return self.prompts_dir / f"{prompt_name}.md"


# Convenience function for simple usage
def load_prompt(prompt_name: str, variables: Optional[Dict[str, str]] = None) -> str:
    """Load a prompt (convenience function).

    Args:
        prompt_name: Name of prompt file (without .md extension)
        variables: Dictionary of variables to substitute

    Returns:
        Processed prompt string

    Example:
        >>> from coffee_maker.autonomous.prompt_loader import load_prompt
        >>> prompt = load_prompt("implement-feature", {
        ...     "PRIORITY_NAME": "US-021",
        ...     "PRIORITY_TITLE": "Refactoring",
        ...     "PRIORITY_CONTENT": "Split daemon.py into smaller files..."
        ... })
    """
    loader = PromptLoader()
    return loader.load(prompt_name, variables)


# Prompt name constants (for type safety and IDE autocomplete)
class PromptNames:
    """Constants for prompt names.

    Agent System Prompts:
        AGENT_PROJECT_MANAGER: System prompt for project_manager and assistant agents

    Task-Specific Prompts (used by code_developer):
        CREATE_TECHNICAL_SPEC: Technical specification generation
        IMPLEMENT_DOCUMENTATION: Documentation implementation
        IMPLEMENT_FEATURE: Feature implementation
        FIX_GITHUB_ISSUE: GitHub issue resolution
        TEST_WEB_APP: Web application testing (Puppeteer)
        CAPTURE_VISUAL_DOCS: Visual documentation capture (Puppeteer)
        VERIFY_DOD_PUPPETEER: Definition of Done verification with Puppeteer
    """

    # Agent system prompts
    AGENT_PROJECT_MANAGER = "agent-project-manager"

    # Task-specific prompts
    CREATE_TECHNICAL_SPEC = "create-technical-spec"
    IMPLEMENT_DOCUMENTATION = "implement-documentation"
    IMPLEMENT_FEATURE = "implement-feature"
    FIX_GITHUB_ISSUE = "fix-github-issue"
    TEST_WEB_APP = "test-web-app"
    CAPTURE_VISUAL_DOCS = "capture-visual-docs"
    VERIFY_DOD_PUPPETEER = "verify-dod-puppeteer"

    # User Story Command Handler prompts (US-012)
    EXTRACT_USER_STORY = "extract_user_story"
    ANALYZE_SIMILARITY = "analyze_similarity"
    SUGGEST_PRIORITIZATION = "suggest_prioritization"
    REFINE_USER_STORY = "refine_user_story"
