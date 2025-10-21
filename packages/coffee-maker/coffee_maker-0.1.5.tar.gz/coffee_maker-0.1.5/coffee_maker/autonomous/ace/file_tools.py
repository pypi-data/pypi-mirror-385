"""File Tools with Ownership Enforcement.

This module provides WriteTool and ReadTool classes that integrate with
the Generator for automatic ownership enforcement. These tools are designed
to be used by agents for file operations, with ownership checks transparently
handled by the Generator.

Architecture:
    WriteTool: Tool for write/edit/delete operations with ownership enforcement
    ReadTool: Tool for read operations (no ownership check needed)
    FileOperation: Base class for file operations

Integration with US-038:
    - WriteTool checks ownership before every write operation
    - Auto-delegates to correct owner if violation detected
    - ReadTool allows unrestricted access (read-only)
    - Generator intercepts all operations transparently

Usage:
    >>> from coffee_maker.autonomous.ace.file_tools import WriteTool, ReadTool
    >>> from coffee_maker.autonomous.agent_registry import AgentType
    >>>
    >>> # Create tools for an agent
    >>> write_tool = WriteTool(AgentType.CODE_DEVELOPER)
    >>> read_tool = ReadTool(AgentType.CODE_DEVELOPER)
    >>>
    >>> # Read any file (unrestricted)
    >>> content = read_tool.read_file(".claude/CLAUDE.md")
    >>>
    >>> # Write to owned file (allowed)
    >>> write_tool.write_file(".claude/CLAUDE.md", "# Updated")
    >>>
    >>> # Write to non-owned file (auto-delegated)
    >>> write_tool.write_file("docs/roadmap/ROADMAP.md", "# Updated")
    >>> # Automatically delegated to project_manager (owner)

Key Features:
    - Ownership enforcement at tool level (Layer 2)
    - Clear error messages for violations
    - Auto-delegation via Generator
    - Read operations always allowed
    - Type hints for better IDE support
    - Comprehensive docstrings
"""

import logging
from pathlib import Path
from typing import List, Optional

from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipViolationError,
)
from coffee_maker.autonomous.ace.generator import Generator, get_generator
from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


class WriteTool:
    """Write tool with ownership enforcement.

    This tool provides write/edit/delete file operations with automatic
    ownership checking via the Generator. If an agent attempts to write
    to a file it doesn't own, the operation is auto-delegated to the
    correct owner.

    Attributes:
        agent_type: Type of agent using this tool
        allowed_paths: Glob patterns this agent can write to
        generator: Generator instance for interception

    Example:
        >>> tool = WriteTool(AgentType.CODE_DEVELOPER)
        >>> tool.write_file("coffee_maker/test.py", "# code")  # Allowed
        >>> tool.write_file("docs/roadmap/ROADMAP.md", "# roadmap")  # Delegated to project_manager
    """

    def __init__(self, agent_type: AgentType, generator: Optional[Generator] = None):
        """Initialize WriteTool for an agent.

        Args:
            agent_type: Type of agent using this tool
            generator: Generator instance (optional, uses singleton if not provided)
        """
        self.agent_type = agent_type
        self.allowed_paths = FileOwnership.get_allowed_paths(agent_type)
        self.generator = generator or get_generator()
        logger.debug(f"WriteTool initialized for {agent_type.value}")

    def write_file(
        self,
        file_path: str,
        content: str,
        raise_on_violation: bool = False,
    ) -> bool:
        """Write content to a file with ownership enforcement.

        Args:
            file_path: Path to file to write
            content: Content to write
            raise_on_violation: If True, raise exception on violation (default: auto-delegate)

        Returns:
            True if write succeeded (including delegated writes), False on error

        Raises:
            OwnershipViolationError: If raise_on_violation=True and ownership violated

        Example:
            >>> tool = WriteTool(AgentType.PROJECT_MANAGER)
            >>> tool.write_file("docs/roadmap/ROADMAP.md", "# Updated")
            True
            >>> tool.write_file("coffee_maker/test.py", "# code")  # Delegated
            True
        """
        # Intercept operation via Generator
        result = self.generator.intercept_file_operation(
            agent_type=self.agent_type,
            file_path=file_path,
            operation="write",
            content=content,
        )

        # Check if delegated
        if result.delegated:
            if raise_on_violation:
                # Raise exception if requested
                owner = FileOwnership.get_owner(file_path)
                raise OwnershipViolationError(self.agent_type, file_path, owner)
            else:
                # Log delegation and continue
                logger.info(
                    f"Write delegated: {file_path} → {result.delegated_to.value} "
                    f"(requested by {self.agent_type.value})"
                )

        # In real implementation, this would actually write the file
        # For now, we just return success based on generator result
        return result.success

    def edit_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        raise_on_violation: bool = False,
    ) -> bool:
        """Edit content in a file with ownership enforcement.

        Args:
            file_path: Path to file to edit
            old_content: Content to replace
            new_content: New content
            raise_on_violation: If True, raise exception on violation

        Returns:
            True if edit succeeded, False on error

        Raises:
            OwnershipViolationError: If raise_on_violation=True and ownership violated

        Example:
            >>> tool = WriteTool(AgentType.CODE_DEVELOPER)
            >>> tool.edit_file("coffee_maker/test.py", "old", "new")
            True
        """
        # Intercept operation via Generator
        result = self.generator.intercept_file_operation(
            agent_type=self.agent_type,
            file_path=file_path,
            operation="edit",
            old_content=old_content,
            new_content=new_content,
        )

        # Check if delegated
        if result.delegated:
            if raise_on_violation:
                owner = FileOwnership.get_owner(file_path)
                raise OwnershipViolationError(self.agent_type, file_path, owner)
            else:
                logger.info(
                    f"Edit delegated: {file_path} → {result.delegated_to.value} "
                    f"(requested by {self.agent_type.value})"
                )

        return result.success

    def delete_file(
        self,
        file_path: str,
        raise_on_violation: bool = False,
    ) -> bool:
        """Delete a file with ownership enforcement.

        Args:
            file_path: Path to file to delete
            raise_on_violation: If True, raise exception on violation

        Returns:
            True if delete succeeded, False on error

        Raises:
            OwnershipViolationError: If raise_on_violation=True and ownership violated

        Example:
            >>> tool = WriteTool(AgentType.CODE_DEVELOPER)
            >>> tool.delete_file("coffee_maker/old_file.py")
            True
        """
        # Intercept operation via Generator
        result = self.generator.intercept_file_operation(
            agent_type=self.agent_type,
            file_path=file_path,
            operation="delete",
        )

        # Check if delegated
        if result.delegated:
            if raise_on_violation:
                owner = FileOwnership.get_owner(file_path)
                raise OwnershipViolationError(self.agent_type, file_path, owner)
            else:
                logger.info(
                    f"Delete delegated: {file_path} → {result.delegated_to.value} "
                    f"(requested by {self.agent_type.value})"
                )

        return result.success

    def get_allowed_paths(self) -> List[str]:
        """Get list of path patterns this agent can write to.

        Returns:
            List of glob patterns

        Example:
            >>> tool = WriteTool(AgentType.CODE_DEVELOPER)
            >>> paths = tool.get_allowed_paths()
            >>> ".claude/**" in paths
            True
        """
        return self.allowed_paths

    def can_write(self, file_path: str) -> bool:
        """Check if agent can write to a file without delegation.

        Args:
            file_path: Path to check

        Returns:
            True if agent owns file, False if would be delegated

        Example:
            >>> tool = WriteTool(AgentType.CODE_DEVELOPER)
            >>> tool.can_write(".claude/CLAUDE.md")
            True
            >>> tool.can_write("docs/roadmap/ROADMAP.md")
            False
        """
        return FileOwnership.check_ownership(self.agent_type, file_path)


class ReadTool:
    """Read tool - unrestricted for all agents.

    This tool provides read operations with no ownership restrictions.
    All agents can read any file in the project. The Generator allows
    read operations without checking ownership.

    Attributes:
        agent_type: Type of agent using this tool
        generator: Generator instance for interception (optional)

    Example:
        >>> tool = ReadTool(AgentType.ASSISTANT)
        >>> content = tool.read_file(".claude/CLAUDE.md")  # Always allowed
        >>> content = tool.read_file("coffee_maker/test.py")  # Always allowed
    """

    def __init__(self, agent_type: AgentType, generator: Optional[Generator] = None):
        """Initialize ReadTool for an agent.

        Args:
            agent_type: Type of agent using this tool
            generator: Generator instance (optional, uses singleton if not provided)
        """
        self.agent_type = agent_type
        self.generator = generator or get_generator()
        logger.debug(f"ReadTool initialized for {agent_type.value}")

    def read_file(self, file_path: str) -> Optional[str]:
        """Read content from a file.

        No ownership check is performed - all agents can read all files.

        Args:
            file_path: Path to file to read

        Returns:
            File content as string, or None if file not found

        Example:
            >>> tool = ReadTool(AgentType.ASSISTANT)
            >>> content = tool.read_file(".claude/CLAUDE.md")
            >>> print(content)
            "# MonolithicCoffeeMakerAgent - Claude Instructions..."
        """
        # Intercept via Generator (will allow read operations)
        result = self.generator.intercept_file_operation(
            agent_type=self.agent_type,
            file_path=file_path,
            operation="read",
        )

        if not result.success:
            logger.error(f"Read operation failed: {file_path}")
            return None

        # In real implementation, this would actually read the file
        # For now, we just return None (implementation needed)
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_text()
            return None
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise

        Example:
            >>> tool = ReadTool(AgentType.ASSISTANT)
            >>> tool.file_exists(".claude/CLAUDE.md")
            True
        """
        try:
            return Path(file_path).exists()
        except Exception as e:
            logger.error(f"Failed to check existence of {file_path}: {e}")
            return False

    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in a directory.

        Args:
            directory: Directory to list
            pattern: Glob pattern to filter files (default: "*")

        Returns:
            List of file paths matching pattern

        Example:
            >>> tool = ReadTool(AgentType.ASSISTANT)
            >>> files = tool.list_files("coffee_maker", "*.py")
            >>> len(files) > 0
            True
        """
        try:
            path = Path(directory)
            if not path.exists() or not path.is_dir():
                return []
            return [str(f) for f in path.glob(pattern)]
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return []


# Convenience functions for creating tools
def create_write_tool(agent_type: AgentType) -> WriteTool:
    """Create a WriteTool for an agent.

    Args:
        agent_type: Type of agent

    Returns:
        WriteTool instance

    Example:
        >>> tool = create_write_tool(AgentType.CODE_DEVELOPER)
        >>> tool.write_file("coffee_maker/test.py", "# code")
    """
    return WriteTool(agent_type)


def create_read_tool(agent_type: AgentType) -> ReadTool:
    """Create a ReadTool for an agent.

    Args:
        agent_type: Type of agent

    Returns:
        ReadTool instance

    Example:
        >>> tool = create_read_tool(AgentType.ASSISTANT)
        >>> content = tool.read_file(".claude/CLAUDE.md")
    """
    return ReadTool(agent_type)
