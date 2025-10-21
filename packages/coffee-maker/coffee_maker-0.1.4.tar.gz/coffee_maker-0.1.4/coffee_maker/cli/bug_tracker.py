"""Bug Ticket Management System for project-manager.

This module provides functionality for creating, managing, and tracking bug tickets
in the integrated bug fixing workflow (PRIORITY 2.11).

Workflow:
    User reports bug → project-manager creates ticket → code_developer fixes bug
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class BugTracker:
    """Manages bug tickets and the bug fixing workflow.

    Attributes:
        tickets_dir: Path to tickets directory
    """

    def __init__(self, tickets_dir: Optional[Path] = None):
        """Initialize bug tracker.

        Args:
            tickets_dir: Directory for bug tickets (default: tickets/)
        """
        if tickets_dir is None:
            tickets_dir = Path("tickets")

        self.tickets_dir = Path(tickets_dir)
        self.tickets_dir.mkdir(exist_ok=True)

    def get_next_bug_number(self) -> int:
        """Get next available bug number.

        Returns:
            Next bug number (e.g., 1, 2, 3...)
        """
        existing_bugs = list(self.tickets_dir.glob("BUG-*.md"))

        if not existing_bugs:
            return 1

        # Extract numbers from existing bug files
        numbers = []
        for bug_file in existing_bugs:
            match = re.search(r"BUG-(\d+)\.md", bug_file.name)
            if match:
                numbers.append(int(match.group(1)))

        return max(numbers) + 1 if numbers else 1

    def extract_bug_title(self, description: str) -> str:
        """Extract concise bug title from description.

        Args:
            description: Full bug description

        Returns:
            Short title (max 80 chars)
        """
        # Try to get first sentence
        sentences = description.split(".")
        title = sentences[0].strip()

        # Remove common bug report prefixes
        prefixes = [
            "there's a bug",
            "there is a bug",
            "bug:",
            "the bug is",
            "i found a bug",
            "there's an issue",
            "there is an issue",
        ]

        title_lower = title.lower()
        for prefix in prefixes:
            if title_lower.startswith(prefix):
                title = title[len(prefix) :].strip()
                break

        # Ensure it starts with a capital letter
        if title:
            title = title[0].upper() + title[1:]

        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + "..."

        return title if title else "Bug Report"

    def assess_bug_priority(self, description: str) -> str:
        """Assess bug priority based on description.

        Args:
            description: Bug description

        Returns:
            Priority: Critical | High | Medium | Low
        """
        description_lower = description.lower()

        # Critical keywords
        critical_keywords = [
            "crash",
            "crashes",
            "crashing",
            "data loss",
            "security",
            "urgent",
            "critical",
            "broken",
            "completely",
            "can't use",
            "cannot use",
        ]

        # High priority keywords
        high_keywords = [
            "stuck",
            "hangs",
            "hanging",
            "blocks",
            "blocking",
            "prevents",
            "error",
            "exception",
            "fails",
            "failing",
        ]

        for keyword in critical_keywords:
            if keyword in description_lower:
                return "Critical"

        for keyword in high_keywords:
            if keyword in description_lower:
                return "High"

        return "Medium"

    def detect_bug_report(self, message: str) -> bool:
        """Detect if message is a bug report.

        Args:
            message: User message

        Returns:
            True if message appears to be a bug report
        """
        message_lower = message.lower()

        # Bug report patterns
        patterns = [
            r"there'?s?\s+a\s+bug",
            r"bug\s+in",
            r"found\s+a\s+bug",
            r"there'?s?\s+an?\s+issue",
            r"not\s+working",
            r"doesn'?t?\s+work",
            r"is\s+broken",
            r"crashes?\s+when",
            r"fails?\s+to",
            r"error\s+when",
            r"getting\s+an?\s+error",
            r"fix\s+(the\s+)?bug",
            r"fix\s+(the\s+)?issue",
        ]

        for pattern in patterns:
            if re.search(pattern, message_lower):
                return True

        return False

    def create_bug_ticket(
        self,
        description: str,
        title: Optional[str] = None,
        priority: Optional[str] = None,
        reproduction_steps: Optional[List[str]] = None,
    ) -> Tuple[int, Path]:
        """Create a new bug ticket.

        Args:
            description: Bug description
            title: Optional bug title (auto-generated if not provided)
            priority: Optional priority (auto-assessed if not provided)
            reproduction_steps: Optional reproduction steps

        Returns:
            Tuple of (bug_number, ticket_path)
        """
        # Generate ticket number
        bug_number = self.get_next_bug_number()

        # Extract/generate title
        if title is None:
            title = self.extract_bug_title(description)

        # Assess priority
        if priority is None:
            priority = self.assess_bug_priority(description)

        # Build ticket content
        ticket_content = self._build_ticket_content(
            bug_number=bug_number,
            title=title,
            description=description,
            priority=priority,
            reproduction_steps=reproduction_steps or [],
        )

        # Write ticket file
        ticket_path = self.tickets_dir / f"BUG-{bug_number:03d}.md"
        ticket_path.write_text(ticket_content)

        return bug_number, ticket_path

    def _build_ticket_content(
        self,
        bug_number: int,
        title: str,
        description: str,
        priority: str,
        reproduction_steps: List[str],
    ) -> str:
        """Build ticket file content.

        Args:
            bug_number: Bug ticket number
            title: Bug title
            description: Bug description
            priority: Bug priority
            reproduction_steps: Steps to reproduce

        Returns:
            Ticket file content as markdown
        """
        now = datetime.now().isoformat()

        steps = "\n".join(f"{i+1}. {step}" for i, step in enumerate(reproduction_steps))
        if not steps:
            steps = "_To be determined during analysis_"

        return f"""# BUG-{bug_number:03d}: {title}

**Status**: 🔴 Open
**Priority**: {priority}
**Created**: {now}
**Reporter**: User
**Assigned**: code_developer

## Description

{description}

## Reproduction Steps

{steps}

## Expected Behavior

_To be determined during analysis_

## Actual Behavior

_To be determined during analysis_

## Definition of Done

- [ ] Bug reproduced locally
- [ ] Root cause identified
- [ ] Technical specification written
- [ ] Fix implemented
- [ ] Regression tests added
- [ ] All tests passing
- [ ] No regressions in existing functionality
- [ ] Documentation updated if needed
- [ ] PR created and reviewed
- [ ] User validated fix

## Analysis (code_developer)

_Phase 1: Analysis - To be filled by code_developer_

## Technical Spec (code_developer)

_Phase 2: Technical Spec - To be filled by code_developer_

## Implementation (code_developer)

_Phase 3: Implementation - To be filled by code_developer_

## Testing Results (code_developer)

_Phase 4: Testing - To be filled by code_developer_

## Regression Test

**Test File**: _Path to test file (e.g., `tests/test_bug_066_roadmap_parser.py`)_

**Test Name**: _Test function name (e.g., `test_roadmap_parser_supports_double_hash`)_

**Coverage**:
- [ ] Bug reproduction test added (fails before fix, passes after fix)
- [ ] Edge cases covered
- [ ] Test runs in CI/CD pipeline
- [ ] Test documentation added

**Notes**: _Additional testing notes, edge cases, or related tests_

## PR Link

_Phase 5: PR Creation - To be filled by code_developer_

---

**Workflow**: User → project-manager → code_developer → Analysis → Tech Spec → Implementation → Testing → Regression Test → PR → Done
"""

    def format_ticket_response(self, bug_number: int, ticket_path: Path, title: str, priority: str) -> str:
        """Format user response for ticket creation.

        Args:
            bug_number: Bug ticket number
            ticket_path: Path to ticket file
            title: Bug title
            priority: Bug priority

        Returns:
            Formatted response message
        """
        priority_emoji = {
            "Critical": "🚨",
            "High": "⚠️",
            "Medium": "🔸",
            "Low": "🔹",
        }.get(priority, "🔸")

        return f"""🐛 **Bug Ticket Created**

**{priority_emoji} BUG-{bug_number:03d}**: {title}
**Priority**: {priority}
**Ticket**: `{ticket_path}`

✅ code_developer has been notified and will:
1. 🔍 Analyze the bug and reproduce it
2. 📝 Write a technical specification
3. 🔧 Implement the fix with tests
4. 🧪 Verify all tests pass
5. 📤 Create a PR for review

You can track progress in the ticket file or ask me for updates!
"""
