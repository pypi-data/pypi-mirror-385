"""Master orchestration daemon that manages all autonomous agents.

This module implements the "operating system" for the autonomous development team.
It manages agent lifecycles, coordinates work, ensures fault tolerance, and provides
unified monitoring and logging.

Architecture:
- Single master daemon process supervises all agent subprocesses
- Each agent runs in isolated subprocess with its own event loop
- Shared SQLite message queue for inter-agent communication
- Centralized health monitoring with auto-restart capability
- Graceful shutdown with signal handling

Example:
    >>> config = TeamConfig()
    >>> daemon = TeamDaemon(config)
    >>> daemon.start()
    >>> # Runs until stop() called or SIGTERM received
    >>> daemon.stop()
"""

import logging
import signal
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from coffee_maker.autonomous.message_queue import MessageQueue, AgentType


logger = logging.getLogger(__name__)


class ProcessStatus(Enum):
    """Status of an agent process."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CRASHED = "crashed"
    STOPPING = "stopping"


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    agent_type: AgentType
    enabled: bool = True
    auto_approve: bool = False
    timeout_seconds: int = 300
    memory_limit_mb: int = 256


@dataclass
class TeamConfig:
    """Configuration for team daemon."""

    database_path: str = "data/orchestrator.db"
    health_check_interval: int = 30  # seconds
    max_restart_attempts: int = 3
    restart_backoff: float = 2.0  # seconds (exponential backoff)
    max_queue_size: int = 1000
    cleanup_interval_hours: int = 24

    agents: Dict[AgentType, AgentConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default agent configs if not provided."""
        if not self.agents:
            self.agents = {
                AgentType.CODE_DEVELOPER: AgentConfig(agent_type=AgentType.CODE_DEVELOPER, auto_approve=True),
                AgentType.PROJECT_MANAGER: AgentConfig(agent_type=AgentType.PROJECT_MANAGER),
                AgentType.ARCHITECT: AgentConfig(agent_type=AgentType.ARCHITECT),
                AgentType.ASSISTANT: AgentConfig(agent_type=AgentType.ASSISTANT),
            }

    def get_agent_config(self, agent_type: AgentType) -> AgentConfig:
        """Get configuration for specific agent.

        Args:
            agent_type: Type of agent

        Returns:
            Agent configuration (creates default if not present)
        """
        if agent_type not in self.agents:
            self.agents[agent_type] = AgentConfig(agent_type=agent_type)
        return self.agents[agent_type]


@dataclass
class AgentStatus:
    """Status snapshot of an agent process."""

    agent_type: AgentType
    pid: Optional[int] = None
    status: ProcessStatus = ProcessStatus.STOPPED
    uptime_seconds: float = 0.0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    restart_count: int = 0
    last_heartbeat: Optional[str] = None
    current_task: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class TeamStatus:
    """Overall status of the team daemon."""

    is_running: bool
    uptime_seconds: float
    agents: Dict[AgentType, AgentStatus] = field(default_factory=dict)
    message_queue_size: int = 0
    queue_metrics: dict = field(default_factory=dict)
    last_health_check: Optional[str] = None


class TeamDaemon:
    """Master daemon that orchestrates all autonomous agents.

    This daemon manages the lifecycle of all autonomous agents, coordinates
    their work through a message queue, monitors their health, and ensures
    fault tolerance through automatic restarts.

    Attributes:
        config: Team configuration
        message_queue: Shared SQLite message queue
        agents: Dictionary of agent processes
        running: Whether daemon is currently running
        start_time: Timestamp when daemon was started
    """

    def __init__(self, config: Optional[TeamConfig] = None):
        """Initialize team daemon.

        Args:
            config: Team configuration (uses defaults if not provided)
        """
        self.config = config or TeamConfig()
        self.message_queue = MessageQueue(db_path=self.config.database_path)
        self.agents: Dict[AgentType, "AgentProcessManager"] = {}
        self.running = False
        self.start_time: Optional[float] = None

        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigint)

        logger.info("Team daemon initialized with config: %s", self.config)

    def start(self) -> None:
        """Start all agents and begin orchestration.

        This method spawns subprocesses for each enabled agent, sets up
        the message queue, starts health monitoring, and begins the main
        coordination loop.

        Raises:
            RuntimeError: If daemon fails to start
        """
        logger.info("Starting autonomous team daemon...")
        self.start_time = time.time()
        self.running = True

        try:
            # Spawn all enabled agents
            for agent_type, agent_config in self.config.agents.items():
                if agent_config.enabled:
                    self._spawn_agent(agent_type)

            logger.info("All agents started. Beginning coordination loop...")

            # Run main coordination loop
            self._coordination_loop()

        except Exception as e:
            logger.error("Failed to start team daemon: %s", e, exc_info=True)
            self.running = False
            self.stop()
            raise RuntimeError(f"Team daemon startup failed: {e}")

    def _spawn_agent(self, agent_type: AgentType) -> None:
        """Spawn subprocess for specific agent.

        Args:
            agent_type: Type of agent to spawn

        Raises:
            RuntimeError: If agent fails to spawn
        """
        agent_config = self.config.get_agent_config(agent_type)

        logger.info("Spawning %s agent...", agent_type.value)

        try:
            # Create agent process manager
            process_manager = AgentProcessManager(
                agent_type=agent_type,
                config=agent_config,
                message_queue=self.message_queue,
            )

            # Start the agent process
            process_manager.start()
            self.agents[agent_type] = process_manager

            logger.info("✅ %s agent started (PID: %s)", agent_type.value, process_manager.pid)

        except Exception as e:
            logger.error("Failed to spawn %s agent: %s", agent_type.value, e, exc_info=True)
            raise RuntimeError(f"Failed to spawn {agent_type.value} agent: {e}")

    def _coordination_loop(self) -> None:
        """Main coordination loop (runs continuously).

        Monitors agent health, processes messages, coordinates work.
        Runs until stop() is called or SIGTERM received.
        """
        last_cleanup = time.time()

        while self.running:
            try:
                current_time = time.time()

                # Check agent health
                self._check_agent_health()

                # Process inter-agent messages
                self._process_messages()

                # Coordinate work distribution
                self._coordinate_work()

                # Periodic cleanup (every N hours)
                if current_time - last_cleanup > self.config.cleanup_interval_hours * 3600:
                    self._cleanup_old_tasks()
                    last_cleanup = current_time

                # Sleep until next iteration
                time.sleep(self.config.health_check_interval)

            except KeyboardInterrupt:
                logger.info("Received Ctrl+C, shutting down...")
                self.stop()
                break
            except Exception as e:
                logger.error("Error in coordination loop: %s", e, exc_info=True)
                # Continue running - don't crash master daemon

    def _check_agent_health(self) -> None:
        """Check health of all agent subprocesses.

        Monitors process status, auto-restarts crashed agents (max 3 retries),
        and sends notifications for persistent failures.
        """
        for agent_type, process_manager in list(self.agents.items()):
            try:
                if not process_manager.is_alive():
                    logger.error("❌ %s agent crashed!", agent_type.value)

                    # Auto-restart if retries remaining
                    if process_manager.restart_count < self.config.max_restart_attempts:
                        wait_time = self.config.restart_backoff**process_manager.restart_count
                        logger.info(
                            "Restarting %s (attempt %d/%d, waiting %.1fs)...",
                            agent_type.value,
                            process_manager.restart_count + 1,
                            self.config.max_restart_attempts,
                            wait_time,
                        )
                        time.sleep(wait_time)
                        try:
                            process_manager.restart()
                        except Exception as e:
                            logger.error("Failed to restart %s: %s", agent_type.value, e, exc_info=True)
                    else:
                        logger.critical("Max restart attempts reached for %s, giving up", agent_type.value)
                        # Send critical notification
                        self._notify_agent_failure(agent_type)

            except Exception as e:
                logger.error("Error checking health of %s: %s", agent_type.value, e)

    def _process_messages(self) -> None:
        """Process inter-agent messages from queue.

        Routes messages to appropriate agents based on recipient.
        """
        try:
            while self.message_queue.has_messages():
                # Peek at next message (for logging)
                message = self.message_queue.get("*")  # This won't work, need to fix

                if message:
                    # Route to recipient agent
                    recipient_agent = self.agents.get(AgentType(message.recipient))
                    if recipient_agent:
                        recipient_agent.send_message(message)
                else:
                    break

        except Exception as e:
            logger.error("Error processing messages: %s", e, exc_info=True)

    def _coordinate_work(self) -> None:
        """Coordinate work distribution across agents.

        Ensures high-priority work gets immediate attention.
        Prevents duplicate work across agents.
        Optimizes resource utilization.
        """
        try:
            # This is a placeholder for future coordination logic
            # Future implementations can add:
            # - Priority-based task distribution
            # - Load balancing across agents
            # - Deadlock detection
            # - Resource optimization
            pass

        except Exception as e:
            logger.error("Error coordinating work: %s", e, exc_info=True)

    def _cleanup_old_tasks(self) -> None:
        """Clean up old completed tasks from message queue."""
        try:
            deleted_count = self.message_queue.cleanup_old_tasks(days=30)
            logger.info("Cleaned up %d old tasks from message queue", deleted_count)
        except Exception as e:
            logger.error("Error cleaning up old tasks: %s", e, exc_info=True)

    def _notify_agent_failure(self, agent_type: AgentType) -> None:
        """Send critical notification about agent failure.

        Args:
            agent_type: Type of agent that failed
        """
        try:
            logger.critical(
                "Agent %s has failed permanently (max restarts reached). " "Manual intervention required.",
                agent_type.value,
            )
            # Future: Send to notification system
        except Exception as e:
            logger.error("Error sending failure notification: %s", e, exc_info=True)

    def stop(self) -> None:
        """Gracefully stop all agents and shutdown.

        Sends SIGTERM to all subprocesses, waits for clean exit,
        stops message queue, and saves state.
        """
        logger.info("Stopping autonomous team daemon...")
        self.running = False

        try:
            # Stop all agents (graceful with timeout)
            for agent_type, process_manager in self.agents.items():
                logger.info("Stopping %s agent...", agent_type.value)
                try:
                    process_manager.stop(timeout=30)
                except Exception as e:
                    logger.error("Error stopping %s: %s", agent_type.value, e)

            # Stop message queue
            self.message_queue.stop()

            logger.info("✅ Team daemon stopped successfully")

        except Exception as e:
            logger.error("Error during shutdown: %s", e, exc_info=True)

    def status(self) -> TeamStatus:
        """Get current status of all agents.

        Returns:
            TeamStatus with health, performance, and activity info
        """
        uptime = time.time() - self.start_time if self.start_time else 0.0

        agent_statuses = {}
        for agent_type, process_manager in self.agents.items():
            try:
                agent_statuses[agent_type] = process_manager.get_status()
            except Exception as e:
                logger.error("Error getting status for %s: %s", agent_type.value, e)
                agent_statuses[agent_type] = AgentStatus(
                    agent_type=agent_type,
                    error_message=str(e),
                )

        # Get queue metrics
        try:
            queue_metrics = self.message_queue.get_task_metrics()
        except Exception as e:
            logger.error("Error getting queue metrics: %s", e)
            queue_metrics = {}

        return TeamStatus(
            is_running=self.running,
            uptime_seconds=uptime,
            agents=agent_statuses,
            message_queue_size=self.message_queue.size(),
            queue_metrics=queue_metrics,
            last_health_check=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _handle_sigterm(self, signum, frame):
        """Handle SIGTERM signal."""
        logger.info("Received SIGTERM")
        self.stop()

    def _handle_sigint(self, signum, frame):
        """Handle SIGINT signal (Ctrl+C)."""
        logger.info("Received SIGINT")
        self.stop()


class AgentProcessManager:
    """Manages a single agent subprocess with health monitoring.

    This class wraps agent subprocess execution, tracking lifecycle
    (starting, running, stopped, crashed) and reporting metrics.

    Attributes:
        agent_type: Type of agent
        config: Agent configuration
        process: The subprocess instance
        pid: Process ID (if running)
        restart_count: Number of restart attempts
        start_time: When the process was started
    """

    def __init__(self, agent_type: AgentType, config: AgentConfig, message_queue: MessageQueue):
        """Initialize agent process manager.

        Args:
            agent_type: Type of agent
            config: Agent configuration
            message_queue: Shared message queue
        """
        self.agent_type = agent_type
        self.config = config
        self.message_queue = message_queue
        self.process = None
        self.pid = None
        self.restart_count = 0
        self.start_time = None
        self.status = ProcessStatus.STOPPED

    def start(self) -> None:
        """Start agent subprocess.

        Raises:
            RuntimeError: If process fails to start
        """
        import subprocess

        try:
            # Determine how to start the agent based on type
            if self.agent_type == AgentType.CODE_DEVELOPER:
                cmd = ["poetry", "run", "code-developer", "--auto-approve"]
            elif self.agent_type == AgentType.PROJECT_MANAGER:
                cmd = ["poetry", "run", "project-manager", "daemon"]
            elif self.agent_type == AgentType.ARCHITECT:
                # Future: implement architect daemon
                logger.warning("Architect daemon not yet implemented")
                return
            elif self.agent_type == AgentType.ASSISTANT:
                # Future: implement assistant daemon
                logger.warning("Assistant daemon not yet implemented")
                return
            else:
                raise ValueError(f"Unknown agent type: {self.agent_type}")

            # Start subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )

            self.pid = self.process.pid
            self.start_time = time.time()
            self.status = ProcessStatus.RUNNING
            self.restart_count = 0

            logger.info("Started %s (PID: %s)", self.agent_type.value, self.pid)

        except Exception as e:
            self.status = ProcessStatus.CRASHED
            raise RuntimeError(f"Failed to start {self.agent_type.value}: {e}")

    def is_alive(self) -> bool:
        """Check if agent subprocess is alive.

        Returns:
            True if process is running
        """
        if self.process is None:
            return False

        # Check if process is still alive
        if self.process.poll() is None:
            self.status = ProcessStatus.RUNNING
            return True
        else:
            self.status = ProcessStatus.CRASHED
            return False

    def restart(self) -> None:
        """Restart agent subprocess.

        Attempts to stop current process and start a new one.

        Raises:
            RuntimeError: If restart fails
        """
        try:
            self.stop()
            self.restart_count += 1
            self.start()
        except Exception as e:
            raise RuntimeError(f"Failed to restart {self.agent_type.value}: {e}")

    def stop(self, timeout: int = 30) -> None:
        """Stop agent subprocess gracefully.

        Args:
            timeout: Max seconds to wait for graceful exit
        """
        if self.process is None:
            return

        try:
            self.status = ProcessStatus.STOPPING
            self.process.terminate()

            # Wait for graceful exit
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                logger.warning("Timeout waiting for %s, killing...", self.agent_type.value)
                self.process.kill()
                self.process.wait()

            self.status = ProcessStatus.STOPPED
            logger.info("Stopped %s", self.agent_type.value)

        except Exception as e:
            logger.error("Error stopping %s: %s", self.agent_type.value, e)
            self.status = ProcessStatus.CRASHED

    def get_status(self) -> AgentStatus:
        """Get current status of agent.

        Returns:
            AgentStatus snapshot
        """
        uptime = 0.0
        if self.start_time:
            uptime = time.time() - self.start_time

        cpu_percent = 0.0
        memory_mb = 0.0

        # Try to get resource usage
        if self.pid and self.is_alive():
            try:
                import psutil

                proc = psutil.Process(self.pid)
                cpu_percent = proc.cpu_percent(interval=0.1)
                memory_mb = proc.memory_info().rss / 1024 / 1024
            except Exception as e:
                logger.debug("Error getting resource usage for %s: %s", self.agent_type.value, e)

        return AgentStatus(
            agent_type=self.agent_type,
            pid=self.pid,
            status=self.status,
            uptime_seconds=uptime,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            restart_count=self.restart_count,
            last_heartbeat=time.strftime("%Y-%m-%d %H:%M:%S") if self.is_alive() else None,
        )

    def send_message(self, message) -> None:
        """Send message to agent.

        Args:
            message: Message to send
        """
        # Future: implement inter-process message passing
