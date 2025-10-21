"""Standardized error handling for CLI commands.

This module provides centralized error handling with consistent formatting,
logging integration, and severity levels for all CLI operations.

Usage:
    from coffee_maker.cli.error_handler import handle_error, handle_success

    try:
        result = load_roadmap()
    except FileNotFoundError as e:
        return handle_error("view", "Roadmap file not found", exception=e)
    except Exception as e:
        return handle_error("view", f"Unexpected error: {e}", exception=e)

    return handle_success("view", "Roadmap displayed successfully")
"""

import logging
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


@dataclass
class ErrorContext:
    """Context information for error handling.

    Attributes:
        command: Command that failed (e.g., "view")
        message: User-facing error message
        exception: Original exception (if any)
        context: Additional context (args, environment, etc.)
        severity: Error severity level
        exit_code: Exit code for CLI
    """

    command: str
    message: str
    exception: Optional[Exception] = None
    context: Optional[dict] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    exit_code: int = 1


def handle_error(
    command: str,
    message: str,
    exception: Optional[Exception] = None,
    context: Optional[dict] = None,
    exit_program: bool = False,
) -> int:
    """Handle errors with consistent formatting and logging.

    Args:
        command: Command that encountered the error
        message: User-friendly error message
        exception: Original exception (if any)
        context: Additional context (args, environment, etc.)
        exit_program: If True, exit the program with error code

    Returns:
        Error exit code (1)

    Example:
        >>> handle_error("view", "Failed to load roadmap", exception=e)
        ❌ Error in 'view': Failed to load roadmap
        1
    """
    # Build user-facing message
    user_message = f"❌ Error in '{command}': {message}"
    print(user_message, file=sys.stderr)

    # Log detailed error
    log_message = f"Command '{command}' failed: {message}"
    if exception:
        logger.error(log_message, exc_info=exception)
    else:
        logger.error(log_message)

    # Log context if available
    if context:
        logger.debug(f"Error context: {context}")

    if exit_program:
        sys.exit(1)

    return 1


def handle_warning(
    command: str,
    message: str,
    context: Optional[dict] = None,
) -> int:
    """Handle warnings (non-critical issues).

    Args:
        command: Command that produced the warning
        message: Warning message
        context: Additional context

    Returns:
        Success exit code (0), warnings don't cause failure

    Example:
        >>> handle_warning("status", "Some metrics unavailable")
        ⚠️  Warning in 'status': Some metrics unavailable
        0
    """
    user_message = f"⚠️  Warning in '{command}': {message}"
    print(user_message, file=sys.stderr)

    logger.warning(f"Command '{command}': {message}")
    if context:
        logger.debug(f"Warning context: {context}")

    return 0  # Warnings don't cause failure


def handle_info(
    command: str,
    message: str,
) -> int:
    """Handle info messages (FYI, not errors).

    Args:
        command: Command that produced the info message
        message: Info message

    Returns:
        Success exit code (0)

    Example:
        >>> handle_info("view", "Showing last 100 lines")
        ℹ️  Info: Showing last 100 lines
        0
    """
    print(f"ℹ️  Info: {message}")
    logger.info(f"Command '{command}': {message}")
    return 0


def handle_success(
    command: str,
    message: str,
) -> int:
    """Handle success messages.

    Args:
        command: Command that completed successfully
        message: Success message

    Returns:
        Success exit code (0)

    Example:
        >>> handle_success("respond", "Notification approved")
        ✅ Success: Notification approved
        0
    """
    print(f"✅ Success: {message}")
    logger.info(f"Command '{command}': {message}")
    return 0
