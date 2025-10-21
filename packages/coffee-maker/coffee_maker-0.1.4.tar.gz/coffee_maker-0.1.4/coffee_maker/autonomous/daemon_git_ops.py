"""Git Operations Mixin for DevDaemon.

This module provides git-related operations for the autonomous development daemon,
extracted from daemon.py to improve code organization and maintainability.

Classes:
    GitOpsMixin: Mixin providing _sync_roadmap_branch() and _merge_to_roadmap()

Usage:
    class DevDaemon(GitOpsMixin, ...):
        pass

Part of US-021 Phase 1 - Option D: Split Large Files
"""

import logging
import subprocess


logger = logging.getLogger(__name__)


class GitOpsMixin:
    """Mixin providing git operations for daemon.

    This mixin provides methods for synchronizing with the roadmap branch
    and merging feature branches back to roadmap for project visibility.

    Required attributes (provided by DevDaemon):
        - self.git: GitManager instance
        - self.notifications: NotificationDB instance

    Methods:
        - _sync_roadmap_branch(): Sync with origin/roadmap
        - _merge_to_roadmap(): Merge feature branch to roadmap

    Example:
        >>> class DevDaemon(GitOpsMixin):
        ...     def __init__(self):
        ...         self.git = GitManager()
        ...         self.notifications = NotificationDB()
        >>> daemon = DevDaemon()
        >>> daemon._sync_roadmap_branch()
        True
    """

    def _sync_roadmap_branch(self) -> bool:
        """Sync with 'roadmap' branch before each iteration.

        CFR-013 COMPLIANT: Since daemon always works on roadmap branch,
        this method simply pulls latest changes from origin/roadmap.

        No branch switching, no merge needed.

        Returns:
            True if sync successful, False if sync failed
        """
        try:
            # Validate we're on roadmap branch (defensive check)
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=self.git.repo_path, text=True
            ).strip()

            # Accept "roadmap" or "roadmap-*" (for worktree parallel execution)
            if current_branch != "roadmap" and not current_branch.startswith("roadmap-"):
                logger.error(
                    f"CFR-013 VIOLATION in _sync_roadmap_branch: On '{current_branch}', expected 'roadmap' or 'roadmap-*'"
                )
                return False

            # Pull latest from origin/roadmap
            logger.info("Pulling latest from origin/roadmap...")
            result = subprocess.run(
                ["git", "pull", "origin", "roadmap", "--no-edit"],
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                # Check if merge conflict
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    logger.error("❌ Merge conflict with origin/roadmap!")
                    logger.error("Manual intervention required to resolve conflicts")

                    # Abort merge
                    subprocess.run(
                        ["git", "merge", "--abort"],
                        cwd=self.git.repo_path,
                        capture_output=True,
                    )
                    return False
                else:
                    logger.warning(f"Pull failed: {result.stderr}")
                    return False

            logger.info("✅ Synced with origin/roadmap")
            return True

        except Exception as e:
            logger.error(f"Error syncing roadmap branch: {e}")
            return False

    def _merge_to_roadmap(self, message: str = "Sync progress to roadmap") -> bool:
        """Push changes to roadmap branch.

        CFR-013 COMPLIANT: Since daemon always works on roadmap branch,
        this method simply commits and pushes changes to origin/roadmap.

        No branch switching, no merging needed.

        Args:
            message: Description of what was accomplished

        Returns:
            True if push successful, False otherwise

        Example:
            >>> # After completing a subtask
            >>> self._merge_to_roadmap("Completed US-056 Phase 1")
            True
        """
        try:
            # Validate we're on roadmap branch (defensive check)
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], cwd=self.git.repo_path, text=True
            ).strip()

            # Accept "roadmap" or "roadmap-*" (for worktree parallel execution)
            if current_branch != "roadmap" and not current_branch.startswith("roadmap-"):
                logger.error(
                    f"CFR-013 VIOLATION in _merge_to_roadmap: On '{current_branch}', expected 'roadmap' or 'roadmap-*'"
                )
                return False

            # Check for uncommitted changes
            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=self.git.repo_path, text=True)

            if status.strip():
                # Commit changes
                logger.info(f"Committing changes: {message}")
                subprocess.run(["git", "add", "-A"], cwd=self.git.repo_path, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=self.git.repo_path, check=True)
            else:
                logger.info("No uncommitted changes to commit")

            # Push to origin/roadmap
            logger.info("Pushing to origin/roadmap...")
            subprocess.run(["git", "push", "origin", "roadmap"], cwd=self.git.repo_path, check=True)

            logger.info(f"✅ Pushed to roadmap: {message}")
            logger.info("✅ project_manager can now see progress")
            return True

        except Exception as e:
            logger.error(f"Failed to push to roadmap: {e}")
            logger.error("PROJECT_MANAGER CANNOT SEE PROGRESS!")
            return False
