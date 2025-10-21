"""
Dependency version analyzer.

Analyzes package version information and recency using PyPI API.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from packaging.version import Version, InvalidVersion

logger = logging.getLogger(__name__)


class VersionAnalyzer:
    """
    Analyzes package version information and recency.

    Uses PyPI JSON API to check latest versions and release notes.
    """

    def __init__(self):
        """Initialize analyzer with PyPI API client."""
        self.pypi_base_url = "https://pypi.org/pypi"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MonolithicCoffeeMakerAgent/1.0"})
        logger.debug("VersionAnalyzer initialized")

    def analyze_version(
        self, package_name: str, requested_version: Optional[str] = None
    ) -> "VersionInfo":  # noqa: F821
        """
        Analyze version information for package.

        Args:
            package_name: Package to analyze
            requested_version: Optional version constraint

        Returns:
            VersionInfo with latest version, deprecation status, etc.

        Implementation:
        1. Fetch package metadata from PyPI
        2. Extract latest stable version (non-pre-release)
        3. Check if requested version is latest
        4. Check deprecation status (metadata or release notes)
        5. Parse release notes for breaking changes (heuristics)
        6. Suggest optimal version constraint
        """
        logger.info(f"Analyzing version for {package_name} (requested: {requested_version or 'latest'})")

        # Fetch PyPI metadata
        metadata = self._fetch_pypi_metadata(package_name)

        # Get all versions
        releases = metadata.get("releases", {})
        all_versions = list(releases.keys())

        # Get latest stable version
        latest_stable = self._get_latest_stable_version(all_versions)

        # Check if requested version is latest
        is_latest = False
        if requested_version:
            # Extract version number from constraint
            version_match = re.search(r"[\d\.]+", requested_version)
            if version_match:
                requested_ver_num = version_match.group(0)
                is_latest = requested_ver_num == latest_stable
        else:
            is_latest = True  # No specific version requested, will use latest

        # Check deprecation status
        is_deprecated = self._is_deprecated(metadata, latest_stable)

        # Parse breaking changes (from release notes)
        breaking_changes = self._parse_breaking_changes(metadata, latest_stable)

        # Suggest version constraint
        suggested_constraint = self._suggest_version_constraint(latest_stable, requested_version)

        # Get release date
        release_date = self._get_release_date(metadata, latest_stable)

        # Import here to avoid circular imports
        from coffee_maker.utils.dependency_analyzer import VersionInfo

        version_info = VersionInfo(
            requested_version=requested_version,
            latest_stable=latest_stable,
            is_latest=is_latest,
            is_deprecated=is_deprecated,
            breaking_changes=breaking_changes,
            suggested_constraint=suggested_constraint,
            release_date=release_date,
        )

        logger.info(
            f"Version analysis for {package_name}: latest={latest_stable}, "
            f"deprecated={is_deprecated}, breaking_changes={len(breaking_changes)}"
        )

        return version_info

    def _fetch_pypi_metadata(self, package_name: str) -> Dict[str, Any]:
        """
        Fetch package metadata from PyPI JSON API.

        Args:
            package_name: Package name

        Returns:
            Dict with package metadata

        Raises:
            PackageNotFoundError: If package doesn't exist
        """
        try:
            url = f"{self.pypi_base_url}/{package_name}/json"
            logger.debug(f"Fetching PyPI metadata: {url}")

            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                from coffee_maker.utils.dependency_analyzer import PackageNotFoundError

                raise PackageNotFoundError(f"Package '{package_name}' not found on PyPI")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to fetch PyPI metadata for {package_name}: {str(e)}")
            # Return minimal metadata on error
            return {"info": {"version": "0.0.0"}, "releases": {}}

    def _get_latest_stable_version(self, versions: List[str]) -> str:
        """
        Get latest stable version (exclude alpha, beta, rc).

        Uses packaging.version.Version for comparison.

        Args:
            versions: List of version strings

        Returns:
            Latest stable version string
        """
        if not versions:
            return "0.0.0"

        stable_versions = []

        for ver_str in versions:
            try:
                ver = Version(ver_str)

                # Exclude pre-releases (alpha, beta, rc, dev)
                if not ver.is_prerelease and not ver.is_devrelease:
                    stable_versions.append((ver, ver_str))

            except InvalidVersion:
                logger.debug(f"Invalid version string: {ver_str}")
                continue

        if not stable_versions:
            # No stable versions found, return the highest version
            logger.warning("No stable versions found, using latest (including pre-release)")
            try:
                all_vers = [(Version(v), v) for v in versions]
                all_vers.sort(reverse=True)
                return all_vers[0][1] if all_vers else "0.0.0"
            except:
                return versions[-1] if versions else "0.0.0"

        # Sort by version and return latest
        stable_versions.sort(reverse=True)
        latest = stable_versions[0][1]

        logger.debug(f"Latest stable version: {latest} (from {len(stable_versions)} stable versions)")
        return latest

    def _is_deprecated(self, metadata: Dict[str, Any], version: str) -> bool:
        """
        Check if version is deprecated.

        Heuristics:
        - Check metadata["yanked"]
        - Check release notes for "deprecated" keyword
        - Check if version is very old (>2 years)

        Args:
            metadata: PyPI metadata dict
            version: Version string

        Returns:
            True if deprecated, False otherwise
        """
        # Check if version is yanked
        releases = metadata.get("releases", {})
        version_releases = releases.get(version, [])

        for release in version_releases:
            if release.get("yanked", False):
                logger.info(f"Version {version} is yanked (deprecated)")
                return True

        # Check release notes for "deprecated"
        info = metadata.get("info", {})
        description = (info.get("description", "") or "").lower()
        summary = (info.get("summary", "") or "").lower()

        if "deprecated" in description or "deprecated" in summary:
            logger.info(f"Version {version} marked as deprecated in description")
            return True

        # Check if version is very old (>2 years)
        release_date_str = self._get_release_date(metadata, version)
        if release_date_str != "Unknown":
            try:
                release_date = datetime.fromisoformat(release_date_str)
                age_days = (datetime.now() - release_date).days

                if age_days > 730:  # 2 years
                    logger.info(f"Version {version} is very old ({age_days} days)")
                    # Don't mark as deprecated just for being old
                    # (many stable packages have old releases)
            except:
                pass

        return False

    def _parse_breaking_changes(self, metadata: Dict[str, Any], version: str) -> List[str]:
        """
        Parse release notes for breaking changes.

        Heuristics:
        - Look for "BREAKING CHANGE", "BREAKING:", "Breaking Changes"
        - Look for "removed", "deprecated" keywords
        - Check major version bump (1.x → 2.x)

        Args:
            metadata: PyPI metadata dict
            version: Version string

        Returns:
            List of breaking change descriptions
        """
        breaking_changes = []

        # Get release notes from description
        info = metadata.get("info", {})
        description = info.get("description", "") or ""

        # Look for breaking change keywords
        breaking_patterns = [
            r"BREAKING\s+CHANGE[S]?:?\s*(.+?)(?:\n\n|\n-|\Z)",
            r"Breaking\s+Changes?:?\s*(.+?)(?:\n\n|\n-|\Z)",
            r"⚠️\s*BREAKING:?\s*(.+?)(?:\n\n|\n-|\Z)",
        ]

        for pattern in breaking_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            for match in matches:
                change = match.strip()
                if change and len(change) < 500:  # Limit length
                    breaking_changes.append(change)

        # Check for major version bump
        try:
            ver = Version(version)
            if ver.major > 1:
                # Check if this is a major version bump from previous
                breaking_changes.append(f"Major version {ver.major} - review changelog for breaking changes")
        except InvalidVersion:
            pass

        # Deduplicate
        breaking_changes = list(set(breaking_changes))

        if breaking_changes:
            logger.info(f"Found {len(breaking_changes)} breaking changes for version {version}")

        return breaking_changes[:5]  # Limit to 5 most relevant

    def _suggest_version_constraint(self, latest_version: str, requested_version: Optional[str]) -> str:
        """
        Suggest optimal version constraint.

        Rules:
        - If no version requested: ^{major}.{minor}.0
        - If exact version: =={version}
        - If range: Keep as-is
        - Prefer caret (^) over tilde (~) for flexibility

        Args:
            latest_version: Latest stable version
            requested_version: Requested version constraint

        Returns:
            Suggested version constraint
        """
        # If version explicitly requested, respect it
        if requested_version:
            # Check if it's already a constraint
            if any(op in requested_version for op in ["^", "~", "==", ">=", "<=", ">", "<"]):
                return requested_version
            # If just a version number, suggest exact match
            return f"=={requested_version}"

        # Suggest caret constraint for latest version
        try:
            ver = Version(latest_version)
            # Use caret constraint: ^major.minor.0
            # This allows patch updates but not minor/major
            return f"^{ver.major}.{ver.minor}.0"
        except InvalidVersion:
            return f"=={latest_version}"

    def _get_release_date(self, metadata: Dict[str, Any], version: str) -> str:
        """
        Get release date for version.

        Args:
            metadata: PyPI metadata dict
            version: Version string

        Returns:
            ISO format date string or "Unknown"
        """
        releases = metadata.get("releases", {})
        version_releases = releases.get(version, [])

        if version_releases:
            # Get upload time from first release file
            upload_time = version_releases[0].get("upload_time", "")
            if upload_time:
                try:
                    # Parse and format date
                    dt = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                    return dt.strftime("%Y-%m-%d")
                except:
                    pass

        return "Unknown"
