"""Multi-Agent Orchestrator - Transform daemon into parallel team execution.

This module implements the OrchestratorAgent that IS an autonomous agent itself
and launches and manages ALL six agents working simultaneously as a coordinated team.

Architecture:
    OrchestratorAgent (7th Agent - inherits BaseAgent)
    ├── Launches 6 agent subprocesses (architect, code_developer, etc.)
    ├── Monitors agent health (heartbeat checking every 30 seconds)
    ├── Restarts crashed agents (with exponential backoff)
    ├── Enforces CFR-013 (all agents on roadmap branch only)
    └── Coordinates graceful shutdown

Agent Processes (running simultaneously):
    1. ARCHITECT - Proactive spec creation (CFR-011)
    2. CODE_DEVELOPER - Implementation execution
    3. PROJECT_MANAGER - GitHub monitoring, DoD verification
    4. ASSISTANT - Demo creation, bug reporting
    5. CODE_SEARCHER - Weekly code analysis
    6. UX_DESIGN_EXPERT - Design reviews and guidance

Inter-Process Communication (IPC):
    - Status files: data/agent_status/{agent}_status.json
    - Message queues: data/agent_messages/{agent}_inbox/
    - File-based for simplicity and observability

Expected Impact:
    - 3-6x speedup through parallel execution (6-9h → 2-3h per priority)
    - Zero spec blocking (architect creates ahead)
    - Continuous QA (assistant demos automatically)
    - Real-time monitoring (project_manager checks GitHub)
    - Weekly code quality improvements (code-searcher analysis)

Prerequisites (US-056):
    - All agents must work on roadmap branch ONLY (CFR-013)
    - Singleton enforcement prevents duplicate instances (US-035)
    - File ownership matrix prevents conflicts (CFR-000)

Usage Examples:
    Start full team (all 6 agents):
    >>> orchestrator = OrchestratorAgent()
    >>> orchestrator.run_continuous()

    Start specific agents only (for testing):
    >>> orchestrator = OrchestratorAgent(
    ...     agent_types=[AgentType.ARCHITECT, AgentType.CODE_DEVELOPER]
    ... )
    >>> orchestrator.run_continuous()

Related:
    SPEC-057: Technical specification
    US-057: Strategic requirement document (7th agent as orchestrator)
    PRE_US_057_REFACTORING_ANALYSIS: Green light approval

Timeline:
    Week 1 (Days 1-3): Foundation (orchestrator + base_agent) - DONE
    Week 2 (Days 4-8): Agent migration (code_developer + architect + PM)
    Week 3 (Days 9-15): Complete team + testing + deployment
"""

import json
import logging
import os
import time
from datetime import datetime
from multiprocessing import Process
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


def _agent_runner_static(agent_type: AgentType, config: Dict, status_dir: Path, message_dir: Path):
    """Target function for agent subprocess (static/module-level for pickling).

    This function runs in the child process and:
    1. Registers agent in singleton registry (CFR-000)
    2. Enforces CFR-013 (roadmap branch only)
    3. Runs agent's continuous work loop
    4. Handles cleanup on exit

    Args:
        agent_type: Type of agent
        config: Agent configuration
        status_dir: Directory for agent status files
        message_dir: Directory for inter-agent messages

    Raises:
        AgentAlreadyRunningError: If agent type already registered
    """
    # Setup logging in subprocess
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
    )

    try:
        logger.info(f"🚀 Starting {config['name']} subprocess (PID: {os.getpid()})")

        # Import agent class dynamically
        logger.info(f"Importing {config['module']}.{config['class']}...")
        module = __import__(config["module"], fromlist=[config["class"]])
        agent_class = getattr(module, config["class"])
        logger.info(f"✅ Agent class imported successfully")

        # Create agent instance
        logger.info(f"Creating agent instance...")
        agent = agent_class(
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=config["check_interval"],
        )
        logger.info(f"✅ Agent instance created")

        # Register agent (CFR-000 singleton enforcement)
        with AgentRegistry.register(agent_type):
            logger.info(f"✅ {config['name']} registered in singleton registry (PID: {os.getpid()})")

            # Run agent's continuous loop
            logger.info(f"Starting continuous loop for {config['name']}...")
            agent.run_continuous()

    except Exception as e:
        logger.error(f"❌ {config['name']} crashed: {e}")
        import traceback

        traceback.print_exc()

        # Write error status before exiting
        try:
            status_file = status_dir / f"{config['name']}_status.json"
            error_status = {
                "agent_type": config["name"],
                "state": "crashed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "pid": os.getpid(),
                "timestamp": datetime.now().isoformat(),
            }
            status_file.write_text(json.dumps(error_status, indent=2))
        except:
            pass

        raise


class OrchestratorAgent(BaseAgent):
    """Multi-agent orchestrator managing parallel team execution.

    This agent IS the 7th autonomous agent and launches ALL six other agents
    in separate subprocesses, coordinating their work through file-based
    messaging and status tracking.

    Responsibilities:
        1. Launch 6 agent subprocesses in priority order
        2. Monitor agent health (heartbeat checking every 30 seconds)
        3. Restart crashed agents (exponential backoff up to max restarts)
        4. Enforce CFR-013 (all agents on roadmap branch)
        5. Coordinate graceful shutdown
        6. Respond to user_listener commands

    Attributes:
        agent_types: List of agents to launch (default: all 6)
        max_restarts: Maximum restarts before giving up
        restart_backoff: Initial backoff delay between restarts (seconds)
        processes: Dictionary mapping AgentType to subprocess.Process
        restart_counts: Dictionary tracking restart attempts per agent
        last_restart: Dictionary tracking last restart time per agent

    Example:
        >>> orchestrator = OrchestratorAgent()
        >>> orchestrator.run_continuous()  # Launches all 6 agents, runs continuously
    """

    def __init__(
        self,
        status_dir: Path = Path("data/agent_status"),
        message_dir: Path = Path("data/agent_messages"),
        check_interval: int = 30,  # Health check every 30 seconds
        max_restarts_per_agent: int = 3,
        restart_backoff: float = 60.0,  # seconds
        agent_types: Optional[List[AgentType]] = None,
    ):
        """Initialize OrchestratorAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between health checks (default: 30)
            max_restarts_per_agent: Maximum restarts before giving up
            restart_backoff: Initial backoff delay between restarts (seconds)
            agent_types: Optional list of agent types to launch (default: all 6)

        Raises:
            CFR013ViolationError: If not on roadmap branch (CFR-013)
        """
        # Initialize BaseAgent
        super().__init__(
            agent_type=AgentType.ORCHESTRATOR,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.max_restarts = max_restarts_per_agent
        self.restart_backoff = restart_backoff

        # Agent configurations
        self.all_agents = self._initialize_agent_configs()

        # Filter to specific agent types if requested (default: all 6 agents)
        if agent_types:
            self.agents = {
                agent_type: config for agent_type, config in self.all_agents.items() if agent_type in agent_types
            }
        else:
            self.agents = self.all_agents

        # Process tracking
        self.processes: Dict[AgentType, Process] = {}
        self.restart_counts: Dict[AgentType, int] = {}
        self.last_restart: Dict[AgentType, datetime] = {}

        # State
        self.team_start_time = None

        logger.info(f"OrchestratorAgent initialized - will manage {len(self.agents)} agents")

    def _initialize_agent_configs(self) -> Dict[AgentType, Dict]:
        """Initialize configurations for all agents.

        Returns:
            Dictionary mapping AgentType to configuration dict

        Configuration includes:
            - name: Agent name for logging
            - module: Python module path
            - class: Agent class name
            - check_interval: Seconds between background work iterations
            - priority: Launch order (lower = earlier)

        Priority order (ensures dependencies):
            1. ARCHITECT (creates specs first, unblocks code_developer)
            2. CODE_DEVELOPER (implements, notifies assistant)
            3. PROJECT_MANAGER (monitors GitHub, verifies DoD)
            4. ASSISTANT (demos, bug reporting)
            5. CODE_SEARCHER (weekly analysis)
            6. UX_DESIGN_EXPERT (design reviews)
        """
        return {
            AgentType.ARCHITECT: {
                "name": "architect",
                "module": "coffee_maker.autonomous.agents.architect_agent",
                "class": "ArchitectAgent",
                "check_interval": 3600,  # 1 hour - proactive spec creation
                "priority": 1,  # Highest: creates specs first (CFR-011)
            },
            AgentType.CODE_DEVELOPER: {
                "name": "code_developer",
                "module": "coffee_maker.autonomous.agents.code_developer_agent",
                "class": "CodeDeveloperAgent",
                "check_interval": 300,  # 5 minutes - frequently checks for new priorities
                "priority": 2,  # High: implementation (main work loop)
            },
            AgentType.PROJECT_MANAGER: {
                "name": "project_manager",
                "module": "coffee_maker.autonomous.agents.project_manager_agent",
                "class": "ProjectManagerAgent",
                "check_interval": 900,  # 15 minutes - GitHub monitoring
                "priority": 3,  # Normal: coordination and monitoring
            },
            AgentType.ASSISTANT: {
                "name": "assistant",
                "module": "coffee_maker.autonomous.agents.assistant_agent",
                "class": "AssistantAgent",
                "check_interval": 1800,  # 30 minutes - demo creation
                "priority": 3,  # Normal: reactive demos and bug reporting
            },
            AgentType.CODE_SEARCHER: {
                "name": "code_searcher",
                "module": "coffee_maker.autonomous.agents.code_searcher_agent",
                "class": "CodeSearcherAgent",
                "check_interval": 86400,  # 24 hours - daily analysis
                "priority": 4,  # Low: weekly deep analysis
            },
            AgentType.UX_DESIGN_EXPERT: {
                "name": "ux_design_expert",
                "module": "coffee_maker.autonomous.agents.ux_design_expert_agent",
                "class": "UXDesignExpertAgent",
                "check_interval": 3600,  # 1 hour - design reviews
                "priority": 4,  # Low: mostly reactive with proactive reviews
            },
        }

    def _do_background_work(self):
        """Orchestrator's background work: monitor agent health, restart crashed agents, route messages.

        This method is called once per check_interval (30 seconds by default) and:
        1. Launches all agents (on first run)
        2. Polls message queue for routing requests
        3. Checks agent health via status files and process liveness
        4. Handles crashed agents with exponential backoff restart
        5. Writes orchestrator status for monitoring

        On first run (team_start_time is None), launches all agents.
        """
        # On first iteration, launch all agents
        if self.team_start_time is None:
            logger.info("Launching all agents in priority order...")
            self._launch_all_agents()
            self.team_start_time = datetime.now()
            self.current_task = {
                "type": "team_orchestration",
                "status": "agents_launched",
                "started_at": self.team_start_time.isoformat(),
                "agents_running": len(self.processes),
            }
            return

        # Poll message queue for routing (check for messages to/from orchestrator)
        self._poll_message_queue()

        # Check agent health
        self._check_agent_health()

        # Handle crashed agents
        self._handle_crashed_agents()

        # Write orchestrator status
        self._write_orchestrator_status()

        # Update metrics
        self.metrics["agents_running"] = sum(1 for p in self.processes.values() if p.is_alive())
        self.metrics["total_restarts"] = sum(self.restart_counts.values())
        self.metrics["uptime_seconds"] = (datetime.now() - self.team_start_time).total_seconds()

    def _poll_message_queue(self):
        """Poll SQLite message queue for messages to orchestrator and route them.

        This method continuously checks the message queue for:
        - USER_REQUEST: From user_listener → route to appropriate agent
        - TASK_REQUEST: From agents → route to suggested recipient
        - TASK_RESPONSE: From agents → route to requester
        - USER_RESPONSE: From agents → route to user_listener

        Messages are processed until queue is empty.
        """
        from coffee_maker.autonomous.message_queue import MessageQueue

        queue = MessageQueue()

        # Process all available messages (up to 100 per iteration to avoid blocking)
        for _ in range(100):
            message = queue.get(recipient="orchestrator", timeout=0.1)

            if message is None:
                break  # No more messages

            try:
                # Mark message as started
                queue.mark_started(message.task_id, agent="orchestrator")

                # Convert Message to dict for _handle_message
                message_dict = {
                    "type": message.type,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "payload": message.payload,
                    "priority": message.priority,
                    "task_id": message.task_id,
                }

                # Route the message
                self._handle_message(message_dict)

                # Mark as completed
                queue.mark_completed(message.task_id, duration_ms=0)

            except Exception as e:
                logger.error(f"Error routing message {message.task_id}: {e}")
                queue.mark_failed(message.task_id, error_message=str(e))

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages and route them to appropriate agents.

        ARCHITECTURAL PRINCIPLE:
        ALL inter-agent communication goes through orchestrator. Agents never
        send directly to each other. This enables:
        - Central routing & load balancing
        - Bottleneck detection (measure task duration)
        - Velocity metrics (track all agent performance)
        - Flexibility (orchestrator can override suggested recipients)

        Message types:
        - user_request: User input from user_listener → route to best agent
        - task_request: Agent needs help from another agent → route intelligently
        - task_response: Agent finished task → route to requester
        - user_response: Agent response for user → route to user_listener
        - status_query: Return orchestrator and agent status
        - shutdown_request: Graceful shutdown request

        Args:
            message: Message dictionary with 'type', 'sender', 'payload', etc.
        """
        from coffee_maker.autonomous.message_queue import MessageType

        msg_type = message.get("type")

        if msg_type == MessageType.USER_REQUEST.value:
            # User input from user_listener → analyze and route to appropriate agent
            self._route_user_request(message)

        elif msg_type == MessageType.TASK_REQUEST.value:
            # Inter-agent task delegation → route based on suggestion + availability
            self._route_task_request(message)

        elif msg_type == MessageType.TASK_RESPONSE.value:
            # Task completion response → route to original requester
            self._route_task_response(message)

        elif msg_type == MessageType.USER_RESPONSE.value:
            # Agent response for user → route to user_listener
            self._route_user_response(message)

        elif msg_type == "status_query":
            logger.info("Status query received from user_listener")
            # Status will be written by _write_status() in next iteration

        elif msg_type == "shutdown_request":
            logger.info("Shutdown request received from user_listener")
            self.running = False

        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def _route_user_request(self, message: Dict):
        """Route user request to appropriate agent based on content analysis.

        Routing logic:
        1. Check payload for suggested_recipient (hint from user_listener)
        2. Analyze user_input content to determine best agent
        3. Check agent availability/load
        4. Route to selected agent
        5. Record start time for metrics

        Args:
            message: USER_REQUEST message from user_listener

        Example:
            Message payload: {
                "user_input": "Implement feature X",
                "suggested_recipient": "assistant"
            }
            → Orchestrator may route to code_developer instead if more appropriate
        """
        from coffee_maker.autonomous.message_queue import MessageQueue, Message, MessageType

        payload = message.get("payload", {})
        user_input = payload.get("user_input", "")
        suggested_recipient = payload.get("suggested_recipient", "assistant")
        sender = message.get("sender", "user_listener")

        logger.info(f"Routing USER_REQUEST: '{user_input[:50]}...' (suggested: {suggested_recipient})")

        # Analyze content to determine best agent
        # For now, use simple keyword matching (future: use LLM for classification)
        recipient = self._select_best_agent(user_input, suggested_recipient)

        logger.info(f"Selected agent: {recipient}")

        # Create routed task message
        routed_message = Message(
            sender="orchestrator",
            recipient=recipient,
            type=MessageType.TASK_REQUEST.value,
            payload={
                "task": user_input,
                "original_sender": sender,
                "routing_reason": f"Orchestrator routed from {sender} suggestion: {suggested_recipient}",
            },
            priority=1,  # High priority for user requests
        )

        # Send to selected agent
        queue = MessageQueue()
        queue.send(routed_message)

        # Record start time for metrics
        start_time = time.time()
        self.metrics[f"task_{routed_message.task_id}_start"] = start_time

        logger.info(f"Routed to {recipient}, task_id: {routed_message.task_id}")

    def _route_task_request(self, message: Dict):
        """Route inter-agent task request based on suggestion + availability.

        Args:
            message: TASK_REQUEST from one agent to another
        """
        from coffee_maker.autonomous.message_queue import MessageQueue, Message, MessageType

        payload = message.get("payload", {})
        task = payload.get("task", "")
        suggested_recipient = payload.get("suggested_recipient")
        reason = payload.get("reason", "")
        sender = message.get("sender")

        logger.info(f"Routing TASK_REQUEST from {sender}: '{task[:50]}...' → {suggested_recipient}")

        # For now, honor the suggestion (future: check availability, load)
        recipient = suggested_recipient

        # Create routed message
        routed_message = Message(
            sender="orchestrator",
            recipient=recipient,
            type=MessageType.TASK_REQUEST.value,
            payload={
                "task": task,
                "original_sender": sender,
                "reason": reason,
                "routing_reason": f"Orchestrator accepted suggestion from {sender}",
            },
            priority=message.get("priority", 5),
        )

        # Send to selected agent
        queue = MessageQueue()
        queue.send(routed_message)

        # Record metrics
        start_time = time.time()
        self.metrics[f"task_{routed_message.task_id}_start"] = start_time

        logger.info(f"Routed TASK_REQUEST to {recipient}, task_id: {routed_message.task_id}")

    def _route_task_response(self, message: Dict):
        """Route task response back to original requester.

        Args:
            message: TASK_RESPONSE from agent that completed work
        """
        from coffee_maker.autonomous.message_queue import MessageQueue, Message, MessageType

        payload = message.get("payload", {})
        response = payload.get("response", "")
        original_task_id = payload.get("original_task_id")
        final_recipient = payload.get("final_recipient")
        sender = message.get("sender")

        logger.info(f"Routing TASK_RESPONSE from {sender} → {final_recipient}")

        # Create routed response
        routed_message = Message(
            sender="orchestrator",
            recipient=final_recipient,
            type=(
                MessageType.TASK_RESPONSE.value
                if final_recipient != "user_listener"
                else MessageType.USER_RESPONSE.value
            ),
            payload={
                "response": response,
                "original_task_id": original_task_id,
                "completed_by": sender,
            },
            priority=2,
        )

        # Send response
        queue = MessageQueue()
        queue.send(routed_message)

        # Calculate and record task duration
        if original_task_id and f"task_{original_task_id}_start" in self.metrics:
            duration = time.time() - self.metrics[f"task_{original_task_id}_start"]
            self.metrics[f"task_{original_task_id}_duration"] = duration
            logger.info(f"Task {original_task_id} completed by {sender} in {duration:.2f}s")

    def _route_user_response(self, message: Dict):
        """Route agent response to user_listener for display.

        Args:
            message: USER_RESPONSE from agent with result for user
        """
        from coffee_maker.autonomous.message_queue import MessageQueue, Message, MessageType

        payload = message.get("payload", {})
        response = payload.get("response", "")
        sender = message.get("sender")

        logger.info(f"Routing USER_RESPONSE from {sender} → user_listener")

        # Forward directly to user_listener
        routed_message = Message(
            sender="orchestrator",
            recipient="user_listener",
            type=MessageType.USER_RESPONSE.value,
            payload={
                "response": response,
                "completed_by": sender,
            },
            priority=1,
        )

        # Send to user_listener
        queue = MessageQueue()
        queue.send(routed_message)

    def _select_best_agent(self, user_input: str, suggested_recipient: str) -> str:
        """Select the best agent to handle a user request.

        Simple keyword-based routing (future: use LLM for intelligent classification).

        Routing rules:
        - "implement", "code", "fix bug" → code_developer
        - "design", "ui", "ux" → ux_design_expert
        - "spec", "architecture", "design system" → architect
        - "github", "pr", "monitor", "verify dod" → project_manager
        - "search", "analyze code", "find" → code_searcher
        - "demo", "show", "test" → assistant
        - Default → assistant (handles general questions)

        Args:
            user_input: User's natural language input
            suggested_recipient: Hint from user_listener

        Returns:
            Agent name (string)
        """
        lower_input = user_input.lower()

        # Code implementation keywords
        if any(keyword in lower_input for keyword in ["implement", "code", "write", "fix bug", "create function"]):
            return "code_developer"

        # Design keywords
        if any(keyword in lower_input for keyword in ["design", "ui", "ux", "tailwind", "component", "layout"]):
            return "ux_design_expert"

        # Architecture keywords
        if any(keyword in lower_input for keyword in ["spec", "architecture", "system design", "dependencies"]):
            return "architect"

        # Project management keywords
        if any(keyword in lower_input for keyword in ["github", "pr", "pull request", "monitor", "verify", "dod"]):
            return "project_manager"

        # Code search keywords
        if any(keyword in lower_input for keyword in ["find", "search code", "analyze", "where is", "forensic"]):
            return "code_searcher"

        # Demo/testing keywords
        if any(keyword in lower_input for keyword in ["demo", "show", "test", "try", "showcase"]):
            return "assistant"

        # Default: Use suggestion or fall back to assistant
        return suggested_recipient if suggested_recipient else "assistant"

    def _enforce_cfr_013(self):
        """Ensure orchestrator is on roadmap branch (CFR-013).

        CFR-013 requires ALL agents to work ONLY on the 'roadmap' branch.
        This validation must happen BEFORE launching any agents.

        Raises:
            CFR013ViolationError: If not on roadmap branch
        """
        current_branch = self.git.get_current_branch()

        if current_branch != "roadmap":
            error_msg = (
                f"❌ CFR-013 VIOLATION: Orchestrator not on roadmap branch!\n\n"
                f"Current branch: {current_branch}\n"
                f"Required branch: roadmap\n\n"
                f"ALL agents MUST work on roadmap branch only.\n"
                f"This ensures single source of truth and no merge conflicts.\n\n"
                f"To fix:\n"
                f"  1. git checkout roadmap\n"
                f"  2. git pull origin roadmap\n"
                f"  3. Restart orchestrator"
            )
            raise CFR013ViolationError(error_msg)

        logger.info("✅ CFR-013 verified: On roadmap branch")

    def _launch_all_agents(self):
        """Launch all agent subprocesses in priority order.

        Agents are launched in priority order (low number = high priority):
        1. ARCHITECT (priority 1) - creates specs proactively
        2. CODE_DEVELOPER (priority 2) - implements features
        3. PROJECT_MANAGER & ASSISTANT (priority 3) - coordination
        4. CODE_SEARCHER & UX_DESIGN_EXPERT (priority 4) - analysis

        Staggered launches (1 second apart) prevent resource contention.
        """
        # Sort by priority (lower number = higher priority)
        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1]["priority"])

        logger.info(f"Launching {len(sorted_agents)} agents in priority order...")

        for agent_type, config in sorted_agents:
            self._launch_agent(agent_type, config)
            time.sleep(1)  # Stagger launches slightly to avoid resource contention

        logger.info(f"✅ All {len(sorted_agents)} agents launched")

    def _launch_agent(self, agent_type: AgentType, config: Dict):
        """Launch a single agent subprocess.

        Args:
            agent_type: Type of agent to launch
            config: Agent configuration dictionary

        Logs:
            - Agent name and PID
            - Check interval and priority
            - Any errors during launch
        """
        try:
            # Create agent process
            process = Process(
                target=_agent_runner_static,
                args=(agent_type, config, self.status_dir, self.message_dir),
                name=f"agent_{config['name']}",
            )

            process.start()
            self.processes[agent_type] = process
            self.restart_counts[agent_type] = 0

            logger.info(
                f"✅ {config['name']} started "
                f"(PID: {process.pid}, Priority: {config['priority']}, "
                f"Check interval: {config['check_interval']}s)"
            )

        except Exception as e:
            logger.error(f"❌ Failed to launch {config['name']}: {e}")

    def _check_agent_health(self):
        """Monitor agent health via status files and process liveness.

        Checks two health indicators per agent:
        1. Process liveness: Is the subprocess still running?
        2. Heartbeat staleness: Is the status file recent (<5 minutes)?

        Warnings logged but no action taken here (handled by _handle_crashed_agents).
        """
        for agent_type, process in list(self.processes.items()):
            config = self.agents[agent_type]
            status_file = self.status_dir / f"{config['name']}_status.json"

            # Check 1: Process is alive
            if not process.is_alive():
                logger.error(f"❌ {config['name']} process died (PID: {process.pid})")
                continue

            # Check 2: Status file exists and is recent
            if status_file.exists():
                try:
                    status = json.loads(status_file.read_text())
                    last_heartbeat = datetime.fromisoformat(status["last_heartbeat"])
                    age_seconds = (datetime.now() - last_heartbeat).total_seconds()

                    # Warn if heartbeat stale (>5 minutes)
                    if age_seconds > 300:
                        logger.warning(f"⚠️  {config['name']} heartbeat stale " f"({age_seconds:.0f}s old)")

                except Exception as e:
                    logger.error(f"Error reading status for {config['name']}: {e}")

    def _handle_crashed_agents(self):
        """Restart crashed agents with exponential backoff.

        Crash recovery logic:
        1. Detect dead process or stale heartbeat
        2. Check if restart limit exceeded
        3. Check if backoff period has elapsed
        4. Launch new process and increment restart count

        Exponential backoff formula:
            delay = restart_backoff * (2 ** restart_count)
            restart_backoff default: 60 seconds
            restart_count starts at 0

        Example timeline:
            1st crash: Wait 60s (2^0)
            2nd crash: Wait 120s (2^1)
            3rd crash: Wait 240s (2^2)
        """
        for agent_type, process in list(self.processes.items()):
            if not process.is_alive():
                config = self.agents[agent_type]

                # Check restart limit
                if self.restart_counts[agent_type] >= self.max_restarts:
                    logger.critical(
                        f"🚨 {config['name']} reached max restarts " f"({self.max_restarts}) - NOT restarting"
                    )
                    continue

                # Check backoff period
                if agent_type in self.last_restart:
                    time_since_restart = (datetime.now() - self.last_restart[agent_type]).total_seconds()

                    # Exponential backoff: 60s, 120s, 240s
                    backoff_delay = self.restart_backoff * (2 ** self.restart_counts[agent_type])

                    if time_since_restart < backoff_delay:
                        logger.info(
                            f"⏳ {config['name']} backoff in progress "
                            f"({time_since_restart:.0f}s / {backoff_delay:.0f}s)"
                        )
                        continue

                # Restart agent
                logger.warning(f"🔄 Restarting {config['name']}...")
                self._launch_agent(agent_type, config)
                self.restart_counts[agent_type] += 1
                self.last_restart[agent_type] = datetime.now()

    def _write_orchestrator_status(self):
        """Write orchestrator status file for monitoring.

        Status includes:
            - Uptime (how long orchestrator has been running)
            - All agent statuses (alive, crashed, etc.)
            - Restart counts per agent
            - Next scheduled check time
        """
        try:
            status_info = {
                "orchestrator": "OrchestratorAgent",
                "started_at": self.team_start_time.isoformat() if self.team_start_time else None,
                "uptime_seconds": (
                    (datetime.now() - self.team_start_time).total_seconds() if self.team_start_time else 0
                ),
                "agents": {},
                "timestamp": datetime.now().isoformat(),
            }

            # Add per-agent status
            for agent_type, process in self.processes.items():
                config = self.agents[agent_type]
                status_info["agents"][config["name"]] = {
                    "pid": process.pid,
                    "alive": process.is_alive(),
                    "restarts": self.restart_counts[agent_type],
                }

            # Write to orchestrator status file
            orch_status_file = self.status_dir / "orchestrator_status.json"
            orch_status_file.write_text(json.dumps(status_info, indent=2))

        except Exception as e:
            logger.error(f"Error writing orchestrator status: {e}")

    def _shutdown_all_agents(self):
        """Gracefully shutdown all agent subprocesses.

        Shutdown sequence:
        1. Send SIGTERM to all agents (graceful shutdown)
        2. Wait up to 10 seconds for cleanup
        3. If still alive, send SIGKILL (force kill)
        4. Wait for process to be reaped

        This ensures clean shutdown without orphaned processes.
        """
        logger.info("🛑 Shutting down all agents...")

        for agent_type, process in self.processes.items():
            config = self.agents[agent_type]

            if process.is_alive():
                logger.info(f"Stopping {config['name']} (PID: {process.pid})...")
                process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                process.join(timeout=10)

                if process.is_alive():
                    logger.warning(f"Force killing {config['name']}...")
                    process.kill()
                    process.join()

        logger.info("✅ All agents stopped")

    def stop(self):
        """Stop the orchestrator gracefully."""
        logger.info("Stopping orchestrator...")
        self.running = False


def main():
    """CLI entry point for starting the OrchestratorAgent.

    Usage:
        python -m coffee_maker.autonomous.orchestrator

    Example:
        # Run all 6 agents
        python -m coffee_maker.autonomous.orchestrator

        # Run specific agents for testing
        python -m coffee_maker.autonomous.orchestrator --agents ARCHITECT,CODE_DEVELOPER
    """
    import argparse

    parser = argparse.ArgumentParser(description="OrchestratorAgent - Multi-agent parallel execution")
    parser.add_argument(
        "--agents",
        type=str,
        help="Comma-separated agent types to launch (default: all 6)",
    )
    parser.add_argument(
        "--status-dir",
        type=str,
        default="data/agent_status",
        help="Directory for agent status files",
    )
    parser.add_argument(
        "--message-dir",
        type=str,
        default="data/agent_messages",
        help="Directory for inter-agent messages",
    )
    parser.add_argument(
        "--max-restarts",
        type=int,
        default=3,
        help="Maximum restarts per agent before giving up",
    )

    args = parser.parse_args()

    # Parse agent types if specified
    agent_types = None
    if args.agents:
        agent_type_names = [a.strip().upper() for a in args.agents.split(",")]
        try:
            agent_types = [AgentType[name] for name in agent_type_names]
        except KeyError as e:
            logger.error(f"Invalid agent type: {e}")
            logger.error(f"Valid types: {[a.name for a in AgentType]}")
            return

    # Create and run orchestrator
    orchestrator = OrchestratorAgent(
        status_dir=Path(args.status_dir),
        message_dir=Path(args.message_dir),
        max_restarts_per_agent=args.max_restarts,
        agent_types=agent_types,
    )

    try:
        orchestrator.run_continuous()
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        import traceback

        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
