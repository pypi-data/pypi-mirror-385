"""Base agent class for all autonomous agents.

This module provides common infrastructure that ALL agents must have:
- CFR-013 enforcement (roadmap branch only)
- CFR-012 interruption handling (urgent requests first)
- Status file writing (heartbeat every iteration)
- Message queue management (inbox for inter-agent delegation)
- Git operations with branch validation

All agents inherit from BaseAgent and implement:
- _do_background_work(): Main continuous work loop
- _handle_message(msg): Process inter-agent messages

Related:
    SPEC-057: Technical specification for multi-agent orchestrator
    CFR-000: File ownership matrix (prevent conflicts)
    CFR-012: Agent responsiveness priority (interrupt handling)
    CFR-013: All agents on roadmap branch only
    US-035: Agent singleton enforcement

Architecture:
    BaseAgent (Abstract)
    ├── _run_continuous(): Main loop with CFR-012 interruption
    ├── _enforce_cfr_013(): Validate roadmap branch
    ├── _check_inbox_urgent(): Check for urgent messages (CFR-012)
    ├── _check_inbox(): Check for regular messages
    ├── _write_status(): Write heartbeat and status
    ├── commit_changes(): Git commit with agent identification
    └── Abstract methods (implemented by subclasses)
        ├── _do_background_work(): Agent-specific continuous tasks
        └── _handle_message(): Process inter-agent delegation

Message Priority System (CFR-012):
    1. Urgent messages (urgent_*.json files) - HIGHEST PRIORITY
       - Spec requests from code_developer
       - Bug fix requests
       - Critical blocking issues
    2. Regular messages (*.json files) - NORMAL PRIORITY
       - Demo requests
       - Analysis requests
       - Information sharing

Interrupt Handling Pattern:
    while running:
        # CFR-012: Check urgent messages FIRST
        urgent_msg = _check_inbox_urgent()
        if urgent_msg:
            _handle_message(urgent_msg)
            continue  # Skip background work this iteration

        # Regular priority
        messages = _check_inbox()
        for msg in messages:
            _handle_message(msg)

        # Background work
        _do_background_work()

        # Status heartbeat
        _write_status()

        # Sleep
        sleep(check_interval)
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.git_manager import GitManager

logger = logging.getLogger(__name__)


class CFR013ViolationError(Exception):
    """Exception raised when CFR-013 is violated (not on roadmap branch)."""


class BaseAgent(ABC):
    """Abstract base class for all autonomous agents.

    This class provides common infrastructure that ALL agents must have:
    - CFR-013 enforcement (roadmap branch only)
    - CFR-012 interruption handling (urgent requests first)
    - Status file writing (heartbeat every 30 seconds)
    - Message queue management (inbox for inter-agent delegation)
    - Git operations with branch validation

    All agents inherit from this base and implement:
    - _do_background_work(): Main continuous work loop
    - _handle_message(msg): Process inter-agent messages

    Attributes:
        agent_type: Type of this agent (from AgentType enum)
        status_dir: Directory for status files
        message_dir: Directory for message queues
        check_interval: Seconds between background work checks
        git: GitManager instance for git operations
        status_file: Path to this agent's status file
        inbox_dir: Path to this agent's message inbox

    Example:
        >>> class MyAgent(BaseAgent):
        ...     def _do_background_work(self):
        ...         print("My background work here")
        ...
        ...     def _handle_message(self, message):
        ...         print(f"Handling message: {message}")
        ...
        >>> agent = MyAgent(
        ...     agent_type=AgentType.ARCHITECT,
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=3600
        ... )
        >>> agent.run_continuous()  # Runs until stopped
    """

    def __init__(
        self,
        agent_type: AgentType,
        status_dir: Path,
        message_dir: Path,
        check_interval: int,
    ):
        """Initialize base agent.

        Args:
            agent_type: Type of this agent (from AgentType enum)
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between background work checks

        Raises:
            CFR013ViolationError: If not on roadmap branch (CFR-013)
        """
        self.agent_type = agent_type
        self.status_dir = Path(status_dir)
        self.message_dir = Path(message_dir)
        self.check_interval = check_interval

        # Git manager for CFR-013 enforcement
        self.git = GitManager()

        # Status tracking
        self.status_file = self.status_dir / f"{agent_type.value}_status.json"
        self.current_task: Optional[Dict[str, Any]] = None
        self.metrics: Dict[str, Any] = {}

        # Message queue
        self.inbox_dir = self.message_dir / f"{agent_type.value}_inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # State
        self.running = False
        self.last_heartbeat: Optional[datetime] = None

        logger.info(f"✅ {agent_type.value} initialized")

    def run_continuous(self):
        """Main continuous work loop with CFR-012 interruption handling.

        This method implements the core agent execution pattern:

        1. CFR-013: Validate we're on roadmap branch
        2. Continuous loop while running:
            a. CFR-012: Check for urgent messages (PRIORITY 1)
               - User requests via user_listener
               - Inter-agent delegation messages
            b. Check for regular messages (PRIORITY 2)
            c. Execute agent-specific background work
            d. Write status (heartbeat)
            e. Sleep before next iteration

        CFR-012 ensures urgent messages interrupt background work.
        CFR-013 ensures all operations on roadmap branch.

        Runs indefinitely until:
            - KeyboardInterrupt (Ctrl+C)
            - Exception in background work (logged and continues)
        """
        self.running = True
        logger.info(f"🤖 {self.agent_type.value} starting continuous loop...")

        # CFR-013: Validate we're on roadmap branch
        self._enforce_cfr_013()

        while self.running:
            try:
                # CFR-012: Check for urgent messages FIRST
                urgent_message = self._check_inbox_urgent()
                if urgent_message:
                    logger.info(f"🚨 {self.agent_type.value} interrupted by urgent message")
                    self._handle_message(urgent_message)
                    continue  # Skip background work this iteration

                # Normal priority: Check for regular messages
                messages = self._check_inbox()
                for message in messages:
                    self._handle_message(message)

                # Background work (agent-specific)
                self._do_background_work()

                # Write status (heartbeat)
                self._write_status()

                # Sleep before next iteration (in small chunks to remain responsive)
                # Split long sleep into 30-second chunks to:
                # 1. Update heartbeat frequently
                # 2. Check for urgent messages during sleep
                # 3. Remain responsive even with long check_intervals (1 hour, 24 hours)
                self._responsive_sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info(f"\n⏹️  {self.agent_type.value} stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ {self.agent_type.value} error: {e}")
                import traceback

                traceback.print_exc()

                # Write error status
                self._write_status(error=str(e))

                # Sleep before retry
                time.sleep(60)

        logger.info(f"🛑 {self.agent_type.value} stopped")

        # Update status to show stopped (don't delete - keep for debugging)
        self._write_status_stopped()

    def _enforce_cfr_013(self):
        """Ensure agent is on roadmap branch (CFR-013).

        CFR-013 requires ALL agents to work ONLY on the 'roadmap' branch.
        This ensures:
        - Single source of truth for all work
        - No merge conflicts between agents
        - All work immediately visible to team

        Raises:
            CFR013ViolationError: If not on roadmap branch
        """
        current_branch = self.git.get_current_branch()

        if current_branch != "roadmap":
            error_msg = (
                f"❌ CFR-013 VIOLATION: {self.agent_type.value} not on roadmap branch!\n\n"
                f"Current branch: {current_branch}\n"
                f"Required branch: roadmap\n\n"
                f"ALL agents MUST work on roadmap branch only.\n"
                f"This ensures single source of truth and no conflicts.\n\n"
                f"To fix:\n"
                f"  1. git checkout roadmap\n"
                f"  2. git pull origin roadmap\n"
                f"  3. Restart agent"
            )
            raise CFR013ViolationError(error_msg)

    def _responsive_sleep(self, total_seconds: int):
        """Sleep in small chunks while remaining responsive to messages.

        Instead of sleeping for the entire check_interval at once (which can be
        1 hour or 24 hours), split the sleep into 30-second chunks. During each
        chunk, we:
        1. Check for urgent messages (can interrupt sleep early)
        2. Update heartbeat (prevents "stale heartbeat" warnings)
        3. Remain responsive to user signals (Ctrl+C)

        This solves the "stale heartbeat" problem where agents with long
        check_intervals (architect=1h, code-searcher=24h) don't update their
        status for hours, causing monitoring systems to report them as unhealthy.

        Args:
            total_seconds: Total time to sleep (in seconds)

        Returns:
            None (may return early if urgent message received)
        """
        HEARTBEAT_INTERVAL = 30  # Update heartbeat every 30 seconds
        elapsed = 0

        while elapsed < total_seconds and self.running:
            # Sleep for the smaller of: remaining time or heartbeat interval
            sleep_time = min(HEARTBEAT_INTERVAL, total_seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time

            # Check for urgent messages during sleep (can interrupt)
            urgent_message = self._check_inbox_urgent()
            if urgent_message:
                logger.info(f"🚨 {self.agent_type.value} interrupted during sleep by urgent message")
                self._handle_message(urgent_message)
                # Exit sleep early to handle urgent message
                break

            # Update heartbeat to show we're alive
            self._write_status()

    def _check_inbox_urgent(self) -> Optional[Dict]:
        """Check inbox for URGENT messages only (CFR-012 Priority 1).

        Urgent messages are files named urgent_*.json in the inbox.
        These represent high-priority requests that should interrupt
        background work:
        - Spec requests from code_developer (blocking work)
        - Bug fix requests
        - Critical user requests

        Returns:
            Urgent message dict if found, None otherwise

        Side effects:
            - Removes message file after reading (one-time processing)
        """
        for msg_file in self.inbox_dir.glob("urgent_*.json"):
            try:
                message = json.loads(msg_file.read_text())
                msg_file.unlink()  # Remove after reading
                logger.info(f"📨 Urgent message received: {message.get('type', 'unknown')}")
                return message
            except Exception as e:
                logger.error(f"Error reading urgent message {msg_file}: {e}")

        return None

    def _check_inbox(self) -> List[Dict]:
        """Check inbox for regular messages.

        Regular messages are files named *.json in the inbox (excluding urgent_*.json).
        These represent normal-priority requests:
        - Demo requests
        - Analysis requests
        - Information sharing

        Returns:
            List of message dictionaries

        Side effects:
            - Removes message files after reading (one-time processing)
        """
        messages = []

        for msg_file in self.inbox_dir.glob("*.json"):
            # Skip urgent messages (handled by _check_inbox_urgent)
            if msg_file.name.startswith("urgent_"):
                continue

            try:
                message = json.loads(msg_file.read_text())
                messages.append(message)
                msg_file.unlink()  # Remove after reading
            except Exception as e:
                logger.error(f"Error reading message {msg_file}: {e}")

        return messages

    def _read_messages(self, type_filter: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Read messages from MessageQueue (SQLite-based).

        This method provides a unified interface for agents to read messages
        from the orchestrator's message queue system. It filters by recipient
        (this agent) and optionally by message type.

        Args:
            type_filter: Optional message type to filter by
            limit: Maximum number of messages to read (default: 10)

        Returns:
            List of message dictionaries

        Example:
            >>> messages = self._read_messages(type_filter="commit_review_request")
            >>> for msg in messages:
            ...     self._handle_message(msg)
        """
        from coffee_maker.autonomous.message_queue import MessageQueue

        messages = []
        queue = MessageQueue()

        try:
            # Read up to 'limit' messages for this agent
            for _ in range(limit):
                message = queue.get(recipient=self.agent_type.value, timeout=0.1)

                if message is None:
                    break  # No more messages

                # Filter by type if requested
                if type_filter and message.type != type_filter:
                    continue

                # Convert Message object to dict for compatibility
                message_dict = {
                    "type": message.type,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "payload": message.payload,
                    "priority": message.priority,
                    "task_id": message.task_id,
                    "timestamp": message.timestamp,
                }

                messages.append(message_dict)

                # Mark message as started (will be marked complete after handling)
                queue.mark_started(message.task_id, agent=self.agent_type.value)

        except Exception as e:
            logger.error(f"Error reading messages from queue: {e}")

        return messages

    def _write_status(self, error: Optional[str] = None):
        """Write status file with current state (heartbeat).

        Status file is written every iteration to track:
        - Agent state (idle, working, error)
        - Current task and progress
        - Heartbeat timestamp
        - Health metrics
        - Error information if any

        The status file is used by:
        - Orchestrator for health monitoring
        - Project_manager for status dashboard
        - Other agents for coordination

        Args:
            error: Optional error message if agent encountered error
        """
        status = {
            "agent_type": self.agent_type.value,
            "state": ("error" if error else ("working" if self.current_task else "idle")),
            "current_task": self.current_task,
            "last_heartbeat": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(seconds=self.check_interval)).isoformat(),
            "health": "unhealthy" if error else "healthy",
            "pid": os.getpid(),
            "metrics": self.metrics,
            "error": error,
        }

        try:
            self.status_file.write_text(json.dumps(status, indent=2))
            self.last_heartbeat = datetime.now()
        except Exception as e:
            logger.error(f"Error writing status: {e}")

    def _write_status_stopped(self):
        """Update status file to show agent stopped.

        This keeps the status file for debugging (especially crash info)
        but marks it as stopped so activity_summary can distinguish between
        running agents and stopped/crashed agents.

        Called automatically when agent stops (normal exit or KeyboardInterrupt).
        """
        status = {
            "agent_type": self.agent_type.value,
            "state": "stopped",
            "current_task": self.current_task,
            "last_heartbeat": datetime.now().isoformat(),
            "stopped_at": datetime.now().isoformat(),
            "health": "stopped",
            "pid": os.getpid(),
            "metrics": self.metrics,
            "error": None,
        }

        try:
            self.status_file.write_text(json.dumps(status, indent=2))
            logger.info(f"✅ Updated status to 'stopped': {self.status_file}")
        except Exception as e:
            logger.error(f"Error updating stopped status: {e}")

    def commit_changes(self, message: str, files: Optional[List[str]] = None):
        """Commit changes with agent identification.

        All commits from agents include:
        - Main message (what was done and why)
        - Agent identification (who made the change)
        - Generated with Claude Code footer

        This enables:
        - Traceability of all changes
        - Quick identification of what agent did what
        - Audit trail of autonomous work

        Args:
            message: Main commit message (what and why)
            files: Optional list of specific files to commit
                   (default: all changes via git add .)

        Example:
            >>> agent.commit_changes(
            ...     "feat: Implement PRIORITY 5 - Dashboard"
            ... )

        Raises:
            CFR013ViolationError: If branch changed (CFR-013)
        """
        # CFR-013: Ensure still on roadmap branch before commit
        self._enforce_cfr_013()

        # Agent identification in commit message
        full_message = (
            f"{message}\n\n"
            f"🤖 Agent: {self.agent_type.value}\n"
            f"🤖 Generated with Claude Code\n\n"
            f"Co-Authored-By: Claude <noreply@anthropic.com>"
        )

        # Commit changes
        if files:
            for file_path in files:
                self.git.add(file_path)
        else:
            self.git.add_all()

        self.git.commit(full_message)

        # Push to roadmap branch
        self.git.push("roadmap")

        logger.info(f"✅ {self.agent_type.value} committed: {message}")

    def send_message_to_agent(
        self,
        to_agent: AgentType,
        message_type: str,
        content: Dict,
        priority: str = "normal",
    ):
        """Send inter-agent message to another agent's inbox.

        Messages enable coordination between agents:
        - code_developer → architect: "Please create spec for priority X"
        - code_developer → assistant: "Feature X complete, please demo"
        - assistant → project_manager: "Bug found in feature X"

        Args:
            to_agent: Recipient agent type
            message_type: Type of message (spec_request, demo_request, etc.)
            content: Message payload (dict)
            priority: "urgent" or "normal" (affects how agent processes it)

        Example:
            >>> agent.send_message_to_agent(
            ...     to_agent=AgentType.ARCHITECT,
            ...     message_type="spec_request",
            ...     content={"priority_name": "US-060"},
            ...     priority="urgent"
            ... )
        """
        message = {
            "message_id": f"{message_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "from": self.agent_type.value,
            "to": to_agent.value,
            "type": message_type,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "content": content,
        }

        # Write to recipient's inbox
        recipient_inbox = self.message_dir / f"{to_agent.value}_inbox"
        recipient_inbox.mkdir(parents=True, exist_ok=True)

        if priority == "urgent":
            msg_file = recipient_inbox / f"urgent_{message['message_id']}.json"
        else:
            msg_file = recipient_inbox / f"{message['message_id']}.json"

        try:
            msg_file.write_text(json.dumps(message, indent=2))
            logger.info(f"📨 Sent {priority} message to {to_agent.value}: {message_type}")
        except Exception as e:
            logger.error(f"Error sending message to {to_agent.value}: {e}")

    @abstractmethod
    def _do_background_work(self):
        """Perform agent-specific background work.

        This method is called once per iteration and should implement
        the agent's continuous work loop logic.

        Subclasses MUST implement this method.

        Example implementations:

        ArchitectAgent:
            - Check ROADMAP for spec coverage
            - Create missing specs proactively
            - Read code-searcher reports
            - Analyze codebase for refactoring

        CodeDeveloperAgent:
            - Check ROADMAP for next priority
            - Implement if spec exists
            - Run tests
            - Commit changes

        ProjectManagerAgent:
            - Check GitHub for PRs and issues
            - Monitor ROADMAP health
            - Verify DoD when requested
            - Generate status reports

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _do_background_work()")

    @abstractmethod
    def _handle_message(self, message: Dict):
        """Handle inter-agent delegation message.

        Args:
            message: Message dictionary with:
                - from: Sending agent type
                - to: This agent (recipient)
                - type: Message type (spec_request, demo_request, etc.)
                - priority: "urgent" or "normal"
                - content: Message-specific payload

        Subclasses MUST implement this method to handle delegation.

        Example implementations:

        ArchitectAgent:
            if message.type == "spec_request":
                # Urgent request from code_developer
                # Create spec immediately

        CodeDeveloperAgent:
            if message.type == "bug_fix_request":
                # Bug found during demo
                # Fix the bug immediately

        ProjectManagerAgent:
            if message.type == "bug_report":
                # Bug found by assistant
                # Add to ROADMAP and notify user

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _handle_message()")
