"""Architect Coordinator for proactive spec creation and worktree merging.

This module coordinates the architect agent for two main responsibilities:
1. Maintain a backlog of 2-3 specs ahead of code_developer
2. Notify architect when parallel work in worktrees is ready for merge

Architecture:
    - Identifies priorities that need specs
    - Maintains spec backlog target (default: 3 specs ahead)
    - Tracks spec creation progress
    - Ensures CFR-011 compliance (architect reads code-searcher reports)
    - Detects completed worktrees (roadmap-* branches)
    - Notifies architect when merges are needed

Related:
    SPEC-104: Technical specification
    US-104: Strategic requirement (PRIORITY 20)
    SPEC-108: Parallel agent execution with git worktree
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.cli.notifications import NotificationDB

logger = logging.getLogger(__name__)


class ArchitectCoordinator:
    """
    Coordinates architect agent for proactive spec creation and worktree merging.

    Responsibilities:
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Prioritize spec creation by ROADMAP order
    - Track spec creation progress
    - Ensure CFR-011 compliance (architect reads code-searcher reports)
    - Detect completed worktrees (roadmap-* branches)
    - Notify architect when merges are needed
    """

    def __init__(self, spec_backlog_target: int = 3):
        """
        Initialize ArchitectCoordinator.

        Args:
            spec_backlog_target: Number of specs to keep ahead of code_developer
        """
        self.spec_backlog_target = spec_backlog_target
        self.notifications = NotificationDB()

    def get_missing_specs(self, priorities: List[Dict]) -> List[Dict]:
        """
        Identify priorities that need specs.

        ONLY returns priorities that are:
        1. Marked as "📝 Planned" in ROADMAP
        2. Missing technical specs

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of priorities missing specs, sorted by priority number
        """
        missing = []

        for priority in priorities:
            # Only consider "Planned" priorities
            status = priority.get("status", "").lower()
            if "planned" not in status and "📝" not in priority.get("status", ""):
                continue

            # Check if spec exists
            if not self._has_spec(priority):
                missing.append(priority)

        return sorted(missing, key=lambda p: p["number"])

    def _has_spec(self, priority: Dict) -> bool:
        """
        Check if technical spec exists for priority.

        Args:
            priority: Priority dict from RoadmapParser with 'name' and 'number' keys

        Returns:
            True if spec exists, False otherwise
        """
        # Extract numeric part from priority
        # Skill returns: number="20" (PRIORITY number), us_id="US-104"
        # Specs are named with US number, not PRIORITY number
        us_id = priority.get("us_id")
        spec_number = None

        if us_id:
            # Extract number from us_id (e.g., "US-104" -> "104")
            spec_number = us_id.replace("US-", "")
        else:
            # Fallback to priority number if no us_id
            spec_number = priority.get("number")

        spec_pattern = f"SPEC-{spec_number}-*.md"
        spec_path = Path("docs/architecture/specs")

        return len(list(spec_path.glob(spec_pattern))) > 0

    def create_spec_backlog(self, priorities: List[Dict]) -> List[str]:
        """
        Create spec backlog (identify first N missing specs).

        Args:
            priorities: List of priority dicts from ROADMAP

        Returns:
            List of task IDs for specs that should be created
        """
        missing_specs = self.get_missing_specs(priorities)[: self.spec_backlog_target]

        task_ids = []

        for priority in missing_specs:
            task_id = f"spec-{priority['number']}"
            task_ids.append(task_id)

            logger.info(f"📋 Queued spec creation: PRIORITY {priority['number']} (task: {task_id})")

        return task_ids

    def get_completed_worktrees(self) -> List[Dict]:
        """
        Detect roadmap-* branches with completed work ready for merge.

        Returns:
            List of worktree info dicts:
            [
                {
                    "branch": "roadmap-wt1",
                    "commits_ahead": 3,
                    "last_commit_msg": "feat: US-048 complete",
                    "us_number": "048"
                },
                ...
            ]
        """
        completed = []

        try:
            # Get all branches matching roadmap-*
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                check=True,
            )

            branches = result.stdout.split("\n")
            roadmap_branches = [
                b.strip().replace("* ", "") for b in branches if "roadmap-" in b and "remotes/" not in b
            ]

            for branch in roadmap_branches:
                if branch == "roadmap":
                    continue

                # Check commits ahead of roadmap
                commits_result = subprocess.run(
                    ["git", "rev-list", "--count", f"roadmap..{branch}"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                commits_ahead = int(commits_result.stdout.strip())

                if commits_ahead > 0:
                    # Get last commit message
                    log_result = subprocess.run(
                        ["git", "log", "-1", "--pretty=format:%s", branch],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    last_commit_msg = log_result.stdout.strip()

                    # Extract US number from branch name (roadmap-wt1 → extract from commit message)
                    # or from commit message (US-048, US-050, etc.)
                    us_number = self._extract_us_number(last_commit_msg)

                    completed.append(
                        {
                            "branch": branch,
                            "commits_ahead": commits_ahead,
                            "last_commit_msg": last_commit_msg,
                            "us_number": us_number,
                        }
                    )

                    logger.info(
                        f"🌿 Detected completed worktree: {branch} ({commits_ahead} commits ahead, US-{us_number})"
                    )

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to detect completed worktrees: {e}")

        return completed

    def _extract_us_number(self, commit_msg: str) -> Optional[str]:
        """
        Extract US number from commit message.

        Args:
            commit_msg: Commit message (e.g., "feat: US-048 - Enforce CFR-009")

        Returns:
            US number (e.g., "048") or None
        """
        import re

        # Match US-XXX pattern
        match = re.search(r"US-(\d+)", commit_msg, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def notify_architect_for_merge(self, worktree_info: Dict) -> None:
        """
        Send notification to architect that worktree is ready for merge.

        Args:
            worktree_info: Dict with branch, commits_ahead, last_commit_msg, us_number
        """
        branch = worktree_info["branch"]
        us_number = worktree_info["us_number"]
        commits_ahead = worktree_info["commits_ahead"]

        title = f"Worktree Ready for Merge: {branch}"
        message = f"""Parallel work in {branch} is ready for merge to roadmap.

US Number: US-{us_number}
Commits Ahead: {commits_ahead}
Last Commit: {worktree_info['last_commit_msg']}

Action Required:
1. Use merge-worktree-branches skill to merge
2. Run tests after merge
3. Push to remote
4. Notify orchestrator when ready for cleanup

Command:
architect merge-worktree-branches --merge {branch} --us-number {us_number}
"""

        # Create high-priority notification for architect
        self.notifications.create_notification(
            type="worktree_merge",
            title=title,
            message=message,
            priority="high",
            sound=False,  # CFR-009: Silent for background agent (orchestrator)
            agent_id="orchestrator",
        )

        logger.info(f"📬 Notified architect to merge {branch} (US-{us_number})")

    def check_and_notify_merges(self) -> int:
        """
        Check for completed worktrees and notify architect if merges needed.

        Returns:
            Number of merge notifications sent
        """
        completed_worktrees = self.get_completed_worktrees()

        notifications_sent = 0
        for worktree in completed_worktrees:
            self.notify_architect_for_merge(worktree)
            notifications_sent += 1

        if notifications_sent > 0:
            logger.info(f"📬 Sent {notifications_sent} merge notification(s) to architect")
        else:
            logger.debug("No completed worktrees detected")

        return notifications_sent
