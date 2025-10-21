"""
Execution Controller for Claude Skills Integration.

Unified controller that decides whether to use skills, prompts, or both (hybrid mode).
Maintains backward compatibility with existing prompt-based system while enabling
Code Execution Tool for complex workflows.

Author: architect agent
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentType

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution mode for tasks."""

    PROMPT_ONLY = "prompt"  # Use prompt template (multi-provider)
    SKILL_ONLY = "skill"  # Use skill with Code Execution Tool (Claude only)
    HYBRID = "hybrid"  # Use both (skill for execution, prompt for reasoning)


class NoSkillFoundError(Exception):
    """Raised when no skill is found for a task."""


@dataclass
class ExecutionResult:
    """Result of execution (skill or prompt)."""

    output: Any
    mode: ExecutionMode
    skills_used: List[str]
    prompts_used: List[str]
    execution_time: float
    success: bool
    errors: List[str]


class ExecutionController:
    """Unified controller for skills and prompts.

    Example:
        >>> controller = ExecutionController(agent_type=AgentType.CODE_DEVELOPER)
        >>> result = controller.execute(
        ...     task="refactor daemon.py using mixins",
        ...     mode=ExecutionMode.SKILL_ONLY
        ... )
    """

    def __init__(self, agent_type: AgentType):
        """Initialize ExecutionController.

        Args:
            agent_type: Type of agent using this controller
        """
        self.agent_type = agent_type

        # Lazy imports to avoid circular dependencies
        self._skill_loader = None
        self._prompt_loader = None
        self._skill_registry = None
        self._skill_invoker = None

    @property
    def skill_loader(self):
        """Lazy-load SkillLoader."""
        if self._skill_loader is None:
            from coffee_maker.autonomous.skill_loader import SkillLoader

            self._skill_loader = SkillLoader(self.agent_type)
        return self._skill_loader

    @property
    def prompt_loader(self):
        """Lazy-load PromptLoader."""
        if self._prompt_loader is None:
            from coffee_maker.autonomous.prompt_loader import load_prompt

            self._prompt_loader = load_prompt
        return self._prompt_loader

    @property
    def skill_registry(self):
        """Lazy-load SkillRegistry."""
        if self._skill_registry is None:
            from coffee_maker.autonomous.skill_registry import SkillRegistry

            self._skill_registry = SkillRegistry(self.agent_type)
        return self._skill_registry

    @property
    def skill_invoker(self):
        """Lazy-load SkillInvoker."""
        if self._skill_invoker is None:
            from coffee_maker.autonomous.skill_invoker import SkillInvoker

            self._skill_invoker = SkillInvoker(self.agent_type)
        return self._skill_invoker

    def execute(
        self,
        task: str,
        mode: ExecutionMode = ExecutionMode.HYBRID,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Execute task using skills, prompts, or both.

        Args:
            task: Task description (e.g., "refactor daemon.py")
            mode: Execution mode (SKILL_ONLY, PROMPT_ONLY, HYBRID)
            context: Context data for skill/prompt execution

        Returns:
            ExecutionResult with output, mode, time, success, errors

        Raises:
            NoSkillFoundError: If SKILL_ONLY mode and no skill found
        """
        context = context or {}

        if mode == ExecutionMode.SKILL_ONLY:
            return self._execute_skill(task, context)
        elif mode == ExecutionMode.PROMPT_ONLY:
            return self._execute_prompt(task, context)
        else:  # HYBRID
            return self._execute_hybrid(task, context)

    def _execute_skill(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        """Execute skill with Code Execution Tool."""
        start_time = time.time()

        # 1. Discover relevant skills
        skills = self.skill_registry.find_skills_for_task(task)

        if not skills:
            raise NoSkillFoundError(
                f"No skill found for task: {task}\n"
                f"Agent: {self.agent_type.value}\n"
                f"Available skills: {self.skill_loader.list_available_skills()}"
            )

        # 2. Invoke skills (may compose multiple)
        result = self.skill_invoker.invoke(skills, context)

        execution_time = time.time() - start_time

        return ExecutionResult(
            output=result.output,
            mode=ExecutionMode.SKILL_ONLY,
            skills_used=[s.name for s in skills],
            prompts_used=[],
            execution_time=execution_time,
            success=result.success,
            errors=result.errors,
        )

    def _execute_prompt(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        """Execute prompt with LLM reasoning (existing)."""
        start_time = time.time()

        # Use existing PromptLoader (unchanged)
        # Note: This is a simplified version - actual implementation may vary
        # based on how prompts are currently loaded in the system

        logger.info(f"Executing PROMPT_ONLY mode for task: {task} " f"(agent: {self.agent_type.value})")

        # TODO: Integrate with existing PromptLoader
        # For now, return placeholder result
        output = f"PROMPT_ONLY: {task}"
        execution_time = time.time() - start_time

        return ExecutionResult(
            output=output,
            mode=ExecutionMode.PROMPT_ONLY,
            skills_used=[],
            prompts_used=[task],
            execution_time=execution_time,
            success=True,
            errors=[],
        )

    def _execute_hybrid(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        """Execute skill + prompt (skill provides data, prompt interprets)."""
        start_time = time.time()

        try:
            # 1. Execute skill to get data
            skill_result = self._execute_skill(task, context)

            # 2. Use prompt to interpret skill output
            context["skill_output"] = skill_result.output
            prompt_result = self._execute_prompt(task, context)

            execution_time = time.time() - start_time

            return ExecutionResult(
                output=prompt_result.output,
                mode=ExecutionMode.HYBRID,
                skills_used=skill_result.skills_used,
                prompts_used=prompt_result.prompts_used,
                execution_time=execution_time,
                success=skill_result.success and prompt_result.success,
                errors=skill_result.errors + prompt_result.errors,
            )

        except NoSkillFoundError:
            # Graceful fallback to prompts if skill not found
            logger.warning(f"No skill found for task '{task}', falling back to PROMPT_ONLY")
            return self._execute_prompt(task, context)
