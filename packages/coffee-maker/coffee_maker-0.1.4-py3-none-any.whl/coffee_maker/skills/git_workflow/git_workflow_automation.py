"""Complete git workflow automation: commit, tag, PR creation, and ROADMAP update."""

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from coffee_maker.skills.git_workflow.commit_generator import (
    CommitMessage,
    CommitMessageGenerator,
)
from coffee_maker.skills.git_workflow.pr_creator import PullRequestCreator


@dataclass
class GitWorkflowResult:
    """Result of complete git workflow execution."""

    success: bool
    commit_hash: Optional[str] = None
    tag_name: Optional[str] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    roadmap_updated: bool = False
    error_message: Optional[str] = None
    files_staged: List[str] = None
    files_committed: int = 0

    def __post_init__(self):
        if self.files_staged is None:
            self.files_staged = []


class GitWorkflowAutomation:
    """Automate complete git workflow for priority implementation.

    This class orchestrates:
    1. Intelligent file staging (exclude secrets, binaries)
    2. Conventional commit message generation
    3. Commit creation with pre-commit validation
    4. Git tag creation (wip-*, dod-verified-*)
    5. Push to remote (CFR-013: roadmap branch only)
    6. PR creation with auto-generated description
    7. ROADMAP.md status update
    """

    # Files/patterns to never stage
    NEVER_STAGE = {
        ".env",
        "*.key",
        "credentials.json",
        "*.pyc",
        "__pycache__",
        ".pytest_cache",
        ".idea",
        ".vscode",
        "*.db",  # Database files (warn before staging)
    }

    # Files/patterns to always stage
    ALWAYS_STAGE = {
        "coffee_maker/**/*.py",
        "tests/**/*.py",
        "docs/**/*.md",
        ".claude/**/*.md",
        "README.md",
    }

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize git workflow automation.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path or Path.cwd()
        self.commit_generator = CommitMessageGenerator(repo_path=self.repo_path)
        self.pr_creator = PullRequestCreator(repo_path=self.repo_path)

    def execute(
        self,
        priority_name: str,
        priority_description: str,
        dod_report_path: Optional[str] = None,
        create_tag: bool = True,
        create_pr: bool = True,
        update_roadmap: bool = True,
        override_type: Optional[str] = None,
        override_scope: Optional[str] = None,
    ) -> GitWorkflowResult:
        """Execute complete git workflow.

        Args:
            priority_name: Priority identifier (e.g., "US-067")
            priority_description: Full priority description
            dod_report_path: Path to DoD verification report (optional)
            create_tag: Whether to create git tag (default: True)
            create_pr: Whether to create PR (default: True)
            update_roadmap: Whether to update ROADMAP.md (default: True)
            override_type: Override auto-detected commit type
            override_scope: Override auto-detected scope

        Returns:
            GitWorkflowResult with execution status and results
        """
        try:
            # Step 1: Check we're on roadmap branch (CFR-013)
            if not self._verify_roadmap_branch():
                return GitWorkflowResult(
                    success=False,
                    error_message="Not on 'roadmap' branch (CFR-013 violation)",
                )

            # Step 2: Stage files intelligently
            staged_files = self._stage_files_intelligently()
            if not staged_files:
                return GitWorkflowResult(
                    success=False,
                    error_message="No files to commit (nothing staged)",
                    files_staged=[],
                )

            # Step 3: Generate conventional commit message
            commit_msg = self.commit_generator.generate(
                priority_name=priority_name,
                priority_description=priority_description,
                staged_only=True,
                override_type=override_type,
                override_scope=override_scope,
            )

            # Step 4: Create commit with validation
            commit_hash = self._create_commit_with_validation(commit_msg)
            if not commit_hash:
                return GitWorkflowResult(
                    success=False,
                    error_message="Commit creation failed (pre-commit hooks failed)",
                    files_staged=staged_files,
                )

            # Step 5: Create git tag (optional)
            tag_name = None
            if create_tag:
                tag_name = self._create_wip_tag(priority_name, commit_msg)

            # Step 6: Push to remote
            push_success = self._push_to_remote(tag_name)
            if not push_success:
                return GitWorkflowResult(
                    success=False,
                    error_message="Push to remote failed",
                    commit_hash=commit_hash,
                    tag_name=tag_name,
                    files_staged=staged_files,
                    files_committed=len(staged_files),
                )

            # Step 7: Create PR (optional)
            pr_number = None
            pr_url = None
            if create_pr:
                pr_title = self._generate_pr_title(priority_name, priority_description)
                pr_result = self.pr_creator.create(
                    title=pr_title,
                    priority_name=priority_name,
                    priority_description=priority_description,
                    dod_report_path=dod_report_path,
                    base_branch="main",
                    head_branch="roadmap",
                    auto_body=True,
                )

                if pr_result.created:
                    pr_number = pr_result.number
                    pr_url = pr_result.url

            # Step 8: Update ROADMAP.md (optional)
            roadmap_updated = False
            if update_roadmap and pr_url:
                roadmap_updated = self._update_roadmap_status(priority_name, pr_url, dod_report_path)

            return GitWorkflowResult(
                success=True,
                commit_hash=commit_hash,
                tag_name=tag_name,
                pr_number=pr_number,
                pr_url=pr_url,
                roadmap_updated=roadmap_updated,
                files_staged=staged_files,
                files_committed=len(staged_files),
            )

        except Exception as e:
            return GitWorkflowResult(success=False, error_message=f"Git workflow failed: {str(e)}")

    def _verify_roadmap_branch(self) -> bool:
        """Verify we're on roadmap branch (CFR-013).

        Returns:
            True if on roadmap branch, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()
            return current_branch == "roadmap"
        except subprocess.CalledProcessError:
            return False

    def _stage_files_intelligently(self) -> List[str]:
        """Stage files intelligently (exclude secrets, include implementation).

        Returns:
            List of staged file paths
        """
        # Get all changed files
        changed_files = self._get_all_changed_files()

        # Filter files to stage
        files_to_stage = []
        files_to_warn = []

        for file_path in changed_files:
            # Never stage secrets/build artifacts
            if self._is_never_stage(file_path):
                continue

            # Warn for database files
            if file_path.endswith(".db"):
                files_to_warn.append(file_path)
                continue

            # Stage implementation/test/docs files
            if self._should_stage(file_path):
                files_to_stage.append(file_path)

        # Warn about database files (but don't stage)
        if files_to_warn:
            print(f"⚠️  WARNING: Database files not staged: {', '.join(files_to_warn)}")

        # Stage files
        staged_files = []
        for file_path in files_to_stage:
            try:
                subprocess.run(
                    ["git", "add", file_path],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )
                staged_files.append(file_path)
            except subprocess.CalledProcessError:
                print(f"Failed to stage: {file_path}")

        return staged_files

    def _get_all_changed_files(self) -> List[str]:
        """Get all changed files (staged + unstaged + untracked).

        Returns:
            List of changed file paths
        """
        all_files = []

        # Staged files
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            all_files.extend([f.strip() for f in result.stdout.split("\n") if f.strip()])
        except subprocess.CalledProcessError:
            pass

        # Unstaged files
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            all_files.extend([f.strip() for f in result.stdout.split("\n") if f.strip()])
        except subprocess.CalledProcessError:
            pass

        # Untracked files
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            all_files.extend([f.strip() for f in result.stdout.split("\n") if f.strip()])
        except subprocess.CalledProcessError:
            pass

        # Remove duplicates
        return list(set(all_files))

    def _is_never_stage(self, file_path: str) -> bool:
        """Check if file should never be staged.

        Args:
            file_path: File path to check

        Returns:
            True if file should never be staged
        """
        file_name = Path(file_path).name

        # Check exact matches
        if file_name in self.NEVER_STAGE:
            return True

        # Check file extensions
        if file_name.endswith(".key") or file_name.endswith(".pyc") or file_name.endswith(".db"):
            return True

        # Check directory patterns
        if any(pattern in file_path for pattern in ["__pycache__", ".pytest_cache", ".idea", ".vscode"]):
            return True

        # Check for secrets in content (basic check)
        if self._might_contain_secrets(file_path):
            print(f"⚠️  WARNING: Potential secrets detected in {file_path} - NOT STAGING")
            return True

        return False

    def _should_stage(self, file_path: str) -> bool:
        """Check if file should be staged.

        Args:
            file_path: File path to check

        Returns:
            True if file should be staged
        """
        # Always stage implementation/test/docs
        if (
            file_path.startswith("coffee_maker/")
            or file_path.startswith("tests/")
            or file_path.startswith("docs/")
            or file_path.startswith(".claude/")
            or file_path == "README.md"
            or file_path == "pyproject.toml"
        ):
            return True

        return False

    def _might_contain_secrets(self, file_path: str) -> bool:
        """Basic check for potential secrets in file.

        Args:
            file_path: File path to check

        Returns:
            True if file might contain secrets
        """
        try:
            full_path = self.repo_path / file_path

            # Only check text files
            if not full_path.exists() or not full_path.is_file():
                return False

            # Skip binary files
            try:
                content = full_path.read_text()
            except (UnicodeDecodeError, PermissionError):
                return False

            # Check for common secret patterns
            secret_patterns = [
                r"API_KEY\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"SECRET\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"PASSWORD\s*=\s*['\"][^'\"]+['\"]",
                r"sk-[a-zA-Z0-9]{20,}",  # Anthropic API keys
            ]

            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True

            return False
        except Exception:
            return False

    def _create_commit_with_validation(self, commit_msg: CommitMessage) -> Optional[str]:
        """Create commit with pre-commit validation.

        Args:
            commit_msg: Commit message to use

        Returns:
            Commit hash if successful, None otherwise
        """
        try:
            # Run pre-commit hooks first
            pre_commit_success = self._run_pre_commit_hooks()

            # If pre-commit failed, try to fix and retry
            if not pre_commit_success:
                print("Pre-commit hooks failed, attempting auto-fix...")
                self._auto_fix_pre_commit()

                # Re-stage fixed files
                subprocess.run(
                    ["git", "add", "-u"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )

            # Create commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg.format()],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            return hash_result.stdout.strip()

        except subprocess.CalledProcessError as e:
            print(f"Failed to create commit: {e.stderr}")
            return None

    def _run_pre_commit_hooks(self) -> bool:
        """Run pre-commit hooks.

        Returns:
            True if all hooks passed
        """
        try:
            subprocess.run(
                ["pre-commit", "run", "--all-files"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _auto_fix_pre_commit(self):
        """Auto-fix common pre-commit failures."""
        try:
            # Run black formatter
            subprocess.run(
                ["black", "coffee_maker/", "tests/"],
                cwd=self.repo_path,
                capture_output=True,
            )

            # Run autoflake to remove unused imports
            subprocess.run(
                [
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "-r",
                    "coffee_maker/",
                    "tests/",
                ],
                cwd=self.repo_path,
                capture_output=True,
            )
        except Exception:
            pass

    def _create_wip_tag(self, priority_name: str, commit_msg: CommitMessage) -> Optional[str]:
        """Create WIP tag for implementation milestone.

        Args:
            priority_name: Priority identifier
            commit_msg: Commit message

        Returns:
            Tag name if created, None otherwise
        """
        try:
            # Generate tag name from priority
            tag_name = self._generate_tag_name(priority_name)

            # Create annotated tag
            tag_message = f"{priority_name} implementation complete\n\n{commit_msg.body}"

            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", tag_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            return tag_name

        except subprocess.CalledProcessError:
            return None

    def _generate_tag_name(self, priority_name: str) -> str:
        """Generate tag name from priority.

        Args:
            priority_name: Priority identifier (e.g., "US-067")

        Returns:
            Tag name (e.g., "wip-us-067")
        """
        # Normalize priority name
        normalized = priority_name.lower().replace(" ", "-").replace("_", "-")

        return f"wip-{normalized}"

    def _push_to_remote(self, tag_name: Optional[str] = None) -> bool:
        """Push commit and tag to remote.

        Args:
            tag_name: Tag name to push (optional)

        Returns:
            True if push successful
        """
        try:
            # Push commits
            subprocess.run(
                ["git", "push", "origin", "roadmap"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Push tag if created
            if tag_name:
                subprocess.run(
                    ["git", "push", "origin", tag_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to push: {e.stderr}")

            # Try pull and rebase if push failed
            try:
                subprocess.run(
                    ["git", "pull", "--rebase", "origin", "roadmap"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )

                # Retry push
                subprocess.run(
                    ["git", "push", "origin", "roadmap"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )

                if tag_name:
                    subprocess.run(
                        ["git", "push", "origin", tag_name],
                        cwd=self.repo_path,
                        capture_output=True,
                        check=True,
                    )

                return True

            except subprocess.CalledProcessError:
                return False

    def _generate_pr_title(self, priority_name: str, priority_description: str) -> str:
        """Generate PR title from priority.

        Args:
            priority_name: Priority identifier
            priority_description: Priority description

        Returns:
            PR title (max 72 chars)
        """
        # Try to extract title from description
        if priority_description:
            first_line = priority_description.split("\n")[0].strip()
            if first_line and len(first_line) < 60:
                return f"{priority_name}: {first_line}"

        return f"Implement {priority_name}"

    def _update_roadmap_status(self, priority_name: str, pr_url: str, dod_report_path: Optional[str]) -> bool:
        """Update ROADMAP.md to mark priority as complete.

        Args:
            priority_name: Priority identifier
            pr_url: PR URL
            dod_report_path: DoD report path (optional)

        Returns:
            True if updated successfully
        """
        try:
            roadmap_path = self.repo_path / "docs/roadmap/ROADMAP.md"

            if not roadmap_path.exists():
                return False

            roadmap_content = roadmap_path.read_text()

            # Find priority section and update status
            # Pattern: ### PRIORITY X: Title 🔄 In Progress
            # Replace with: ### PRIORITY X: Title ✅ Complete
            pattern = rf"(###\s+{re.escape(priority_name)}[^\n]*)\s+🔄\s+In Progress"
            replacement = r"\1 ✅ Complete"

            updated_content = re.sub(pattern, replacement, roadmap_content)

            # Add completion metadata
            pr_number = pr_url.split("/pull/")[-1] if "/pull/" in pr_url else "N/A"
            completion_date = datetime.now().strftime("%Y-%m-%d")

            completion_info = f"\n\n**PR**: #{pr_number} ({pr_url})"
            if dod_report_path:
                completion_info += f"\n**DoD**: Verified ({dod_report_path})"
            completion_info += f"\n**Completed**: {completion_date}\n"

            # Insert completion info after priority header
            pattern = rf"(###\s+{re.escape(priority_name)}[^\n]*✅\s+Complete)"
            replacement = r"\1" + completion_info

            updated_content = re.sub(pattern, replacement, updated_content)

            # Write back
            roadmap_path.write_text(updated_content)

            # Commit ROADMAP update
            subprocess.run(
                ["git", "add", "docs/roadmap/ROADMAP.md"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"docs(roadmap): Mark {priority_name} as complete\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
                ],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            subprocess.run(
                ["git", "push", "origin", "roadmap"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )

            return True

        except Exception as e:
            print(f"Failed to update ROADMAP: {str(e)}")
            return False
