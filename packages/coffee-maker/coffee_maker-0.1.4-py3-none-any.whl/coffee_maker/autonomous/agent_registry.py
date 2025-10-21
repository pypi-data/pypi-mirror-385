"""Agent Registry for singleton enforcement across autonomous agents.

This module provides a thread-safe registry that ensures only ONE instance of
each agent type can run at a time. This prevents:
- File corruption from concurrent writes
- Race conditions in daemon operations
- Duplicate work execution
- Resource conflicts

Architecture:
    AgentRegistry: Singleton class with thread-safe agent tracking
    AgentAlreadyRunningError: Exception raised when duplicate agent launch attempted
    AgentType: Enum of valid agent types

Usage:
    >>> from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType
    >>> registry = AgentRegistry()
    >>> registry.register_agent(AgentType.CODE_DEVELOPER)
    >>> # ... do work ...
    >>> registry.unregister_agent(AgentType.CODE_DEVELOPER)

Context Manager Pattern (Recommended):
    >>> with AgentRegistry.register(AgentType.CODE_DEVELOPER):
    ...     # Agent work here
    ...     pass  # Automatically unregistered on exit

Key Features:
    - Thread-safe locking using threading.Lock
    - Singleton pattern ensures single registry instance
    - Clear error messages for duplicate launches
    - Context manager for automatic cleanup
    - Process ID tracking for debugging
"""

import logging
import os
import threading
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of valid agent types in the system.

    The 8 autonomous agents that work together:
        ORCHESTRATOR (8) - Coordinates all other 7 agents
        ARCHITECT (1) - Creates technical specifications
        CODE_DEVELOPER (2) - Implements priorities from ROADMAP
        PROJECT_MANAGER (3) - Monitors GitHub, verifies DoD
        ASSISTANT (4) - Creates demos, reports bugs
        CODE_SEARCHER (5) - Deep code analysis
        UX_DESIGN_EXPERT (6) - Design guidance
        CODE_REVIEWER (7) - Quality assurance and code review

    Backend infrastructure:
        USER_LISTENER - Primary user interface
        GENERATOR - ACE framework (observes executions)
        REFLECTOR - ACE framework (extracts insights)
        CURATOR - ACE framework (maintains playbooks)
    """

    # Autonomous agents (8)
    ORCHESTRATOR = "orchestrator"  # 8th agent - launches and manages all others
    ARCHITECT = "architect"
    CODE_DEVELOPER = "code_developer"
    PROJECT_MANAGER = "project_manager"
    ASSISTANT = "assistant"
    CODE_SEARCHER = "code-searcher"
    UX_DESIGN_EXPERT = "ux-design-expert"
    CODE_REVIEWER = "code_reviewer"

    # Infrastructure
    USER_LISTENER = "user_listener"
    GENERATOR = "generator"
    REFLECTOR = "reflector"
    CURATOR = "curator"


class AgentAlreadyRunningError(Exception):
    """Exception raised when attempting to launch an agent that is already running."""

    def __init__(self, agent_type: AgentType, existing_pid: int, existing_started_at: str):
        self.agent_type = agent_type
        self.existing_pid = existing_pid
        self.existing_started_at = existing_started_at
        message = (
            f"Agent '{agent_type.value}' is already running!\n"
            f"  PID: {existing_pid}\n"
            f"  Started at: {existing_started_at}\n"
            f"\n"
            f"Only ONE instance of each agent type can run at a time.\n"
            f"Please stop the existing agent before starting a new one."
        )
        super().__init__(message)


class AgentRegistry:
    """Thread-safe singleton registry for tracking running agents.

    This class ensures that only ONE instance of each agent type can run at a time.
    It uses thread-safe locking to prevent race conditions and provides clear
    error messages when duplicate launches are attempted.

    Attributes:
        _instance: Singleton instance (class variable)
        _lock: Thread lock for thread-safe operations (class variable)
        _agents: Dictionary tracking active agents (instance variable)

    Example:
        >>> registry = AgentRegistry()
        >>> registry.register_agent(AgentType.CODE_DEVELOPER)
        >>> registry.is_registered(AgentType.CODE_DEVELOPER)
        True
        >>> registry.unregister_agent(AgentType.CODE_DEVELOPER)
    """

    _instance: Optional["AgentRegistry"] = None
    _lock = threading.Lock()  # Class-level lock for singleton creation

    def __new__(cls):
        """Singleton pattern to ensure only one registry exists.

        Uses double-checked locking for thread safety.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check inside lock
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the agent registry.

        Only initializes once (singleton pattern).
        """
        # Only initialize once (singleton pattern)
        if self._initialized:
            return

        # Instance-level lock for agent operations
        self._agent_lock = threading.Lock()

        # Track active agents: {AgentType: {pid, started_at}}
        self._agents: Dict[AgentType, Dict[str, any]] = {}

        self._initialized = True
        logger.info("AgentRegistry initialized (singleton)")

    def register_agent(self, agent_type: AgentType, pid: Optional[int] = None) -> None:
        """Register an agent as running.

        Args:
            agent_type: Type of agent to register
            pid: Process ID (defaults to current process)

        Raises:
            AgentAlreadyRunningError: If agent of this type is already running
            ValueError: If agent_type is not a valid AgentType

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register_agent(AgentType.CODE_DEVELOPER)
        """
        if not isinstance(agent_type, AgentType):
            raise ValueError(f"Invalid agent_type: {agent_type}. Must be an AgentType enum.")

        with self._agent_lock:
            # Check if agent is already registered
            if agent_type in self._agents:
                existing = self._agents[agent_type]
                raise AgentAlreadyRunningError(
                    agent_type=agent_type,
                    existing_pid=existing["pid"],
                    existing_started_at=existing["started_at"],
                )

            # Register the agent
            self._agents[agent_type] = {
                "pid": pid or os.getpid(),
                "started_at": datetime.now().isoformat(),
            }

            logger.info(f"Agent registered: {agent_type.value} (PID: {self._agents[agent_type]['pid']})")

    def unregister_agent(self, agent_type: AgentType) -> None:
        """Unregister an agent.

        Args:
            agent_type: Type of agent to unregister

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register_agent(AgentType.CODE_DEVELOPER)
            >>> registry.unregister_agent(AgentType.CODE_DEVELOPER)
        """
        if not isinstance(agent_type, AgentType):
            raise ValueError(f"Invalid agent_type: {agent_type}. Must be an AgentType enum.")

        with self._agent_lock:
            if agent_type in self._agents:
                pid = self._agents[agent_type]["pid"]
                del self._agents[agent_type]
                logger.info(f"Agent unregistered: {agent_type.value} (PID: {pid})")
            else:
                logger.warning(f"Attempted to unregister non-registered agent: {agent_type.value}")

    def is_registered(self, agent_type: AgentType) -> bool:
        """Check if an agent is currently registered.

        Args:
            agent_type: Type of agent to check

        Returns:
            True if agent is registered, False otherwise

        Example:
            >>> registry = AgentRegistry()
            >>> registry.is_registered(AgentType.CODE_DEVELOPER)
            False
        """
        if not isinstance(agent_type, AgentType):
            raise ValueError(f"Invalid agent_type: {agent_type}. Must be an AgentType enum.")

        with self._agent_lock:
            return agent_type in self._agents

    def get_agent_info(self, agent_type: AgentType) -> Optional[Dict[str, any]]:
        """Get information about a registered agent.

        Args:
            agent_type: Type of agent to query

        Returns:
            Dictionary with 'pid' and 'started_at' keys, or None if not registered

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register_agent(AgentType.CODE_DEVELOPER)
            >>> info = registry.get_agent_info(AgentType.CODE_DEVELOPER)
            >>> info['pid']
            12345
        """
        if not isinstance(agent_type, AgentType):
            raise ValueError(f"Invalid agent_type: {agent_type}. Must be an AgentType enum.")

        with self._agent_lock:
            return self._agents.get(agent_type)

    def get_all_registered_agents(self) -> Dict[AgentType, Dict[str, any]]:
        """Get information about all registered agents.

        Returns:
            Dictionary mapping AgentType to agent info

        Example:
            >>> registry = AgentRegistry()
            >>> all_agents = registry.get_all_registered_agents()
            >>> len(all_agents)
            0
        """
        with self._agent_lock:
            return dict(self._agents)  # Return copy for safety

    def reset(self) -> None:
        """Reset the registry (useful for testing).

        WARNING: This clears all registered agents. Use with caution.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.reset()  # Clear all agents
        """
        with self._agent_lock:
            self._agents.clear()
            logger.warning("AgentRegistry reset - all agents unregistered")

    @classmethod
    @contextmanager
    def register(cls, agent_type: AgentType, pid: Optional[int] = None):
        """Context manager for automatic agent registration/unregistration.

        This is the RECOMMENDED way to use the registry as it ensures
        proper cleanup even if exceptions occur.

        Args:
            agent_type: Type of agent to register
            pid: Process ID (defaults to current process)

        Yields:
            AgentRegistry instance

        Raises:
            AgentAlreadyRunningError: If agent is already running

        Example:
            >>> with AgentRegistry.register(AgentType.CODE_DEVELOPER):
            ...     # Do agent work here
            ...     pass  # Automatically unregistered on exit
        """
        registry = cls()
        registry.register_agent(agent_type, pid=pid)
        try:
            yield registry
        finally:
            registry.unregister_agent(agent_type)


# Convenience function for getting the singleton instance
def get_agent_registry() -> AgentRegistry:
    """Get the singleton AgentRegistry instance.

    Returns:
        AgentRegistry singleton instance

    Example:
        >>> registry = get_agent_registry()
        >>> registry.register_agent(AgentType.CODE_DEVELOPER)
    """
    return AgentRegistry()
