"""File Ownership Registry for enforcing document ownership boundaries.

This module implements CFR-001 (Document Ownership Boundaries) by providing
a centralized registry that maps files and directories to their owning agents.

The registry uses glob patterns to match file paths and determine ownership,
ensuring that only the designated agent can modify specific files.

Architecture:
    FileOwnership: Static class with ownership rule matching
    OwnershipViolationError: Exception raised when ownership violated
    OwnershipUnclearError: Exception raised when ownership ambiguous

Usage:
    >>> from coffee_maker.autonomous.ace.file_ownership import FileOwnership
    >>> owner = FileOwnership.get_owner(".claude/CLAUDE.md")
    >>> print(owner)
    AgentType.CODE_DEVELOPER

Key Features:
    - Glob pattern matching for flexible ownership rules
    - Comprehensive ownership matrix from CRITICAL_FUNCTIONAL_REQUIREMENTS.md
    - Clear error messages for violations
    - Support for special cases and dual ownership scenarios
    - Caching for performance optimization

Integration:
    - Used by generator agent for ownership enforcement (US-038)
    - Prevents file conflicts (CFR-000 - MASTER REQUIREMENT)
    - Enables auto-delegation to correct owner
"""

import logging
from fnmatch import fnmatch

from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


class OwnershipViolationError(Exception):
    """Exception raised when an agent attempts to modify a file it doesn't own."""

    def __init__(self, agent: AgentType, file_path: str, owner: AgentType):
        self.agent = agent
        self.file_path = file_path
        self.owner = owner
        message = (
            f"Ownership Violation Detected!\n"
            f"\n"
            f"Agent '{agent.value}' attempted to modify:\n"
            f"  {file_path}\n"
            f"\n"
            f"Owner of this file:\n"
            f"  {owner.value}\n"
            f"\n"
            f"This violates CFR-001 (Document Ownership Boundaries).\n"
            f"\n"
            f"Action: generator will auto-delegate to {owner.value}\n"
        )
        super().__init__(message)


class OwnershipUnclearError(Exception):
    """Exception raised when file ownership cannot be determined."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        message = (
            f"Ownership Unclear!\n"
            f"\n"
            f"Cannot determine owner for:\n"
            f"  {file_path}\n"
            f"\n"
            f"This file/directory is not covered by ownership rules.\n"
            f"Please update CRITICAL_FUNCTIONAL_REQUIREMENTS.md and file_ownership.py.\n"
        )
        super().__init__(message)


class FileOwnership:
    """Registry mapping files and directories to their owning agents.

    This class implements CFR-001 (Document Ownership Boundaries) by providing
    a centralized ownership registry. It uses glob patterns to match file paths
    and determine which agent owns each file.

    The ownership rules are derived from docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md
    and ensure that EXACTLY ONE agent owns any given file.

    Class Attributes:
        OWNERSHIP_RULES: Dictionary mapping glob patterns to agent owners
        _ownership_cache: LRU cache for performance optimization

    Example:
        >>> owner = FileOwnership.get_owner("coffee_maker/cli/roadmap_cli.py")
        >>> print(owner)
        AgentType.CODE_DEVELOPER

        >>> owner = FileOwnership.get_owner("docs/roadmap/ROADMAP.md")
        >>> print(owner)
        AgentType.PROJECT_MANAGER
    """

    # Ownership rules based on CRITICAL_FUNCTIONAL_REQUIREMENTS.md CFR-001
    # Each pattern maps to EXACTLY ONE owning agent (CFR-003: No Overlap)
    OWNERSHIP_RULES = {
        # code_developer owns implementation and technical configurations
        ".claude/**": AgentType.CODE_DEVELOPER,
        ".claude/*": AgentType.CODE_DEVELOPER,
        ".claude/CLAUDE.md": AgentType.CODE_DEVELOPER,
        ".claude/agents/**": AgentType.CODE_DEVELOPER,
        ".claude/commands/**": AgentType.CODE_DEVELOPER,
        ".claude/mcp/**": AgentType.CODE_DEVELOPER,
        "coffee_maker/**": AgentType.CODE_DEVELOPER,
        "tests/**": AgentType.CODE_DEVELOPER,
        "scripts/**": AgentType.CODE_DEVELOPER,
        ".pre-commit-config.yaml": AgentType.CODE_DEVELOPER,
        # project_manager owns strategic documentation
        "docs/*.md": AgentType.PROJECT_MANAGER,  # Top-level docs only
        "docs/roadmap/**": AgentType.PROJECT_MANAGER,
        "docs/templates/**": AgentType.PROJECT_MANAGER,
        "docs/tutorials/**": AgentType.PROJECT_MANAGER,
        "docs/code-searcher/**": AgentType.PROJECT_MANAGER,
        "docs/user_interpret/**": AgentType.PROJECT_MANAGER,
        "docs/code_developer/**": AgentType.PROJECT_MANAGER,
        "docs/PRIORITY_*_STRATEGIC_SPEC.md": AgentType.PROJECT_MANAGER,
        # architect owns technical specifications and dependencies
        "docs/architecture/**": AgentType.ARCHITECT,
        "pyproject.toml": AgentType.ARCHITECT,
        "poetry.lock": AgentType.ARCHITECT,
        # ACE agents own their trace/insight directories
        "docs/generator/**": AgentType.GENERATOR,
        "docs/reflector/**": AgentType.REFLECTOR,
        "docs/curator/**": AgentType.CURATOR,
        # user_interpret owns operational data
        "data/user_interpret/**": AgentType.USER_LISTENER,
    }

    # Cache for performance optimization
    _ownership_cache: dict[str, AgentType] = {}

    @classmethod
    def get_owner(cls, file_path: str) -> AgentType:
        """Get the agent that owns the specified file.

        Args:
            file_path: Path to file (relative to project root)

        Returns:
            AgentType that owns this file

        Raises:
            OwnershipUnclearError: If ownership cannot be determined

        Example:
            >>> owner = FileOwnership.get_owner(".claude/CLAUDE.md")
            >>> print(owner)
            AgentType.CODE_DEVELOPER
        """
        # Check cache first for performance
        if file_path in cls._ownership_cache:
            return cls._ownership_cache[file_path]

        # Normalize path (remove leading ./ if present, but preserve leading dot in filenames)
        normalized_path = file_path
        if normalized_path.startswith("./"):
            normalized_path = normalized_path[2:]  # Remove only "./"

        # Try to match against ownership rules
        # More specific patterns are checked first (longer patterns)
        sorted_patterns = sorted(cls.OWNERSHIP_RULES.keys(), key=len, reverse=True)

        for pattern in sorted_patterns:
            if cls._matches_pattern(normalized_path, pattern):
                owner = cls.OWNERSHIP_RULES[pattern]
                # Cache the result
                cls._ownership_cache[file_path] = owner
                logger.debug(f"Ownership: {file_path} → {owner.value} (matched: {pattern})")
                return owner

        # No match found - ownership unclear
        raise OwnershipUnclearError(file_path)

    @classmethod
    @classmethod
    def _matches_pattern(cls, file_path: str, pattern: str) -> bool:
        """Check if file path matches glob pattern.

        Args:
            file_path: File path to check
            pattern: Glob pattern to match against

        Returns:
            True if path matches pattern, False otherwise

        Example:
            >>> FileOwnership._matches_pattern("coffee_maker/cli/test.py", "coffee_maker/**")
            True
        """
        return Path(file_path).match(pattern)

    @classmethod
    def check_ownership(cls, agent: AgentType, file_path: str, raise_on_violation: bool = False) -> bool:
        """Check if an agent owns the specified file.

        Args:
            agent: Agent attempting the operation
            file_path: Path to file being accessed
            raise_on_violation: If True, raise OwnershipViolationError on mismatch

        Returns:
            True if agent owns file, False otherwise

        Raises:
            OwnershipViolationError: If raise_on_violation=True and ownership violated

        Example:
            >>> FileOwnership.check_ownership(
            ...     AgentType.CODE_DEVELOPER,
            ...     ".claude/CLAUDE.md"
            ... )
            True
        """
        try:
            owner = cls.get_owner(file_path)
        except OwnershipUnclearError:
            # If ownership unclear, log warning and allow (fail open)
            logger.warning(f"Ownership unclear for {file_path}, allowing {agent.value} to proceed")
            return True

        is_owner = agent == owner

        if not is_owner and raise_on_violation:
            raise OwnershipViolationError(agent, file_path, owner)

        return is_owner

    @classmethod
    def get_allowed_paths(cls, agent: AgentType) -> list[str]:
        """Get list of path patterns that an agent owns.

        Args:
            agent: Agent to get allowed paths for

        Returns:
            List of glob patterns that agent owns

        Example:
            >>> paths = FileOwnership.get_allowed_paths(AgentType.CODE_DEVELOPER)
            >>> ".claude/**" in paths
            True
        """
        return [pattern for pattern, owner in cls.OWNERSHIP_RULES.items() if owner == agent]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the ownership cache.

        Useful for testing or after ownership rules change.

        Example:
            >>> FileOwnership.clear_cache()
        """
        cls._ownership_cache.clear()
        logger.debug("Ownership cache cleared")

    @classmethod
    def validate_rules(cls) -> bool:
        """Validate that ownership rules have no conflicts.

        Returns:
            True if rules are valid, False if conflicts detected

        Example:
            >>> FileOwnership.validate_rules()
            True
        """
        # Check for overlapping patterns that map to different owners
        patterns = list(cls.OWNERSHIP_RULES.keys())

        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i + 1 :]:
                # Check if patterns could overlap
                if cls._patterns_could_overlap(pattern1, pattern2):
                    owner1 = cls.OWNERSHIP_RULES[pattern1]
                    owner2 = cls.OWNERSHIP_RULES[pattern2]

                    if owner1 != owner2:
                        logger.error(
                            f"Ownership conflict: {pattern1} → {owner1.value}, " f"{pattern2} → {owner2.value}"
                        )
                        return False

        return True

    @classmethod
    def _patterns_could_overlap(cls, pattern1: str, pattern2: str) -> bool:
        """Check if two glob patterns could match the same file.

        Args:
            pattern1: First glob pattern
            pattern2: Second glob pattern

        Returns:
            True if patterns could overlap, False otherwise

        Example:
            >>> FileOwnership._patterns_could_overlap("docs/**", "docs/roadmap/**")
            True
        """
        # Simple heuristic: if one pattern is a prefix of the other
        if pattern1.startswith(pattern2.rstrip("*")) or pattern2.startswith(pattern1.rstrip("*")):
            return True

        return False
