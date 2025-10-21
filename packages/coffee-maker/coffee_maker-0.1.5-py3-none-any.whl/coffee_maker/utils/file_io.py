"""File I/O utilities for consistent JSON operations.

This module provides utilities for reading and writing JSON files with:
- Consistent error handling
- Standard encoding (UTF-8)
- Atomic writes to prevent corruption
- Optional schema validation
- Default value support

Example:
    >>> from coffee_maker.utils.file_io import read_json_file, write_json_file
    >>> data = read_json_file("status.json", default={})
    >>> data["status"] = "running"
    >>> write_json_file("status.json", data)
"""

import json
import logging
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class FileOperationError(Exception):
    """File read/write operation errors."""


def read_json_file(file_path: Path | str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Read JSON file with consistent error handling and encoding.

    Reads a JSON file and returns its contents as a dictionary. If the file
    doesn't exist or can't be parsed, returns the default value (if provided)
    or raises an error.

    Args:
        file_path: Path to the JSON file to read
        default: Default value to return if file doesn't exist or is invalid.
                If None, errors are raised instead.

    Returns:
        Dictionary containing the JSON data, or default if provided and file not found

    Raises:
        FileOperationError: If file can't be read and no default provided
        json.JSONDecodeError: If file contains invalid JSON and no default provided

    Example:
        >>> # With default value
        >>> data = read_json_file("config.json", default={"enabled": False})
        >>> print(data["enabled"])
        >>>
        >>> # Raise error if file doesn't exist
        >>> try:
        ...     data = read_json_file("required.json")
        ... except FileOperationError:
        ...     print("Required file missing!")
    """
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            logger.debug(f"File {file_path} not found, using default value")
            return default
        raise FileOperationError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        if default is not None:
            logger.warning(f"Invalid JSON in {file_path}, using default value. Error: {e}")
            return default
        raise FileOperationError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        if default is not None:
            logger.error(f"Error reading {file_path}, using default value. Error: {e}")
            return default
        raise FileOperationError(f"Error reading {file_path}: {e}")


def write_json_file(file_path: Path | str, data: Dict[str, Any], indent: int = 2) -> None:
    """Write JSON file with consistent formatting and error handling.

    Writes data to a JSON file with standard formatting (UTF-8 encoding,
    specified indentation). Creates parent directories if they don't exist.

    Args:
        file_path: Path to the JSON file to write
        data: Dictionary to write as JSON
        indent: Number of spaces for indentation (default: 2)

    Raises:
        FileOperationError: If file can't be written

    Example:
        >>> data = {"status": "running", "pid": 12345}
        >>> write_json_file("status.json", data)
        >>> # File is written with 2-space indentation
        >>>
        >>> # Custom indentation
        >>> write_json_file("config.json", data, indent=4)
    """
    file_path = Path(file_path)

    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        logger.debug(f"Successfully wrote JSON to {file_path}")
    except Exception as e:
        raise FileOperationError(f"Error writing to {file_path}: {e}")


def atomic_write_json(file_path: Path | str, data: Dict[str, Any], indent: int = 2) -> None:
    """Write JSON file atomically to prevent corruption.

    Writes data to a temporary file first, then atomically renames it to the
    target path. This prevents file corruption if the write is interrupted
    (e.g., by system crash, KeyboardInterrupt).

    Args:
        file_path: Path to the JSON file to write
        data: Dictionary to write as JSON
        indent: Number of spaces for indentation (default: 2)

    Raises:
        FileOperationError: If file can't be written

    Example:
        >>> # Critical data that must not be corrupted
        >>> status = {"pid": 12345, "status": "running", "timestamp": time.time()}
        >>> atomic_write_json("daemon_status.json", status)
        >>> # File is written atomically - either fully written or not at all
    """
    file_path = Path(file_path)

    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file in same directory (for atomic rename)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=file_path.parent, delete=False, suffix=".tmp"
        ) as tmp_file:
            json.dump(data, tmp_file, indent=indent, ensure_ascii=False)
            tmp_path = Path(tmp_file.name)

        # Atomic rename (works on all platforms)
        tmp_path.replace(file_path)

        logger.debug(f"Successfully wrote JSON atomically to {file_path}")
    except Exception as e:
        # Clean up temporary file if it exists
        if "tmp_path" in locals():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise FileOperationError(f"Error writing atomically to {file_path}: {e}")


def read_text_file(file_path: Path | str, default: Optional[str] = None) -> str:
    """Read text file with consistent error handling and encoding.

    Args:
        file_path: Path to the text file to read
        default: Default value to return if file doesn't exist.
                If None, errors are raised instead.

    Returns:
        File content as string, or default if provided and file not found

    Raises:
        FileOperationError: If file can't be read and no default provided

    Example:
        >>> content = read_text_file("README.md")
        >>> print(len(content))
        >>>
        >>> # With default
        >>> content = read_text_file("optional.txt", default="")
    """
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        if default is not None:
            logger.debug(f"File {file_path} not found, using default value")
            return default
        raise FileOperationError(f"File not found: {file_path}")
    except Exception as e:
        if default is not None:
            logger.error(f"Error reading {file_path}, using default value. Error: {e}")
            return default
        raise FileOperationError(f"Error reading {file_path}: {e}")


def write_text_file(file_path: Path | str, content: str) -> None:
    """Write text file with consistent error handling and encoding.

    Args:
        file_path: Path to the text file to write
        content: String content to write

    Raises:
        FileOperationError: If file can't be written

    Example:
        >>> write_text_file("output.txt", "Hello, World!")
        >>> # File is written with UTF-8 encoding
    """
    file_path = Path(file_path)

    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.debug(f"Successfully wrote text to {file_path}")
    except Exception as e:
        raise FileOperationError(f"Error writing to {file_path}: {e}")


def ensure_directory(directory: Path | str) -> None:
    """Ensure directory exists, creating it if necessary.

    Args:
        directory: Path to the directory

    Raises:
        FileOperationError: If directory can't be created

    Example:
        >>> ensure_directory("data/logs")
        >>> # Directory and parents are created if they don't exist
    """
    directory = Path(directory)

    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        raise FileOperationError(f"Error creating directory {directory}: {e}")


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug format.

    Converts text to lowercase, replaces spaces and special characters with
    hyphens, and removes consecutive hyphens.

    Args:
        text: Text to convert to slug

    Returns:
        Slugified text (lowercase, hyphen-separated, no special chars)

    Example:
        >>> slugify("Claude Skills Integration")
        'claude-skills-integration'
        >>> slugify("US-050: Architect POC Creation")
        'us-050-architect-poc-creation'
        >>> slugify("Multi-Agent   System!!!")
        'multi-agent-system'
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove special characters (keep alphanumeric and hyphens)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug
