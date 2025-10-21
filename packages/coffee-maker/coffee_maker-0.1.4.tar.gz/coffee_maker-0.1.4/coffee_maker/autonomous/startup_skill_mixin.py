"""Startup Skill Mixin - Agent initialization with CFR-007 validation

This mixin provides a standardized initialization pattern for all agents.
It executes the agent's startup skill, validates CFR-007 compliance,
and ensures all pre-flight checks pass before agent begins work.

Usage:
    from coffee_maker.autonomous.startup_skill_mixin import StartupSkillMixin

    class MyAgent(StartupSkillMixin):
        def __init__(self):
            # Execute startup skill (this runs automatically)
            self._execute_startup_skill()

            # Agent-specific initialization
            self.my_attribute = value

        @property
        def agent_name(self) -> str:
            return "my_agent"

Related:
    - SPEC-063: Agent Startup Skills Implementation
    - coffee_maker/autonomous/startup_skill_executor.py
"""

import logging

from coffee_maker.autonomous.startup_skill_executor import (
    StartupSkillExecutor,
    StartupError,
    SkillExecutionResult,
)

logger = logging.getLogger(__name__)


class StartupSkillMixin:
    """Mixin providing startup skill execution for agents.

    Subclasses MUST:
    1. Define agent_name property
    2. Call _execute_startup_skill() in __init__

    Example:
        class CodeDeveloperAgent(StartupSkillMixin):
            @property
            def agent_name(self) -> str:
                return "code_developer"

            def __init__(self):
                self._execute_startup_skill()
                # Rest of initialization
    """

    @property
    def agent_name(self) -> str:
        """Agent name (must be overridden by subclass)."""
        raise NotImplementedError("Subclass must define agent_name property")

    def _execute_startup_skill(self) -> SkillExecutionResult:
        """Execute startup skill during agent initialization.

        This method:
        1. Loads the agent's startup skill from .claude/skills/
        2. Validates CFR-007 context budget compliance
        3. Executes health checks
        4. Initializes agent resources
        5. Raises StartupError if anything fails

        Returns:
            SkillExecutionResult with startup details

        Raises:
            StartupError: If startup skill fails
            CFR007ViolationError: If context budget exceeded
            HealthCheckError: If health checks fail
            FileNotFoundError: If startup skill file not found

        Example:
            result = self._execute_startup_skill()
            print(f"Agent started: {result.agent_name}")
            print(f"Context budget: {result.context_budget_pct:.1f}%")
        """
        executor = StartupSkillExecutor()

        logger.info(f"🚀 Starting {self.agent_name} agent...")

        # Execute startup skill
        result = executor.execute_startup_skill(self.agent_name)

        if not result.success:
            # Startup failed - format error message
            error_msg = (
                f"❌ {self.agent_name} startup failed\n"
                f"Error: {result.error_message}\n"
                f"Steps completed: {result.steps_completed}/{result.total_steps}\n"
            )

            if result.suggested_fixes:
                error_msg += "\nSuggested fixes:\n"
                for i, fix in enumerate(result.suggested_fixes, 1):
                    error_msg += f"  {i}. {fix}\n"

            logger.error(error_msg)
            raise StartupError(error_msg)

        # Startup succeeded - log metrics
        logger.info(f"✅ {self.agent_name} started successfully")
        logger.info(
            f"   Context budget: {result.context_budget_pct:.1f}% (<{StartupSkillExecutor.CFR007_BUDGET_PCT}% target)"
        )
        logger.info(
            f"   Health checks: {sum(1 for h in result.health_checks if h.passed)}/{len(result.health_checks)} passed"
        )
        logger.info(f"   Startup time: {result.execution_time_seconds:.2f}s")

        # Store result for debugging
        self.startup_result = result

        return result

    def _log_startup_summary(self) -> None:
        """Log startup summary for debugging.

        Use after successful startup to record initialization details.
        """
        if not hasattr(self, "startup_result"):
            logger.warning(f"{self.agent_name}: No startup_result available")
            return

        result = self.startup_result

        summary = f"\n{'='*60}\n"
        summary += f"STARTUP SUMMARY: {self.agent_name}\n"
        summary += f"{'='*60}\n"
        summary += f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}\n"
        summary += f"Steps: {result.steps_completed}/{result.total_steps}\n"
        summary += f"Context Budget: {result.context_budget_pct:.1f}%\n"
        summary += f"Health Checks: {sum(1 for h in result.health_checks if h.passed)}/{len(result.health_checks)}\n"
        summary += f"Time: {result.execution_time_seconds:.2f}s\n"

        if result.health_checks:
            summary += f"\nHealth Checks:\n"
            for check in result.health_checks:
                status = "✓" if check.passed else "✗"
                summary += f"  {status} {check.name}"
                if check.details:
                    summary += f" ({check.details})"
                summary += "\n"

        summary += f"{'='*60}\n"

        logger.info(summary)
