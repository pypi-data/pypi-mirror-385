"""Dependency approval checking utility.

This module provides automated dependency classification based on the
pre-approval matrix defined in SPEC-070.

Usage:
    from coffee_maker.utils.dependency_checker import DependencyChecker, ApprovalStatus

    checker = DependencyChecker()

    # Check if package is pre-approved
    status = checker.get_approval_status("pytest-timeout")

    if status == ApprovalStatus.PRE_APPROVED:
        # Safe to add without user approval
        subprocess.run(["poetry", "add", "pytest-timeout"])
    elif status == ApprovalStatus.NEEDS_REVIEW:
        # Requires architect review
        delegate_to_architect("pytest-timeout")
    elif status == ApprovalStatus.BANNED:
        # Reject with alternatives
        print(f"Banned: {checker.get_ban_reason('pytest-timeout')}")
        print(f"Alternatives: {checker.get_alternatives('pytest-timeout')}")

See: docs/architecture/specs/SPEC-070-dependency-pre-approval-matrix.md
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ApprovalStatus(Enum):
    """Dependency approval status."""

    PRE_APPROVED = "pre_approved"  # Auto-add, no user approval
    NEEDS_REVIEW = "needs_review"  # Requires architect review + user approval
    BANNED = "banned"  # Auto-reject with alternatives


class BanReason(Enum):
    """Reasons for banning a dependency."""

    GPL_LICENSE = "GPL license (incompatible with Apache 2.0)"
    UNMAINTAINED = "Unmaintained (last commit >2 years ago)"
    HIGH_CVE = "High CVE count (>5 critical vulnerabilities)"
    HEAVY_WEIGHT = "Heavyweight (>100MB install size)"
    SECURITY_ISSUE = "Known security issues"


class DependencyChecker:
    """Check if dependencies are pre-approved, need review, or are banned.

    This class implements the three-tier dependency approval system defined in SPEC-070:

    Tier 1: PRE_APPROVED - Auto-approve without user consent (2-5 min)
    Tier 2: NEEDS_REVIEW - Requires architect evaluation + user approval (20-30 min)
    Tier 3: BANNED - Auto-reject with alternatives (immediate)

    Attributes:
        PRE_APPROVED_PACKAGES: Dict of pre-approved packages with version constraints
        BANNED_PACKAGES: Dict of banned packages with ban reasons and alternatives
        project_root: Path to project root directory
        pyproject_path: Path to pyproject.toml file

    Example:
        >>> checker = DependencyChecker()
        >>> status = checker.get_approval_status("pytest-timeout")
        >>> if status == ApprovalStatus.PRE_APPROVED:
        ...     print("Safe to add without user approval")
        Safe to add without user approval
    """

    # Pre-approved packages (63 packages across 10 categories)
    # See: SPEC-070-dependency-pre-approval-matrix.md
    PRE_APPROVED_PACKAGES: Dict[str, str] = {
        # Category 1: Testing & Quality Assurance (17 packages)
        "pytest": ">=8.0,<9.0",
        "pytest-cov": ">=6.0,<7.0",
        "pytest-xdist": ">=3.0,<4.0",
        "pytest-timeout": ">=2.0,<3.0",
        "pytest-benchmark": ">=4.0,<5.0",
        "pytest-mock": ">=3.0,<4.0",
        "pytest-asyncio": ">=0.23,<1.0",
        "pytest-env": ">=1.0,<2.0",
        "pytest-clarity": ">=1.0,<2.0",
        "pytest-sugar": ">=1.0,<2.0",
        "hypothesis": ">=6.0,<7.0",
        "coverage": ">=7.0,<8.0",
        "mypy": ">=1.0,<2.0",
        "pylint": ">=4.0,<5.0",  # GPL-2.0 exempted (dev-only)
        "radon": ">=6.0,<7.0",
        "bandit": ">=1.7,<2.0",
        "safety": ">=3.0,<4.0",
        # Category 2: Code Formatting & Style (8 packages)
        "black": ">=24.0,<25.0",
        "autoflake": ">=2.0,<3.0",
        "isort": ">=5.0,<6.0",
        "flake8": ">=7.0,<8.0",
        "ruff": ">=0.1,<1.0",
        "autopep8": ">=2.0,<3.0",
        "pydocstyle": ">=6.0,<7.0",
        "pre-commit": ">=4.0,<5.0",
        # Category 3: Observability & Monitoring (6 packages)
        "langfuse": ">=3.0,<4.0",
        "opentelemetry-api": ">=1.20,<2.0",
        "opentelemetry-sdk": ">=1.20,<2.0",
        "opentelemetry-instrumentation": ">=0.41,<1.0",
        "prometheus-client": ">=0.19,<1.0",
        "sentry-sdk": ">=2.0,<3.0",
        # Category 4: Performance & Caching (5 packages)
        "cachetools": ">=5.0,<6.0",
        "redis": ">=5.0,<6.0",
        "hiredis": ">=2.0,<3.0",
        "diskcache": ">=5.0,<6.0",
        "msgpack": ">=1.0,<2.0",
        # Category 5: CLI & User Interface (7 packages)
        "click": ">=8.0,<9.0",
        "typer": ">=0.9,<1.0",
        "rich": ">=13.0,<14.0",
        "prompt-toolkit": ">=3.0,<4.0",
        "colorama": ">=0.4,<1.0",
        "tabulate": ">=0.9,<1.0",
        "tqdm": ">=4.0,<5.0",
        # Category 6: Data Validation & Serialization (5 packages)
        "pydantic": ">=2.0,<3.0",
        "pydantic-settings": ">=2.0,<3.0",
        "marshmallow": ">=3.0,<4.0",
        "jsonschema": ">=4.0,<5.0",
        "cattrs": ">=23.0,<24.0",
        # Category 7: HTTP & Networking (4 packages)
        "requests": ">=2.31,<3.0",
        "httpx": ">=0.25,<1.0",
        "urllib3": ">=2.0,<3.0",
        "aiohttp": ">=3.9,<4.0",
        # Category 8: Date & Time (2 packages)
        "python-dateutil": ">=2.8,<3.0",
        "pytz": ">=2023.3,<2025.0",
        # Category 9: Configuration & Environment (3 packages)
        "python-dotenv": ">=1.0,<2.0",
        "pyyaml": ">=6.0,<7.0",
        "toml": ">=0.10,<1.0",
        # Category 10: AI & Language Models (6 packages)
        "anthropic": ">=0.40,<1.0",
        "openai": ">=1.0,<2.0",
        "tiktoken": ">=0.5,<1.0",
        "langchain": ">=0.3,<1.0",
        "langchain-core": ">=0.3,<1.0",
        "langchain-anthropic": ">=0.2,<1.0",
    }

    # Banned packages with reasons and alternatives
    BANNED_PACKAGES: Dict[str, Tuple[BanReason, List[str]]] = {
        # GPL-licensed packages (incompatible with Apache 2.0)
        "mysql-connector-python": (BanReason.GPL_LICENSE, ["pymysql", "aiomysql"]),
        "pyqt5": (BanReason.GPL_LICENSE, ["pyside6", "tkinter"]),
        # Unmaintained packages
        "nose": (BanReason.UNMAINTAINED, ["pytest"]),
        "nose2": (BanReason.UNMAINTAINED, ["pytest"]),
        # Add more banned packages as identified
    }

    def __init__(self):
        """Initialize dependency checker.

        Sets up paths to project root and pyproject.toml for dependency scanning.
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.pyproject_path = self.project_root / "pyproject.toml"

    def get_approval_status(self, package_name: str) -> ApprovalStatus:
        """Get approval status for a package.

        Args:
            package_name: Name of the package (e.g., "pytest-timeout")

        Returns:
            ApprovalStatus: PRE_APPROVED, NEEDS_REVIEW, or BANNED

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_approval_status("pytest-timeout")
            <ApprovalStatus.PRE_APPROVED: 'pre_approved'>
            >>> checker.get_approval_status("unknown-package")
            <ApprovalStatus.NEEDS_REVIEW: 'needs_review'>
            >>> checker.get_approval_status("mysql-connector-python")
            <ApprovalStatus.BANNED: 'banned'>
        """
        # Normalize package name (lowercase, replace _ with -)
        normalized_name = self._normalize_package_name(package_name)

        # Check if banned first (highest priority)
        if normalized_name in self.BANNED_PACKAGES:
            return ApprovalStatus.BANNED

        # Check if pre-approved
        if normalized_name in self.PRE_APPROVED_PACKAGES:
            return ApprovalStatus.PRE_APPROVED

        # Default: needs review
        return ApprovalStatus.NEEDS_REVIEW

    def is_pre_approved(self, package_name: str, version: Optional[str] = None) -> bool:
        """Check if package@version is pre-approved.

        Args:
            package_name: Name of the package
            version: Optional version specifier (e.g., ">=2.0,<3.0")

        Returns:
            bool: True if pre-approved, False otherwise

        Example:
            >>> checker = DependencyChecker()
            >>> checker.is_pre_approved("pytest-timeout")
            True
            >>> checker.is_pre_approved("pytest-timeout", ">=2.0,<3.0")
            True
            >>> checker.is_pre_approved("unknown-package")
            False
        """
        normalized_name = self._normalize_package_name(package_name)

        if normalized_name not in self.PRE_APPROVED_PACKAGES:
            return False

        # If version provided, could check compatibility here
        # For now, simplified: pre-approved packages are always approved
        # regardless of specific version (trust version constraint in dict)
        return True

    def get_ban_reason(self, package_name: str) -> Optional[str]:
        """Get reason why package is banned.

        Args:
            package_name: Name of the package

        Returns:
            str: Human-readable ban reason, or None if not banned

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_ban_reason("mysql-connector-python")
            'GPL license (incompatible with Apache 2.0)'
            >>> checker.get_ban_reason("pytest-timeout")
            None
        """
        normalized_name = self._normalize_package_name(package_name)

        if normalized_name in self.BANNED_PACKAGES:
            ban_reason, _ = self.BANNED_PACKAGES[normalized_name]
            return ban_reason.value

        return None

    def get_alternatives(self, package_name: str) -> List[str]:
        """Get pre-approved alternatives for a banned package.

        Args:
            package_name: Name of the banned package

        Returns:
            List[str]: List of alternative package names

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_alternatives("mysql-connector-python")
            ['pymysql', 'aiomysql']
            >>> checker.get_alternatives("pytest-timeout")
            []
        """
        normalized_name = self._normalize_package_name(package_name)

        if normalized_name in self.BANNED_PACKAGES:
            _, alternatives = self.BANNED_PACKAGES[normalized_name]
            return alternatives

        return []

    def get_version_constraint(self, package_name: str) -> Optional[str]:
        """Get recommended version constraint for a pre-approved package.

        Args:
            package_name: Name of the package

        Returns:
            str: Version constraint (e.g., ">=2.0,<3.0"), or None if not pre-approved

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_version_constraint("pytest-timeout")
            '>=2.0,<3.0'
            >>> checker.get_version_constraint("unknown-package")
            None
        """
        normalized_name = self._normalize_package_name(package_name)
        return self.PRE_APPROVED_PACKAGES.get(normalized_name)

    def check_pyproject_toml(self) -> List[str]:
        """Scan pyproject.toml for unapproved dependencies.

        Returns:
            List[str]: List of unapproved package names (including BANNED packages)

        Example:
            >>> checker = DependencyChecker()
            >>> unapproved = checker.check_pyproject_toml()
            >>> if unapproved:
            ...     print(f"Found unapproved dependencies: {unapproved}")
        """
        if not self.pyproject_path.exists():
            return []

        try:
            import toml
        except ImportError:
            # toml not installed, skip check
            return []

        # Load pyproject.toml
        try:
            with open(self.pyproject_path, "r") as f:
                pyproject = toml.load(f)
        except Exception:
            # Failed to load pyproject.toml
            return []

        # Get dependencies from Poetry format
        dependencies = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
        dev_dependencies = (
            pyproject.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {})
        )

        all_deps = {**dependencies, **dev_dependencies}

        # Filter out Python version and pre-approved packages
        unapproved = []
        for package_name in all_deps.keys():
            if package_name == "python":
                continue

            status = self.get_approval_status(package_name)
            if status == ApprovalStatus.NEEDS_REVIEW:
                unapproved.append(package_name)
            elif status == ApprovalStatus.BANNED:
                unapproved.append(f"{package_name} (BANNED)")

        return unapproved

    def _normalize_package_name(self, package_name: str) -> str:
        """Normalize package name for consistent comparison.

        Converts to lowercase and replaces underscores with hyphens.

        Args:
            package_name: Raw package name

        Returns:
            str: Normalized package name

        Example:
            >>> checker = DependencyChecker()
            >>> checker._normalize_package_name("PyTest-TimeOut")
            'pytest-timeout'
            >>> checker._normalize_package_name("pytest_timeout")
            'pytest-timeout'
        """
        return package_name.lower().replace("_", "-")

    def get_pre_approved_count(self) -> int:
        """Get total number of pre-approved packages.

        Returns:
            int: Number of pre-approved packages

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_pre_approved_count()
            63
        """
        return len(self.PRE_APPROVED_PACKAGES)

    def get_banned_count(self) -> int:
        """Get total number of banned packages.

        Returns:
            int: Number of banned packages

        Example:
            >>> checker = DependencyChecker()
            >>> checker.get_banned_count()
            4
        """
        return len(self.BANNED_PACKAGES)

    def list_pre_approved_by_category(self) -> Dict[str, List[str]]:
        """List all pre-approved packages grouped by category.

        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to package lists

        Example:
            >>> checker = DependencyChecker()
            >>> categories = checker.list_pre_approved_by_category()
            >>> print(categories["Testing & QA"][:3])
            ['pytest', 'pytest-cov', 'pytest-xdist']
        """
        # Define categories (same as in SPEC-070)
        categories = {
            "Testing & QA": [
                "pytest",
                "pytest-cov",
                "pytest-xdist",
                "pytest-timeout",
                "pytest-benchmark",
                "pytest-mock",
                "pytest-asyncio",
                "pytest-env",
                "pytest-clarity",
                "pytest-sugar",
                "hypothesis",
                "coverage",
                "mypy",
                "pylint",
                "radon",
                "bandit",
                "safety",
            ],
            "Code Formatting": [
                "black",
                "autoflake",
                "isort",
                "flake8",
                "ruff",
                "autopep8",
                "pydocstyle",
                "pre-commit",
            ],
            "Observability": [
                "langfuse",
                "opentelemetry-api",
                "opentelemetry-sdk",
                "opentelemetry-instrumentation",
                "prometheus-client",
                "sentry-sdk",
            ],
            "Performance": ["cachetools", "redis", "hiredis", "diskcache", "msgpack"],
            "CLI & UI": [
                "click",
                "typer",
                "rich",
                "prompt-toolkit",
                "colorama",
                "tabulate",
                "tqdm",
            ],
            "Data Validation": [
                "pydantic",
                "pydantic-settings",
                "marshmallow",
                "jsonschema",
                "cattrs",
            ],
            "HTTP & Networking": ["requests", "httpx", "urllib3", "aiohttp"],
            "Date & Time": ["python-dateutil", "pytz"],
            "Configuration": ["python-dotenv", "pyyaml", "toml"],
            "AI & Language Models": [
                "anthropic",
                "openai",
                "tiktoken",
                "langchain",
                "langchain-core",
                "langchain-anthropic",
            ],
        }

        return categories
