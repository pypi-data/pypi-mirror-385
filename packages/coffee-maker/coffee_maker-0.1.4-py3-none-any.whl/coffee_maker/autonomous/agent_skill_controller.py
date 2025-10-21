"""
Agent Skill Controller for Claude Skills Integration.

Per-agent skill orchestration with automatic skill discovery and execution.

Author: architect agent
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import logging
from typing import Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.execution_controller import NoSkillFoundError
from coffee_maker.autonomous.skill_invoker import (
    SkillExecutionResult,
    SkillInvoker,
)
from coffee_maker.autonomous.skill_loader import SkillLoader
from coffee_maker.autonomous.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


class AgentSkillController:
    """Skill controller for a specific agent.

    Example (code_developer):
        >>> controller = AgentSkillController(AgentType.CODE_DEVELOPER)
        >>> result = controller.execute_task(
        ...     "implement feature with tests",
        ...     context={"priority": "US-055", "files": ["daemon.py"]}
        ... )
        >>> print(result.output)  # TDD workflow result
    """

    def __init__(self, agent_type: AgentType):
        """Initialize AgentSkillController.

        Args:
            agent_type: Type of agent using this controller
        """
        self.agent_type = agent_type
        self.loader = SkillLoader(agent_type)
        self.registry = SkillRegistry(agent_type)
        self.invoker = SkillInvoker(agent_type)

    def execute_task(self, task_description: str, context: Optional[Dict] = None) -> SkillExecutionResult:
        """Execute task using relevant skills.

        Args:
            task_description: Description of task to execute
            context: Context data for skill execution

        Returns:
            SkillExecutionResult

        Raises:
            NoSkillFoundError: If no skills found for task
        """
        # 1. Find relevant skills
        skills = self.registry.find_skills_for_task(task_description)

        if not skills:
            raise NoSkillFoundError(
                f"No skills found for task: {task_description}\n" f"Available skills: {self.list_skills()}"
            )

        # 2. Invoke skills
        context = context or {}
        context["task_description"] = task_description
        context["agent_type"] = self.agent_type.value

        result = self.invoker.invoke(skills, context)

        # 3. Track usage (for Langfuse integration in Phase 2)
        self._track_usage(skills, result)

        return result

    def list_skills(self) -> List[str]:
        """List all skills available to this agent.

        Returns:
            List of skill names
        """
        skills = self.loader.list_available_skills()
        return [skill.name for skill in skills]

    def has_skill(self, skill_name: str) -> bool:
        """Check if agent has access to a skill.

        Args:
            skill_name: Name of skill to check

        Returns:
            True if skill exists, False otherwise
        """
        return self.loader.skill_exists(skill_name)

    def _track_usage(self, skills, result: SkillExecutionResult):
        """Track skill usage for observability (Phase 2: Langfuse integration).

        Args:
            skills: List of skills executed
            result: Execution result
        """
        logger.info(
            f"Agent {self.agent_type.value} executed skills: "
            f"{[s.name for s in skills]} "
            f"(duration: {result.duration:.2f}s, success: {result.success})"
        )
