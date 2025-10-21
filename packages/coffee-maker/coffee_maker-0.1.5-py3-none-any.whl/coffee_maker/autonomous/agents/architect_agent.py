"""ArchitectAgent - Proactive technical specification creation.

This agent is responsible for creating technical specifications BEFORE code_developer
needs them, ensuring code_developer is never blocked waiting for specs.

Architecture:
    BaseAgent
      └── ArchitectAgent
            ├── _do_background_work(): Proactive spec creation
            └── _handle_message(): Urgent spec requests from code_developer

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    CFR-008: Only architect creates technical specs
    CFR-011: Architect proactive spec creation (prevents blocking)
    CFR-013: All agents work on roadmap branch only
    US-057: Strategic requirement for multi-agent system

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Parse ROADMAP.md for planned priorities
    3. For each priority WITHOUT a spec:
       - Check if it needs a technical spec (complexity-based)
       - Create specification using Claude API
       - Document decision in ADR (Architectural Decision Record)
       - Commit changes
    4. Sleep for check_interval seconds (default: 1 hour)

Message Handling:
    - spec_request (urgent): Immediate spec creation from code_developer
    - design_review: Reactive design guidance from other agents

Message Format:
    {
        "type": "spec_request",
        "priority": "urgent" or "normal",
        "content": {
            "priority": priority_dict,
            "reason": "Implementation blocked - spec missing",
            "requester": "code_developer"
        }
    }
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent
from coffee_maker.autonomous.agents.architect_skills_mixin import ArchitectSkillsMixin

logger = logging.getLogger(__name__)


class ArchitectAgent(ArchitectSkillsMixin, BaseAgent):
    """Architect agent - Proactive technical specification creation.

    Responsibilities:
    - Proactively create technical specs for planned priorities (CFR-011)
    - Respond urgently to spec requests from code_developer (CFR-012)
    - Document architectural decisions (ADRs)
    - Manage dependencies in pyproject.toml
    - Provide design guidance to other agents

    Key Insight (CFR-011 - Proactive Spec Creation):
        Architect doesn't wait for code_developer to request specs.
        Instead, it continuously creates specs for planned priorities,
        ensuring code_developer NEVER blocks on missing specs.

    Example:
        >>> agent = ArchitectAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=3600  # 1 hour
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 3600,  # 1 hour for proactive spec creation
        roadmap_file: str = "docs/roadmap/ROADMAP.md",
    ):
        """Initialize ArchitectAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between spec creation checks (default: 1 hour)
            roadmap_file: Path to ROADMAP.md file
        """
        super().__init__(
            agent_type=AgentType.ARCHITECT,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        self.roadmap_file = roadmap_file
        self.specs_dir = Path("docs/architecture/specs")
        self.adrs_dir = Path("docs/architecture/decisions")

        # Create directories if they don't exist
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.adrs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ ArchitectAgent initialized (proactive spec creation)")

    def _do_background_work(self):
        """Architect's background work: skills integration + proactive spec creation.

        Workflow (Enhanced with Skills):
        1. Process commit review requests (CRITICAL priority)
        2. Run weekly refactoring analysis (if Monday + >7 days)
        3. Pull latest from roadmap
        4. Parse ROADMAP for planned priorities
        5. For each priority without a spec:
           - Run architecture reuse check (MANDATORY)
           - Determine if spec is needed (complexity-based)
           - Create specification
           - Document in ADR
           - Commit changes
        6. Sleep for check_interval

        This ensures code_developer always has specs available.
        """
        # STEP 1 & 2: Enhanced background work from mixin (commit reviews + refactoring)
        self._enhanced_background_work()

        # STEP 3+: Original proactive spec creation
        logger.info("🏗️  Architect: Checking for specs to create...")

        # Sync with roadmap branch
        logger.info("🔄 Syncing with roadmap branch...")
        self.git.pull("roadmap")

        # Parse ROADMAP for priorities
        from coffee_maker.autonomous.roadmap_parser import RoadmapParser

        roadmap = RoadmapParser(self.roadmap_file)

        # Get all planned priorities
        priorities = roadmap.get_priorities()
        planned = [p for p in priorities if "planned" in p["status"].lower() or "📝" in p["status"]]

        logger.info(f"Found {len(planned)} planned priorities to check for specs")

        # Check each planned priority for missing specs
        for priority in planned:
            priority_number = priority.get("number", "")
            priority_name = priority.get("name", "")

            if not priority_number:
                continue

            # Check if spec already exists
            spec_file = self._find_existing_spec(priority_number)

            if spec_file:
                logger.info(f"✅ Spec exists for {priority_name}: {spec_file.name}")
                continue

            # Spec missing - create it!
            logger.warning(f"📝 Creating spec for {priority_name}")
            self._create_spec_for_priority(priority)
            break  # Create one spec per iteration

        # Update metrics
        self.metrics["specs_created"] = self.metrics.get("specs_created", 0)
        self.metrics["last_check"] = datetime.now().isoformat()

        # Update current task
        self.current_task = {
            "type": "spec_creation",
            "status": "idle",
            "last_check": datetime.now().isoformat(),
        }

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - commit_review_request: Code_developer commit needs review (handled in background work)
        - spec_request (urgent): Code_developer blocked on missing spec
        - design_review: Request for design guidance
        - dependency_check: Request for dependency management

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")
        msg_priority = message.get("priority", "normal")

        if msg_type == "commit_review_request":
            # Commit review requests are handled by _process_commit_reviews() in background work
            # Just log it here for visibility
            commit_sha = message.get("content", {}).get("commit_sha", "unknown")
            logger.info(f"📬 Commit review request queued: {commit_sha[:7]} (priority: {msg_priority})")
            # Review will be processed in next background work iteration

        elif msg_type == "spec_request":
            # Urgent spec request from code_developer
            priority_info = message.get("content", {}).get("priority", {})
            priority_name = priority_info.get("name", "unknown")

            logger.warning(f"🚨 URGENT spec request from code_developer for {priority_name}")

            if msg_priority == "urgent":
                logger.info(f"Creating spec for {priority_name} (URGENT)...")
                # Create spec immediately
                self._create_spec_for_priority(priority_info)

                # Notify code_developer that spec is ready
                self.send_message_to_agent(
                    to_agent=AgentType.CODE_DEVELOPER,
                    message_type="spec_ready",
                    content={
                        "priority": priority_name,
                        "spec_file": f"SPEC-{priority_info.get('number', 'unknown')}-*.md",
                    },
                    priority="normal",
                )

                logger.info(f"✅ Spec created for {priority_name}, notified code_developer")

        elif msg_type == "design_review":
            # Request for design guidance
            feature = message.get("content", {}).get("feature", "unknown")
            logger.info(f"Design review requested for {feature}")
            # In Phase 3: Implement design review logic

        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def _find_existing_spec(self, priority_number: str) -> Optional[Path]:
        """Find existing technical specification for a priority.

        Args:
            priority_number: Priority number (e.g., "9", "2.6")

        Returns:
            Path to spec file if found, None otherwise
        """
        # Try architect's specs directory (CFR-008)
        specs_dir = self.specs_dir
        if specs_dir.exists():
            # Try multiple patterns
            patterns = [
                f"SPEC-{priority_number}-*.md",
                f"SPEC-{priority_number.replace('.', '-')}-*.md",
                f"SPEC-{priority_number.zfill(3)}-*.md",
            ]

            # Also try without dots/dashes for edge cases
            if "." in priority_number:
                major, minor = priority_number.split(".", 1)
                patterns.extend(
                    [
                        f"SPEC-{major.zfill(3)}-{minor}-*.md",
                        f"SPEC-{major}-{minor}-*.md",
                    ]
                )

            for pattern in patterns:
                for spec_file in specs_dir.glob(pattern):
                    return spec_file

        return None

    def _create_spec_for_priority(self, priority: Dict):
        """Create technical specification for a priority using Claude.

        MANDATORY STEPS (in order):
        1. Enforce CFR-011 (architect must read code-searcher reports + analyze codebase)
        2. Run architecture reuse check BEFORE creating spec

        Args:
            priority: Priority dictionary from ROADMAP
        """
        priority_name = priority.get("name", "unknown")
        priority_number = priority.get("number", "unknown")
        priority_title = priority.get("title", "")
        priority_content = priority.get("content", "")

        logger.info(f"📝 Creating spec for {priority_name}: {priority_title}")

        # CFR-011: Enforce daily integration before creating specs
        from coffee_maker.autonomous.architect_daily_routine import ArchitectDailyRoutine, CFR011ViolationError

        try:
            routine = ArchitectDailyRoutine()
            routine.enforce_cfr_011()
            logger.info("✅ CFR-011 compliance verified - proceeding with spec creation")
        except CFR011ViolationError as e:
            logger.error(f"❌ CFR-011 violation detected: {e}")

            # Create notification for user
            try:
                from coffee_maker.cli.notifications import NotificationDB

                notifications = NotificationDB()
                notifications.create_notification(
                    type="cfr_violation",
                    title=f"CFR-011 Violation: Cannot Create Spec for {priority_name}",
                    message=str(e),
                    priority="critical",
                    context={
                        "priority_name": priority_name,
                        "enforcement": "CFR-011",
                        "action_required": "architect must complete daily integration",
                    },
                    sound=False,  # CFR-009: architect is background agent
                    agent_id="architect",
                )
            except Exception as notify_error:
                logger.error(f"Failed to create notification: {notify_error}")

            # Block spec creation - return early
            logger.error(f"⛔ Blocking spec creation for {priority_name} until CFR-011 compliant")
            return

        # Update current task
        self.current_task = {
            "type": "spec_creation",
            "priority": priority_name,
            "started_at": datetime.now().isoformat(),
            "progress": 0.1,
        }

        # MANDATORY: Run architecture reuse check BEFORE spec creation
        logger.info(f"🔍 Running MANDATORY architecture reuse check for {priority_name}")
        reuse_analysis = self._run_architecture_reuse_check_before_spec(priority)

        # Update progress
        self.current_task["progress"] = 0.3

        # US-050: Extract requirements and check if POC needed
        requirements = self._extract_requirements_from_priority(priority)
        effort_hours = requirements.get("estimated_effort_hours", 0)
        complexity = requirements.get("technical_complexity", "unknown")

        # Check if POC should be created (US-050)
        needs_poc = self._should_create_poc(effort_hours, complexity)
        poc_dir = None

        if needs_poc:
            logger.info(f"🔬 POC required for {priority_name} (effort: {effort_hours}h, complexity: {complexity})")
            poc_dir = self._create_poc(priority, requirements)
            if poc_dir:
                logger.info(f"✅ POC created: {poc_dir}")
                logger.info("⚠️ Note: POC skeleton created, architect should implement POC code manually")
            else:
                logger.warning("⚠️ POC creation failed, continuing with spec creation")

        # Load prompt
        from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

        # Include reuse analysis in the spec creation context
        poc_reference = ""
        if poc_dir:
            poc_reference = f"""

## 🔬 Proof of Concept

A POC has been created for this priority at: `{poc_dir}/`

The technical spec should reference this POC and explain what it proves.
"""

        spec_context = f"""{priority_content[:1500]}

## 🔍 Architecture Reuse Analysis

{reuse_analysis}

**IMPORTANT**: Use components from the reuse analysis above when creating this spec.
{poc_reference}
"""

        prompt = load_prompt(
            PromptNames.CREATE_TECHNICAL_SPEC,
            {
                "PRIORITY_NAME": priority_name,
                "PRIORITY_TITLE": priority_title,
                "PRIORITY_CONTENT": spec_context,
                "SPEC_NUMBER": priority_number,
            },
        )

        # Update progress
        self.current_task["progress"] = 0.4

        # Execute with Claude
        from coffee_maker.autonomous.claude_cli_interface import ClaudeCLIInterface

        claude = ClaudeCLIInterface()
        logger.info("🤖 Executing Claude API for spec creation...")

        try:
            result = claude.execute_prompt(prompt, timeout=3600)
            if not result or not getattr(result, "success", False):
                logger.error(f"Claude API failed: {getattr(result, 'error', 'Unknown error')}")
                return
            logger.info("✅ Claude API complete")
        except Exception as e:
            logger.error(f"❌ Error executing Claude API: {e}")
            return

        # Update progress
        self.current_task["progress"] = 0.8

        # Commit changes
        commit_message = f"docs: Add technical spec for {priority_name} - {priority_title}"
        self.commit_changes(commit_message)

        logger.info(f"✅ Spec created and committed for {priority_name}")

        # Update metrics
        self.metrics["specs_created"] = self.metrics.get("specs_created", 0) + 1
        self.metrics["last_spec_created"] = priority_name
        self.metrics["last_spec_time"] = datetime.now().isoformat()

        # Update progress
        self.current_task["progress"] = 1.0
        self.current_task["status"] = "complete"

    def _should_create_poc(self, effort_hours: float, complexity: str) -> bool:
        """Determine if POC creation is needed using decision matrix.

        Decision Matrix:
        - Effort >16 hours (>2 days) AND Complexity = High → POC REQUIRED
        - Effort >16 hours AND Complexity = Medium → MAYBE (default: no)
        - All other cases → No POC

        Args:
            effort_hours: Estimated implementation effort in hours
            complexity: Technical complexity ("low", "medium", "high")

        Returns:
            True if POC should be created, False otherwise

        Example:
            >>> agent._should_create_poc(20, "high")
            True
            >>> agent._should_create_poc(10, "high")
            False
            >>> agent._should_create_poc(20, "medium")
            False
        """
        complexity_lower = complexity.lower()

        # Effort > 2 days (16 hours) AND complexity = High → POC REQUIRED
        if effort_hours > 16 and complexity_lower == "high":
            logger.info(f"✅ POC REQUIRED: effort={effort_hours}h (>16), complexity={complexity} → Creating POC")
            return True

        # Effort > 2 days AND complexity = Medium → MAYBE (ask user in future, default: no)
        if effort_hours > 16 and complexity_lower == "medium":
            logger.info(f"⚠️ POC MAYBE: effort={effort_hours}h (>16), complexity={complexity} → Defaulting to NO")
            # TODO: Ask user via user_listener (US-051 future enhancement)
            return False

        # All other cases → No POC
        logger.info(f"❌ POC NOT NEEDED: effort={effort_hours}h, complexity={complexity}")
        return False

    def _create_poc(self, priority: Dict, requirements: Dict) -> Optional[Path]:
        """Create POC directory and files from template.

        Creates:
        1. POC directory: docs/architecture/pocs/POC-{number}-{slug}/
        2. README.md from template
        3. Skeleton Python files (future enhancement)

        Args:
            priority: Priority dictionary from ROADMAP
            requirements: Requirements dict with title, effort_hours, complexity

        Returns:
            Path to POC directory if created, None on error

        Example:
            >>> priority = {"number": "055", "name": "US-055"}
            >>> requirements = {
            ...     "title": "Claude Skills Integration",
            ...     "estimated_effort_hours": 84,
            ...     "technical_complexity": "high"
            ... }
            >>> poc_dir = agent._create_poc(priority, requirements)
            >>> print(poc_dir)
            docs/architecture/pocs/POC-055-claude-skills-integration/
        """
        from coffee_maker.utils.file_io import slugify

        priority_number = priority.get("number", "unknown")
        title = requirements.get("title", "unknown")
        feature_slug = slugify(title)

        # Create POC directory
        poc_dir = Path(f"docs/architecture/pocs/POC-{priority_number}-{feature_slug}")

        try:
            poc_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created POC directory: {poc_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create POC directory: {e}")
            return None

        # Generate README from template
        readme_content = self._generate_poc_readme(priority, requirements)

        try:
            readme_path = poc_dir / "README.md"
            readme_path.write_text(readme_content, encoding="utf-8")
            logger.info(f"📝 Created POC README: {readme_path}")
        except Exception as e:
            logger.error(f"❌ Failed to write POC README: {e}")
            return None

        # Copy template Python files
        try:
            template_dir = Path("docs/architecture/pocs/POC-000-template")
            if template_dir.exists():
                # Copy example_component.py
                example_py = template_dir / "example_component.py"
                if example_py.exists():
                    dest_py = poc_dir / "example_component.py"
                    dest_py.write_text(example_py.read_text(encoding="utf-8"), encoding="utf-8")
                    logger.info(f"📄 Copied example_component.py to {dest_py}")

                # Copy test_poc.py
                test_py = template_dir / "test_poc.py"
                if test_py.exists():
                    dest_test = poc_dir / "test_poc.py"
                    dest_test.write_text(test_py.read_text(encoding="utf-8"), encoding="utf-8")
                    logger.info(f"📄 Copied test_poc.py to {dest_test}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to copy template files (non-critical): {e}")

        logger.info(f"✅ POC created: {poc_dir}")
        logger.info("🔧 Next: architect should implement POC code manually")

        return poc_dir

    def _generate_poc_readme(self, priority: Dict, requirements: Dict) -> str:
        """Generate README.md content for POC from template.

        Args:
            priority: Priority dictionary from ROADMAP
            requirements: Requirements dict with title, effort_hours, complexity

        Returns:
            README.md content as string
        """
        from datetime import date

        priority_number = priority.get("number", "unknown")
        priority_name = priority.get("name", "unknown")
        title = requirements.get("title", "Unknown Feature")
        effort_hours = requirements.get("estimated_effort_hours", 0)
        requirements.get("technical_complexity", "unknown")

        # Calculate POC time budget (20-30% of full implementation)
        poc_time_min = int(effort_hours * 0.2)
        poc_time_max = int(effort_hours * 0.3)

        # Read template
        template_path = Path("docs/architecture/pocs/POC-000-template/README.md")
        if not template_path.exists():
            logger.error(f"❌ Template not found: {template_path}")
            return "# POC README Template Missing"

        template = template_path.read_text(encoding="utf-8")

        # Replace placeholders
        readme = template.replace("{number}", str(priority_number))
        readme = readme.replace("{Feature Name}", title)
        readme = readme.replace("{Date}", str(date.today()))
        readme = readme.replace("{X-Y}", f"{poc_time_min}-{poc_time_max}")
        readme = readme.replace("{Total hours for SPEC-{number}}", f"{effort_hours} hours (SPEC-{priority_number})")

        # Add context about what to prove
        readme = readme.replace(
            "{specific technical concepts}",
            f"core technical concepts for {priority_name} ({title})",
        )

        return readme

    def _extract_requirements_from_priority(self, priority: Dict) -> Dict:
        """Extract requirements from priority for POC decision.

        Parses priority content to extract:
        - title: Feature title
        - estimated_effort_hours: Effort estimate in hours
        - technical_complexity: low/medium/high

        Args:
            priority: Priority dictionary from ROADMAP

        Returns:
            Requirements dict with title, estimated_effort_hours, technical_complexity
        """
        import re

        priority_content = priority.get("content", "")
        priority_title = priority.get("title", "Unknown Feature")

        # Extract estimated effort (look for patterns like "8-16 hours", "1-2 days", "84-104 hours")
        effort_hours = 8  # Default to 8 hours (1 day)

        # Look for hour estimates
        hours_match = re.search(r"(\d+)-(\d+)\s*hours?", priority_content, re.IGNORECASE)
        if hours_match:
            # Use the upper bound of the estimate
            effort_hours = int(hours_match.group(2))
        else:
            # Look for day estimates and convert to hours
            days_match = re.search(r"(\d+)-(\d+)\s*days?", priority_content, re.IGNORECASE)
            if days_match:
                effort_hours = int(days_match.group(2)) * 8  # Upper bound in days * 8 hours

        # Extract technical complexity (look for "complexity" keyword)
        complexity = "medium"  # Default

        complexity_patterns = [
            (r"complexity[:\s]+high", "high"),
            (r"complexity[:\s]+medium", "medium"),
            (r"complexity[:\s]+low", "low"),
            (r"very\s+high\s+complexity", "high"),
            (r"high\s+complexity", "high"),
            (r"medium\s+complexity", "medium"),
            (r"low\s+complexity", "low"),
        ]

        for pattern, level in complexity_patterns:
            if re.search(pattern, priority_content, re.IGNORECASE):
                complexity = level
                break

        # Check for complexity indicators
        high_complexity_indicators = [
            "novel architectural pattern",
            "external system integration",
            "multi-process",
            "async complexity",
            "performance-critical",
            "security-sensitive",
            "cross-cutting concerns",
            "multi-agent",
            "orchestration",
        ]

        # If no explicit complexity found, infer from content
        if complexity == "medium":
            for indicator in high_complexity_indicators:
                if indicator.lower() in priority_content.lower():
                    complexity = "high"
                    break

        logger.info(
            f"📊 Extracted requirements: effort={effort_hours}h, complexity={complexity}, title={priority_title}"
        )

        return {
            "title": priority_title,
            "estimated_effort_hours": effort_hours,
            "technical_complexity": complexity,
        }
