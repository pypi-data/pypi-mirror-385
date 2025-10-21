"""ACE (Agentic Context Engineering) Framework.

This package implements the ACE framework for autonomous agent learning and improvement.
The framework consists of three core components:

1. Generator: Dual execution observation and trace capture
2. Reflector: Insight extraction from traces
3. Curator: Playbook maintenance and semantic de-duplication

Key Features:
    - File ownership enforcement (CFR-001)
    - Auto-delegation to correct owner
    - Delegation trace logging
    - WriteTool and ReadTool for agents
    - Integration with FileOwnership registry

Usage:
    >>> from coffee_maker.autonomous.ace import Generator, WriteTool, ReadTool
    >>> from coffee_maker.autonomous.agent_registry import AgentType
    >>>
    >>> # Create tools for an agent
    >>> write_tool = WriteTool(AgentType.CODE_DEVELOPER)
    >>> read_tool = ReadTool(AgentType.CODE_DEVELOPER)
    >>>
    >>> # Read any file
    >>> content = read_tool.read_file(".claude/CLAUDE.md")
    >>>
    >>> # Write to owned file
    >>> write_tool.write_file("coffee_maker/test.py", "# code")

Reference:
    https://www.arxiv.org/abs/2510.04618
"""

from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipUnclearError,
    OwnershipViolationError,
)
from coffee_maker.autonomous.ace.file_tools import (
    ReadTool,
    WriteTool,
    create_read_tool,
    create_write_tool,
)
from coffee_maker.autonomous.ace.generator import (
    DelegationTrace,
    FileOperationType,
    Generator,
    OperationResult,
    get_generator,
)

__all__ = [
    # File Ownership
    "FileOwnership",
    "OwnershipViolationError",
    "OwnershipUnclearError",
    # Generator
    "Generator",
    "get_generator",
    "OperationResult",
    "DelegationTrace",
    "FileOperationType",
    # File Tools
    "WriteTool",
    "ReadTool",
    "create_write_tool",
    "create_read_tool",
]
