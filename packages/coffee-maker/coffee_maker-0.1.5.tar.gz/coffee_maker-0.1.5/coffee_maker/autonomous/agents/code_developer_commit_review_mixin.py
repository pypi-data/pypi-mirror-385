"""Code Developer Commit Review Mixin - Sends commit review requests to architect.

This mixin extends CodeDeveloperAgent with the ability to send commit review
requests to architect after each successful commit.

Related ADRs:
    - ADR-010: Architect Commit Review and Skills Maintenance
    - ADR-011: Orchestrator-Based Commit Review (No Git Hooks)

Usage:
    class CodeDeveloperAgent(CodeDeveloperCommitReviewMixin, BaseAgent):
        pass
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class CodeDeveloperCommitReviewMixin:
    """Mixin adding commit review request capabilities to CodeDeveloperAgent.

    New Capabilities:
    1. Send commit_review_request messages to architect after commits
    2. Determine review priority (CRITICAL vs NORMAL)
    3. Process tactical_feedback from architect
    """

    def _after_commit_success(self, commit_sha: str, files_changed: List[str], commit_message: str, priority_name: str):
        """Called after successful commit to send review request to architect.

        Args:
            commit_sha: Commit SHA (e.g., "a1b2c3d4e5f6...")
            files_changed: List of files changed in commit
            commit_message: Commit message
            priority_name: Priority name (e.g., "PRIORITY 10")

        Sends message to architect:
        {
            "type": "commit_review_request",
            "priority": "CRITICAL" or "NORMAL",
            "content": {
                "commit_sha": "a1b2c3d",
                "files_changed": ["file1.py", "file2.py"],
                "loc_added": 150,
                "loc_removed": 50,
                "commit_message": "feat: ...",
                "priority_name": "PRIORITY 10"
            }
        }
        """
        logger.info(f"📋 Preparing commit review request for {commit_sha[:7]}")

        # Determine review priority
        priority = self._determine_review_priority(commit_sha, files_changed)

        # Count LOC added/removed
        loc_stats = self._count_loc_changes(commit_sha)

        # Create review request message
        message = {
            "type": "commit_review_request",
            "sender": "code_developer",
            "recipient": "architect",
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "content": {
                "commit_sha": commit_sha,
                "branch": "roadmap",
                "priority_name": priority_name,
                "files_changed": files_changed,
                "loc_added": loc_stats.get("added", 0),
                "loc_removed": loc_stats.get("removed", 0),
                "commit_message": commit_message,
            },
        }

        # Send message to architect
        self._send_message("architect", message)

        logger.info(
            f"✉️  Sent commit review request to architect "
            f"(SHA: {commit_sha[:7]}, Priority: {priority}, Files: {len(files_changed)})"
        )

    def _determine_review_priority(self, commit_sha: str, files_changed: List[str]) -> str:
        """Determine if commit needs CRITICAL (urgent) or NORMAL review.

        CRITICAL if:
        - Security-related files changed (auth/, security/, password, jwt, token)
        - Critical infrastructure changed (daemon.py, orchestrator.py, agent_registry.py)
        - >500 LOC changed (large refactoring)

        Otherwise: NORMAL

        Args:
            commit_sha: Commit SHA
            files_changed: List of files changed

        Returns:
            "CRITICAL" or "NORMAL"
        """
        # Check for security files
        security_patterns = ["auth/", "security/", "jwt", "password", "token", "credential", "api_key"]
        for file_path in files_changed:
            file_lower = file_path.lower()
            if any(pattern in file_lower for pattern in security_patterns):
                logger.info(f"🚨 CRITICAL review: Security file changed ({file_path})")
                return "CRITICAL"

        # Check for critical infrastructure
        critical_files = [
            "daemon.py",
            "orchestrator.py",
            "agent_registry.py",
            "base_agent.py",
            "skill_loader.py",
        ]
        for file_path in files_changed:
            if any(file_path.endswith(cf) for cf in critical_files):
                logger.info(f"🚨 CRITICAL review: Critical infrastructure changed ({file_path})")
                return "CRITICAL"

        # Check LOC changed
        loc_stats = self._count_loc_changes(commit_sha)
        total_loc = loc_stats.get("added", 0) + loc_stats.get("removed", 0)
        if total_loc > 500:
            logger.info(f"🚨 CRITICAL review: Large change ({total_loc} LOC)")
            return "CRITICAL"

        # Default: NORMAL
        return "NORMAL"

    def _count_loc_changes(self, commit_sha: str) -> dict:
        """Count lines of code added and removed in commit.

        Args:
            commit_sha: Commit SHA

        Returns:
            Dictionary with 'added' and 'removed' counts
        """
        try:
            # Use git diff --numstat to get LOC changes
            import subprocess

            result = subprocess.run(
                ["git", "diff", "--numstat", f"{commit_sha}^", commit_sha],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to count LOC for {commit_sha[:7]}")
                return {"added": 0, "removed": 0}

            # Parse output (format: "added\tremoved\tfilename")
            total_added = 0
            total_removed = 0

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) >= 2:
                    try:
                        added = int(parts[0]) if parts[0].isdigit() else 0
                        removed = int(parts[1]) if parts[1].isdigit() else 0
                        total_added += added
                        total_removed += removed
                    except ValueError:
                        continue

            return {"added": total_added, "removed": total_removed}

        except Exception as e:
            logger.error(f"Error counting LOC: {e}")
            return {"added": 0, "removed": 0}

    def _process_tactical_feedback(self, message: dict):
        """Process tactical feedback from architect.

        Message format:
        {
            "type": "tactical_feedback",
            "priority": "HIGH" or "NORMAL",
            "content": {
                "commit_sha": "a1b2c3d",
                "issues": [
                    {
                        "severity": "CRITICAL|HIGH|MEDIUM",
                        "description": "...",
                        "fix": "..."
                    }
                ],
                "action_required": true/false
            }
        }

        Actions:
        - Log feedback
        - If action_required: Create TODO file or notify user
        - Update metrics
        """
        content = message.get("content", {})
        commit_sha = content.get("commit_sha", "unknown")
        issues = content.get("issues", [])
        action_required = content.get("action_required", False)

        logger.info(f"📬 Received tactical feedback from architect ({commit_sha[:7]})")
        logger.info(f"   Issues found: {len(issues)}")
        logger.info(f"   Action required: {action_required}")

        # Log each issue
        for issue in issues:
            severity = issue.get("severity", "UNKNOWN")
            description = issue.get("description", "")
            fix = issue.get("fix", "")

            logger.warning(f"   [{severity}] {description}")
            if fix:
                logger.info(f"      Fix: {fix}")

        # If action required, create feedback file for visibility
        if action_required:
            feedback_dir = Path("data/architect_feedback")
            feedback_dir.mkdir(parents=True, exist_ok=True)

            feedback_file = feedback_dir / f"{commit_sha[:7]}_tactical.md"
            feedback_content = f"""# Tactical Feedback: {commit_sha[:7]}

**Priority**: {message.get('priority', 'NORMAL')}
**Action Required**: {'YES' if action_required else 'NO'}
**Timestamp**: {datetime.now().isoformat()}

## Issues Found

"""
            for i, issue in enumerate(issues, 1):
                feedback_content += f"""### {i}. {issue.get('severity', 'UNKNOWN')}

**Description**: {issue.get('description', '')}

**Fix**: {issue.get('fix', '')}

---

"""

            feedback_file.write_text(feedback_content, encoding="utf-8")
            logger.info(f"💾 Feedback saved to: {feedback_file}")

        # Update metrics
        self.metrics["tactical_feedback_received"] = self.metrics.get("tactical_feedback_received", 0) + 1
        if action_required:
            self.metrics["action_required_feedback"] = self.metrics.get("action_required_feedback", 0) + 1
