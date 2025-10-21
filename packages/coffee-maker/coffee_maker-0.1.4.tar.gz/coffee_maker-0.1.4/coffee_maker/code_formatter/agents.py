"""LangChain agent helpers for the code formatter domain."""

from __future__ import annotations

import argparse
import logging
import sys
import json
import textwrap
from typing import Any, Dict, Optional, Sequence, Tuple

import langfuse
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langfuse import Langfuse

from coffee_maker.langfuse_observe.agents import configure_llm

load_dotenv()

from langfuse.langchain import CallbackHandler

langfuse_callback_handler = CallbackHandler()

logger = logging.getLogger(__name__)


def _initialise_llm(*, strict: bool = False) -> Tuple[Any, str, Optional[str]]:
    return configure_llm(strict=strict)


llm, llm_provider, llm_model = _initialise_llm(strict=False)


def _escape_braces(value: str) -> str:
    """Escape braces so ChatPromptTemplate does not treat them as placeholders."""

    return value.replace("{", "{{").replace("}", "}}")


def _extract_prompt_text(prompt_obj: Any) -> str:
    for attr in ("prompt", "text", "template"):
        value = getattr(prompt_obj, attr, None)
        if isinstance(value, str):
            return value
    return str(prompt_obj)


def _build_prompt(system_message: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", "File path: {file_path}\\n\\nFile content:\\n{file_content}"),
        ]
    )


def _build_agent_config(
    *,
    role: str,
    goal: str,
    backstory: str,
    prompt: ChatPromptTemplate,
    llm_override: Optional[Any] = None,
    tools: Sequence[Any] = (),
    verbose: bool = True,
    allow_delegation: bool = False,
) -> Dict[str, Any]:
    return {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "prompt": prompt,
        "llm": llm_override or llm,
        "tools": tuple(tools),
        "verbose": verbose,
        "allow_delegation": allow_delegation,
    }


def create_react_formatter_agent(
    langfuse_client: Langfuse,
    llm,
    use_auto_picker: bool = False,
    tier: str = "tier1",
    include_llm_tools: bool = True,
):
    """Create a ReAct formatter agent.

    Args:
        langfuse_client: Langfuse client for prompt management
        llm: LLM instance to use (can be AutoPickerLLMRefactored or regular LLM)
        use_auto_picker: If True and llm is not AutoPickerLLMRefactored, wrap it in AutoPickerLLMRefactored
        tier: API tier for rate limiting if use_auto_picker=True
        include_llm_tools: If True, include LLM invocation tools for specialized tasks

    Returns:
        Tuple of (agent, tools, llm_used)
    """
    # agent = ReAct agent with less complex and tools to use
    from langchain.agents import create_react_agent

    from coffee_maker.langfuse_observe.tools import (
        get_pr_modified_files,
        get_pr_file_content,
        post_suggestion_in_pr_review,
        github_tools,
    )

    # Wrap in AutoPickerLLMRefactored if requested
    from coffee_maker.langfuse_observe.auto_picker_llm_refactored import AutoPickerLLMRefactored

    if use_auto_picker and not isinstance(llm, AutoPickerLLMRefactored):
        logger.info("Wrapping LLM in AutoPickerLLMRefactored for rate limiting and fallback")
        from coffee_maker.langfuse_observe.create_auto_picker import create_auto_picker_for_react_agent

        llm = create_auto_picker_for_react_agent(tier=tier, streaming=True)

    # 2. Define the tools
    tools = list(github_tools) + [get_pr_modified_files, get_pr_file_content, post_suggestion_in_pr_review]

    # Add LLM tools if requested
    if include_llm_tools:
        from coffee_maker.langfuse_observe.llm_tools import create_llm_tools

        llm_tools = create_llm_tools(tier=tier)
        tools = tools + list(llm_tools)
        logger.info(f"Added {len(llm_tools)} LLM tools to ReAct agent")

    styleguide = langfuse_client.get_prompt("styleguide.md").prompt
    from langchain.prompts import PromptTemplate

    # Build additional context about LLM tools if included
    llm_tools_context = ""
    if include_llm_tools:
        llm_tools_context = """

IMPORTANT: You have access to specialized LLM tools for different purposes:
- invoke_llm_openai_reasoning / invoke_llm_gemini_reasoning: Advanced reasoning, planning, and problem-solving with extended thinking
- invoke_llm_openai_best_model / invoke_llm_gemini_best_model: Best overall quality and performance (use for critical tasks)
- invoke_llm_openai_long_context / invoke_llm_gemini_long_context: Use for tasks requiring very long context (large files)
- invoke_llm_openai_accurate / invoke_llm_gemini_accurate: Use for complex code analysis requiring high accuracy
- invoke_llm_openai_second_best_model / invoke_llm_gemini_second_best_model: Use for balanced performance and cost
- invoke_llm_openai_fast / invoke_llm_gemini_fast: Use for quick, simple analysis tasks
- invoke_llm_openai_budget / invoke_llm_gemini_budget: Use for simple tasks to minimize costs

When you need to analyze code, consider delegating to these specialized LLMs based on the task requirements.
For example, use reasoning for complex problem-solving, best_model for critical reviews, long_context for large files, fast for simple checks.
"""

    # ReAct agents require specific variables: tools, tool_names, input, agent_scratchpad
    # Embed the styleguide directly in the template string
    template_str = f"""You are a senior software Engineer with high Python development experience.
You will be given some tasks that consists of reviewing a pull request and make of review of the code.
You will be especially meticulous to reformat code that are in the pull request according to the styleguide.
Use the tools at your disposal in order to post suggestions in the pull request.

Here is the style guide (formatted in markdown):
{styleguide}
{llm_tools_context}
You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought:{{agent_scratchpad}}"""

    react_prompt = PromptTemplate.from_template(template_str)

    agent = create_react_agent(
        llm,
        tools=tools,
        prompt=react_prompt,
    )

    return agent, tools, llm  # Return llm so caller can access AutoPickerLLM stats if used


def create_langchain_code_formatter_agent(
    langfuse_client: Langfuse, *, llm_override: Optional[Any] = None
) -> Dict[str, Any]:
    """Return the LangChain configuration for the formatter agent."""

    try:
        main_prompt = langfuse_client.get_prompt("code_formatter_main_llm_entry")
    except Exception as exc:  # pragma: no cover - surfaced to callers/tests
        logger.exception("Failed to fetch formatter prompts", exc_info=exc)
        raise

    main_prompt_text = _extract_prompt_text(main_prompt)

    # Use the main prompt which contains full instructions for JSON output
    system_message = _escape_braces(main_prompt_text)

    # Build prompt with placeholders for file_path and code_to_modify
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            (
                "user",
                """CODE TO MODIFY (file_path : {file_path}) (only the string between ------ delimiters):
------
{code_to_modify}
------""",
            ),
        ]
    )

    llm_instance = llm_override or llm

    def _invoke_formatter(file_content: str, file_path: str) -> str:
        chain = prompt | llm_instance
        # Use variable names matching the Langfuse prompt template
        # we pass the callback handler to the chain to trace the run in Langfuse
        response = chain.invoke(
            input={"file_path": file_path, "code_to_modify": file_content},
            config={"callbacks": [langfuse_callback_handler]},
        )
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _parse_formatter_output(raw_output: str) -> list[dict[str, Any]]:
        """Parse LLM output, handling markdown code blocks and whitespace.

        Args:
            raw_output: Raw string output from the LLM

        Returns:
            List of dictionaries containing code suggestions

        Raises:
            json.JSONDecodeError: If the content is not valid JSON
        """
        content = extract_brackets(raw_output)
        # Handle empty content
        if not content:
            return []

        try:
            result = json.loads(content)
            # Ensure result is a list
            if not isinstance(result, list):
                assert isinstance(result, dict), "Expected dictionary or list of dictionaries"
                result = [result]
            return result
        except json.JSONDecodeError as exc:
            logger.critical(f"Could not parse JSON output. Error: {exc}\n" f"Raw output : {raw_output}")
            raise

    def get_result_from_llm(file_content: str, file_path: str) -> str:
        """Invoke the formatter LLM and return raw output.

        Args:
            file_content: Source code content to format
            file_path: Logical file path for context

        Returns:
            Raw LLM response as string (may include markdown formatting)

        Example:
            >>> result = get_result_from_llm("def foo():\\n  pass", "demo.py")
            >>> print(result)  # Returns formatted code suggestions
        """
        return _invoke_formatter(file_content, file_path)

    def get_list_of_dict_from_llm(
        file_content: str, file_path: str, *, skip_empty_files: bool = True
    ) -> list[dict[str, Any]]:
        """Invoke formatter LLM and parse output as structured list of suggestions.

        Args:
            file_content: Source code content to format
            file_path: Logical file path for context
            skip_empty_files: If True, return empty list for empty files without LLM call

        Returns:
            List of dictionaries containing parsed code suggestions.
            Returns empty list if file is empty and skip_empty_files=True.

        Raises:
            json.JSONDecodeError: If LLM output cannot be parsed as valid JSON

        Example:
            >>> suggestions = get_list_of_dict_from_llm("def foo():\\n  pass", "demo.py")
            >>> print(len(suggestions))  # Number of formatting suggestions
        """
        if skip_empty_files and not file_content.strip():
            return []
        raw_output = _invoke_formatter(file_content, file_path)
        return _parse_formatter_output(raw_output)

    agent = _build_agent_config(
        role="Senior Software Engineer: python code formatter",
        goal="",
        backstory="",
        prompt=prompt,
        llm_override=llm_override,
        tools=(),
    )

    agent["get_result_from_llm"] = get_result_from_llm
    agent["get_list_of_dict_from_llm"] = get_list_of_dict_from_llm

    return agent


def extract_brackets(s: str) -> str:
    """Extract content between first opening and last closing bracket.

    Finds the first occurrence of '[' or '{' and the last occurrence of ']' or '}'
    in the string, then returns the substring between them (inclusive).

    Args:
        s: Input string to extract from

    Returns:
        Substring between first opening and last closing bracket,
        or empty string if no valid brackets found

    Example:
        >>> extract_brackets('text before [{"key": "value"}] text after')
        '[{"key": "value"}]'
        >>> extract_brackets('no brackets here')
        ''
    """
    # Remove any char surrounding the json list of dict
    first_open = min((i for i in [s.find("["), s.find("{")] if i != -1), default=-1)
    last_close = max((i for i in [s.rfind("]"), s.rfind("}")] if i != -1), default=-1)

    if first_open == -1 or last_close == -1:
        return ""

    return s[first_open : last_close + 1]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run a small end-to-end example with hard-coded input."""

    parser = argparse.ArgumentParser(description="Run the formatter agent demo")
    parser.add_argument(
        "--file-path",
        default="demo/non_compliant.py",
        help="Logical path attached to the demo file contents.",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider (e.g., anthropic, openai, gemini). Uses default if not specified.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model name. Uses provider default if not specified.",
    )
    args = parser.parse_args(argv)
    langfuse_client = langfuse.get_client()
    try:
        new_llm, new_provider, new_model = configure_llm(
            provider=args.provider,
            model=args.model,
            strict=True,
        )
    except Exception as exc:  # pragma: no cover - exercised in manual usage
        logger.error("Unable to initialise the LLM: %s", exc)
        print(f"Formatter demo aborted. Configuration error: {exc}", file=sys.stderr)
        return 1

    globals()["llm"], globals()["llm_provider"], globals()["llm_model"] = new_llm, new_provider, new_model

    agent_config = create_langchain_code_formatter_agent(langfuse_client=langfuse_client, llm_override=new_llm)

    chain = agent_config["prompt"] | agent_config["llm"]

    sample_code = textwrap.dedent(
        """
        import math


        def   calculateDistance(x1,y1,x2,y2):
            dx = x2-x1
            dy = y2-y1
            distance =   math.sqrt(dx*dx + dy*dy)
            print('result:',distance)
            return distance
        """
    ).strip()

    payload = {"file_path": args.file_path, "code_to_modify": sample_code}

    print("=== Demo input (non compliant) ===")
    print(sample_code)
    print()
    print("=== Formatter agent output ===")

    try:
        response = chain.invoke(payload)
    except Exception as exc:  # pragma: no cover - manual execution path
        logger.error("Formatter agent failed: %s", exc, exc_info=True)
        print(f"Formatter agent failed to run: {exc}", file=sys.stderr)
        return 1

    content = getattr(response, "content", response)
    print(content)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
