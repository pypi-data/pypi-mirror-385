"""AssistantAgent - Demo creation, bug reporting, and documentation.

This agent is responsible for creating visual demos, testing features, reporting bugs,
and providing documentation assistance.

Architecture:
    BaseAgent
      └── AssistantAgent
            ├── _do_background_work(): Respond to demo requests
            └── _handle_message(): Handle demo & documentation requests

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    US-045: Puppeteer-based Definition of Done verification
    CFR-013: All agents work on roadmap branch only
    US-057: Strategic requirement for multi-agent system

Continuous Work Loop:
    1. Check message queue for demo requests (from code_developer)
    2. For each requested feature:
       - Create visual demo with Puppeteer
       - Test acceptance criteria
       - Generate screenshots
       - Report any bugs found
    3. Send bug reports to project_manager if issues found
    4. Sleep for check_interval seconds (default: 30 minutes)

Message Handling:
    - demo_request: Feature complete, create visual demo
    - documentation_request: Create documentation for feature
    - test_request: Test feature for bugs/regressions

Key Responsibilities:
    1. DEMO CREATION (only agent that creates demos)
    2. BUG DETECTION (tests find bugs during demos)
    3. BUG REPORTING (comprehensive analysis to project_manager)
    4. DOCUMENTATION (creates visual docs and guides)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AssistantAgent(BaseAgent):
    """Assistant agent - Demo creation, bug reporting, and documentation.

    Responsibilities:
    - Create visual demos using Puppeteer MCP (ONLY agent that creates demos)
    - Test features and detect bugs
    - Report comprehensive bug analysis to project_manager
    - Create feature documentation
    - Provide intelligent dispatch recommendations

    Key Point: ONLY Agent That Creates Demos
        No other agent creates demos. This is exclusive to assistant.
        When user_listener asks for a demo, it delegates to assistant.

    Example:
        >>> agent = AssistantAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=1800  # 30 minutes
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 1800,  # 30 minutes for demo creation
    ):
        """Initialize AssistantAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between demo checks (default: 30 minutes)
        """
        super().__init__(
            agent_type=AgentType.ASSISTANT,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        logger.info("✅ AssistantAgent initialized (demo creation + bug reporting)")

    def _do_background_work(self):
        """Assistant's background work: create demos and test features.

        Workflow:
        1. Check message queue for demo requests
        2. For each feature:
           - Use Puppeteer to create visual demo
           - Screenshot key steps
           - Test acceptance criteria
           - Check for bugs/regressions
        3. If bugs found:
           - Create comprehensive bug report
           - Send to project_manager (urgent)
        4. Log demo completion

        Future (Phase 3):
        - Puppeteer integration for automated testing
        - Screenshot generation and documentation
        - Comprehensive bug analysis
        """
        logger.info("🎬 Assistant: Checking for demo requests...")

        # TODO: Implement demo creation with Puppeteer
        # For now, just log and continue
        logger.info("ℹ️  Demo creation not yet implemented")

        # Update metrics
        self.metrics["demos_created"] = self.metrics.get("demos_created", 0)
        self.metrics["bugs_found"] = self.metrics.get("bugs_found", 0)
        self.metrics["last_check"] = datetime.now().isoformat()

        # Update current task
        self.current_task = {
            "type": "demo_creation",
            "status": "idle",
            "last_check": datetime.now().isoformat(),
        }

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - demo_request: Feature complete, create visual demo
        - documentation_request: Create documentation
        - test_request: Test feature for bugs

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")

        if msg_type == "demo_request":
            # Feature complete - create visual demo
            feature_info = message.get("content", {})
            feature_name = feature_info.get("feature", "unknown")

            logger.info(f"🎬 Demo request for {feature_name}")
            logger.info(f"Title: {feature_info.get('title', 'No title')}")

            # TODO: Create demo with Puppeteer
            # In Phase 3: Implement Puppeteer integration
            # - Navigate to feature
            # - Test acceptance criteria
            # - Screenshot results
            # - Report any bugs

        elif msg_type == "documentation_request":
            # Documentation request
            doc_info = message.get("content", {})
            logger.info(f"📝 Documentation request: {doc_info.get('title', 'untitled')}")

            # TODO: Create documentation
            # In Phase 3: Implement documentation generation

        elif msg_type == "test_request":
            # Test request (from project_manager)
            test_info = message.get("content", {})
            logger.info(f"🧪 Test request: {test_info.get('feature', 'unknown')}")

            # TODO: Run tests with Puppeteer
            # In Phase 3: Implement automated testing

        else:
            logger.warning(f"Unknown message type: {msg_type}")
