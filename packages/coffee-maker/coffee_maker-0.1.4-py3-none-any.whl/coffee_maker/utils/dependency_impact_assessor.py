"""
Dependency impact assessor.

Assesses the impact of adding a dependency (installation time, bundle size, sub-dependencies).
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class ImpactAssessor:
    """
    Assesses the impact of adding a dependency.

    Estimates installation time, bundle size, and sub-dependencies.
    """

    def __init__(self, project_root: Path):
        """
        Initialize assessor with project root.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.pypi_base_url = "https://pypi.org/pypi"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MonolithicCoffeeMakerAgent/1.0"})
        logger.debug(f"ImpactAssessor initialized for {project_root}")

    def assess_impact(self, package_name: str, version: Optional[str] = None) -> "ImpactAssessment":  # noqa: F821
        """
        Assess installation impact for package.

        Args:
            package_name: Package to assess
            version: Optional version constraint

        Returns:
            ImpactAssessment with time, size, sub-deps

        Implementation:
        1. Run `poetry show {package}` to get package info
        2. Parse output for wheel size (or estimate from PyPI)
        3. Count sub-dependencies from `poetry show --tree`
        4. Estimate install time (heuristic: 2s base + 0.5s per sub-dep)
        5. Check platform compatibility (metadata)
        """
        logger.info(f"Assessing impact for {package_name} (version: {version or 'latest'})")

        # Estimate bundle size
        bundle_size_mb = self._estimate_bundle_size(package_name, version)

        # Count sub-dependencies
        total_sub_deps, sub_dep_list = self._count_sub_dependencies(package_name, version)

        # Estimate install time
        install_time_seconds = self._estimate_install_time(total_sub_deps, bundle_size_mb)

        # Check platform compatibility
        platform_compat = self._check_platform_compatibility(package_name)

        # Import here to avoid circular imports
        from coffee_maker.utils.dependency_analyzer import ImpactAssessment

        impact = ImpactAssessment(
            estimated_install_time_seconds=install_time_seconds,
            bundle_size_mb=bundle_size_mb,
            sub_dependencies_added=sub_dep_list,
            platform_compatibility=platform_compat,
        )

        logger.info(
            f"Impact assessment for {package_name}: {bundle_size_mb:.2f}MB, "
            f"{total_sub_deps} sub-deps, ~{install_time_seconds}s install"
        )

        return impact

    def _estimate_bundle_size(self, package_name: str, version: Optional[str]) -> float:
        """
        Estimate bundle size in MB.

        Methods:
        1. Check PyPI metadata for wheel size
        2. If not available, estimate from package downloads
        3. Fallback: 1 MB (conservative estimate)

        Args:
            package_name: Package name
            version: Optional version constraint

        Returns:
            Estimated bundle size in MB
        """
        try:
            # Fetch PyPI metadata
            url = f"{self.pypi_base_url}/{package_name}/json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                metadata = response.json()

                # Get latest version info
                info = metadata.get("info", {})
                latest_version = info.get("version", "")

                # Get release files for latest version
                releases = metadata.get("releases", {})
                version_files = releases.get(latest_version, [])

                if version_files:
                    # Find wheel file (preferred) or source distribution
                    wheel_files = [f for f in version_files if f.get("packagetype") == "bdist_wheel"]
                    sdist_files = [f for f in version_files if f.get("packagetype") == "sdist"]

                    target_file = wheel_files[0] if wheel_files else (sdist_files[0] if sdist_files else None)

                    if target_file:
                        size_bytes = target_file.get("size", 0)
                        size_mb = size_bytes / (1024 * 1024)
                        logger.debug(f"Bundle size for {package_name}: {size_mb:.2f}MB")
                        return round(size_mb, 2)

        except Exception as e:
            logger.debug(f"Could not estimate bundle size for {package_name}: {str(e)}")

        # Fallback: conservative estimate
        return 1.0

    def _count_sub_dependencies(self, package_name: str, version: Optional[str]) -> Tuple[int, List[str]]:
        """
        Count sub-dependencies and return list.

        Uses `poetry show --tree` (simulated with --dry-run).

        Args:
            package_name: Package name
            version: Optional version constraint

        Returns:
            Tuple of (count, list of sub-dependency names)
        """
        sub_deps = []

        try:
            # Try to get dependency tree
            result = subprocess.run(
                ["poetry", "show", package_name, "--tree"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                tree_output = result.stdout
                lines = tree_output.split("\n")

                for line in lines:
                    # Parse dependency names from tree
                    # Format: "├── package-name version"
                    if "──" in line:
                        # Extract package name
                        parts = line.split("──")
                        if len(parts) > 1:
                            dep_info = parts[1].strip()
                            # Get just the package name (before version)
                            dep_name = dep_info.split()[0] if dep_info else ""
                            if dep_name and dep_name != package_name:
                                sub_deps.append(dep_name)

                logger.debug(f"Found {len(sub_deps)} sub-dependencies for {package_name}")

        except Exception as e:
            logger.debug(f"Could not count sub-dependencies for {package_name}: {str(e)}")

        # Remove duplicates and return
        unique_sub_deps = list(set(sub_deps))
        return len(unique_sub_deps), unique_sub_deps

    def _estimate_install_time(self, sub_dep_count: int, bundle_size_mb: float) -> int:
        """
        Estimate installation time in seconds.

        Heuristic:
        - Base: 2 seconds (poetry overhead)
        - Per sub-dependency: 0.5 seconds
        - Per MB: 0.2 seconds (download + extract)

        Args:
            sub_dep_count: Number of sub-dependencies
            bundle_size_mb: Bundle size in MB

        Returns:
            Estimated install time in seconds
        """
        base_time = 2  # Poetry overhead
        sub_dep_time = sub_dep_count * 0.5
        download_time = bundle_size_mb * 0.2

        total_time = int(base_time + sub_dep_time + download_time)

        # Minimum 2 seconds
        return max(2, total_time)

    def _check_platform_compatibility(self, package_name: str) -> Dict[str, bool]:
        """
        Check platform compatibility from PyPI metadata.

        Returns: {"linux": True, "macos": True, "windows": True}

        Args:
            package_name: Package name

        Returns:
            Dict with platform compatibility flags
        """
        # Default: assume compatible with all platforms
        platform_compat = {
            "linux": True,
            "macos": True,
            "windows": True,
        }

        try:
            # Fetch PyPI metadata
            url = f"{self.pypi_base_url}/{package_name}/json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                metadata = response.json()
                info = metadata.get("info", {})

                # Check classifiers for OS-specific info
                classifiers = info.get("classifiers", [])

                # Look for OS-specific classifiers
                # "Operating System :: POSIX :: Linux"
                # "Operating System :: MacOS"
                # "Operating System :: Microsoft :: Windows"

                has_os_restrictions = False
                supports_linux = False
                supports_macos = False
                supports_windows = False

                for classifier in classifiers:
                    if "Operating System ::" in classifier:
                        has_os_restrictions = True
                        if "Linux" in classifier or "POSIX" in classifier:
                            supports_linux = True
                        if "MacOS" in classifier or "Mac OS" in classifier:
                            supports_macos = True
                        if "Windows" in classifier or "Microsoft" in classifier:
                            supports_windows = True

                # If OS restrictions found, update compatibility
                if has_os_restrictions:
                    platform_compat["linux"] = supports_linux
                    platform_compat["macos"] = supports_macos
                    platform_compat["windows"] = supports_windows

                    logger.debug(
                        f"Platform compatibility for {package_name}: "
                        f"linux={supports_linux}, macos={supports_macos}, windows={supports_windows}"
                    )

        except Exception as e:
            logger.debug(f"Could not check platform compatibility for {package_name}: {str(e)}")

        return platform_compat
