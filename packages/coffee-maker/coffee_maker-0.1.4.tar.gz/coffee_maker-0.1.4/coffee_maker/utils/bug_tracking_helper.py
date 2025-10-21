"""Bug Tracking Helper - Easy import for all agents.

This module provides a simple way for any agent to use the bug tracking skill
without having to manage sys.path manipulation.

Usage:
    from coffee_maker.utils.bug_tracking_helper import get_bug_skill

    bug_skill = get_bug_skill()
    result = bug_skill.report_bug(
        title="Bug title",
        description="Description",
        reporter="assistant"
    )

Related:
    .claude/skills/shared/bug-tracking/bug_tracking.py
    SPEC-111: Bug Tracking Database and Skill
"""

import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Cache the bug tracking skill instance
_bug_skill_instance = None


def get_bug_skill():
    """Get bug tracking skill instance (singleton).

    Returns:
        BugTrackingSkill instance
    """
    global _bug_skill_instance

    if _bug_skill_instance is None:
        # Import bug tracking skill
        bug_tracking_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "bug-tracking"

        sys.path.insert(0, str(bug_tracking_dir))
        try:
            from bug_tracking import BugTrackingSkill

            _bug_skill_instance = BugTrackingSkill()
            logger.info("Bug tracking skill initialized")
        finally:
            sys.path.pop(0)

    return _bug_skill_instance


def report_bug_quick(
    title: str,
    description: str,
    reporter: str,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    reproduction_steps: Optional[list] = None,
) -> dict:
    """Quick helper to report a bug.

    Args:
        title: Bug title
        description: Bug description
        reporter: Reporter name (assistant, code_developer, etc.)
        priority: Priority (Critical, High, Medium, Low)
        category: Category (crash, performance, ui, logic, etc.)
        reproduction_steps: List of reproduction steps

    Returns:
        Dict with bug_id, bug_number, ticket_file_path, status
    """
    skill = get_bug_skill()
    return skill.report_bug(
        title=title,
        description=description,
        reporter=reporter,
        priority=priority,
        category=category,
        reproduction_steps=reproduction_steps,
    )


def update_bug_status_quick(
    bug_number: int,
    status: str,
    assigned_to: Optional[str] = None,
    notes: Optional[str] = None,
) -> bool:
    """Quick helper to update bug status.

    Args:
        bug_number: Bug number
        status: New status (open, analyzing, in_progress, testing, resolved, closed)
        assigned_to: Reassign to different agent
        notes: Status change notes

    Returns:
        True if successful
    """
    skill = get_bug_skill()
    return skill.update_bug_status(
        bug_number=bug_number,
        status=status,
        assigned_to=assigned_to,
        notes=notes,
    )


def add_bug_details_quick(
    bug_number: int,
    root_cause: Optional[str] = None,
    fix_description: Optional[str] = None,
    expected_behavior: Optional[str] = None,
    actual_behavior: Optional[str] = None,
    test_file_path: Optional[str] = None,
    test_name: Optional[str] = None,
) -> bool:
    """Quick helper to add bug details.

    Args:
        bug_number: Bug number
        root_cause: Root cause analysis
        fix_description: How the bug was fixed
        expected_behavior: What should happen
        actual_behavior: What actually happens
        test_file_path: Path to regression test file
        test_name: Name of regression test function

    Returns:
        True if successful
    """
    skill = get_bug_skill()
    return skill.add_bug_details(
        bug_number=bug_number,
        root_cause=root_cause,
        fix_description=fix_description,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        test_file_path=test_file_path,
        test_name=test_name,
    )


def link_bug_to_commit_quick(bug_number: int, commit_sha: str) -> bool:
    """Quick helper to link bug to commit.

    Args:
        bug_number: Bug number
        commit_sha: Git commit SHA

    Returns:
        True if successful
    """
    skill = get_bug_skill()
    return skill.link_bug_to_commit(bug_number=bug_number, commit_sha=commit_sha)


def link_bug_to_pr_quick(bug_number: int, pr_url: str) -> bool:
    """Quick helper to link bug to PR.

    Args:
        bug_number: Bug number
        pr_url: GitHub PR URL

    Returns:
        True if successful
    """
    skill = get_bug_skill()
    return skill.link_bug_to_pr(bug_number=bug_number, pr_url=pr_url)


def query_bugs_quick(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
) -> list:
    """Quick helper to query bugs.

    Args:
        status: Filter by status
        priority: Filter by priority
        assigned_to: Filter by assignee
        category: Filter by category
        limit: Max results

    Returns:
        List of bug dictionaries
    """
    skill = get_bug_skill()
    return skill.query_bugs(
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        category=category,
        limit=limit,
    )


def get_open_bugs_summary_quick() -> dict:
    """Quick helper to get open bugs summary.

    Returns:
        Dict with counts: {"critical": 2, "high": 5, "medium": 3, "low": 1}
    """
    skill = get_bug_skill()
    return skill.get_open_bugs_summary()


# Convenience exports
__all__ = [
    "get_bug_skill",
    "report_bug_quick",
    "update_bug_status_quick",
    "add_bug_details_quick",
    "link_bug_to_commit_quick",
    "link_bug_to_pr_quick",
    "query_bugs_quick",
    "get_open_bugs_summary_quick",
]
