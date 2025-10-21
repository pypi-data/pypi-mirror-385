"""GitHub API utilities for pull request operations.

This module provides utilities for interacting with GitHub pull requests,
including posting code suggestions, fetching PR files, and handling review conflicts.

Features:
- Post code suggestions as PR review comments with automatic retry on conflicts
- Fetch list of modified files from PRs (with Python file filtering)
- Fetch file content from PR head commits
- Automatic handling of pending review conflicts
- GitHubPRClient wrapper for convenient PR operations

Example:
    >>> from coffee_maker.utils.github import GitHubPRClient
    >>>
    >>> # Create client
    >>> client = GitHubPRClient()
    >>>
    >>> # Get modified Python files
    >>> files = client.get_pr_modified_files("owner/repo", 123)
    >>> print(f"Found {len(files['python_files'])} Python files")
    >>>
    >>> # Post code suggestion
    >>> client.post_suggestion_in_pr_review(
    ...     "owner/repo", 123, "src/main.py",
    ...     start_line=10, end_line=12,
    ...     suggestion_body="improved code",
    ...     comment_text="Better implementation"
    ... )

Technical Notes:
- Requires GITHUB_TOKEN environment variable (loaded via ConfigManager)
- Uses PyGithub library for GitHub API access
- Includes Langfuse observability decorators for monitoring
- Automatically handles pending review conflicts with retry logic
- Line numbers are 1-indexed (first line is 1)
"""

import logging
from typing import Callable, Optional, Tuple

from github import Auth, Github, GithubException
from langfuse import observe

from coffee_maker.config import ConfigManager
from coffee_maker.langfuse_observe.retry import with_conditional_retry

LOGGER = logging.getLogger(__name__)


def get_github_client_instance() -> Github:
    """Create and return an authenticated GitHub client instance.

    Uses ConfigManager to load GITHUB_TOKEN from environment and creates
    an authenticated GitHub client using PyGithub.

    Returns:
        Github: Authenticated GitHub client instance

    Raises:
        APIKeyMissingError: If GITHUB_TOKEN environment variable is not set

    Example:
        >>> client = get_github_client_instance()
        >>> user = client.get_user()
        >>> print(user.login)
    """
    token = ConfigManager.get_github_token()
    auth = Auth.Token(token)
    return Github(auth=auth)


github_client_instance = get_github_client_instance()


def _is_pending_review_conflict(exc: GithubException) -> bool:
    """Return True if exception indicates an existing pending review blocks new comments."""

    message = (exc.data or {}).get("message", "") if isinstance(exc.data, dict) else ""
    if "pending review" in message.lower():
        return True

    errors = (exc.data or {}).get("errors", []) if isinstance(exc.data, dict) else []
    for error in errors:
        if isinstance(error, dict) and "pending review" in error.get("message", "").lower():
            return True

    return "pending review" in str(exc).lower()


def _clear_pending_review(pr, login: str) -> bool:
    """Delete any pending review authored by the provided login.

    Returns True when a review was removed, False otherwise.
    """

    try:
        for review in pr.get_reviews():
            if getattr(review, "state", "").upper() == "PENDING" and getattr(review.user, "login", None) == login:
                LOGGER.info("Found existing pending review for %s. Deleting before retrying comment.", login)
                review.delete()
                return True
    except Exception as cleanup_error:  # pragma: no cover - defensive logging
        LOGGER.warning("Unable to clear pending review: %s", cleanup_error)

    return False


def _create_pending_review_retry_condition(
    pr, current_user_login: str
) -> Callable[[Exception], Tuple[bool, Optional[Callable]]]:
    """Create a retry condition checker for pending review conflicts.

    Args:
        pr: GitHub PR object
        current_user_login: Current user's GitHub login

    Returns:
        Function that checks if error is pending review conflict and returns cleanup function
    """

    def check_pending_review_conflict(error: Exception) -> Tuple[bool, Optional[Callable]]:
        """Check if error is a pending review conflict and return cleanup function.

        Args:
            error: Exception that occurred

        Returns:
            Tuple of (should_retry, cleanup_function)
        """
        if not isinstance(error, GithubException):
            return False, None

        if error.status != 422:
            return False, None

        if not _is_pending_review_conflict(error):
            return False, None

        LOGGER.info("Detected pending review conflict. Will cleanup and retry.")

        # Return cleanup function that clears pending review
        def cleanup():
            cleared = _clear_pending_review(pr, current_user_login)
            if not cleared:
                LOGGER.warning("Failed to clear pending review during cleanup")

        return True, cleanup

    return check_pending_review_conflict


@observe
def post_suggestion_in_pr_review(
    repo_full_name: Optional[str] = None,
    pr_number: Optional[int] = None,
    file_path: Optional[str] = None,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    suggestion_body: Optional[str] = None,
    comment_text: Optional[str] = None,
    g: Github = github_client_instance,
) -> str:
    """
    Post a code suggestion as a review comment on a GitHub pull request.

    Automatically handles pending review conflicts with retry logic.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number
        file_path (str): Path to the file in the repository
        start_line (int): Starting line number (1-indexed)
        end_line (int): Ending line number (1-indexed)
        suggestion_body (str): The suggested code (plain text, no markdown)
        comment_text (str): Explanatory text for the suggestion

    Example input (use \\n for newlines in JSON strings): {
        "repo_full_name": "owner/repo",
        "pr_number": 123,
        "file_path": "src/main.py",
        "start_line": 10,
        "end_line": 12,
        "suggestion_body": "def improved():\\n    pass",
        "comment_text": "Better implementation"
    }

    IMPORTANT: In JSON, use \\n for newlines, not actual line breaks!

    Returns:
        str: Success message

    Notes:
        - Line numbers are 1-indexed (first line is 1)
        - start_line and end_line can be the same for single-line suggestions
        - suggestion_body should NOT include markdown code fences
        - Automatically retries if pending review conflict detected
    """

    try:
        LOGGER.info(
            f"Attempting to post suggestion to repo: {repo_full_name}, PR: {pr_number}, "
            f"file: {file_path}, lines: {start_line}-{end_line}"
        )
        current_user_login = g.get_user().login

        try:
            repo = g.get_repo(repo_full_name)
        except Exception as repo_error:
            LOGGER.error(f"Failed to access repository '{repo_full_name}': {repo_error}")
            LOGGER.error("Make sure the repository name is in format 'owner/repo' and exists")
            raise ValueError(
                f"Repository '{repo_full_name}' not found. "
                f"Check the repository name format (should be 'owner/repo'). Error: {repo_error}"
            ) from repo_error

        pr = repo.get_pull(pr_number)
        latest_commit_sha = pr.head.sha

        formatted_suggestion = f"```suggestion\n{suggestion_body}\n```"

        # Validate file path
        LOGGER.info("PR review: validating file path")
        valid_paths = {pull_file.filename for pull_file in pr.get_files()}
        if file_path not in valid_paths:
            raise ValueError(
                f"File path '{file_path}' not found in PR #{pr_number}. " f"Available paths: {sorted(valid_paths)}"
            )

        # Prepare comment arguments
        comment_kwargs = {
            "body": f"{comment_text}\n{formatted_suggestion}",
            "commit": latest_commit_sha,
            "path": file_path,
            "line": int(end_line),
            "side": "RIGHT",
        }

        if start_line is not None and start_line != end_line:
            comment_kwargs.update(
                {
                    "start_line": int(start_line),
                    "start_side": "RIGHT",
                }
            )

        # Create retry condition for pending review conflicts
        retry_condition = _create_pending_review_retry_condition(pr, current_user_login)

        # Post comment with retry on pending review conflict
        @with_conditional_retry(
            condition_check=retry_condition,
            max_attempts=2,  # Original + 1 retry after cleanup
            backoff_base=1.0,  # No need for long backoff after cleanup
        )
        def _post_review_comment():
            """Inner function to post review comment with retry logic."""
            LOGGER.info("PR review: posting review commit suggestion")
            pr.create_review_comment(**comment_kwargs)

        # Execute with retry
        _post_review_comment()

        LOGGER.info("PR review: Successfully posted review commit suggestion")
        return f"Successfully posted suggestion for {file_path} in PR #{pr_number}"

    except Exception as e:
        LOGGER.error("PR review: Failed to post review commit suggestion")
        LOGGER.error(f"Error details: {type(e).__name__}: {e}", exc_info=True)
        raise


@observe
def get_pr_modified_files(repo_full_name, pr_number, g: Github = github_client_instance):
    """
    Fetches the list of modified files from a pull request.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number

    Example input: {"repo_full_name": "owner/repo", "pr_number": 123}

    Returns:
        Dict with "python_files" (list of .py filenames) and "total_files" count
    """
    LOGGER.info(f"Fetching modified files from PR #{pr_number} in {repo_full_name}")
    try:
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        files = pull_request.get_files()
        file_list = []
        for file in files:
            # Only include filename and status, NOT the patch (to save tokens)
            file_list.append(
                {
                    "filename": file.filename,
                    "status": getattr(file, "status", None),
                }
            )
        LOGGER.info(f"Found {len(file_list)} modified files in PR #{pr_number}")
        # Return just the filenames as a simple list to minimize tokens
        filenames = [f["filename"] for f in file_list if f["filename"] and f["filename"].endswith(".py")]
        return {"python_files": filenames, "total_files": len(file_list)}
    except Exception:
        LOGGER.error(f"Could not fetch modified files from PR #{pr_number}.", exc_info=True)
        return {"python_files": [], "total_files": 0}


@observe
def get_pr_file_content(repo_full_name, pr_number, file_path, g: Github = github_client_instance):
    """
    Fetches the content of a specific file from a PR's head commit.

    Args (provide as JSON):
        repo_full_name (str): Full repository name, e.g., 'owner/repo'
        pr_number (int): Pull request number
        file_path (str): Path to the file in the repository

    Example input: {"repo_full_name": "owner/repo", "pr_number": 123, "file_path": "src/main.py"}

    Returns:
        File content as string, or None if fetch fails
    """
    LOGGER.info(f"Fetching content for '{file_path}' from PR #{pr_number}")
    try:
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        contents = repo.get_contents(file_path, ref=pull_request.head.sha)
        content = contents.decoded_content.decode("utf-8")
        LOGGER.info(f"Successfully fetched {len(content)} bytes from '{file_path}'")
        return content
    except Exception:
        LOGGER.error(f"Could not fetch content for '{file_path}' from GitHub.", exc_info=True)
        return None


class GitHubPRClient:
    """Convenience wrapper that reuses a persistent Github client for PR utilities."""

    def __init__(self, github_client: Optional[Github] = None) -> None:
        """Initialize GitHubPRClient with an optional GitHub client.

        Args:
            github_client: Optional Github client instance. If None, uses the global instance.

        Example:
            >>> client = GitHubPRClient()
            >>> # Or with custom client:
            >>> custom_client = Github(auth=Auth.Token("custom_token"))
            >>> client = GitHubPRClient(custom_client)
        """
        self._client = github_client or github_client_instance

    @property
    def client(self) -> Github:
        """Expose the underlying Github client for advanced operations."""

        return self._client

    def post_suggestion_in_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        file_path: str,
        start_line: int,
        end_line: int,
        suggestion_body: str,
        comment_text: str,
    ) -> str:
        """Post a code suggestion as a review comment on a GitHub pull request.

        Wrapper method that uses the client instance to post suggestions.

        Args:
            repo_full_name: Full repository name, e.g., 'owner/repo'
            pr_number: Pull request number
            file_path: Path to the file in the repository
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            suggestion_body: The suggested code (plain text, no markdown)
            comment_text: Explanatory text for the suggestion

        Returns:
            Success message string

        Example:
            >>> client = GitHubPRClient()
            >>> result = client.post_suggestion_in_pr_review(
            ...     "owner/repo", 123, "src/main.py", 10, 12,
            ...     "improved code", "Better implementation"
            ... )
        """
        return post_suggestion_in_pr_review(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            suggestion_body=suggestion_body,
            comment_text=comment_text,
            g=self._client,
        )

    def get_pr_modified_files(self, repo_full_name: str, pr_number: int):
        """Fetch the list of modified files from a pull request.

        Args:
            repo_full_name: Full repository name, e.g., 'owner/repo'
            pr_number: Pull request number

        Returns:
            Dict with "python_files" (list of .py filenames) and "total_files" count

        Example:
            >>> client = GitHubPRClient()
            >>> files = client.get_pr_modified_files("owner/repo", 123)
            >>> print(f"Found {files['total_files']} files")
        """
        return get_pr_modified_files(repo_full_name=repo_full_name, pr_number=pr_number, g=self._client)

    def get_pr_file_content(self, repo_full_name: str, pr_number: int, file_path: str):
        """Fetch the content of a specific file from a PR's head commit.

        Args:
            repo_full_name: Full repository name, e.g., 'owner/repo'
            pr_number: Pull request number
            file_path: Path to the file in the repository

        Returns:
            File content as string, or None if fetch fails

        Example:
            >>> client = GitHubPRClient()
            >>> content = client.get_pr_file_content("owner/repo", 123, "src/main.py")
            >>> if content:
            ...     print(f"File has {len(content)} bytes")
        """
        return get_pr_file_content(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            file_path=file_path,
            g=self._client,
        )
