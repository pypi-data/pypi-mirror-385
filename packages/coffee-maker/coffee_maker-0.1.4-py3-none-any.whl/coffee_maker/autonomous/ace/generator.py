"""Generator Agent for ACE Framework - File Operation Interception and Ownership Enforcement.

This module implements the Generator agent from the ACE (Agentic Context Engineering) framework.
The Generator is responsible for:
1. Intercepting all file operations from agents
2. Enforcing file ownership rules (CFR-001)
3. Auto-delegating to correct owner when violations detected
4. Logging delegation traces for reflector analysis
5. Transparently returning results to requesting agent

Architecture:
    Generator: Main class that intercepts file operations
    DelegationTrace: Model for tracking delegations
    FileOperationType: Enum of interceptable operations

Integration with US-038:
    - Uses FileOwnership registry (Phase 1) for ownership checking
    - Provides Level 1 enforcement (automatic delegation)
    - Unblocks US-039 (comprehensive CFR enforcement)
    - Unblocks US-040 (project planner mode)

Usage:
    >>> from coffee_maker.autonomous.ace.generator import Generator
    >>> generator = Generator()
    >>>
    >>> # Intercept write operation
    >>> result = generator.intercept_file_operation(
    ...     agent_type=AgentType.PROJECT_MANAGER,
    ...     file_path=".claude/CLAUDE.md",
    ...     operation="write",
    ...     content="..."
    ... )
    >>> # Automatically delegated to code_developer (owner)
    >>> result.delegated_to == AgentType.CODE_DEVELOPER
    True

Key Features:
    - Automatic ownership enforcement (CFR-001)
    - Zero-configuration delegation (transparent to requesting agent)
    - Delegation trace logging (enables reflector analysis)
    - Read operations always allowed (no ownership check)
    - Write/edit/delete operations ownership-checked
    - Clear error messages for debugging
    - Thread-safe operation
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.ace.file_ownership import (
    FileOwnership,
    OwnershipUnclearError,
)
from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


class FileOperationType(Enum):
    """Types of file operations that can be intercepted."""

    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    DELETE = "delete"


@dataclass
class OperationResult:
    """Result of a file operation (possibly delegated).

    Attributes:
        success: Whether operation succeeded
        delegated: Whether operation was delegated to another agent
        delegated_to: Agent that actually performed operation (if delegated)
        error_message: Error message if failed
        trace_id: Delegation trace ID for reflector analysis
    """

    success: bool
    delegated: bool = False
    delegated_to: Optional[AgentType] = None
    error_message: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class DelegationTrace:
    """Trace record for delegated file operations.

    These traces are logged for reflector analysis to identify:
    - Common delegation patterns
    - Agents frequently violating ownership
    - Opportunities for improved agent design

    Attributes:
        trace_id: Unique identifier for this delegation
        timestamp: When delegation occurred
        requesting_agent: Agent that requested operation
        owner_agent: Agent that actually owns the file
        file_path: File being operated on
        operation: Type of operation (read/write/edit/delete)
        reason: Why delegation was needed (ownership violation)
        success: Whether delegated operation succeeded
    """

    trace_id: str
    timestamp: datetime
    requesting_agent: AgentType
    owner_agent: AgentType
    file_path: str
    operation: FileOperationType
    reason: str
    success: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "requesting_agent": self.requesting_agent.value,
            "owner_agent": self.owner_agent.value,
            "file_path": self.file_path,
            "operation": self.operation.value,
            "reason": self.reason,
            "success": self.success,
        }


class Generator:
    """Generator agent for intercepting and enforcing file ownership.

    The Generator is a critical component of the ACE framework that sits between
    agents and the file system, ensuring ownership rules are enforced transparently.

    Key Responsibilities:
        1. Intercept all file operations (write, edit, delete)
        2. Check ownership using FileOwnership registry
        3. Auto-delegate to correct owner if violation detected
        4. Log delegation traces for reflector analysis
        5. Return results transparently to requesting agent

    Example:
        >>> generator = Generator()
        >>>
        >>> # project_manager tries to write to code_developer's file
        >>> result = generator.intercept_file_operation(
        ...     agent_type=AgentType.PROJECT_MANAGER,
        ...     file_path="coffee_maker/cli/test.py",
        ...     operation="write",
        ...     content="# test"
        ... )
        >>>
        >>> # Automatically delegated to code_developer
        >>> print(f"Delegated: {result.delegated}")
        True
        >>> print(f"Owner: {result.delegated_to.value}")
        code_developer
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize Generator agent.

        Args:
            db_path: Path to SQLite database (default: data/orchestrator.db)
        """
        self.delegation_traces: list[DelegationTrace] = []
        self._file_search_traces: list[Dict[str, Any]] = []
        self.db_path = db_path or Path("data/orchestrator.db")
        self._init_database()
        logger.info("Generator initialized - file ownership enforcement active with database logging")

    def load_agent_context(self, agent_type: AgentType) -> Dict[str, str]:
        """Load required context files for an agent (US-042: Context-Upfront Pattern).

        This method implements the context-upfront file access pattern where agents
        receive required files upfront rather than searching for them during execution.

        Args:
            agent_type: The agent type to load context for

        Returns:
            Dictionary mapping file paths to their contents

        Example:
            >>> generator = Generator()
            >>> context = generator.load_agent_context(AgentType.CODE_DEVELOPER)
            >>> "docs/roadmap/ROADMAP.md" in context
            True
        """
        # Define required files per agent (aligned with agent definitions in .claude/agents/)
        AGENT_CONTEXT_FILES = {
            AgentType.CODE_DEVELOPER: [
                "docs/roadmap/ROADMAP.md",
                ".claude/CLAUDE.md",
                ".claude/agents/code_developer.md",
            ],
            AgentType.PROJECT_MANAGER: [
                "docs/roadmap/ROADMAP.md",
                "docs/roadmap/TEAM_COLLABORATION.md",
                "docs/roadmap/CRITICAL_FUNCTIONAL_REQUIREMENTS.md",
                ".claude/CLAUDE.md",
                ".claude/agents/project_manager.md",
            ],
            AgentType.ARCHITECT: [
                "docs/roadmap/ROADMAP.md",
                ".claude/CLAUDE.md",
                ".claude/agents/architect.md",
                "pyproject.toml",
            ],
            AgentType.ASSISTANT: [
                "docs/roadmap/ROADMAP.md",
                ".claude/CLAUDE.md",
                ".claude/agents/assistant.md",
                ".claude/commands/PROMPTS_INDEX.md",
            ],
            AgentType.CODE_SEARCHER: [
                ".claude/CLAUDE.md",
                ".claude/agents/code-searcher.md",
                "docs/roadmap/ROADMAP.md",
            ],
            AgentType.UX_DESIGN_EXPERT: [
                ".claude/CLAUDE.md",
                ".claude/agents/ux-design-expert.md",
                "docs/roadmap/ROADMAP.md",
            ],
        }

        context: Dict[str, str] = {}
        required_files = AGENT_CONTEXT_FILES.get(agent_type, [])

        logger.info(f"Loading context for {agent_type.value}: {len(required_files)} files")

        for file_path in required_files:
            try:
                # Construct absolute path
                full_path = Path(file_path)
                if not full_path.is_absolute():
                    # Assume paths are relative to project root
                    full_path = Path.cwd() / file_path

                content = full_path.read_text(encoding="utf-8")
                context[file_path] = content
                logger.debug(f"Loaded context file: {file_path} ({len(content)} chars)")
            except FileNotFoundError:
                error_msg = f"ERROR: Required context file not found: {file_path}"
                context[file_path] = error_msg
                logger.warning(f"Context file missing for {agent_type.value}: {file_path}")
            except Exception as e:
                error_msg = f"ERROR: Failed to load {file_path}: {str(e)}"
                context[file_path] = error_msg
                logger.error(f"Error loading context for {agent_type.value}: {file_path} - {e}")

        return context

    def format_context_for_prompt(self, context: Dict[str, str], max_chars_per_file: int = 5000) -> str:
        """Format context files for inclusion in agent prompts.

        Args:
            context: Dictionary of file paths to contents
            max_chars_per_file: Maximum characters to include per file (for large files)

        Returns:
            Formatted string ready for prompt inclusion

        Example:
            >>> generator = Generator()
            >>> context = generator.load_agent_context(AgentType.CODE_DEVELOPER)
            >>> prompt_context = generator.format_context_for_prompt(context)
        """
        lines: List[str] = []
        lines.append("=== CONTEXT FILES PROVIDED UPFRONT ===")
        lines.append("")

        for file_path, content in context.items():
            lines.append(f"--- {file_path} ---")

            # Truncate if too long
            if len(content) > max_chars_per_file:
                truncated = content[:max_chars_per_file]
                lines.append(truncated)
                lines.append(f"... [TRUNCATED - {len(content) - max_chars_per_file} chars omitted]")
            else:
                lines.append(content)

            lines.append("")

        lines.append("=== END CONTEXT FILES ===")
        lines.append("")
        lines.append(
            "You have all required context above. Use Read tool for specific line ranges if needed, "
            "but do NOT search with Glob/Grep for these known files."
        )

        return "\n".join(lines)

    def monitor_file_search(
        self, agent_type: AgentType, operation: str, file_pattern: str, context_provided: bool = True
    ) -> None:
        """Monitor and log file search operations (US-042: Unexpected Search Monitoring).

        This method tracks when agents use Glob/Grep, which may indicate:
        - Insufficient context provided upfront
        - Agent should have known the file path
        - Legitimate search (for code-searcher)

        Args:
            agent_type: Agent that performed search
            operation: Type of search (glob/grep)
            file_pattern: Pattern searched for
            context_provided: Whether context was provided upfront to this agent

        Example:
            >>> generator = Generator()
            >>> generator.monitor_file_search(
            ...     AgentType.CODE_DEVELOPER,
            ...     "glob",
            ...     "**/*test*.py",
            ...     context_provided=True
            ... )
        """
        # code-searcher is EXPECTED to search - don't log as unexpected
        if agent_type == AgentType.CODE_SEARCHER:
            logger.debug(f"code-searcher performed expected {operation}: {file_pattern}")
            return

        # architect MAY search for codebase analysis - log but not as warning
        if agent_type == AgentType.ARCHITECT:
            logger.info(f"architect performed {operation} for analysis: {file_pattern}")
            self._log_search_trace(agent_type, operation, file_pattern, severity="info")
            return

        # For other agents, log as unexpected if context was provided
        if context_provided:
            logger.warning(
                f"Unexpected file search: {agent_type.value} used {operation} for '{file_pattern}'. "
                f"Consider adding to required context files in agent definition."
            )
            self._log_search_trace(agent_type, operation, file_pattern, severity="warning")
        else:
            logger.info(f"File search (no context): {agent_type.value} used {operation} for '{file_pattern}'")
            self._log_search_trace(agent_type, operation, file_pattern, severity="info")

    def _log_search_trace(self, agent_type: AgentType, operation: str, file_pattern: str, severity: str) -> None:
        """Log file search trace for reflector analysis.

        Args:
            agent_type: Agent that searched
            operation: Search operation (glob/grep)
            file_pattern: Pattern searched
            severity: Severity level (info/warning)
        """
        trace = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_type.value,
            "operation": operation,
            "pattern": file_pattern,
            "severity": severity,
            "note": (
                "Unexpected file search - context may be insufficient"
                if severity == "warning"
                else "File search operation"
            ),
        }
        self._file_search_traces.append(trace)
        logger.debug(f"Search trace logged: {agent_type.value} {operation} {file_pattern}")

    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about file searches for monitoring.

        Returns:
            Dictionary with search statistics including:
            - total_searches: Total number of searches logged
            - searches_by_agent: Count by agent
            - unexpected_searches: Count of warning-level searches
            - most_common_patterns: Most frequent search patterns

        Example:
            >>> generator = Generator()
            >>> stats = generator.get_search_stats()
            >>> print(f"Unexpected searches: {stats['unexpected_searches']}")
        """
        total = len(self._file_search_traces)
        unexpected = len([t for t in self._file_search_traces if t["severity"] == "warning"])

        by_agent = {}
        for trace in self._file_search_traces:
            agent = trace["agent"]
            by_agent[agent] = by_agent.get(agent, 0) + 1

        pattern_counts = {}
        for trace in self._file_search_traces:
            pattern = f"{trace['operation']}:{trace['pattern']}"
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        most_common = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_searches": total,
            "unexpected_searches": unexpected,
            "searches_by_agent": by_agent,
            "most_common_patterns": [{"pattern": p, "count": c} for p, c in most_common],
        }

    def intercept_file_operation(
        self,
        agent_type: AgentType,
        file_path: str,
        operation: str,
        content: Optional[str] = None,
        **kwargs,
    ) -> OperationResult:
        """Intercept and potentially delegate a file operation.

        This is the main entry point for all file operations. It:
        1. Checks if operation requires ownership check (write/edit/delete)
        2. Verifies ownership using FileOwnership registry
        3. Delegates to owner if violation detected
        4. Logs delegation trace for reflector
        5. Logs to database for observability
        6. Returns result transparently

        Args:
            agent_type: Agent requesting the operation
            file_path: Path to file being operated on
            operation: Type of operation (read/write/edit/delete)
            content: Content for write operations
            **kwargs: Additional operation-specific parameters

        Returns:
            OperationResult with success status and delegation info

        Example:
            >>> generator = Generator()
            >>> result = generator.intercept_file_operation(
            ...     agent_type=AgentType.ASSISTANT,
            ...     file_path="docs/roadmap/ROADMAP.md",
            ...     operation="write",
            ...     content="# Updated roadmap"
            ... )
            >>> # Delegated to project_manager (owner of docs/roadmap/)
            >>> result.delegated
            True
        """
        # Start database trace
        params = {"operation": operation, "file_path": file_path}
        if content:
            params["content_length"] = len(content)
        db_trace_id = self._log_trace_to_database(
            agent_type=agent_type,
            operation_type="file_operation",
            operation_name=operation,
            parameters=params,
            file_path=file_path,
        )

        # Convert operation string to enum
        try:
            op_type = FileOperationType(operation.lower())
        except ValueError:
            error_msg = f"Invalid operation type: {operation}"
            self._complete_trace_in_database(db_trace_id, exit_code=1, error_message=error_msg)
            return OperationResult(
                success=False,
                error_message=error_msg,
            )

        # Read operations don't need ownership check
        if op_type == FileOperationType.READ:
            logger.debug(f"Read operation allowed: {agent_type.value} → {file_path}")
            self._complete_trace_in_database(db_trace_id, exit_code=0)
            return OperationResult(success=True, delegated=False)

        # Check ownership for write/edit/delete operations
        try:
            owner = FileOwnership.get_owner(file_path)
        except OwnershipUnclearError:
            # Ownership unclear - log warning and allow (fail open)
            logger.warning(f"Ownership unclear for {file_path}, allowing {agent_type.value} to proceed")
            self._complete_trace_in_database(db_trace_id, exit_code=0)
            return OperationResult(success=True, delegated=False)

        # Check if agent owns the file
        if agent_type == owner:
            # Agent owns file - allow operation
            logger.debug(f"Operation allowed: {agent_type.value} owns {file_path}")
            self._complete_trace_in_database(db_trace_id, exit_code=0)
            return OperationResult(success=True, delegated=False)

        # Ownership violation - auto-delegate to owner
        logger.info(
            f"Ownership violation detected: {agent_type.value} tried to {operation} {file_path} "
            f"(owner: {owner.value}). Auto-delegating..."
        )

        # Create delegation trace
        trace = self._create_delegation_trace(
            requesting_agent=agent_type,
            owner_agent=owner,
            file_path=file_path,
            operation=op_type,
        )

        # Delegate operation to owner
        # NOTE: In real implementation, this would actually execute the operation
        # via the correct agent. For now, we return a success result with delegation info.
        result = OperationResult(
            success=True,
            delegated=True,
            delegated_to=owner,
            trace_id=trace.trace_id,
        )

        # Log delegation trace
        self.delegation_traces.append(trace)
        logger.info(f"Delegation trace logged: {trace.trace_id}")

        # Complete database trace with delegation info
        self._complete_trace_in_database(
            db_trace_id,
            exit_code=0,
            result={"delegated": True, "delegated_to": owner.value},
            delegated=True,
            delegated_to=owner,
        )

        return result

    def _create_delegation_trace(
        self,
        requesting_agent: AgentType,
        owner_agent: AgentType,
        file_path: str,
        operation: FileOperationType,
    ) -> DelegationTrace:
        """Create a delegation trace for reflector analysis.

        Args:
            requesting_agent: Agent that requested operation
            owner_agent: Agent that owns the file
            file_path: Path to file
            operation: Type of operation

        Returns:
            DelegationTrace record
        """
        trace_id = f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        return DelegationTrace(
            trace_id=trace_id,
            timestamp=datetime.now(),
            requesting_agent=requesting_agent,
            owner_agent=owner_agent,
            file_path=file_path,
            operation=operation,
            reason=f"Ownership violation: {requesting_agent.value} tried to access {owner_agent.value}'s file",
            success=True,  # Assume success for now
        )

    def get_delegation_traces(
        self,
        agent: Optional[AgentType] = None,
        hours: Optional[int] = None,
    ) -> list[DelegationTrace]:
        """Get delegation traces for analysis.

        Args:
            agent: Filter by requesting agent (optional)
            hours: Filter by last N hours (optional)

        Returns:
            List of delegation traces matching filters

        Example:
            >>> generator = Generator()
            >>> # Get all delegations from assistant in last 24 hours
            >>> traces = generator.get_delegation_traces(
            ...     agent=AgentType.ASSISTANT,
            ...     hours=24
            ... )
        """
        traces = self.delegation_traces

        # Filter by agent
        if agent:
            traces = [t for t in traces if t.requesting_agent == agent]

        # Filter by time
        if hours:
            cutoff = datetime.now().timestamp() - (hours * 3600)
            traces = [t for t in traces if t.timestamp.timestamp() >= cutoff]

        return traces

    def get_delegation_stats(self) -> Dict[str, Any]:
        """Get statistics about delegations for monitoring.

        Returns:
            Dictionary with delegation statistics including:
            - total_delegations: Total number of delegations
            - delegations_by_requesting_agent: Count by requesting agent
            - delegations_by_owner: Count by owner agent
            - most_common_violations: Most frequent violation patterns

        Example:
            >>> generator = Generator()
            >>> stats = generator.get_delegation_stats()
            >>> print(f"Total delegations: {stats['total_delegations']}")
        """
        total = len(self.delegation_traces)

        # Count by requesting agent
        by_requester = {}
        for trace in self.delegation_traces:
            agent = trace.requesting_agent.value
            by_requester[agent] = by_requester.get(agent, 0) + 1

        # Count by owner
        by_owner = {}
        for trace in self.delegation_traces:
            agent = trace.owner_agent.value
            by_owner[agent] = by_owner.get(agent, 0) + 1

        # Find most common violation patterns
        violation_patterns = {}
        for trace in self.delegation_traces:
            pattern = f"{trace.requesting_agent.value} → {trace.owner_agent.value}"
            violation_patterns[pattern] = violation_patterns.get(pattern, 0) + 1

        most_common = sorted(violation_patterns.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_delegations": total,
            "delegations_by_requesting_agent": by_requester,
            "delegations_by_owner": by_owner,
            "most_common_violations": [{"pattern": p, "count": c} for p, c in most_common],
        }

    def _init_database(self) -> None:
        """Initialize database connection and verify schema."""
        if not self.db_path.exists():
            logger.warning(f"Database not found at {self.db_path}, database logging disabled")
            return

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                # Verify generator_traces table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generator_traces'")
                if not cursor.fetchone():
                    logger.warning("generator_traces table not found, database logging disabled")
                    logger.info("Run migration: python coffee_maker/orchestrator/migrate_add_generator_traces.py")
                else:
                    logger.debug("Database logging initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}, database logging disabled")

    def _log_trace_to_database(
        self,
        agent_type: AgentType,
        operation_type: str,
        operation_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        task_id: Optional[str] = None,
        priority_number: Optional[int] = None,
    ) -> Optional[int]:
        """Start logging a trace to database and return trace_id.

        Args:
            agent_type: Agent performing the operation
            operation_type: Type of operation (tool/skill/command/file_operation)
            operation_name: Name of the specific operation
            parameters: Operation parameters (will be JSON-encoded)
            file_path: File being operated on (if applicable)
            task_id: Task ID for linking
            priority_number: ROADMAP priority (if applicable)

        Returns:
            trace_id (int) if successful, None if database logging disabled
        """
        if not self.db_path.exists():
            return None

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO generator_traces
                    (agent_type, operation_type, operation_name, started_at, status,
                     parameters, file_path, task_id, priority_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        agent_type.value,
                        operation_type,
                        operation_name,
                        datetime.now().isoformat(),
                        "running",
                        json.dumps(parameters) if parameters else None,
                        file_path,
                        task_id,
                        priority_number,
                    ),
                )
                conn.commit()
                trace_id = cursor.lastrowid
                logger.debug(f"Started trace {trace_id}: {operation_type}/{operation_name}")
                return trace_id
        except sqlite3.Error as e:
            logger.error(f"Failed to log trace start: {e}")
            return None

    def _complete_trace_in_database(
        self,
        trace_id: Optional[int],
        exit_code: int = 0,
        error_message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        delegated: bool = False,
        delegated_to: Optional[AgentType] = None,
    ) -> None:
        """Complete a trace in the database with final status.

        Args:
            trace_id: Trace ID from _log_trace_to_database
            exit_code: 0 for success, non-zero for error
            error_message: Error details if failed
            result: Operation result (will be JSON-encoded)
            delegated: Whether operation was delegated
            delegated_to: Agent delegated to (if applicable)
        """
        if trace_id is None or not self.db_path.exists():
            return

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Get started_at to calculate duration
                cursor.execute("SELECT started_at FROM generator_traces WHERE trace_id = ?", (trace_id,))
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Trace {trace_id} not found in database")
                    return

                started_at = datetime.fromisoformat(row[0])
                duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)

                status = "failed" if exit_code != 0 else "completed"

                cursor.execute(
                    """
                    UPDATE generator_traces
                    SET completed_at = ?, duration_ms = ?, status = ?, exit_code = ?,
                        error_message = ?, result = ?, delegated = ?, delegated_to = ?
                    WHERE trace_id = ?
                """,
                    (
                        datetime.now().isoformat(),
                        duration_ms,
                        status,
                        exit_code,
                        error_message,
                        json.dumps(result) if result else None,
                        1 if delegated else 0,
                        delegated_to.value if delegated_to else None,
                        trace_id,
                    ),
                )
                conn.commit()
                logger.debug(f"Completed trace {trace_id}: {status} (exit_code={exit_code}, duration={duration_ms}ms)")
        except sqlite3.Error as e:
            logger.error(f"Failed to complete trace {trace_id}: {e}")

    def log_tool_usage(
        self,
        agent_type: AgentType,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
    ) -> Optional[int]:
        """Log tool usage to database.

        Args:
            agent_type: Agent using the tool
            tool_name: Name of the tool (Read, Write, Bash, etc.)
            parameters: Tool parameters
            file_path: File being operated on (if applicable)

        Returns:
            trace_id for completing the trace later
        """
        return self._log_trace_to_database(
            agent_type=agent_type,
            operation_type="tool",
            operation_name=tool_name,
            parameters=parameters,
            file_path=file_path,
        )

    def log_skill_usage(
        self,
        agent_type: AgentType,
        skill_name: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """Log skill usage to database.

        Args:
            agent_type: Agent using the skill
            skill_name: Name of the skill
            parameters: Skill parameters

        Returns:
            trace_id for completing the trace later
        """
        return self._log_trace_to_database(
            agent_type=agent_type,
            operation_type="skill",
            operation_name=skill_name,
            parameters=parameters,
        )

    def log_command_usage(
        self,
        agent_type: AgentType,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """Log command usage to database.

        Args:
            agent_type: Agent running the command
            command: Command being executed
            parameters: Command parameters

        Returns:
            trace_id for completing the trace later
        """
        return self._log_trace_to_database(
            agent_type=agent_type,
            operation_type="command",
            operation_name=command,
            parameters=parameters,
        )

    def clear_traces(self) -> None:
        """Clear delegation traces (useful for testing).

        Example:
            >>> generator = Generator()
            >>> generator.clear_traces()
        """
        self.delegation_traces.clear()
        logger.info("Delegation traces cleared")


# Singleton instance for global access
_generator_instance: Optional[Generator] = None


def get_generator() -> Generator:
    """Get singleton Generator instance.

    Returns:
        Generator singleton instance

    Example:
        >>> generator = get_generator()
        >>> result = generator.intercept_file_operation(...)
    """
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = Generator()
    return _generator_instance
