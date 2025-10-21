"""Git hooks integration for automatic code review.

This module provides Git hooks that automatically run code review:
- Pre-commit: Review staged files before commit
- Pre-push: Review all changed files before push
- Manual: Review specific files or branches

The hooks can be configured to:
- Block commits/pushes with critical issues
- Generate reports for review
- Only check changed lines
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from coffee_maker.code_reviewer.models import ReviewReport
from coffee_maker.code_reviewer.report_generator import ReportGenerator
from coffee_maker.code_reviewer.reviewer import MultiModelCodeReviewer


class GitIntegration:
    """Integrates code reviewer with Git workflows.

    Provides Git hooks and utilities for automatic code review during:
    - Pre-commit (review staged files)
    - Pre-push (review all changes)
    - Manual review (specific files/commits)

    Example:
        >>> integration = GitIntegration()
        >>> integration.install_pre_commit_hook()
        >>> # Now pre-commit hook will run automatically
    """

    def __init__(
        self,
        repo_path: Optional[str] = None,
        block_on_critical: bool = True,
        block_on_high: bool = False,
    ):
        """Initialize Git integration.

        Args:
            repo_path: Path to Git repository (defaults to current directory)
            block_on_critical: Block commits if critical issues found
            block_on_high: Block commits if high severity issues found
        """
        self.repo_path = Path(repo_path or ".").resolve()
        self.git_dir = self.repo_path / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        self.block_on_critical = block_on_critical
        self.block_on_high = block_on_high

        self.reviewer = MultiModelCodeReviewer()
        self.report_generator = ReportGenerator()

    def get_staged_files(self) -> List[str]:
        """Get list of staged Python files.

        Returns:
            List of staged file paths

        Example:
            >>> integration = GitIntegration()
            >>> files = integration.get_staged_files()
            >>> print(f"Staged: {files}")
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Filter for Python files
            files = [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]
            return files

        except subprocess.CalledProcessError:
            return []

    def get_changed_files(self, base_branch: str = "main") -> List[str]:
        """Get list of changed Python files compared to base branch.

        Args:
            base_branch: Base branch to compare against

        Returns:
            List of changed file paths

        Example:
            >>> integration = GitIntegration()
            >>> files = integration.get_changed_files("main")
        """
        try:
            result = subprocess.run(
                ["git", "diff", f"{base_branch}...HEAD", "--name-only", "--diff-filter=ACM"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Filter for Python files
            files = [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]
            return files

        except subprocess.CalledProcessError:
            return []

    def review_staged_files(self) -> Tuple[List[ReviewReport], bool]:
        """Review all staged Python files.

        Returns:
            Tuple of (list of reports, should_block)
            should_block is True if issues warrant blocking the commit

        Example:
            >>> integration = GitIntegration()
            >>> reports, should_block = integration.review_staged_files()
            >>> if should_block:
            ...     print("Cannot commit: critical issues found")
        """
        staged_files = self.get_staged_files()
        if not staged_files:
            return [], False

        reports = []
        should_block = False

        for file_path in staged_files:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue

            try:
                report = self.reviewer.review_file(str(full_path))
                reports.append(report)

                # Check if we should block
                if self.block_on_critical and report.metrics.get("critical", 0) > 0:
                    should_block = True
                if self.block_on_high and report.metrics.get("high", 0) > 0:
                    should_block = True

            except Exception as e:
                print(f"Error reviewing {file_path}: {e}", file=sys.stderr)

        return reports, should_block

    def install_pre_commit_hook(self, force: bool = False) -> bool:
        """Install pre-commit hook for automatic code review.

        Args:
            force: Overwrite existing hook

        Returns:
            True if hook was installed successfully

        Example:
            >>> integration = GitIntegration()
            >>> if integration.install_pre_commit_hook():
            ...     print("Pre-commit hook installed!")
        """
        if not self.git_dir.exists():
            print(f"Error: Not a git repository: {self.repo_path}", file=sys.stderr)
            return False

        self.hooks_dir.mkdir(exist_ok=True)
        hook_path = self.hooks_dir / "pre-commit"

        if hook_path.exists() and not force:
            print(
                f"Pre-commit hook already exists at {hook_path}",
                file=sys.stderr,
            )
            print("Use force=True to overwrite", file=sys.stderr)
            return False

        # Create hook script
        hook_script = f'''#!/usr/bin/env python3
"""Pre-commit hook for Coffee Maker Agent code review."""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from coffee_maker.code_reviewer.git_integration import GitIntegration

def main():
    """Run code review on staged files."""
    integration = GitIntegration(
        block_on_critical={self.block_on_critical},
        block_on_high={self.block_on_high}
    )

    print("🔍 Running code review on staged files...")
    reports, should_block = integration.review_staged_files()

    if not reports:
        print("✅ No Python files to review")
        return 0

    # Print summary
    total_issues = sum(r.metrics.get("total_issues", 0) for r in reports)
    critical_issues = sum(r.metrics.get("critical", 0) for r in reports)
    high_issues = sum(r.metrics.get("high", 0) for r in reports)

    print(f"\\n📊 Review Results:")
    print(f"   Files reviewed: {{len(reports)}}")
    print(f"   Total issues: {{total_issues}}")
    print(f"   Critical: {{critical_issues}}")
    print(f"   High: {{high_issues}}")

    # Save detailed reports
    reports_dir = project_root / "code_review_reports"
    reports_dir.mkdir(exist_ok=True)

    for report in reports:
        file_name = Path(report.file_path).name
        report_path = reports_dir / f"{{file_name}}_review.html"

        from coffee_maker.code_reviewer.report_generator import ReportGenerator
        generator = ReportGenerator()
        generator.save_html_report(report, str(report_path))

    print(f"\\n📄 Detailed reports saved to: {{reports_dir}}")

    if should_block:
        print("\\n❌ COMMIT BLOCKED: Critical issues found!")
        print("   Fix critical issues or use --no-verify to skip")
        return 1

    if total_issues > 0:
        print("\\n⚠️  Issues found but commit allowed")
        print("   Review the reports and consider fixing them")

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

        hook_path.write_text(hook_script)
        hook_path.chmod(0o755)  # Make executable

        print(f"✅ Pre-commit hook installed at {hook_path}")
        return True

    def install_pre_push_hook(self, force: bool = False) -> bool:
        """Install pre-push hook for code review.

        Args:
            force: Overwrite existing hook

        Returns:
            True if hook was installed successfully

        Example:
            >>> integration = GitIntegration()
            >>> integration.install_pre_push_hook()
        """
        if not self.git_dir.exists():
            print(f"Error: Not a git repository: {self.repo_path}", file=sys.stderr)
            return False

        self.hooks_dir.mkdir(exist_ok=True)
        hook_path = self.hooks_dir / "pre-push"

        if hook_path.exists() and not force:
            print(f"Pre-push hook already exists at {hook_path}", file=sys.stderr)
            print("Use force=True to overwrite", file=sys.stderr)
            return False

        # Create hook script
        hook_script = f'''#!/usr/bin/env python3
"""Pre-push hook for Coffee Maker Agent code review."""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from coffee_maker.code_reviewer.git_integration import GitIntegration

def main():
    """Run code review on all changed files."""
    integration = GitIntegration(
        block_on_critical={self.block_on_critical},
        block_on_high={self.block_on_high}
    )

    print("🔍 Running code review on changed files...")
    changed_files = integration.get_changed_files()

    if not changed_files:
        print("✅ No Python files changed")
        return 0

    # Review all changed files
    reports = []
    should_block = False

    for file_path in changed_files:
        full_path = integration.repo_path / file_path
        if full_path.exists():
            try:
                report = integration.reviewer.review_file(str(full_path))
                reports.append(report)

                if integration.block_on_critical and report.metrics.get("critical", 0) > 0:
                    should_block = True
                if integration.block_on_high and report.metrics.get("high", 0) > 0:
                    should_block = True

            except Exception as e:
                print(f"Error reviewing {{file_path}}: {{e}}", file=sys.stderr)

    # Print summary
    if reports:
        total_issues = sum(r.metrics.get("total_issues", 0) for r in reports)
        critical_issues = sum(r.metrics.get("critical", 0) for r in reports)
        high_issues = sum(r.metrics.get("high", 0) for r in reports)

        print(f"\\n📊 Review Results:")
        print(f"   Files reviewed: {{len(reports)}}")
        print(f"   Total issues: {{total_issues}}")
        print(f"   Critical: {{critical_issues}}")
        print(f"   High: {{high_issues}}")

        if should_block:
            print("\\n❌ PUSH BLOCKED: Critical issues found!")
            return 1

        if total_issues > 0:
            print("\\n⚠️  Issues found but push allowed")

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

        hook_path.write_text(hook_script)
        hook_path.chmod(0o755)

        print(f"✅ Pre-push hook installed at {hook_path}")
        return True

    def uninstall_hooks(self) -> None:
        """Uninstall all code review hooks.

        Example:
            >>> integration = GitIntegration()
            >>> integration.uninstall_hooks()
        """
        hooks = ["pre-commit", "pre-push"]

        for hook_name in hooks:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists():
                # Check if it's our hook (contains "Coffee Maker Agent")
                if "Coffee Maker Agent" in hook_path.read_text():
                    hook_path.unlink()
                    print(f"✅ Removed {hook_name} hook")
                else:
                    print(f"⚠️  {hook_name} exists but wasn't created by Coffee Maker Agent")
