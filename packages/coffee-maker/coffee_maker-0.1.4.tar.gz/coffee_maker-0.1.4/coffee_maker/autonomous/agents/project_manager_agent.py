"""ProjectManagerAgent - GitHub monitoring and DoD verification.

This agent is responsible for monitoring GitHub (PRs, issues, CI/CD) and verifying
that completed work meets the Definition of Done before marking it complete.

Architecture:
    BaseAgent
      └── ProjectManagerAgent (with StartupSkillMixin)
            ├── _do_background_work(): Monitor GitHub & verify DoD
            └── _handle_message(): Handle status queries & DoD requests

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    SPEC-063: Agent Startup Skills Implementation
    US-045: Puppeteer-based Definition of Done verification
    US-064: project_manager-startup Skill Integration
    CFR-013: All agents work on roadmap branch only
    US-057: Strategic requirement for multi-agent system

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Query GitHub for PR status
    3. Check for issues/bugs reported
    4. Monitor CI/CD pipeline
    5. When feature complete (from code_developer):
       - Use Puppeteer to verify DoD criteria
       - Generate verification report
       - Mark ROADMAP as "Verified"
    6. Sleep for check_interval seconds (default: 15 minutes)

Message Handling:
    - dod_verification: Verify completed priority with Puppeteer
    - bug_report: Bug found during testing
    - status_query: Return current project status

Startup Skill Integration (US-064):
    - Executes project_manager-startup skill at initialization
    - Validates CFR-007 context budget compliance (<30%)
    - Performs health checks (ROADMAP.md exists, gh CLI available)
    - Ensures all required resources are accessible
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent
from coffee_maker.autonomous.startup_skill_mixin import StartupSkillMixin

logger = logging.getLogger(__name__)


class ProjectManagerAgent(StartupSkillMixin, BaseAgent):
    """Project Manager agent - GitHub monitoring and DoD verification.

    Responsibilities:
    - Monitor GitHub for PRs, issues, CI/CD status
    - Verify completed work meets Definition of Done
    - Update ROADMAP with verification results
    - Generate project status reports
    - Track metrics (velocity, quality, etc.)

    Example:
        >>> agent = ProjectManagerAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=900  # 15 minutes
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    @property
    def agent_name(self) -> str:
        """Agent name for startup skill execution (required by StartupSkillMixin)."""
        return "project_manager"

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 900,  # 15 minutes for GitHub monitoring
        roadmap_file: str = "docs/roadmap/ROADMAP.md",
    ):
        """Initialize ProjectManagerAgent with startup skill execution.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between GitHub checks (default: 15 minutes)
            roadmap_file: Path to ROADMAP.md file

        Raises:
            StartupError: If startup skill execution fails
            CFR007ViolationError: If context budget exceeds 30%
            HealthCheckError: If required health checks fail
        """
        # Execute startup skill (US-064)
        # This validates:
        # - CFR-007 context budget <30%
        # - ROADMAP.md exists and is parseable
        # - GitHub CLI (gh) is available
        # - Required directories are accessible
        self._execute_startup_skill()

        # Initialize base agent
        super().__init__(
            agent_type=AgentType.PROJECT_MANAGER,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.roadmap_file = roadmap_file

        logger.info(
            "✅ ProjectManagerAgent initialized "
            f"(context budget: {self.startup_result.context_budget_pct:.1f}%, "
            f"health checks: {sum(1 for h in self.startup_result.health_checks if h.passed)}/{len(self.startup_result.health_checks)})"
        )

    def _do_background_work(self):
        """Project Manager's background work: GitHub monitoring & DoD verification.

        Workflow:
        1. Check GitHub for PR status
        2. Monitor CI/CD pipeline
        3. Check for reported issues
        4. Update ROADMAP status
        5. Generate metrics

        Future (Phase 3):
        - Use Puppeteer to verify DoD criteria
        - Automated testing coordination
        - Performance metrics tracking
        """
        logger.info("📊 Project Manager: Monitoring GitHub...")

        # TODO: Implement GitHub monitoring
        # For now, just log and continue
        logger.info("ℹ️  GitHub monitoring not yet implemented")

        # Update metrics
        self.metrics["prs_checked"] = self.metrics.get("prs_checked", 0)
        self.metrics["ci_status"] = "monitoring"
        self.metrics["last_check"] = datetime.now().isoformat()

        # Update current task
        self.current_task = {
            "type": "project_monitoring",
            "status": "monitoring",
            "last_check": datetime.now().isoformat(),
        }

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - dod_verification: Verify completed priority meets DoD
        - bug_report: Bug found during testing (from assistant)
        - status_query: Return project status

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")

        if msg_type == "dod_verification":
            # DoD verification request
            priority_info = message.get("content", {}).get("priority", {})
            priority_name = priority_info.get("name", "unknown")

            logger.info(f"📋 DoD verification requested for {priority_name}")

            # TODO: Use Puppeteer to verify DoD criteria
            # In Phase 3: Implement DoD verification with Puppeteer

        elif msg_type == "bug_report":
            # Bug found by assistant during demo
            bug_info = message.get("content", {})
            feature = bug_info.get("feature", "unknown")

            logger.error(f"🐛 Bug reported by assistant for {feature}")
            logger.error(f"Details: {bug_info.get('description', 'No description')}")

            # TODO: Add bug to ROADMAP as critical priority
            # In Phase 3: Implement bug prioritization

        elif msg_type == "status_query":
            logger.info("Status query received")
            # Status will be written by _write_status() in next iteration

        else:
            logger.warning(f"Unknown message type: {msg_type}")
