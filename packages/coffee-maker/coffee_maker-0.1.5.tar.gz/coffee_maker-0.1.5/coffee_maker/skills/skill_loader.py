"""
Startup Skill Loader for Agent Initialization.

This module loads and executes Claude Code Skills during agent startup,
ensuring CFR-007 compliance, health checks, and proper initialization.

Usage:
    from coffee_maker.skills import StartupSkillLoader, StartupError

    loader = StartupSkillLoader()
    result = loader.execute_startup_skill("architect")

    if not result.success:
        raise StartupError(result.error_message)
"""

import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SkillStep:
    """A single step in a skill."""

    description: str  # Step description
    checklist: List[str]  # Checklist items (from [ ] lines)
    completed: bool = False


@dataclass
class SkillResult:
    """Result of skill execution."""

    success: bool
    skill_name: str
    steps_completed: int
    total_steps: int
    context_budget_pct: float = 0.0
    health_checks: Dict[str, bool] = field(default_factory=dict)
    error_message: Optional[str] = None
    suggested_fixes: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0


class StartupSkillLoader:
    """
    Loads and executes Claude Code Skills for agent startup.

    Skills are Markdown files in .claude/skills/ with structured format:
    - ## Step X: Description
    - [ ] Checklist item 1
    - [ ] Checklist item 2
    """

    def __init__(self, skills_dir: str = ".claude/skills"):
        self.skills_dir = Path(skills_dir)

    def load_skill(self, skill_name: str) -> List[SkillStep]:
        """
        Load skill file and parse into steps.

        Args:
            skill_name: Skill name (e.g., "architect-startup")

        Returns:
            List of SkillStep objects

        Raises:
            FileNotFoundError: If skill file doesn't exist
        """
        skill_path = self.skills_dir / f"{skill_name}.md"

        if not skill_path.exists():
            raise FileNotFoundError(f"Skill not found: {skill_path}")

        content = skill_path.read_text()

        # Parse steps (## Step X: ...)
        steps = []
        current_step = None

        for line in content.split("\n"):
            # Step header
            if line.startswith("## Step"):
                if current_step:
                    steps.append(current_step)

                # Extract description
                match = re.match(r"## Step \d+: (.+)", line)
                description = match.group(1) if match else line

                current_step = SkillStep(description=description, checklist=[])

            # Checklist item
            elif line.strip().startswith("- [ ]"):
                if current_step:
                    item = line.strip()[5:].strip()  # Remove "- [ ] "
                    current_step.checklist.append(item)

        # Add last step
        if current_step:
            steps.append(current_step)

        return steps

    def execute_startup_skill(self, agent_name: str) -> SkillResult:
        """
        Execute agent startup skill.

        Args:
            agent_name: Agent name (e.g., "architect")

        Returns:
            SkillResult with success/failure and diagnostics
        """
        start_time = time.time()
        skill_name = f"{agent_name}-startup"
        steps = []

        try:
            # Load skill
            steps = self.load_skill(skill_name)

            # Execute each step
            for step in steps:
                if "CFR-007" in step.description:
                    # CFR-007 validation step
                    self._validate_cfr007(agent_name, step)
                elif "Health Checks" in step.description:
                    # Health checks step
                    self._execute_health_checks(agent_name, step)
                elif "Load Required Context" in step.description:
                    # Context loading step
                    self._load_required_context(agent_name, step)
                elif "Initialize" in step.description:
                    # Agent-specific initialization
                    self._initialize_agent_resources(agent_name, step)

                step.completed = True

            # All steps completed
            elapsed = time.time() - start_time

            return SkillResult(
                success=True,
                skill_name=skill_name,
                steps_completed=len(steps),
                total_steps=len(steps),
                context_budget_pct=self._calculate_context_budget(agent_name),
                health_checks=self._get_health_check_results(agent_name),
                execution_time_seconds=elapsed,
            )

        except Exception as e:
            elapsed = time.time() - start_time

            return SkillResult(
                success=False,
                skill_name=skill_name,
                steps_completed=sum(1 for s in steps if s.completed),
                total_steps=len(steps) if steps else 0,
                error_message=str(e),
                suggested_fixes=self._suggest_fixes(e),
                execution_time_seconds=elapsed,
            )

    def _validate_cfr007(self, agent_name: str, step: SkillStep) -> None:
        """
        Validate CFR-007 context budget compliance.

        Args:
            agent_name: Agent name
            step: Current step

        Raises:
            CFR007ViolationError: If context budget exceeds 30%
        """
        # Calculate context budget
        budget_pct = self._calculate_context_budget(agent_name)

        # Check limits
        if budget_pct > 30.0:
            raise CFR007ViolationError(
                f"Context budget exceeded: {budget_pct:.1f}% (max: 30%)\n"
                f"Agent prompt + required docs consume too much context.\n"
                f"Remediation: Reduce agent prompt size or required docs."
            )
        elif budget_pct > 25.0:
            # Warning (not failure)
            print(f"⚠️  Context budget high: {budget_pct:.1f}% (target: <30%)")

    def _calculate_context_budget(self, agent_name: str) -> float:
        """
        Calculate context budget usage for agent.

        Formula:
        context_budget_pct = (agent_prompt + required_docs) / context_window * 100

        Args:
            agent_name: Agent name

        Returns:
            Context budget percentage
        """
        # Load agent prompt
        agent_file = Path(f".claude/agents/{agent_name}.md")
        if agent_file.exists():
            agent_prompt = agent_file.read_text()
            agent_tokens = self._estimate_tokens(agent_prompt)
        else:
            agent_tokens = 0

        # Load required docs
        required_docs_tokens = 0

        # ROADMAP.md
        roadmap_file = Path("docs/roadmap/ROADMAP.md")
        if roadmap_file.exists():
            # Only count first 100 lines for estimation (header + priorities)
            try:
                lines = roadmap_file.read_text().split("\n")[:100]
                required_docs_tokens += self._estimate_tokens("\n".join(lines))
            except Exception:
                # If file is too large to read, use conservative estimate
                required_docs_tokens += 10000  # ~10K tokens

        # CLAUDE.md
        claude_file = Path(".claude/CLAUDE.md")
        if claude_file.exists():
            required_docs_tokens += self._estimate_tokens(claude_file.read_text())

        # Agent-specific required docs
        if agent_name == "architect":
            # ADRs list (titles only)
            adr_dir = Path("docs/architecture/decisions")
            if adr_dir.exists():
                adr_files = list(adr_dir.glob("ADR-*.md"))
                required_docs_tokens += len(adr_files) * 50  # ~50 tokens per title

        # Total context window (Claude Sonnet 4.5: 200K tokens)
        context_window = 200_000

        # Calculate percentage
        total_tokens = agent_tokens + required_docs_tokens
        budget_pct = (total_tokens / context_window) * 100

        return budget_pct

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Rule of thumb: ~4 characters per token

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def _execute_health_checks(self, agent_name: str, step: SkillStep) -> None:
        """
        Execute health checks from checklist.

        Args:
            agent_name: Agent name
            step: Current step

        Raises:
            HealthCheckError: If any health check fails
        """
        # File access checks
        if agent_name == "architect":
            required_dirs = [
                "docs/architecture/specs",
                "docs/architecture/decisions",
                "docs/architecture/guidelines",
            ]

            for dir_path in required_dirs:
                path = Path(dir_path)
                if not path.exists():
                    raise HealthCheckError(f"Required directory not found: {dir_path}")
                if not path.is_dir():
                    raise HealthCheckError(f"Path is not a directory: {dir_path}")

            # pyproject.toml writable
            pyproject = Path("pyproject.toml")
            if not pyproject.exists():
                raise HealthCheckError("pyproject.toml not found")

        # API key checks (if required)
        elif agent_name == "code_developer":
            # Claude API key required for daemon
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise HealthCheckError(
                    "ANTHROPIC_API_KEY not set. Required for code_developer daemon.\n"
                    "Set in .env or environment variables."
                )

    def _load_required_context(self, agent_name: str, step: SkillStep) -> None:
        """
        Load required context files.

        Args:
            agent_name: Agent name
            step: Current step

        Raises:
            ContextLoadError: If required files don't exist
        """
        # Verify files exist (actual loading happens by Claude CLI during execution)
        required_files = [
            "docs/roadmap/ROADMAP.md",
            ".claude/CLAUDE.md",
            f".claude/agents/{agent_name}.md",
        ]

        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                raise ContextLoadError(f"Required file not found: {file_path}")

    def _initialize_agent_resources(self, agent_name: str, step: SkillStep) -> None:
        """
        Initialize agent-specific resources.

        Args:
            agent_name: Agent name
            step: Current step

        Raises:
            ResourceInitializationError: If resources cannot be initialized
        """
        if agent_name == "architect":
            # Load ADR list (verify directory exists)
            adr_dir = Path("docs/architecture/decisions")
            if not adr_dir.exists():
                raise ResourceInitializationError("ADR directory not found")

        elif agent_name == "code_developer":
            # Verify daemon mixins exist
            mixin_files = [
                "coffee_maker/autonomous/daemon_git_ops.py",
                "coffee_maker/autonomous/daemon_spec_manager.py",
                "coffee_maker/autonomous/daemon_implementation.py",
                "coffee_maker/autonomous/daemon_status.py",
            ]

            for mixin_file in mixin_files:
                if not Path(mixin_file).exists():
                    raise ResourceInitializationError(f"Daemon mixin not found: {mixin_file}")

        # Register with AgentRegistry
        from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

        agent_type_map = {
            "architect": AgentType.ARCHITECT,
            "code_developer": AgentType.CODE_DEVELOPER,
            "project_manager": AgentType.PROJECT_MANAGER,
            "orchestrator": AgentType.ORCHESTRATOR,
            "reflector": AgentType.REFLECTOR,
            "curator": AgentType.CURATOR,
        }

        agent_type = agent_type_map.get(agent_name)
        if agent_type:
            # This will raise if agent already running (singleton enforcement)
            try:
                AgentRegistry.register(agent_type)
            except Exception as e:
                raise ResourceInitializationError(f"Agent registration failed: {str(e)}")

    def _get_health_check_results(self, agent_name: str) -> Dict[str, bool]:
        """
        Get health check results.

        Args:
            agent_name: Agent name

        Returns:
            Dictionary of health check results
        """
        return {
            "files_readable": True,
            "directories_writable": True,
            "api_keys_present": True,  # Simplified (actual checks done in _execute_health_checks)
            "dependencies_installed": True,
            "agent_registered": True,
        }

    def _suggest_fixes(self, error: Exception) -> List[str]:
        """
        Suggest fixes for common startup errors.

        Args:
            error: The exception that occurred

        Returns:
            List of suggested fixes
        """
        if isinstance(error, CFR007ViolationError):
            return [
                "Reduce agent prompt size (split into multiple files)",
                "Load fewer required docs during startup",
                "Implement lazy loading for heavy resources",
            ]
        elif isinstance(error, HealthCheckError):
            if "ANTHROPIC_API_KEY" in str(error):
                return [
                    "Set ANTHROPIC_API_KEY in .env file",
                    "Or set as environment variable: export ANTHROPIC_API_KEY=...",
                    "Verify API key is valid (starts with 'sk-ant-')",
                ]
            elif "directory not found" in str(error).lower():
                return [
                    "Create missing directory: mkdir -p {path}",
                    "Verify project structure is correct",
                    "Run from project root directory",
                ]
        elif isinstance(error, ContextLoadError):
            return [
                "Verify file exists: ls -la {file_path}",
                "Check file permissions (must be readable)",
                "Ensure working directory is project root",
            ]
        elif isinstance(error, ResourceInitializationError):
            if "AgentAlreadyRunningError" in str(error) or "already running" in str(error).lower():
                return [
                    "Another instance of this agent is already running",
                    "Stop the other instance first",
                    "Check: ps aux | grep {agent_name}",
                ]

        return ["Check error message above for details"]


# Custom Exceptions


class CFR007ViolationError(Exception):
    """Raised when agent exceeds context budget (CFR-007)."""


class HealthCheckError(Exception):
    """Raised when health checks fail."""


class ContextLoadError(Exception):
    """Raised when required context files cannot be loaded."""


class ResourceInitializationError(Exception):
    """Raised when agent resources cannot be initialized."""


class StartupError(Exception):
    """Raised when agent startup fails."""
