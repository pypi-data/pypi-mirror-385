"""
Main Orchestration Module for Code Formatter System.

This module serves as a simplified entry point for automated code formatting
and review. It directly uses LangChain agents without CrewAI orchestration.

Workflow:
    1. Fetch list of modified files from the specified GitHub PR
    2. For each file (or single file if specified), fetch its content
    3. Run the formatter agent to analyze and suggest improvements
    4. Parse the agent's output to extract suggestions
    5. Post each suggestion as a GitHub PR review comment

Environment Variables Required:
    GITHUB_TOKEN: GitHub personal access token with repo permissions
    LANGFUSE_SECRET_KEY: Langfuse secret key for authentication
    LANGFUSE_PUBLIC_KEY: Langfuse public key for authentication
    LANGFUSE_HOST: Langfuse host URL (e.g., https://cloud.langfuse.com)
    GOOGLE_API_KEY: Google API key for Gemini LLM

Functions:
    run_code_formatter: Main orchestration function for the entire workflow

Usage:
    Command line:
        python -m coffee_maker.code_formatter.main --repo owner/repo --pr 123
        python -m coffee_maker.code_formatter.main --repo owner/repo --pr 123 --file path/to/file.py

    Programmatic:
        from coffee_maker.code_formatter.main import run_code_formatter
        result = run_code_formatter("owner/repo", 123)
        result = run_code_formatter("owner/repo", 123, file_path="path/to/file.py")
"""

import asyncio
import logging
import os
from datetime import datetime
from functools import partial
from typing import Callable, Optional

from dotenv import load_dotenv
from langfuse import Langfuse, observe

from coffee_maker.code_formatter.agents import create_langchain_code_formatter_agent, create_react_formatter_agent
from coffee_maker.config.manager import ConfigManager
from coffee_maker.utils.github import get_pr_file_content, get_pr_modified_files, post_suggestion_in_pr_review

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# --- Initialize the global Langfuse client ---
try:
    langfuse_client = Langfuse(
        secret_key=ConfigManager.get_langfuse_secret_key(required=True),
        public_key=ConfigManager.get_langfuse_public_key(required=True),
        host=os.getenv("LANGFUSE_HOST"),
    )
except Exception:
    logger.critical("Langfuse client could not be initialized. Check environment variables.", exc_info=True)
    raise


async def _process_single_file(
    agent_config: dict,
    file_path: str,
    get_file_content: Callable[[], Optional[str]],
    repo_full_name: str,
    pr_number: int,
    skip_empty_files: bool = True,
    semaphore: Optional[asyncio.Semaphore] = None,
) -> dict:
    if semaphore is not None:
        async with semaphore:
            return await _process_single_file(
                agent_config,
                file_path,
                get_file_content,
                repo_full_name,
                pr_number,
                skip_empty_files=skip_empty_files,
                semaphore=None,
            )
    """
    Process a single file through the formatter agent and post suggestions.

    Args:
        agent_config: LangChain agent configuration dictionary
        file_path: Path to the file in the repository
        file_content: Content of the file
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number

    Returns:
        Dictionary with processing results including file_path, suggestions_count, and any errors
    """
    logger.info(f"Processing file: {file_path}")

    try:
        logger.info(f"Invoking formatter agent for {file_path}")

        file_content = await asyncio.to_thread(get_file_content)

        if file_content is None:
            logger.error("Formatter skipped %s: unable to fetch content", file_path)
            return {"file_path": file_path, "error": "missing content", "success": False}

        if skip_empty_files and not file_content.strip():
            logger.info("Formatter skipped %s: empty file", file_path)
            return {"file_path": file_path, "suggestions_count": 0, "posted_count": 0, "success": True}

        suggestions = await asyncio.to_thread(
            agent_config["get_list_of_dict_from_llm"], file_content, file_path, skip_empty_files=skip_empty_files
        )

        logger.info(f"Agent outputs {len(suggestions)} modifications for {file_path}")

        # Post each suggestion to GitHub
        async def _post(idx: int, suggestion: dict) -> bool:
            try:
                start_line_raw = suggestion.get("start_line")
                end_line_raw = suggestion.get("end_line")
                if end_line_raw is None:
                    logger.error("Suggestion %s for %s missing end_line", idx, file_path)
                    return False

                start_line_int = int(start_line_raw) if start_line_raw is not None else None
                end_line_int = int(end_line_raw)

                logger.info(
                    "Posting suggestion %s/%s for %s (lines %s-%s)",
                    idx,
                    len(suggestions),
                    file_path,
                    start_line_int,
                    end_line_int,
                )

                await asyncio.to_thread(
                    post_suggestion_in_pr_review,
                    repo_full_name,
                    pr_number,
                    file_path,
                    start_line_int,
                    end_line_int,
                    str(suggestion.get("modified_code", "")),
                    str(suggestion.get("explanation", "")),
                )
                return True
            except Exception as post_error:
                logger.error(
                    "Failed to post suggestion %s for %s: %s",
                    idx,
                    file_path,
                    post_error,
                    exc_info=True,
                )
                return False

        posted_count = 0
        for idx, suggestion in enumerate(suggestions, 1):
            if await _post(idx, suggestion):
                posted_count += 1

        logger.info(f"Successfully posted {posted_count}/{len(suggestions)} suggestions for {file_path}")

        return {
            "file_path": file_path,
            "suggestions_count": len(suggestions),
            "posted_count": posted_count,
            "success": True,
        }

    except Exception as exc:
        logger.error(f"Failed to process file {file_path}: {exc}", exc_info=True)
        return {
            "file_path": file_path,
            "error": str(exc),
            "success": False,
        }


@observe
async def run_code_formatter(
    repo_full_name: str, pr_number: int, file_path: Optional[str] = None, skip_empty_files=True
) -> list[dict]:
    """
    Run the code formatter on files in a GitHub pull request.

    Args:
        repo_full_name: Full repository name (e.g., 'owner/repo')
        pr_number: Pull request number
        file_path: Optional specific file path to process. If None, processes all Python files in the PR.

    Returns:
        List of dictionaries containing processing results for each file
    """
    logger.info(f"Starting code formatter for {repo_full_name} PR #{pr_number}")

    # Initialize Langfuse trace
    langfuse_client.update_current_trace(
        session_id=f"pr-review-{repo_full_name}-{pr_number}-{datetime.now().isoformat()}",
        metadata={
            "repo": repo_full_name,
            "pr_number": pr_number,
            "file_path": file_path,
        },
    )

    # Create the formatter agent
    logger.info("Initializing formatter agent")
    agent_config = create_langchain_code_formatter_agent(langfuse_client)
    logger.info("Formatter agent initialized")

    # Determine which files to process
    if file_path:
        # Process only the specified file
        logger.info(f"Processing single file: {file_path}")
        files_to_process: list[tuple[str, Callable[[], Optional[str]]]] = [
            (file_path, partial(get_pr_file_content, repo_full_name, pr_number, file_path))
        ]

    else:
        files_info = await asyncio.to_thread(get_pr_modified_files, repo_full_name, pr_number)
        filenames = [f["filename"] for f in files_info if f["filename"].endswith(".py")]

        if not files_info or len(filenames) == 0:
            logger.warning(f"No modified files .py files found in PR #{pr_number}")
            return []

        logger.info(f"Found {len(filenames)} Python files in PR #{pr_number}")

        files_to_process = [
            (filename, partial(get_pr_file_content, repo_full_name, pr_number, filename)) for filename in filenames
        ]

    logger.info(f"Processing {len(files_to_process)} file(s)")

    max_concurrency = int(os.getenv("COFFEE_MAKER_MAX_CONCURRENCY", "5"))
    concurrency_limit = max(1, min(len(files_to_process), max_concurrency))
    semaphore = asyncio.Semaphore(concurrency_limit)

    # Process files asynchronously
    tasks = [
        _process_single_file(
            agent_config=agent_config,
            file_path=file_path,
            get_file_content=get_file_content,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            skip_empty_files=skip_empty_files,
            semaphore=semaphore,
        )
        for file_path, get_file_content in files_to_process
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions that were returned
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Task failed with exception: {result}", exc_info=result)
            processed_results.append({"error": str(result), "success": False})
        else:
            processed_results.append(result)

    # Log summary
    successful = sum(1 for r in processed_results if r.get("success"))
    logger.info(f"Code formatter completed: {successful}/{len(processed_results)} files processed successfully")

    # Flush Langfuse to ensure all events are sent
    langfuse_client.flush()

    return processed_results


# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run code formatter on a GitHub PR")
    parser.add_argument("--repo", default="Bobain/MonolithicCoffeeMakerAgent", help="Full repository name (owner/repo)")
    parser.add_argument("--pr", type=int, default=113, help="Pull request number")
    parser.add_argument("--file", type=str, default=None, help="Optional: specific file path to process")
    args = parser.parse_args()

    langfuse_client.update_current_trace(
        session_id=f"{datetime.now().isoformat()} code_formatter_main {args.repo=} {args.pr=} {args.file=}"
    )

    from langchain.agents import AgentExecutor
    from langchain.callbacks.base import BaseCallbackHandler

    # Create a custom callback handler to display LLM thinking process
    class StreamingCallbackHandler(BaseCallbackHandler):
        """Callback handler to display LLM thinking process in real-time."""

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            """Run on new LLM token. Only available when streaming is enabled."""
            print(token, end="", flush=True)

        def on_llm_end(self, response, **kwargs) -> None:
            """Run when LLM ends running."""
            print("\n")

        def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
            """Run when tool starts running."""
            print(f"\n🔧 {serialized.get('name', 'Tool')}: ", end="", flush=True)

        def on_tool_end(self, output: str, **kwargs) -> None:
            """Run when tool ends running."""
            print("✓")

        def on_tool_error(self, error: Exception, **kwargs) -> None:
            """Run when tool errors."""
            print(f"✗ {error}")

    # Get LLM with streaming enabled - use AutoPickerLLMRefactored for rate limiting and fallback
    from coffee_maker.langfuse_observe.create_auto_picker import create_auto_picker_for_react_agent

    auto_picker_llm = create_auto_picker_for_react_agent(tier="tier1", streaming=True)
    react_agent, tools, llm_instance = create_react_formatter_agent(
        langfuse_client, auto_picker_llm, use_auto_picker=False  # Already using AutoPickerLLMRefactored
    )

    # Create an agent executor with streaming enabled
    streaming_handler = StreamingCallbackHandler()
    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=tools,
        verbose=False,  # Disable verbose to reduce output
        callbacks=[streaming_handler],
        return_intermediate_steps=False,  # Don't return intermediate steps
        max_iterations=15,  # Limit iterations to prevent long runs
    )

    # 4. Run the Agent asynchronously to allow streaming
    logger.info(f"Starting ReAct agent for PR #{args.pr} in {args.repo}")
    response = agent_executor.invoke(
        {"input": f"Review PR #{args.pr} in repository {args.repo}"},
        config={"callbacks": [streaming_handler]},
    )
    logger.info(f"\nAgent completed. Response: {response}")

    # Print AutoPickerLLMRefactored statistics
    from coffee_maker.langfuse_observe.auto_picker_llm_refactored import AutoPickerLLMRefactored

    if isinstance(llm_instance, AutoPickerLLMRefactored):
        stats = llm_instance.get_stats()
        logger.info("\n=== AutoPickerLLMRefactored Statistics ===")
        logger.info(f"Total requests: {stats['total_requests']}")
        logger.info(f"Primary model requests: {stats['primary_requests']} ({stats['primary_usage_percent']:.1f}%)")
        logger.info(f"Fallback requests: {stats['fallback_requests']} ({stats['fallback_usage_percent']:.1f}%)")
        logger.info(f"Rate limit waits: {stats['rate_limit_waits']}")
        logger.info(f"Rate limit fallbacks: {stats['rate_limit_fallbacks']}")

    # # Run the async function:
    # agent = basic agent with complex prompt and strict expected outputs that are then parsed and used to call
    #           functions
    # asyncio.run(
    #     run_code_formatter(repo_full_name=args.repo, pr_number=args.pr, file_path=args.file, skip_empty_files=True)
    # )
