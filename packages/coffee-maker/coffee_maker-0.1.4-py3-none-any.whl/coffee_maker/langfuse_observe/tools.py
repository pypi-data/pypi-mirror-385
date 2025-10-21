from typing import Callable

from langchain.agents import Tool
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langfuse import observe

from coffee_maker.utils.github import (
    get_pr_file_content as _get_pr_file_content,
    get_pr_modified_files as _get_pr_modified_files,
    post_suggestion_in_pr_review as _post_suggestion_in_pr_review,
)


def make_func_a_tool(name: str, func: Callable) -> Tool:
    import json

    @observe
    def _func(tool_input):
        # Handle both string and dict inputs from the agent
        if isinstance(tool_input, str):
            # Try to parse as JSON
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                # If parsing fails, check if it looks like JSON with code blocks
                # Remove ```json and ``` markers that the LLM sometimes adds
                cleaned = tool_input.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]  # Remove ```json
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]  # Remove ```
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]  # Remove trailing ```
                cleaned = cleaned.strip()

                try:
                    tool_input = json.loads(cleaned)
                except json.JSONDecodeError as e:
                    # Last resort: if it still looks like JSON (starts with { or [),
                    # it's probably malformed JSON - try to fix it
                    if cleaned.startswith("{") or cleaned.startswith("["):
                        # Try to fix common JSON issues
                        fixed = cleaned

                        # Fix 1: Replace single quotes with double quotes
                        fixed = fixed.replace("'", '"')

                        # Fix 2: Escape unescaped newlines within string values
                        # This regex finds quoted strings and escapes literal newlines
                        import re

                        def escape_newlines_in_strings(match):
                            s = match.group(0)
                            # Replace actual newlines with \\n
                            return s.replace("\n", "\\n").replace("\r", "\\r")

                        # Match quoted strings (handling escaped quotes)
                        fixed = re.sub(r'"(?:[^"\\]|\\.)*"', escape_newlines_in_strings, fixed)

                        try:
                            tool_input = json.loads(fixed)
                        except json.JSONDecodeError:
                            # Give up and raise an informative error
                            raise ValueError(
                                f"Invalid JSON input. Original error: {e}. Input preview: {cleaned[:200]}..."
                            )
                    else:
                        # Only try key-value parsing if it doesn't look like JSON
                        # This handles simple cases like "repo_full_name: X, pr_number: Y"
                        try:
                            # Pattern to match "key: value" with multi-word keys (single line only)
                            pattern = r"([\w\s]+?)\s*[:=]\s*([^,]+?)(?:,|$)"
                            matches = re.findall(pattern, cleaned)
                            if matches:
                                parsed = {}
                                for key, value in matches:
                                    # Normalize key: remove spaces, convert to snake_case
                                    key = key.strip().lower().replace(" ", "_")
                                    # Special mappings for common variations
                                    key_mappings = {
                                        "repository_full_name": "repo_full_name",
                                        "pr": "pr_number",
                                        "pull_request_number": "pr_number",
                                    }
                                    key = key_mappings.get(key, key)

                                    # Clean up the value
                                    value = value.strip()
                                    # Try to convert to int if it looks like a number
                                    if value.isdigit():
                                        parsed[key] = int(value)
                                    else:
                                        parsed[key] = value
                                if parsed:
                                    tool_input = parsed
                        except Exception:
                            pass

        # If tool_input is a dict, expand it as kwargs
        if isinstance(tool_input, dict):
            return func(**tool_input)
        else:
            # Otherwise pass as single argument
            return func(tool_input)

    _func.__doc__ = func.__doc__

    return Tool(name, _func, description=func.__doc__)


get_pr_modified_files = make_func_a_tool("get_pr_modified_files", _get_pr_modified_files)
get_pr_file_content = make_func_a_tool("get_pr_file_content", _get_pr_file_content)
post_suggestion_in_pr_review = make_func_a_tool("post_suggestion_in_pr_review", _post_suggestion_in_pr_review)


# Préparer les outils GitHub
# L'API Wrapper gère les appels à l'API GitHub
# Le Toolkit est une collection d'outils prêts à l'emploi pour GitHub
try:
    _github_toolkit = GitHubToolkit.from_github_api_wrapper(GitHubAPIWrapper())
    github_tools = _github_toolkit.get_tools()
except Exception:
    # If GitHub API wrapper initialization fails (e.g., missing GITHUB_APP_ID),
    # provide an empty list of tools
    github_tools = []
