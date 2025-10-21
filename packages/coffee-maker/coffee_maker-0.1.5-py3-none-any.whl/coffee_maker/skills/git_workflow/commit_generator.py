"""Generate conventional commit messages from git diff analysis."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CommitMessage:
    """Structured conventional commit message."""

    type: str  # feat, fix, refactor, docs, test, perf, chore
    scope: Optional[str]  # Component scope (e.g., api, auth, daemon)
    subject: str  # Short description
    body: str  # Detailed description
    footer: str  # References and co-author

    def format(self) -> str:
        """Format as conventional commit message."""
        header = f"{self.type}"
        if self.scope:
            header += f"({self.scope})"
        header += f": {self.subject}"

        parts = [header]
        if self.body:
            parts.append("")
            parts.append(self.body)
        if self.footer:
            parts.append("")
            parts.append(self.footer)

        return "\n".join(parts)


class CommitMessageGenerator:
    """Generate conventional commit messages from git diff."""

    # Conventional commit types
    COMMIT_TYPES = {
        "feat": "New feature",
        "fix": "Bug fix",
        "refactor": "Code restructuring",
        "docs": "Documentation only",
        "test": "Adding or updating tests",
        "perf": "Performance improvement",
        "chore": "Build/deps/config changes",
    }

    # Directory to scope mapping
    SCOPE_MAPPING = {
        "coffee_maker/api": "api",
        "coffee_maker/autonomous": "daemon",
        "coffee_maker/cli": "cli",
        "coffee_maker/skills": "skills",
        "coffee_maker/utils": "utils",
        "tests": "tests",
        "docs": "docs",
        ".claude": "config",
    }

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize commit message generator.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path or Path.cwd()

    def generate(
        self,
        priority_name: Optional[str] = None,
        priority_description: Optional[str] = None,
        diff_since: Optional[str] = None,
        staged_only: bool = False,
        override_type: Optional[str] = None,
        override_scope: Optional[str] = None,
    ) -> CommitMessage:
        """Generate conventional commit message from git diff.

        Args:
            priority_name: Priority identifier (e.g., "PRIORITY 10", "US-067")
            priority_description: Full priority description
            diff_since: Commit to diff since (default: HEAD~1)
            staged_only: Only analyze staged changes
            override_type: Override auto-detected commit type
            override_scope: Override auto-detected scope

        Returns:
            CommitMessage with type, scope, subject, body, footer
        """
        # Get changed files
        changed_files = self._get_changed_files(diff_since, staged_only)

        # Get diff statistics
        diff_stats = self._get_diff_stats(diff_since, staged_only)

        # Detect commit type
        commit_type = override_type or self._detect_commit_type(changed_files)

        # Detect scope
        scope = override_scope or self._detect_scope(changed_files)

        # Generate subject
        subject = self._generate_subject(commit_type, changed_files, priority_name, priority_description)

        # Generate body
        body = self._generate_body(changed_files, diff_stats, priority_name, priority_description)

        # Generate footer
        footer = self._generate_footer(priority_name)

        return CommitMessage(
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footer=footer,
        )

    def _get_changed_files(self, diff_since: Optional[str], staged_only: bool) -> List[str]:
        """Get list of changed files.

        Args:
            diff_since: Commit to diff since
            staged_only: Only get staged files

        Returns:
            List of changed file paths
        """
        try:
            if staged_only:
                # Get staged files only
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            elif diff_since:
                # Get files changed since commit
                result = subprocess.run(
                    ["git", "diff", "--name-only", diff_since],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # Get all changed files (staged + unstaged)
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

            # Also get untracked files if not staged_only
            if not staged_only:
                untracked_result = subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                untracked = [f.strip() for f in untracked_result.stdout.split("\n") if f.strip()]
                files.extend(untracked)

            return files
        except subprocess.CalledProcessError:
            return []

    def _get_diff_stats(self, diff_since: Optional[str], staged_only: bool) -> Dict[str, int]:
        """Get diff statistics (files changed, insertions, deletions).

        Args:
            diff_since: Commit to diff since
            staged_only: Only analyze staged changes

        Returns:
            Dict with 'files_changed', 'insertions', 'deletions'
        """
        try:
            cmd = ["git", "diff", "--stat"]
            if staged_only:
                cmd.insert(2, "--cached")
            elif diff_since:
                cmd.append(diff_since)

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse last line: "X files changed, Y insertions(+), Z deletions(-)"
            lines = result.stdout.strip().split("\n")
            if lines and "changed" in lines[-1]:
                summary = lines[-1]
                stats = {
                    "files_changed": 0,
                    "insertions": 0,
                    "deletions": 0,
                }

                # Parse files changed
                if "file" in summary:
                    parts = summary.split("file")
                    if parts[0].strip().isdigit():
                        stats["files_changed"] = int(parts[0].strip())

                # Parse insertions
                if "insertion" in summary:
                    parts = summary.split("insertion")
                    before = parts[0].split(",")[-1].strip()
                    if before.isdigit():
                        stats["insertions"] = int(before)

                # Parse deletions
                if "deletion" in summary:
                    parts = summary.split("deletion")
                    before = parts[0].split(",")[-1].strip()
                    if before.isdigit():
                        stats["deletions"] = int(before)

                return stats

            return {"files_changed": 0, "insertions": 0, "deletions": 0}
        except subprocess.CalledProcessError:
            return {"files_changed": 0, "insertions": 0, "deletions": 0}

    def _detect_commit_type(self, changed_files: List[str]) -> str:
        """Detect commit type from changed files.

        Args:
            changed_files: List of changed file paths

        Returns:
            Commit type (feat, fix, refactor, docs, test, chore)
        """
        # Count files by category
        test_files = sum(1 for f in changed_files if f.startswith("tests/"))
        doc_files = sum(1 for f in changed_files if f.startswith("docs/") or f.endswith(".md") or f.endswith(".rst"))
        config_files = sum(
            1
            for f in changed_files
            if f.endswith((".toml", ".yaml", ".yml", ".json", ".ini")) or f.startswith(".claude/")
        )
        impl_files = sum(1 for f in changed_files if f.startswith("coffee_maker/"))

        # Decision logic
        if doc_files > 0 and impl_files == 0 and test_files == 0:
            return "docs"
        elif test_files > 0 and impl_files == 0:
            return "test"
        elif config_files > 0 and impl_files == 0 and test_files == 0:
            return "chore"
        elif any("fix" in f.lower() for f in changed_files):
            return "fix"
        elif any("refactor" in f.lower() for f in changed_files):
            return "refactor"
        else:
            # Default: feat (new functionality)
            return "feat"

    def _detect_scope(self, changed_files: List[str]) -> Optional[str]:
        """Detect scope from changed files.

        Args:
            changed_files: List of changed file paths

        Returns:
            Scope (e.g., 'api', 'daemon', 'cli') or None
        """
        # Count files per scope
        scope_counts: Dict[str, int] = {}

        for file_path in changed_files:
            for prefix, scope in self.SCOPE_MAPPING.items():
                if file_path.startswith(prefix):
                    scope_counts[scope] = scope_counts.get(scope, 0) + 1
                    break

        if not scope_counts:
            return None

        # Return most common scope
        return max(scope_counts.items(), key=lambda x: x[1])[0]

    def _generate_subject(
        self,
        commit_type: str,
        changed_files: List[str],
        priority_name: Optional[str],
        priority_description: Optional[str],
    ) -> str:
        """Generate commit subject line.

        Args:
            commit_type: Commit type (feat, fix, etc.)
            changed_files: List of changed files
            priority_name: Priority identifier
            priority_description: Priority description

        Returns:
            Subject line (max 72 chars)
        """
        # Try to extract subject from priority description
        if priority_description:
            # Look for first sentence or line
            first_line = priority_description.split("\n")[0].strip()
            if first_line and len(first_line) < 60:
                return first_line

        # Generate from commit type and priority
        if priority_name:
            return f"Implement {priority_name}"

        # Fallback: describe changed files
        if len(changed_files) == 1:
            file_name = Path(changed_files[0]).stem
            return f"Update {file_name}"
        elif len(changed_files) <= 3:
            return f"Update {len(changed_files)} files"
        else:
            return f"Update multiple files ({len(changed_files)} changed)"

    def _generate_body(
        self,
        changed_files: List[str],
        diff_stats: Dict[str, int],
        priority_name: Optional[str],
        priority_description: Optional[str],
    ) -> str:
        """Generate commit body with details.

        Args:
            changed_files: List of changed files
            diff_stats: Diff statistics
            priority_name: Priority identifier
            priority_description: Priority description

        Returns:
            Commit body with bullet points
        """
        lines = []

        # Add priority context
        if priority_name:
            lines.append(f"Implements {priority_name}")
            if priority_description:
                # Add first few lines of description
                desc_lines = priority_description.split("\n")[:3]
                for line in desc_lines:
                    if line.strip():
                        lines.append(f"- {line.strip()}")

        # Add file change summary
        if changed_files:
            lines.append("")
            lines.append("Changes:")

            # Group files by type
            impl_files = [f for f in changed_files if f.startswith("coffee_maker/")]
            test_files = [f for f in changed_files if f.startswith("tests/")]
            doc_files = [f for f in changed_files if f.startswith("docs/") or f.endswith((".md", ".rst"))]

            if impl_files:
                lines.append(f"- Implementation: {len(impl_files)} files")
            if test_files:
                lines.append(f"- Tests: {len(test_files)} files")
            if doc_files:
                lines.append(f"- Documentation: {len(doc_files)} files")

        # Add diff statistics
        if diff_stats["insertions"] > 0 or diff_stats["deletions"] > 0:
            lines.append("")
            lines.append(f"Stats: +{diff_stats['insertions']} -{diff_stats['deletions']}")

        return "\n".join(lines)

    def _generate_footer(self, priority_name: Optional[str]) -> str:
        """Generate commit footer with references and co-author.

        Args:
            priority_name: Priority identifier

        Returns:
            Footer with references and co-author
        """
        lines = []

        # Add priority reference
        if priority_name:
            if priority_name.startswith("US-"):
                lines.append(f"Implements: {priority_name}")
            elif priority_name.startswith("PRIORITY"):
                lines.append(f"Relates-to: {priority_name}")

        # Add standard footer
        lines.append("")
        lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")
        lines.append("")
        lines.append("Co-Authored-By: Claude <noreply@anthropic.com>")

        return "\n".join(lines)
