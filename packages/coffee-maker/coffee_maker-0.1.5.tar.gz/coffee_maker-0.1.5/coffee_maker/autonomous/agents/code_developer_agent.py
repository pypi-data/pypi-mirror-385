"""CodeDeveloperAgent - Autonomous implementation of ROADMAP priorities.

This agent is responsible for implementing priorities from ROADMAP.md autonomously.
It inherits from BaseAgent and implements continuous work loop that:
1. Syncs with roadmap branch (CFR-013)
2. Gets next planned priority
3. Checks spec exists (waits for architect if needed)
4. Implements priority using Claude API
5. Runs tests
6. Commits to roadmap branch
7. Notifies assistant for demo creation

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    CFR-008: Only architect creates technical specs
    CFR-011: Architect proactive spec creation (prevents blocking)
    CFR-013: All agents work on roadmap branch only
    US-056: CFR-013 enforcement implementation

Architecture:
    BaseAgent
      └── CodeDeveloperAgent
            ├── _do_background_work(): Implement next priority
            └── _handle_message(): Handle bug fixes, spec notifications

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Parse ROADMAP.md for next "📝 Planned" priority
    3. Check if technical spec exists
    4. If no spec: Send urgent message to architect, wait
    5. If spec exists: Implement priority using Claude API
    6. Run tests (pytest)
    7. Commit changes with agent identification
    8. Push to roadmap
    9. Send message to assistant: "Demo needed for priority X"
    10. Sleep for check_interval seconds (default: 5 minutes)

Message Handling:
    - bug_fix_request: Urgent fix from assistant after demo
    - spec_ready: Notification from architect that spec is ready
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent
from coffee_maker.autonomous.agents.code_developer_commit_review_mixin import CodeDeveloperCommitReviewMixin
from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface
from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.autonomous.roadmap_parser import RoadmapParser

logger = logging.getLogger(__name__)


class CodeDeveloperAgent(CodeDeveloperCommitReviewMixin, BaseAgent):
    """Code developer agent - Autonomous implementation execution.

    Responsibilities:
    - Implement priorities from ROADMAP (same as current daemon)
    - Stay on roadmap branch (CFR-013)
    - Frequent commits with agent identification
    - Notify assistant when features complete
    - Run tests before committing

    Continuous Loop:
    1. Sync with roadmap branch
    2. Get next planned priority
    3. Ensure spec exists (wait for architect if needed)
    4. Implement priority
    5. Run tests
    6. Commit changes
    7. Notify assistant for demo

    Example:
        >>> agent = CodeDeveloperAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=300  # 5 minutes
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 300,  # 5 minutes
        roadmap_file: str = "docs/roadmap/ROADMAP.md",
        auto_approve: bool = True,
    ):
        """Initialize CodeDeveloperAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between priority checks (default: 5 minutes)
            roadmap_file: Path to ROADMAP.md file
            auto_approve: Auto-approve implementation (default: True for daemon)
        """
        super().__init__(
            agent_type=AgentType.CODE_DEVELOPER,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.roadmap = RoadmapParser(roadmap_file)
        self.claude = ClaudeCLIInterface()
        self.auto_approve = auto_approve
        self.attempted_priorities: Dict[str, int] = {}
        self.max_retries = 3
        self._current_priority_name = None  # Track current priority for commit reviews

        logger.info(f"✅ CodeDeveloperAgent initialized (auto_approve={auto_approve})")

    def commit_changes(self, message: str, files: Optional[List[str]] = None):
        """Override commit_changes to send review request to architect.

        This method:
        1. Captures files changed BEFORE commit
        2. Calls parent's commit_changes (does the actual commit)
        3. Extracts commit SHA from git log
        4. Sends commit_review_request to architect (via mixin)

        Args:
            message: Commit message
            files: Optional list of specific files to commit
        """
        # STEP 1: Get list of changed files BEFORE commit
        import subprocess

        try:
            # Get staged + unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            files_changed = [f for f in result.stdout.strip().split("\n") if f]

            # Also get staged files
            result_staged = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            files_staged = [f for f in result_staged.stdout.strip().split("\n") if f]

            # Combine and deduplicate
            files_changed = list(set(files_changed + files_staged))

            if not files_changed:
                logger.warning("No files changed - skipping commit review request")
                # Still commit though
                super().commit_changes(message, files)
                return

        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            # Continue with commit anyway
            super().commit_changes(message, files)
            return

        # STEP 2: Commit changes (call parent)
        super().commit_changes(message, files)

        # STEP 3: Get commit SHA from git log
        try:
            result_sha = subprocess.run(
                ["git", "log", "-1", "--format=%H"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            commit_sha = result_sha.stdout.strip()

            if not commit_sha:
                logger.warning("Could not get commit SHA - skipping review request")
                return

        except Exception as e:
            logger.error(f"Error getting commit SHA: {e}")
            return

        # STEP 4: Send review request to architect (via mixin)
        try:
            self._after_commit_success(
                commit_sha=commit_sha,
                files_changed=files_changed,
                commit_message=message,
                priority_name=self._current_priority_name or "unknown",
            )
        except Exception as e:
            logger.error(f"Error sending commit review request: {e}")
            # Don't fail the commit if review request fails

    def _do_background_work(self):
        """Implement next planned priority from ROADMAP.

        Workflow:
        1. Sync with roadmap branch (pull latest)
        2. Parse ROADMAP for next planned priority
        3. Check if spec exists
           - If missing: Send urgent message to architect, return (wait)
           - If exists: Continue
        4. Implement priority using Claude API
        5. Run tests (pytest)
        6. Commit changes
        7. Push to roadmap
        8. Send message to assistant for demo
        9. Update metrics

        Returns early if:
        - No more planned priorities
        - Spec missing (wait for architect)
        - Implementation failed
        """
        # Sync with roadmap branch
        logger.info("🔄 Syncing with roadmap branch...")
        self.git.pull("roadmap")
        self.roadmap.reload()

        # Get next priority
        next_priority = self.roadmap.get_next_planned_priority()

        if not next_priority:
            logger.info("✅ No more planned priorities - all done!")
            self.current_task = None
            return

        priority_name = next_priority["name"]
        logger.info(f"📋 Next priority: {priority_name}")

        # Track current priority for commit reviews
        self._current_priority_name = priority_name

        # Update current task for status tracking
        self.current_task = {
            "type": "implementation",
            "priority": priority_name,
            "title": next_priority.get("title", ""),
            "started_at": datetime.now().isoformat(),
            "progress": 0.0,
        }

        # Check spec exists (CFR-008: architect creates specs)
        spec_file = self._find_spec(next_priority)
        if not spec_file:
            logger.warning(f"⚠️  Spec missing for {priority_name}")
            logger.info("📨 Sending urgent spec request to architect...")

            # Send urgent message to architect
            self.send_message_to_agent(
                to_agent=AgentType.ARCHITECT,
                message_type="spec_request",
                content={
                    "priority": next_priority,
                    "reason": "Implementation blocked - spec missing",
                    "requester": "code_developer",
                },
                priority="urgent",
            )

            logger.info("⏳ Waiting for architect to create spec... (will retry next iteration)")
            return  # Return and check again next iteration

        logger.info(f"✅ Spec found: {spec_file}")

        # Check retry limit
        attempt_count = self.attempted_priorities.get(priority_name, 0)
        if attempt_count >= self.max_retries:
            logger.warning(f"⏭️  Skipping {priority_name} - already attempted {attempt_count} times")
            return

        # Increment attempt counter
        self.attempted_priorities[priority_name] = attempt_count + 1
        logger.info(
            f"🚀 Starting implementation (attempt {self.attempted_priorities[priority_name]}/{self.max_retries})"
        )

        # Implement priority
        success = self._implement_priority(next_priority, spec_file)

        if success:
            # Notify assistant to create demo
            self._notify_assistant_demo_needed(next_priority)

            # Update metrics
            self.metrics["priorities_completed"] = self.metrics.get("priorities_completed", 0) + 1
            self.metrics["last_completed_priority"] = priority_name
            self.metrics["last_completion_time"] = datetime.now().isoformat()

            logger.info(f"✅ {priority_name} implementation complete!")
        else:
            logger.error(f"❌ Implementation failed for {priority_name}")

    def _implement_priority(self, priority: Dict, spec_file: Path) -> bool:
        """Implement a priority using Claude API.

        Args:
            priority: Priority dictionary from ROADMAP
            spec_file: Path to technical specification

        Returns:
            True if successful, False otherwise
        """
        priority_name = priority["name"]
        logger.info(f"⚙️  Implementing {priority_name}...")

        # Update task progress
        self.current_task["progress"] = 0.2
        self.current_task["step"] = "Loading prompt"

        # Load implementation prompt
        prompt = load_prompt(
            PromptNames.IMPLEMENT_FEATURE,
            {
                "PRIORITY_NAME": priority_name,
                "PRIORITY_TITLE": priority.get("title", ""),
                "SPEC_FILE": str(spec_file),
                "PRIORITY_CONTENT": priority.get("content", "")[:1000],
            },
        )

        # Update task progress
        self.current_task["progress"] = 0.3
        self.current_task["step"] = "Executing Claude API"

        # Execute with Claude
        logger.info("🤖 Executing Claude API...")
        try:
            result = self.claude.execute_prompt(prompt, timeout=3600)
            if not result or not getattr(result, "success", False):
                logger.error(f"Claude API failed: {getattr(result, 'error', 'Unknown error')}")
                return False
            logger.info(f"✅ Claude API complete")
        except Exception as e:
            logger.error(f"❌ Error executing Claude API: {e}")
            return False

        # Update task progress
        self.current_task["progress"] = 0.6
        self.current_task["step"] = "Checking changes"

        # Check if files changed
        if self.git.is_clean():
            logger.warning("⚠️  No files changed - priority may already be complete")
            return True  # Return True to avoid retry loop

        # Update task progress
        self.current_task["progress"] = 0.7
        self.current_task["step"] = "Running tests"

        # Run tests
        test_result = self._run_tests()
        if not test_result:
            logger.error("❌ Tests failed!")
            return False

        logger.info("✅ All tests passed")

        # Update task progress
        self.current_task["progress"] = 0.8
        self.current_task["step"] = "Committing changes"

        # Commit changes
        commit_message = f"feat: Implement {priority_name} - {priority.get('title', '')}"
        self.commit_changes(commit_message)

        logger.info("✅ Changes committed and pushed")

        # Update task progress
        self.current_task["progress"] = 1.0
        self.current_task["step"] = "Complete"

        return True

    def _find_spec(self, priority: Dict) -> Optional[Path]:
        """Find technical specification for a priority.

        Looks in:
        - docs/architecture/specs/SPEC-{us_number}-*.md (priority: US-104)
        - docs/architecture/specs/SPEC-{priority_number}-*.md (fallback)
        - docs/roadmap/PRIORITY_{priority_number}_TECHNICAL_SPEC.md

        Args:
            priority: Priority dictionary

        Returns:
            Path to spec file if found, None otherwise
        """
        import re

        priority_number = priority.get("number", "")
        priority_title = priority.get("title", "")

        if not priority_number:
            return None

        # Extract US number from title (e.g., "US-104" from "US-104 - Orchestrator...")
        us_match = re.search(r"US-(\d+)", priority_title)
        us_number = us_match.group(1) if us_match else None

        # Try architect's specs directory first (CFR-008)
        specs_dir = Path("docs/architecture/specs")
        if specs_dir.exists():
            patterns = []

            # PRIMARY: Try US number first (e.g., SPEC-104-*.md for US-104)
            if us_number:
                patterns.extend(
                    [
                        f"SPEC-{us_number}-*.md",  # SPEC-104-*.md
                        f"SPEC-{us_number.zfill(3)}-*.md",  # SPEC-104-*.md (padded)
                    ]
                )

            # FALLBACK: Try priority number (e.g., SPEC-20-*.md for PRIORITY 20)
            patterns.extend(
                [
                    f"SPEC-{priority_number}-*.md",  # SPEC-20-*.md
                    f"SPEC-{priority_number.replace('.', '-')}-*.md",  # SPEC-2-6-*.md
                    f"SPEC-{priority_number.zfill(5).replace('.', '-')}-*.md",  # SPEC-002-6-*.md (padded)
                ]
            )

            # Also try without dots/dashes for edge cases
            if "." in priority_number:
                major, minor = priority_number.split(".", 1)
                patterns.extend(
                    [
                        f"SPEC-{major.zfill(3)}-{minor}-*.md",  # SPEC-002-6-*.md
                        f"SPEC-{major}-{minor}-*.md",  # SPEC-2-6-*.md
                    ]
                )

            for pattern in patterns:
                for spec_file in specs_dir.glob(pattern):
                    logger.info(f"Found spec: {spec_file}")
                    return spec_file

        # Fallback: Check old strategic spec location
        roadmap_spec = Path(f"docs/roadmap/PRIORITY_{priority_number}_TECHNICAL_SPEC.md")
        if roadmap_spec.exists():
            return roadmap_spec

        return None

    def _run_tests(self) -> bool:
        """Run pytest test suite.

        Returns:
            True if tests pass, False otherwise
        """
        import subprocess

        logger.info("🧪 Running tests...")

        try:
            result = subprocess.run(
                ["pytest", "tests/unit/", "--ignore=tests/unit/_deprecated", "-q"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            if result.returncode == 0:
                logger.info("✅ Tests passed")
                return True
            else:
                logger.error(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")

                # Use test-failure-analysis skill (US-065)
                analysis = self._analyze_test_failures(
                    test_output=result.stdout + "\n" + result.stderr,
                    files_changed=self._get_changed_files(),
                    priority_name=self.current_task.get("priority", "UNKNOWN") if self.current_task else "UNKNOWN",
                )

                if analysis:
                    logger.info(f"📊 Test Failure Analysis:\n{analysis}")
                    self._save_test_analysis(analysis)

                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Tests timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ Error running tests: {e}")
            return False

    def _analyze_test_failures(self, test_output: str, files_changed: List[str], priority_name: str) -> Optional[str]:
        """Analyze test failures using test-failure-analysis skill.

        Args:
            test_output: Full pytest output (stdout + stderr)
            files_changed: List of files changed in current implementation
            priority_name: Current priority being implemented

        Returns:
            Analysis report string, or None if analysis failed
        """
        try:
            from coffee_maker.autonomous.skill_loader import load_skill, SkillNames

            # Load test-failure-analysis skill
            skill_content = load_skill(
                SkillNames.TEST_FAILURE_ANALYSIS,
                {
                    "TEST_OUTPUT": test_output,
                    "FILES_CHANGED": ", ".join(files_changed) if files_changed else "None",
                    "PRIORITY_NAME": priority_name,
                },
            )

            logger.info("📊 Analyzing test failures with skill...")

            # Execute with LLM
            from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

            claude = ClaudeCLIInterface()
            result = claude.execute_prompt(skill_content)

            if result and result.success:
                return result.content
            else:
                logger.warning(f"Test failure analysis failed: {result.error_message if result else 'Unknown error'}")
                return None

        except Exception as e:
            logger.error(f"Error during test failure analysis: {e}")
            return None

    def _get_changed_files(self) -> List[str]:
        """Get list of files changed in current git working directory.

        Returns:
            List of changed file paths
        """
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                return files
            else:
                logger.warning("Failed to get changed files from git")
                return []

        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []

    def _save_test_analysis(self, analysis: str):
        """Save test failure analysis to file for review.

        Args:
            analysis: Analysis report string
        """
        try:
            # Create analysis directory if needed
            analysis_dir = Path("data/test_analyses")
            analysis_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            priority_name = self.current_task.get("priority", "UNKNOWN") if self.current_task else "UNKNOWN"
            filename = f"test_analysis_{priority_name}_{timestamp}.md"

            analysis_file = analysis_dir / filename

            # Write analysis
            analysis_file.write_text(analysis)

            logger.info(f"📝 Test analysis saved to: {analysis_file}")

        except Exception as e:
            logger.error(f"Error saving test analysis: {e}")

    def _notify_assistant_demo_needed(self, priority: Dict):
        """Notify assistant that feature is complete and needs demo.

        Args:
            priority: Priority dictionary
        """
        self.send_message_to_agent(
            to_agent=AgentType.ASSISTANT,
            message_type="demo_request",
            content={
                "feature": priority["name"],
                "title": priority.get("title", ""),
                "acceptance_criteria": priority.get("acceptance_criteria", []),
                "description": priority.get("content", "")[:500],
            },
            priority="normal",
        )

        logger.info(f"📨 Notified assistant: demo needed for {priority['name']}")

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - tactical_feedback: Feedback from architect commit review (requires action)
        - bug_fix_request: Bug found during demo (from assistant)
        - spec_ready: Notification that spec is ready (from architect)

        Args:
            message: Message dictionary
        """
        msg_type = message.get("type")

        if msg_type == "tactical_feedback":
            # Tactical feedback from architect (via mixin)
            self._process_tactical_feedback(message)

        elif msg_type == "bug_fix_request":
            # Bug found by assistant during demo
            bug_info = message["content"]
            priority_name = bug_info.get("feature", "unknown")

            logger.info(f"🐛 Bug fix request for {priority_name}")
            logger.info(f"Bug details: {bug_info.get('description', 'No description')}")

            # TODO: Implement bug fix logic
            # For now, just log and continue
            logger.warning("Bug fix not yet implemented - will be added in Phase 3")

        elif msg_type == "spec_ready":
            # Spec is now ready, can retry implementation
            priority_name = message["content"].get("priority", "unknown")
            logger.info(f"✅ Spec ready for {priority_name} - will retry next iteration")

        else:
            logger.warning(f"Unknown message type: {msg_type}")
