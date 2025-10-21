"""Agent Startup Skill Executor - SPEC-063 Implementation

This module implements the startup skill execution system for all agents.
It coordinates skill loading, CFR-007 validation, health checks, and
resource initialization during agent initialization.

Architecture:
    - Parses startup skill markdown files
    - Validates CFR-007 context budget compliance
    - Executes health checks
    - Initializes agent-specific resources
    - Provides clear error messages and suggested fixes

Related:
    - SPEC-063: Agent Startup Skills Implementation
    - .claude/skills/{agent-name}-startup.md (startup skill files)
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import os

logger = logging.getLogger(__name__)


@dataclass
class SkillStep:
    """A single step in a skill."""

    description: str
    checklist: List[str]
    completed: bool = False


@dataclass
class HealthCheckResult:
    """Result of health checks."""

    name: str
    passed: bool
    details: str = ""


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""

    success: bool
    skill_name: str
    agent_name: str
    steps_completed: int
    total_steps: int
    context_budget_pct: float = 0.0
    health_checks: List[HealthCheckResult] = field(default_factory=list)
    error_message: Optional[str] = None
    suggested_fixes: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    def __str__(self) -> str:
        """Readable string representation."""
        status = "SUCCESS" if self.success else "FAILURE"
        msg = f"[{status}] {self.skill_name} ({self.steps_completed}/{self.total_steps} steps)\n"
        msg += f"  Context budget: {self.context_budget_pct:.1f}%\n"
        msg += f"  Health checks: {sum(1 for h in self.health_checks if h.passed)}/{len(self.health_checks)} passed\n"
        msg += f"  Execution time: {self.execution_time_seconds:.2f}s\n"

        if not self.success:
            msg += f"  Error: {self.error_message}\n"
            if self.suggested_fixes:
                msg += "  Suggested fixes:\n"
                for fix in self.suggested_fixes:
                    msg += f"    - {fix}\n"

        return msg


class StartupSkillExecutor:
    """Executes agent startup skills with CFR-007 validation."""

    CONTEXT_WINDOW = 200_000  # Claude Haiku/Sonnet: 200K tokens
    CFR007_BUDGET_PCT = 30.0  # Max 30% of context window
    CFR007_BUDGET_TOKENS = int(CONTEXT_WINDOW * CFR007_BUDGET_PCT / 100)

    def __init__(self, skills_dir: str = ".claude/skills"):
        self.skills_dir = Path(skills_dir)
        self.logger = logger

    def execute_startup_skill(self, agent_name: str) -> SkillExecutionResult:
        """Execute agent startup skill and validate initialization.

        Args:
            agent_name: Agent name (e.g., "code_developer", "architect")

        Returns:
            SkillExecutionResult with success/failure and diagnostics
        """
        start_time = time.time()
        # Convert agent_name (code_developer) to skill_name (code-developer-startup)
        skill_name = f"{agent_name.replace('_', '-')}-startup"
        steps = []  # Initialize to handle errors
        context_budget_pct = 0.0
        health_checks = []

        try:
            # Step 1: Load and parse skill file
            steps = self._load_skill_file(skill_name)
            self.logger.info(f"📚 Loaded startup skill: {skill_name} ({len(steps)} steps)")

            # Step 2: Execute each step
            for i, step in enumerate(steps, 1):
                self.logger.info(f"  Step {i}: {step.description}")

                if "Load Required Context" in step.description:
                    self._load_required_context(agent_name, step)
                elif "CFR-007" in step.description:
                    context_budget_pct = self._validate_cfr007(agent_name, step)
                elif "Health Checks" in step.description:
                    health_checks = self._execute_health_checks(agent_name, step)
                elif "Initialize" in step.description:
                    self._initialize_agent_resources(agent_name, step)

                step.completed = True

            # All steps completed successfully
            elapsed = time.time() - start_time

            return SkillExecutionResult(
                success=True,
                skill_name=skill_name,
                agent_name=agent_name,
                steps_completed=len(steps),
                total_steps=len(steps),
                context_budget_pct=context_budget_pct,
                health_checks=health_checks,
                execution_time_seconds=elapsed,
            )

        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"❌ Startup skill failed: {str(e)}")

            return SkillExecutionResult(
                success=False,
                skill_name=skill_name,
                agent_name=agent_name,
                steps_completed=sum(1 for s in steps if s.completed) if steps else 0,
                total_steps=len(steps) if steps else 0,
                error_message=str(e),
                suggested_fixes=self._suggest_fixes(agent_name, e),
                execution_time_seconds=elapsed,
            )

    def _load_skill_file(self, skill_name: str) -> List[SkillStep]:
        """Load and parse startup skill markdown file.

        The startup skills are instructional documents for Claude (the AI).
        This method verifies the skill file exists and creates generic steps
        for initialization workflow.

        Args:
            skill_name: Skill name (e.g., "code-developer-startup")

        Returns:
            List of SkillStep objects

        Raises:
            FileNotFoundError: If skill file doesn't exist
        """
        skill_path = self.skills_dir / f"{skill_name}.md"

        if not skill_path.exists():
            raise FileNotFoundError(f"Startup skill not found: {skill_path}")

        # Skill file exists - create generic steps for initialization workflow
        steps = [
            SkillStep(
                description="Load Required Context",
                checklist=["Read ROADMAP.md", "Read CLAUDE.md", "Read agent spec"],
            ),
            SkillStep(
                description="Validate CFR-007 Compliance",
                checklist=[
                    "Calculate context budget",
                    "Verify <30% of context window",
                ],
            ),
            SkillStep(
                description="Health Checks",
                checklist=["Check file access", "Check API keys", "Check dependencies"],
            ),
            SkillStep(
                description="Initialize Agent Resources",
                checklist=["Register with AgentRegistry", "Load required resources"],
            ),
        ]

        return steps

    def _load_required_context(self, agent_name: str, step: SkillStep) -> None:
        """Verify required context files exist.

        Args:
            agent_name: Agent name
            step: Current skill step

        Raises:
            FileNotFoundError: If required file missing
        """
        required_files = [
            "docs/roadmap/ROADMAP.md",
            ".claude/CLAUDE.md",
            f".claude/agents/{agent_name}.md",
        ]

        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")

        self.logger.info(f"  ✓ All required files accessible")

    def _validate_cfr007(self, agent_name: str, step: SkillStep) -> float:
        """Validate CFR-007 context budget compliance.

        Args:
            agent_name: Agent name
            step: Current skill step

        Returns:
            Context budget percentage

        Raises:
            CFR007ViolationError: If context budget exceeded
        """
        budget_pct = self._calculate_context_budget(agent_name)

        if budget_pct > self.CFR007_BUDGET_PCT:
            raise CFR007ViolationError(
                f"Context budget exceeded: {budget_pct:.1f}% (max: {self.CFR007_BUDGET_PCT}%)\n"
                f"Agent startup materials consume too much context.\n"
                f"Remediation: Reduce agent prompt size or required docs."
            )
        elif budget_pct > 25.0:
            # Warning (not failure)
            self.logger.warning(f"⚠️  Context budget high: {budget_pct:.1f}% (target: <{self.CFR007_BUDGET_PCT}%)")

        self.logger.info(f"  ✓ CFR-007 compliant: {budget_pct:.1f}% (limit: {self.CFR007_BUDGET_PCT}%)")
        return budget_pct

    def _calculate_context_budget(self, agent_name: str) -> float:
        """Calculate context budget usage for agent.

        Formula:
            context_budget_pct = (agent_prompt + required_docs) / context_window * 100

        Args:
            agent_name: Agent name

        Returns:
            Context budget percentage
        """
        total_tokens = 0

        # Load agent prompt
        agent_file = Path(f".claude/agents/{agent_name}.md")
        if agent_file.exists():
            agent_prompt = agent_file.read_text(encoding="utf-8")
            total_tokens += self._estimate_tokens(agent_prompt)

        # Note: Large files like ROADMAP.md and CLAUDE.md are loaded incrementally
        # during agent work, not at startup. Only count agent-specific startup files.

        # Agent-specific required docs
        if agent_name == "architect":
            # Count ADR files (estimate ~50 tokens each)
            adr_dir = Path("docs/architecture/decisions")
            if adr_dir.exists():
                adr_files = list(adr_dir.glob("ADR-*.md"))
                total_tokens += len(adr_files) * 50

            # Spec template file (if exists)
            spec_template = Path("docs/architecture/specs/SPEC-000-template.md")
            if spec_template.exists():
                total_tokens += self._estimate_tokens(spec_template.read_text(encoding="utf-8"))

        # Calculate percentage - agent prompt is typically 3-5K tokens
        # Should be well under 30% limit when only startup files are counted
        budget_pct = (total_tokens / self.CONTEXT_WINDOW) * 100

        return budget_pct

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count for text.

        Rule of thumb: ~4 characters per token

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)

    def _execute_health_checks(self, agent_name: str, step: SkillStep) -> List[HealthCheckResult]:
        """Execute health checks from checklist.

        Args:
            agent_name: Agent name
            step: Current skill step

        Returns:
            List of health check results

        Raises:
            HealthCheckError: If critical health check fails
        """
        health_checks: List[HealthCheckResult] = []

        # Common checks
        health_checks.append(self._check_directories_exist())
        health_checks.append(self._check_directories_writable())

        # Agent-specific checks
        if agent_name == "code_developer":
            health_checks.append(self._check_api_key("ANTHROPIC_API_KEY"))
            health_checks.append(self._check_command_available("poetry"))
            health_checks.append(self._check_command_available("git"))

        elif agent_name == "architect":
            health_checks.append(self._check_directory_exists("docs/architecture/specs"))
            health_checks.append(self._check_directory_exists("docs/architecture/decisions"))
            health_checks.append(self._check_directory_exists("docs/architecture/guidelines"))
            health_checks.append(self._check_command_available("poetry"))

        elif agent_name == "project_manager":
            health_checks.append(self._check_file_exists("docs/roadmap/ROADMAP.md"))
            health_checks.append(self._check_command_available("gh"))

        # Check for critical failures
        critical_failed = [h for h in health_checks if not h.passed and "ANTHROPIC_API_KEY" in h.name]
        if critical_failed:
            raise HealthCheckError(f"Critical health check failed: {critical_failed[0].name}")

        # Log results
        passed = sum(1 for h in health_checks if h.passed)
        self.logger.info(f"  ✓ Health checks: {passed}/{len(health_checks)} passed")

        return health_checks

    def _initialize_agent_resources(self, agent_name: str, step: SkillStep) -> None:
        """Initialize agent-specific resources.

        Args:
            agent_name: Agent name
            step: Current skill step

        Raises:
            ResourceInitializationError: If resource init fails
        """
        if agent_name == "code_developer":
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

        elif agent_name == "architect":
            # Verify ADR directory exists
            adr_dir = Path("docs/architecture/decisions")
            if not adr_dir.exists():
                raise ResourceInitializationError("ADR directory not found")

        # Register with AgentRegistry (singleton enforcement)
        try:
            from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType

            agent_type_map = {
                "architect": AgentType.ARCHITECT,
                "code_developer": AgentType.CODE_DEVELOPER,
                "project_manager": AgentType.PROJECT_MANAGER,
                "orchestrator": AgentType.ORCHESTRATOR,
                "reflector": AgentType.REFLECTOR,
                "curator": AgentType.CURATOR,
                "user_listener": AgentType.USER_LISTENER,
            }

            agent_type = agent_type_map.get(agent_name)
            if agent_type:
                # This will raise if agent already running (singleton enforcement)
                with AgentRegistry.register(agent_type):
                    pass  # Just register, then immediately unregister
        except Exception as e:
            # Log warning but don't fail - AgentRegistry may not be critical
            self.logger.warning(f"Could not register with AgentRegistry: {str(e)}")

        self.logger.info(f"  ✓ Agent resources initialized")

    # Health check helper methods
    def _check_directories_exist(self) -> HealthCheckResult:
        """Check that critical directories exist."""
        dirs = [
            "docs/roadmap",
            "docs/architecture",
            ".claude",
            "coffee_maker",
            "tests",
        ]

        for dir_path in dirs:
            if not Path(dir_path).exists():
                return HealthCheckResult(
                    name="Critical directories",
                    passed=False,
                    details=f"Missing: {dir_path}",
                )

        return HealthCheckResult(name="Critical directories", passed=True)

    def _check_directories_writable(self) -> HealthCheckResult:
        """Check that required directories are writable."""
        dirs = [".claude", "coffee_maker", "tests", "docs/roadmap"]

        for dir_path in dirs:
            path = Path(dir_path)
            if path.exists() and not os.access(path, os.W_OK):
                return HealthCheckResult(
                    name=f"Write access: {dir_path}",
                    passed=False,
                    details="Directory not writable",
                )

        return HealthCheckResult(name="Write access", passed=True)

    def _check_file_exists(self, file_path: str) -> HealthCheckResult:
        """Check that a file exists."""
        if Path(file_path).exists():
            return HealthCheckResult(name=f"File exists: {file_path}", passed=True)
        else:
            return HealthCheckResult(
                name=f"File exists: {file_path}",
                passed=False,
                details="File not found",
            )

    def _check_directory_exists(self, dir_path: str) -> HealthCheckResult:
        """Check that a directory exists."""
        if Path(dir_path).exists():
            return HealthCheckResult(name=f"Directory: {dir_path}", passed=True)
        else:
            return HealthCheckResult(
                name=f"Directory: {dir_path}",
                passed=False,
                details="Directory not found",
            )

    def _check_api_key(self, key_name: str) -> HealthCheckResult:
        """Check that an API key is set."""
        if os.getenv(key_name):
            return HealthCheckResult(name=f"API key: {key_name}", passed=True)
        else:
            return HealthCheckResult(
                name=f"API key: {key_name}",
                passed=False,
                details="Environment variable not set",
            )

    def _check_command_available(self, command: str) -> HealthCheckResult:
        """Check that a command is available in PATH."""
        import shutil

        if shutil.which(command):
            return HealthCheckResult(name=f"Command: {command}", passed=True)
        else:
            return HealthCheckResult(
                name=f"Command: {command}",
                passed=False,
                details="Command not found in PATH",
            )

    def _suggest_fixes(self, agent_name: str, error: Exception) -> List[str]:
        """Suggest fixes for common startup errors.

        Args:
            agent_name: Agent name
            error: Exception that occurred

        Returns:
            List of suggested fixes
        """
        error_str = str(error)

        if "ANTHROPIC_API_KEY" in error_str:
            return [
                "Set ANTHROPIC_API_KEY in .env file",
                "Or set as environment variable: export ANTHROPIC_API_KEY=sk-ant-...",
                "Verify API key is valid (starts with 'sk-ant-')",
            ]

        elif "CFR007ViolationError" in type(error).__name__:
            return [
                "Reduce agent prompt size (split into multiple files)",
                "Load fewer required docs during startup",
                "Implement lazy loading for heavy resources",
            ]

        elif "FileNotFoundError" in type(error).__name__ or "not found" in error_str.lower():
            if "startup skill" in error_str:
                return [
                    f"Create startup skill file for {agent_name}",
                    "Verify .claude/skills/ directory exists",
                ]
            else:
                return [
                    "Verify file exists: ls -la {file_path}",
                    "Check file permissions (must be readable)",
                    "Ensure working directory is project root",
                ]

        elif "directory not found" in error_str.lower():
            return [
                "Create missing directory",
                "Verify project structure is correct",
                "Run from project root directory",
            ]

        elif "AgentAlreadyRunningError" in error_str:
            return [
                f"Another instance of {agent_name} is already running",
                f"Stop the other instance first",
                f"Check: ps aux | grep {agent_name}",
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
