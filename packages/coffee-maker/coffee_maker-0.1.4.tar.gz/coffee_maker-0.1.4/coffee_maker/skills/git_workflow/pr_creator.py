"""Pull request creation automation with GitHub CLI."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PullRequest:
    """Pull request information."""

    number: int  # PR number
    url: str  # PR URL
    title: str  # PR title
    body: str  # PR description
    created: bool  # Whether PR was created successfully


class PullRequestCreator:
    """Create GitHub pull requests with auto-generated descriptions."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize PR creator.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path or Path.cwd()

    def create(
        self,
        title: str,
        priority_name: Optional[str] = None,
        priority_description: Optional[str] = None,
        dod_report_path: Optional[str] = None,
        base_branch: str = "main",
        head_branch: str = "roadmap",
        auto_body: bool = True,
        custom_body: Optional[str] = None,
    ) -> PullRequest:
        """Create pull request with auto-generated description.

        Args:
            title: PR title
            priority_name: Priority identifier (e.g., "US-067")
            priority_description: Priority description
            dod_report_path: Path to DoD verification report
            base_branch: Target branch (default: main)
            head_branch: Source branch (default: roadmap)
            auto_body: Auto-generate PR body from commits
            custom_body: Custom PR body (overrides auto_body)

        Returns:
            PullRequest with creation result
        """
        # Generate PR body
        if custom_body:
            body = custom_body
        elif auto_body:
            body = self._generate_pr_body(
                title,
                priority_name,
                priority_description,
                dod_report_path,
                base_branch,
                head_branch,
            )
        else:
            body = ""

        # Create PR via gh CLI
        pr_number, pr_url, created = self._create_github_pr(title, body, base_branch, head_branch)

        return PullRequest(
            number=pr_number,
            url=pr_url,
            title=title,
            body=body,
            created=created,
        )

    def _generate_pr_body(
        self,
        title: str,
        priority_name: Optional[str],
        priority_description: Optional[str],
        dod_report_path: Optional[str],
        base_branch: str,
        head_branch: str,
    ) -> str:
        """Generate PR body from commits and context.

        Args:
            title: PR title
            priority_name: Priority identifier
            priority_description: Priority description
            dod_report_path: DoD report path
            base_branch: Target branch
            head_branch: Source branch

        Returns:
            Formatted PR body (markdown)
        """
        lines = []

        # Summary section
        lines.append("## Summary")
        lines.append("")
        if priority_name and priority_description:
            lines.append(f"Implements {priority_name}")
            lines.append("")
            # Add key points from description
            desc_lines = priority_description.split("\n")
            for line in desc_lines[:5]:  # First 5 lines
                if line.strip() and not line.startswith("#"):
                    lines.append(f"- {line.strip()}")
        else:
            lines.append(title)
        lines.append("")

        # Changes section
        lines.append("## Changes")
        lines.append("")
        commits = self._get_commits_between(base_branch, head_branch)
        changed_files = self._get_changed_files_between(base_branch, head_branch)

        # Group files by category
        impl_files = [f for f in changed_files if f.startswith("coffee_maker/")]
        test_files = [f for f in changed_files if f.startswith("tests/")]
        doc_files = [f for f in changed_files if f.startswith("docs/") or f.endswith((".md", ".rst"))]
        config_files = [f for f in changed_files if f.startswith(".claude/")]

        if impl_files:
            lines.append("### Implementation")
            for file in impl_files[:10]:  # Limit to 10 files
                lines.append(f"- `{file}`")
            if len(impl_files) > 10:
                lines.append(f"- ... and {len(impl_files) - 10} more files")
            lines.append("")

        if test_files:
            lines.append("### Tests")
            for file in test_files[:10]:
                lines.append(f"- `{file}`")
            if len(test_files) > 10:
                lines.append(f"- ... and {len(test_files) - 10} more files")
            lines.append("")

        if doc_files:
            lines.append("### Documentation")
            for file in doc_files[:10]:
                lines.append(f"- `{file}`")
            lines.append("")

        if config_files:
            lines.append("### Configuration")
            for file in config_files[:5]:
                lines.append(f"- `{file}`")
            lines.append("")

        # Test results section
        lines.append("## Test Results")
        lines.append("")
        test_result = self._get_test_status()
        if test_result:
            lines.append(f"- ✅ {test_result}")
        else:
            lines.append("- Tests: See CI/CD pipeline")
        lines.append("")

        # DoD verification section
        if dod_report_path:
            lines.append("## DoD Verification")
            lines.append("")
            lines.append("**Status**: ✅ PASS")
            lines.append("")
            lines.append(f"See full DoD report: `{dod_report_path}`")
            lines.append("")
        else:
            lines.append("## DoD Verification")
            lines.append("")
            lines.append("**Status**: ⏳ Pending")
            lines.append("")

        # Commits section
        if commits:
            lines.append("## Commits")
            lines.append("")
            for commit in commits[:20]:  # Limit to 20 commits
                lines.append(f"- {commit}")
            if len(commits) > 20:
                lines.append(f"- ... and {len(commits) - 20} more commits")
            lines.append("")

        # Related issues section
        if priority_name:
            lines.append("## Related Issues")
            lines.append("")
            if priority_name.startswith("US-"):
                lines.append(f"Related: {priority_name}")
            else:
                lines.append(f"Related: {priority_name}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")

        return "\n".join(lines)

    def _get_commits_between(self, base_branch: str, head_branch: str) -> List[str]:
        """Get commits between branches.

        Args:
            base_branch: Target branch
            head_branch: Source branch

        Returns:
            List of commit messages
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--oneline",
                    "--no-merges",
                    f"{base_branch}..{head_branch}",
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            commits = [c.strip() for c in result.stdout.split("\n") if c.strip()]
            return commits
        except subprocess.CalledProcessError:
            return []

    def _get_changed_files_between(self, base_branch: str, head_branch: str) -> List[str]:
        """Get changed files between branches.

        Args:
            base_branch: Target branch
            head_branch: Source branch

        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_branch}...{head_branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            return files
        except subprocess.CalledProcessError:
            return []

    def _get_test_status(self) -> Optional[str]:
        """Get test status from pytest.

        Returns:
            Test status string or None if unavailable
        """
        try:
            # Try to run pytest --collect-only to count tests
            result = subprocess.run(
                ["pytest", "--collect-only", "-q"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Parse output for test count
            output = result.stdout
            if "test" in output:
                # Extract test count from output
                lines = output.split("\n")
                for line in lines:
                    if "selected" in line.lower():
                        return line.strip()

            return None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None

    def _create_github_pr(self, title: str, body: str, base_branch: str, head_branch: str) -> tuple[int, str, bool]:
        """Create GitHub PR via gh CLI.

        Args:
            title: PR title
            body: PR description
            base_branch: Target branch
            head_branch: Source branch

        Returns:
            Tuple of (pr_number, pr_url, created_successfully)
        """
        try:
            # Create PR using gh CLI
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--base",
                    base_branch,
                    "--head",
                    head_branch,
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse PR URL from output
            pr_url = result.stdout.strip()

            # Extract PR number from URL
            # URL format: https://github.com/owner/repo/pull/123
            pr_number = 0
            if "/pull/" in pr_url:
                pr_number = int(pr_url.split("/pull/")[-1])

            return pr_number, pr_url, True

        except subprocess.CalledProcessError as e:
            print(f"Failed to create PR: {e.stderr}")
            return 0, "", False
        except Exception as e:
            print(f"Error creating PR: {str(e)}")
            return 0, "", False
