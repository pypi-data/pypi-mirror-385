"""
Skill Invoker for Claude Skills Integration.

Executes skills using Code Execution Tool with sandboxed execution.
Supports skill composition (chaining multiple skills).
Supports parallel execution for independent skills (Phase 3 optimization).

Author: architect agent
Date: 2025-10-19
Related: SPEC-055, SPEC-057, US-055, US-057
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.skill_loader import SkillMetadata

logger = logging.getLogger(__name__)


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""

    output: Any
    exit_code: int
    duration: float
    skill_name: str
    errors: List[str]

    @property
    def success(self) -> bool:
        """Check if skill executed successfully."""
        return self.exit_code == 0


class SkillInvoker:
    """Execute Claude Skills with Code Execution Tool.

    Example:
        >>> invoker = SkillInvoker(AgentType.CODE_DEVELOPER)
        >>> result = invoker.invoke([skill_metadata], context={"priority": "US-055"})
        >>> print(result.output)
    """

    def __init__(
        self,
        agent_type: AgentType,
        timeout: int = 300,  # 5 minutes default
    ):
        """Initialize SkillInvoker.

        Args:
            agent_type: Type of agent using this invoker
            timeout: Timeout in seconds for skill execution
        """
        self.agent_type = agent_type
        self.timeout = timeout

    def invoke(self, skills: List[SkillMetadata], context: Dict[str, Any]) -> SkillExecutionResult:
        """Invoke skills with context (skills execute in composition order).

        Args:
            skills: List of skills to execute
            context: Context data for skill execution

        Returns:
            SkillExecutionResult with output, exit code, duration, errors
        """
        start = time.time()

        # Execute skills in sequence (composition)
        current_context = context.copy()
        outputs = []
        errors = []

        for skill in skills:
            try:
                result = self._execute_single_skill(skill, current_context)
                outputs.append(result.output)

                # Pass output to next skill
                current_context["previous_skill_output"] = result.output

                if not result.success:
                    errors.extend(result.errors)

            except Exception as e:
                logger.error(f"Skill {skill.name} failed: {e}", exc_info=True)
                errors.append(f"{skill.name}: {str(e)}")

        duration = time.time() - start

        return SkillExecutionResult(
            output=outputs[-1] if outputs else None,
            exit_code=0 if not errors else 1,
            duration=duration,
            skill_name=", ".join([s.name for s in skills]),
            errors=errors,
        )

    def invoke_parallel(self, skills: List[SkillMetadata], context: Dict[str, Any]) -> SkillExecutionResult:
        """Invoke multiple skills in parallel (for independent skills).

        Phase 3 optimization: Execute independent skills concurrently for 2-3x speedup.

        Args:
            skills: List of independent skills to execute in parallel
            context: Context data for skill execution (shared across all skills)

        Returns:
            SkillExecutionResult with combined outputs, errors, and total duration

        Note:
            Only use this for truly independent skills. For composed skills that
            depend on each other's output, use invoke() instead.
        """
        start = time.time()

        outputs = []
        errors = []
        skill_names = []

        # Execute skills in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(3, len(skills))) as executor:
            # Submit all skills for execution
            future_to_skill = {
                executor.submit(self._execute_single_skill, skill, context.copy()): skill for skill in skills
            }

            # Collect results as they complete
            for future in as_completed(future_to_skill):
                skill = future_to_skill[future]
                try:
                    result = future.result()
                    outputs.append(result.output)
                    skill_names.append(skill.name)

                    if not result.success:
                        errors.extend(result.errors)

                    logger.info(f"Parallel skill {skill.name} completed in {result.duration:.2f}s")

                except Exception as e:
                    logger.error(f"Parallel skill {skill.name} failed: {e}", exc_info=True)
                    errors.append(f"{skill.name}: {str(e)}")

        duration = time.time() - start

        logger.info(f"Parallel execution of {len(skills)} skills completed in {duration:.2f}s")

        return SkillExecutionResult(
            output=outputs,  # List of all outputs (not just last one)
            exit_code=0 if not errors else 1,
            duration=duration,
            skill_name=", ".join(skill_names),
            errors=errors,
        )

    def _execute_single_skill(self, skill: SkillMetadata, context: Dict[str, Any]) -> SkillExecutionResult:
        """Execute a single skill using Code Execution Tool.

        Args:
            skill: Skill metadata
            context: Context data

        Returns:
            SkillExecutionResult
        """
        start = time.time()

        # Read skill code
        skill_code = self._read_skill_code(skill)

        # Execute with Code Execution Tool
        # NOTE: This is a placeholder - actual implementation will integrate
        # with Claude CLI Interface once Code Execution Tool is enabled
        logger.info(f"Executing skill: {skill.name}")
        logger.debug(f"Skill code length: {len(skill_code)} bytes")
        logger.debug(f"Context: {context}")

        # TODO: Implement actual Code Execution Tool integration
        # For now, return placeholder result
        output = f"SKILL_PLACEHOLDER: {skill.name}"
        exit_code = 0
        errors = []

        duration = time.time() - start

        return SkillExecutionResult(
            output=output,
            exit_code=exit_code,
            duration=duration,
            skill_name=skill.name,
            errors=errors,
        )

    def _read_skill_code(self, skill: SkillMetadata) -> str:
        """Read skill code from skill directory.

        Args:
            skill: Skill metadata

        Returns:
            Skill code as string

        Raises:
            FileNotFoundError: If no Python script found
        """
        skill_dir = skill.skill_path

        # Try multiple naming conventions
        possible_files = [
            skill_dir / f"{skill.name}.py",
            skill_dir / "skill.py",
            skill_dir / "main.py",
        ]

        for py_script in possible_files:
            if py_script.exists():
                return py_script.read_text()

        raise FileNotFoundError(f"No Python script found in {skill_dir}\n" f"Tried: {[str(f) for f in possible_files]}")
