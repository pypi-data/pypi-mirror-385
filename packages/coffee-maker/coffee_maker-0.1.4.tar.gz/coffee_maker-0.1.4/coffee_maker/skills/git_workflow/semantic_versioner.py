"""Semantic versioning and git tagging automation."""

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class VersionBump:
    """Semantic version bump result."""

    current_version: str  # Current version (e.g., "1.2.3")
    new_version: str  # New version (e.g., "1.3.0")
    bump_type: str  # major, minor, patch
    commits_analyzed: int  # Number of commits analyzed
    reason: str  # Why this bump type was chosen


@dataclass
class GitTag:
    """Git tag information."""

    tag_name: str  # Tag name (e.g., "wip-us-067", "stable-v1.3.0")
    tag_type: str  # wip, dod-verified, stable
    message: str  # Tag annotation message
    created: bool  # Whether tag was created successfully


class SemanticVersioner:
    """Semantic versioning and git tagging automation."""

    # Tag type prefixes
    TAG_TYPES = {
        "wip": "wip-",  # Work in progress (implementation complete)
        "dod-verified": "dod-verified-",  # DoD verification complete
        "stable": "stable-v",  # Production release
    }

    # Semantic version regex
    VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize semantic versioner.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path or Path.cwd()

    def calculate_version_bump(
        self,
        since_tag: Optional[str] = None,
        override_version: Optional[str] = None,
    ) -> VersionBump:
        """Calculate semantic version bump from commits.

        Args:
            since_tag: Tag to analyze commits since (default: latest stable tag)
            override_version: Override auto-calculated version

        Returns:
            VersionBump with current, new version, and reasoning
        """
        # Get current version
        current_version = self._get_latest_stable_version()

        # If override provided, use it
        if override_version:
            return VersionBump(
                current_version=current_version,
                new_version=override_version,
                bump_type="manual",
                commits_analyzed=0,
                reason="Manual version override",
            )

        # Get commits since tag
        commits = self._get_commits_since(since_tag or f"stable-v{current_version}")

        # Analyze commits for version bump
        bump_type = self._analyze_commits_for_bump(commits)

        # Calculate new version
        new_version = self._bump_version(current_version, bump_type)

        return VersionBump(
            current_version=current_version,
            new_version=new_version,
            bump_type=bump_type,
            commits_analyzed=len(commits),
            reason=self._get_bump_reason(commits, bump_type),
        )

    def create_tag(
        self,
        tag_type: str,
        name: str,
        message: Optional[str] = None,
        version: Optional[str] = None,
    ) -> GitTag:
        """Create annotated git tag.

        Args:
            tag_type: Tag type (wip, dod-verified, stable)
            name: Tag name/identifier (e.g., "us-067", "1.3.0")
            message: Custom tag message (auto-generated if None)
            version: Version for stable tags (auto-calculated if None)

        Returns:
            GitTag with creation result
        """
        # Validate tag type
        if tag_type not in self.TAG_TYPES:
            raise ValueError(f"Invalid tag_type: {tag_type}. Must be one of {list(self.TAG_TYPES.keys())}")

        # Format tag name
        if tag_type == "stable":
            # For stable tags, name should be version (1.3.0)
            if not version:
                version = name
            tag_name = f"{self.TAG_TYPES[tag_type]}{version}"
        else:
            # For wip/dod-verified, name is identifier (us-067)
            tag_name = f"{self.TAG_TYPES[tag_type]}{name}"

        # Generate message if not provided
        if not message:
            message = self._generate_tag_message(tag_type, name, version)

        # Create annotated tag
        created = self._create_git_tag(tag_name, message)

        return GitTag(
            tag_name=tag_name,
            tag_type=tag_type,
            message=message,
            created=created,
        )

    def _get_latest_stable_version(self) -> str:
        """Get latest stable version from git tags.

        Returns:
            Latest stable version (e.g., "1.2.3") or "0.0.0" if none found
        """
        try:
            # Get all stable tags
            result = subprocess.run(
                ["git", "tag", "-l", "stable-v*"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            tags = [t.strip() for t in result.stdout.split("\n") if t.strip()]

            if not tags:
                return "0.0.0"

            # Extract versions and sort
            versions = []
            for tag in tags:
                version_str = tag.replace("stable-v", "")
                match = self.VERSION_PATTERN.match(version_str)
                if match:
                    major, minor, patch = map(int, match.groups())
                    versions.append((major, minor, patch, version_str))

            if not versions:
                return "0.0.0"

            # Sort by version tuple and return latest
            versions.sort(reverse=True)
            return versions[0][3]  # Return version string

        except subprocess.CalledProcessError:
            return "0.0.0"

    def _get_commits_since(self, since_tag: str) -> List[str]:
        """Get commit messages since tag.

        Args:
            since_tag: Tag to get commits since

        Returns:
            List of commit messages
        """
        try:
            # Check if tag exists
            tag_check = subprocess.run(
                ["git", "rev-parse", since_tag],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if tag_check.returncode != 0:
                # Tag doesn't exist, get all commits
                result = subprocess.run(
                    ["git", "log", "--oneline", "--no-merges"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # Get commits since tag
                result = subprocess.run(
                    ["git", "log", "--oneline", "--no-merges", f"{since_tag}..HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

            commits = [c.strip() for c in result.stdout.split("\n") if c.strip()]
            return commits

        except subprocess.CalledProcessError:
            return []

    def _analyze_commits_for_bump(self, commits: List[str]) -> str:
        """Analyze commits to determine version bump type.

        Args:
            commits: List of commit messages

        Returns:
            Bump type: "major", "minor", or "patch"
        """
        has_breaking = False
        has_feat = False
        has_fix = False

        for commit in commits:
            # Check for breaking changes
            if "BREAKING CHANGE" in commit or "!" in commit.split(":")[0]:
                has_breaking = True

            # Check for features
            if commit.startswith("feat(") or commit.startswith("feat:"):
                has_feat = True

            # Check for fixes
            if commit.startswith("fix(") or commit.startswith("fix:"):
                has_fix = True

        # Determine bump type
        if has_breaking:
            return "major"
        elif has_feat:
            return "minor"
        elif has_fix:
            return "patch"
        else:
            # No significant changes, default to patch
            return "patch"

    def _bump_version(self, version: str, bump_type: str) -> str:
        """Bump version based on type.

        Args:
            version: Current version (e.g., "1.2.3")
            bump_type: Bump type (major, minor, patch)

        Returns:
            New version string
        """
        match = self.VERSION_PATTERN.match(version)
        if not match:
            # Invalid version, start from 1.0.0
            return "1.0.0"

        major, minor, patch = map(int, match.groups())

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1

        return f"{major}.{minor}.{patch}"

    def _get_bump_reason(self, commits: List[str], bump_type: str) -> str:
        """Get reason for version bump.

        Args:
            commits: List of commit messages
            bump_type: Bump type chosen

        Returns:
            Human-readable reason
        """
        feat_count = sum(1 for c in commits if c.startswith("feat(") or c.startswith("feat:"))
        fix_count = sum(1 for c in commits if c.startswith("fix(") or c.startswith("fix:"))
        breaking_count = sum(1 for c in commits if "BREAKING CHANGE" in c or "!" in c)

        reasons = []
        if breaking_count > 0:
            reasons.append(f"{breaking_count} breaking change(s)")
        if feat_count > 0:
            reasons.append(f"{feat_count} new feature(s)")
        if fix_count > 0:
            reasons.append(f"{fix_count} bug fix(es)")

        if reasons:
            return f"{bump_type.capitalize()} bump: {', '.join(reasons)}"
        else:
            return f"{bump_type.capitalize()} bump: routine maintenance"

    def _generate_tag_message(self, tag_type: str, name: str, version: Optional[str]) -> str:
        """Generate tag annotation message.

        Args:
            tag_type: Tag type (wip, dod-verified, stable)
            name: Tag identifier
            version: Version (for stable tags)

        Returns:
            Formatted tag message
        """
        lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if tag_type == "wip":
            lines.append(f"Work in Progress: {name}")
            lines.append("")
            lines.append("Implementation complete, tests passing")
            lines.append("Awaiting DoD verification")
        elif tag_type == "dod-verified":
            lines.append(f"DoD Verified: {name}")
            lines.append("")
            lines.append("All Definition of Done criteria met")
            lines.append("Ready for production release")
        elif tag_type == "stable":
            lines.append(f"Release {version}")
            lines.append("")
            # Get commits since last stable
            commits = self._get_commits_since(f"stable-v{self._get_latest_stable_version()}")
            lines.append(f"Changes: {len(commits)} commits")
            lines.append("")
            lines.append("See git log for detailed changelog")

        lines.append("")
        lines.append(f"Created: {timestamp}")
        lines.append("🤖 Generated with Claude Code")

        return "\n".join(lines)

    def _create_git_tag(self, tag_name: str, message: str) -> bool:
        """Create annotated git tag.

        Args:
            tag_name: Tag name
            message: Tag annotation message

        Returns:
            True if tag created successfully, False otherwise
        """
        try:
            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            # Tag might already exist or other error
            print(f"Failed to create tag {tag_name}: {e.stderr}")
            return False
