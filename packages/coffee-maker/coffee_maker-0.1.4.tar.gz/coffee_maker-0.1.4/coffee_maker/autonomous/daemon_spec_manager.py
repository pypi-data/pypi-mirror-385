"""Technical Specification Management Mixin for DevDaemon.

This module provides technical specification enforcement and management functionality
for the autonomous development daemon, extracted from daemon.py to improve code
organization and maintainability.

US-047 UPDATE: Enforces CFR-008 - ARCHITECT-ONLY SPEC CREATION
- code_developer BLOCKS when spec is missing (does NOT create)
- Notifies user and architect about missing spec
- architect must create specs proactively in docs/architecture/specs/
- No delegation - just blocking with clear notification

US-054 UPDATE: Enforces CFR-011 - ARCHITECT DAILY INTEGRATION
- architect MUST read code-searcher reports before creating specs
- architect MUST analyze codebase weekly (max 7 days between analyses)
- Spec creation BLOCKED if CFR-011 violations detected
- Ensures continuous integration of code quality findings

Classes:
    SpecManagerMixin: Mixin providing _ensure_technical_spec() and spec checking

Usage:
    class DevDaemon(SpecManagerMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files

Architecture:
- daemon checks if technical spec exists for priority
- If spec exists: implementation proceeds normally
- If spec missing: daemon BLOCKS with notification
- architect creates specs proactively in docs/architecture/specs/
"""

import logging
from coffee_maker.autonomous.architect_daily_routine import (
    ArchitectDailyRoutine,
    CFR011ViolationError,
)

logger = logging.getLogger(__name__)


class SpecManagerMixin:
    """Mixin providing technical specification management for daemon.

    This mixin provides methods for ensuring technical specifications exist
    before implementing priorities, and creating them using Claude if missing.

    Required attributes (provided by DevDaemon):
        - self.roadmap_path: Path to ROADMAP.md
        - self.claude: ClaudeAPI instance
        - self.git: GitManager instance

    Methods:
        - _ensure_technical_spec(): Ensure spec exists or create it
        - _build_spec_creation_prompt(): Build prompt for creating specs

    Example:
        >>> class DevDaemon(SpecManagerMixin):
        ...     def __init__(self):
        ...         self.roadmap_path = Path("docs/roadmap/ROADMAP.md")
        ...         self.claude = ClaudeAPI()
        ...         self.git = GitManager()
        >>> daemon = DevDaemon()
        >>> priority = {"name": "US-021", "title": "Refactoring"}
        >>> daemon._ensure_technical_spec(priority)
        True
    """

    def _ensure_technical_spec(self, priority: dict) -> bool:
        """Ensure technical specification exists for this priority.

        US-047: ENFORCE CFR-008 - Architect-Only Spec Creation
        1. Check if spec already exists
        2. If spec exists: allow implementation to proceed
        3. If spec missing: BLOCK and notify user/architect
        4. Do NOT create specs (code_developer cannot create specs per CFR-008)

        US-054: ENFORCE CFR-011 - Architect Daily Integration
        BEFORE allowing spec check, ensure architect has:
        - Read all code-searcher reports
        - Performed weekly codebase analysis (<7 days ago)

        BUG-002 FIX: Validate priority fields before accessing them.

        Args:
            priority: Priority dictionary

        Returns:
            True if spec exists, False if missing (blocks implementation)
        """
        # BUG-002: Validate required fields
        if not priority.get("name"):
            logger.error("❌ Priority missing 'name' field - cannot check for technical spec")
            return False

        # US-054: ENFORCE CFR-011 BEFORE checking for spec
        # This ensures architect has read all findings before ANY spec-related work
        # SKIP in parallel execution mode (specific_priority set) - worktrees are isolated
        if not hasattr(self, "specific_priority") or self.specific_priority is None:
            routine = ArchitectDailyRoutine()
            try:
                routine.enforce_cfr_011()
                logger.info("✅ CFR-011 compliant - architect has integrated code-searcher findings")
            except CFR011ViolationError as e:
                logger.error(f"❌ CFR-011 violation detected: {e}")
                # Notify user about CFR-011 violation
                self._notify_cfr_011_violation(priority, str(e))
                # BLOCK spec checking until architect complies
                return False
        else:
            logger.info("⏭️  Skipping CFR-011 enforcement (parallel execution mode)")

        priority_name = priority["name"]
        priority_title = priority.get("title", "")

        # Extract number from priority name/title for spec prefix
        # Priority: Check if title contains US-XXX (e.g., "US-047 - Description")
        if "US-" in priority_title:
            # Extract US number from title
            import re

            match = re.search(r"US-(\d+)", priority_title)
            if match:
                spec_number = match.group(1)
                spec_prefix = f"SPEC-{spec_number}"
            else:
                # Fallback to priority number
                priority_num = priority_name.replace("PRIORITY", "").strip()
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        elif priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]
            spec_prefix = f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                major, minor = priority_num.split(".")
                spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
            else:
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        else:
            spec_prefix = f"SPEC-{priority_name.replace(' ', '-')}"

        # Locate architect's spec directory
        docs_dir = self.roadmap_path.parent.parent
        architect_spec_dir = docs_dir / "architecture" / "specs"

        logger.info(f"🔍 Checking for spec: {spec_prefix}-*.md in {architect_spec_dir}")

        # Step 1: Check if spec already exists
        if architect_spec_dir.exists():
            spec_pattern = f"{spec_prefix}-*.md"
            matching_specs = list(architect_spec_dir.glob(spec_pattern))
            logger.info(f"   Pattern: {spec_pattern}, Found {len(matching_specs)} matches")

            for spec_file in matching_specs:
                logger.info(f"✅ Technical spec found: {spec_file.name}")
                return True
        else:
            logger.error(f"   Spec directory doesn't exist: {architect_spec_dir}")

        # Step 2: Spec missing - DELEGATE to architect and BLOCK (US-045)
        logger.error(f"❌ Technical spec REQUIRED but missing for {priority_name}")
        logger.error(f"   Expected pattern: {spec_prefix}-*.md")
        logger.error(f"   CFR-008: code_developer CANNOT create specs")
        logger.error(f"   → Delegating to architect to create: docs/architecture/specs/{spec_prefix}-*.md")
        logger.error(f"   ⛔ BLOCKING implementation until spec exists")

        # US-045: Delegate to architect agent to create spec (CRITICAL)
        self._delegate_spec_creation_to_architect(priority, spec_prefix)

        # Create notification to alert user (for visibility)
        self._notify_spec_missing(priority, spec_prefix)

        # Return False to BLOCK implementation (daemon waits for architect to create spec)
        return False

    def _notify_spec_missing(self, priority: dict, spec_prefix: str) -> None:
        """Notify user and architect about missing technical specification.

        CFR-008: ARCHITECT-ONLY SPEC CREATION

        Creates a notification alerting the user and architect that a technical
        specification is missing for a priority. This blocks implementation until
        the architect creates the spec.

        Args:
            priority: Priority dictionary
            spec_prefix: Expected spec filename prefix (e.g., "SPEC-047")

        Example:
            >>> priority = {"name": "US-047", "title": "Enforce CFR-008"}
            >>> self._notify_spec_missing(priority, "SPEC-047")
        """
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "Unknown Title")
        priority_effort = priority.get("estimated_effort", "Unknown")

        # Create notification message with actionable guidance
        title = f"CFR-008: Missing Spec for {priority_name}"
        message = (
            f"Technical specification REQUIRED for '{priority_title}'.\n\n"
            f"Priority: {priority_name}\n"
            f"Title: {priority_title}\n"
            f"Estimated Effort: {priority_effort}\n"
            f"Expected spec prefix: {spec_prefix}\n\n"
            f"CFR-008 ENFORCEMENT: code_developer cannot create specs.\n"
            f"→ architect must create: docs/architecture/specs/{spec_prefix}-<feature-name>.md\n\n"
            f"Implementation is BLOCKED until architect creates the spec.\n\n"
            f"ACTIONS:\n"
            f"1. Invoke architect agent to create technical spec\n"
            f"2. architect reviews {priority_name} in ROADMAP.md\n"
            f"3. architect creates comprehensive spec in docs/architecture/specs/\n"
            f"4. code_developer will auto-resume when spec exists"
        )

        context = {
            "priority_name": priority_name,
            "priority_title": priority_title,
            "priority_effort": priority_effort,
            "spec_prefix": spec_prefix,
            "enforcement": "CFR-008",
            "action_required": "architect must create technical spec",
            "spec_directory": "docs/architecture/specs/",
        }

        try:
            self.notifications.create_notification(
                type="error",
                title=title,
                message=message,
                priority="critical",
                context=context,
                sound=False,  # CFR-009: code_developer must use sound=False
                agent_id="code_developer",  # CFR-009: identify calling agent
            )

            logger.info(f"✅ Created CFR-008 notification for {priority_name}")

        except Exception as e:
            logger.error(f"Failed to create notification: {e}", exc_info=True)
            # Don't fail - notification is nice-to-have but not critical

    def _notify_cfr_011_violation(self, priority: dict, violation_details: str) -> None:
        """Notify user about CFR-011 violation.

        CFR-011: ARCHITECT DAILY INTEGRATION
        architect MUST read code-searcher reports and analyze codebase weekly
        before creating specs.

        Creates a notification alerting the user that architect has violated
        CFR-011 and must complete daily integration before spec creation can proceed.

        Args:
            priority: Priority dictionary
            violation_details: Details about the violation from CFR011ViolationError

        Example:
            >>> priority = {"name": "US-054", "title": "CFR-011 Enforcement"}
            >>> violation = "Unread code-searcher reports: ANALYSIS.md"
            >>> self._notify_cfr_011_violation(priority, violation)
        """
        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "Unknown Title")

        # Create notification message with actionable guidance
        title = f"CFR-011: architect Must Review Code Findings"
        message = (
            f"CFR-011 violation detected for '{priority_title}'.\n\n"
            f"Priority: {priority_name}\n"
            f"Title: {priority_title}\n\n"
            f"VIOLATION DETAILS:\n{violation_details}\n\n"
            f"CFR-011 REQUIREMENT:\n"
            f"architect MUST read all code-searcher reports AND analyze codebase weekly\n"
            f"BEFORE creating or checking technical specifications.\n\n"
            f"ACTIONS REQUIRED:\n"
            f"1. Run: architect daily-integration (read code-searcher reports)\n"
            f"2. Run: architect analyze-codebase (if >7 days since last analysis)\n"
            f"3. Check compliance: architect cfr-011-status\n\n"
            f"Implementation is BLOCKED until CFR-011 compliance achieved."
        )

        context = {
            "priority_name": priority_name,
            "priority_title": priority_title,
            "enforcement": "CFR-011",
            "violation_details": violation_details,
            "action_required": "architect must complete daily integration and weekly analysis",
            "commands": [
                "architect daily-integration",
                "architect analyze-codebase",
                "architect cfr-011-status",
            ],
        }

        try:
            self.notifications.create_notification(
                type="error",
                title=title,
                message=message,
                priority="critical",
                context=context,
                sound=False,  # CFR-009: code_developer must use sound=False
                agent_id="code_developer",  # CFR-009: identify calling agent
            )

            logger.info(f"✅ Created CFR-011 violation notification for {priority_name}")

        except Exception as e:
            logger.error(f"Failed to create CFR-011 notification: {e}", exc_info=True)
            # Don't fail - notification is nice-to-have but not critical

    def _delegate_spec_creation_to_architect(self, priority: dict, spec_prefix: str) -> None:
        """Delegate spec creation to architect agent via message queue.

        US-045: DAEMON-TO-ARCHITECT DELEGATION
        Instead of just blocking, daemon actively requests architect to create the spec
        by sending an urgent message to architect's inbox.

        Args:
            priority: Priority dictionary (with name, title, content, etc.)
            spec_prefix: Expected spec filename prefix (e.g., "SPEC-047")

        Example:
            >>> priority = {"name": "US-047", "title": "Enforce CFR-008", "content": "..."}
            >>> self._delegate_spec_creation_to_architect(priority, "SPEC-047")
            # Creates urgent message in data/agent_messages/architect_inbox/
        """
        from pathlib import Path
        import json
        from datetime import datetime

        priority_name = priority.get("name", "Unknown Priority")
        priority_title = priority.get("title", "Unknown Title")
        priority_content = priority.get("content", "")

        # Create message for architect
        message = {
            "message_id": f"spec_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "from": "code_developer",
            "to": "architect",
            "type": "spec_request",
            "priority": "urgent",  # Urgent because daemon is blocked
            "timestamp": datetime.now().isoformat(),
            "content": {
                "priority_name": priority_name,
                "priority_title": priority_title,
                "priority_content": priority_content[:1500],  # Truncate for message size
                "spec_prefix": spec_prefix,
                "requester": "code_developer",
                "reason": "Implementation blocked - spec missing",
                "expected_location": f"docs/architecture/specs/{spec_prefix}-*.md",
            },
        }

        # Write to architect's inbox
        message_dir = Path("data/agent_messages")
        architect_inbox = message_dir / "architect_inbox"
        architect_inbox.mkdir(parents=True, exist_ok=True)

        # Urgent message gets urgent_ prefix so architect processes it first (CFR-012)
        msg_file = architect_inbox / f"urgent_{message['message_id']}.json"

        try:
            msg_file.write_text(json.dumps(message, indent=2), encoding="utf-8")
            logger.info(f"📨 Sent URGENT spec_request to architect for {priority_name}")
            logger.info(f"   Message file: {msg_file}")
            logger.info(f"   architect will create: {spec_prefix}-*.md")
        except Exception as e:
            logger.error(f"Failed to send message to architect: {e}", exc_info=True)
            # Don't fail - daemon can still notify user via notification
