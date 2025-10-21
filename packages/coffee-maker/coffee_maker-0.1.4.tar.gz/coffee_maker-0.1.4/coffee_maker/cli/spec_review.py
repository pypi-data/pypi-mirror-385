"""Spec Coverage Review Tool for architect - US-047 Phase 2.

This module provides tools for architect to review technical spec coverage
across all ROADMAP priorities.

The SpecReviewReport tool:
1. Parses ROADMAP.md for all priorities
2. Checks which have technical specifications
3. Generates a markdown report showing spec coverage
4. Highlights priorities missing specs (action items for architect)

Usage:
    >>> from coffee_maker.cli.spec_review import SpecReviewReport
    >>> report = SpecReviewReport()
    >>> print(report.generate_report())

CLI Usage:
    project-manager spec-review
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

from coffee_maker.config import ROADMAP_PATH

logger = logging.getLogger(__name__)


class SpecReviewReport:
    """Generate technical spec coverage reports for architect.

    This tool helps architect proactively ensure all priorities have technical
    specifications, enforcing CFR-008.

    Attributes:
        roadmap_path: Path to ROADMAP.md file
        spec_dir: Path to architecture specs directory
    """

    def __init__(self, roadmap_path: Path = None, spec_dir: Path = None):
        """Initialize spec review tool.

        Args:
            roadmap_path: Path to ROADMAP.md (defaults to project ROADMAP)
            spec_dir: Path to specs directory (defaults to docs/architecture/specs)
        """
        self.roadmap_path = roadmap_path or ROADMAP_PATH
        # ROADMAP is at docs/ROADMAP.md, so parent is docs/, then we add architecture/specs
        self.spec_dir = spec_dir or (self.roadmap_path.parent / "architecture" / "specs")

    def generate_report(self) -> str:
        """Generate markdown report of spec coverage.

        Steps:
            1. Parse ROADMAP.md for all priorities
            2. Check which have technical specs
            3. Format as markdown table with summary stats
            4. Return formatted report

        Returns:
            Markdown-formatted report string
        """
        # Parse priorities from ROADMAP
        priorities = self._parse_roadmap()

        if not priorities:
            return "❌ No priorities found in ROADMAP.md"

        # Check spec existence for each priority
        coverage_data = []
        for priority in priorities:
            spec_exists = self._check_spec_exists(priority)
            coverage_data.append(
                {
                    "priority": priority["name"],
                    "title": priority["title"],
                    "spec_exists": spec_exists,
                }
            )

        # Generate report
        report = self._format_report(coverage_data, priorities)
        return report

    def _parse_roadmap(self) -> List[Dict]:
        """Parse ROADMAP.md to extract all priorities.

        Looks for markdown headers like:
        - ### PRIORITY 1: Title
        - ### US-001: Title
        - ### PRIORITY 1.5: Title (decimal notation)

        Returns:
            List of priority dictionaries with name, title, status
        """
        if not self.roadmap_path.exists():
            logger.error(f"ROADMAP not found: {self.roadmap_path}")
            return []

        try:
            content = self.roadmap_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read ROADMAP: {e}")
            return []

        priorities = []

        # Regex patterns for priority headers
        patterns = [
            r"^###\s+(PRIORITY\s+[\d.]+):\s+(.+?)(?:\s+\[[^]]+\])?$",  # PRIORITY 1: Title [status]
            r"^###\s+(US-\d+):\s+(.+?)(?:\s+\[[^]]+\])?$",  # US-001: Title [status]
        ]

        for line in content.split("\n"):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    name = match.group(1).strip()
                    title = match.group(2).strip()
                    priorities.append({"name": name, "title": title})
                    break

        return priorities

    def _check_spec_exists(self, priority: Dict) -> bool:
        """Check if technical spec exists for this priority.

        Args:
            priority: Priority dictionary with name and title

        Returns:
            True if spec exists, False otherwise
        """
        priority_name = priority.get("name", "")
        priority_title = priority.get("title", "")

        # Priority: Check if title contains US-XXX (e.g., "US-047 - Description")
        # This handles cases like "PRIORITY 12: US-047 - ..." where spec is SPEC-047
        if "US-" in priority_title:
            # Extract US number from title
            match = re.search(r"US-(\d+)", priority_title)
            if match:
                spec_number = match.group(1)
                spec_prefix = f"SPEC-{spec_number}"
                logger.debug(f"Checking {priority_name}: Found US-{spec_number} in title, checking {spec_prefix}")
                if self._check_spec_prefix_exists(spec_prefix):
                    logger.debug(f"  → Found spec for {priority_name}")
                    return True
                else:
                    logger.debug(f"  → No spec found for {spec_prefix}")

        # Generate expected spec prefix from priority name
        if priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]
            spec_prefix = f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                major, minor = priority_num.split(".")
                spec_prefix = f"SPEC-{major.zfill(3)}-{minor}"
            else:
                spec_prefix = f"SPEC-{priority_num.zfill(3)}"
        else:
            return False

        logger.debug(f"Checking {priority_name}: Fallback check for {spec_prefix}")
        result = self._check_spec_prefix_exists(spec_prefix)
        logger.debug(f"  → Result: {result}")
        return result

    def _check_spec_prefix_exists(self, spec_prefix: str) -> bool:
        """Check if any spec file with the given prefix exists.

        Args:
            spec_prefix: Spec prefix like "SPEC-047" or "SPEC-012"

        Returns:
            True if spec file exists, False otherwise
        """
        # Check if spec file exists
        if not self.spec_dir.exists():
            logger.debug(f"Spec dir does not exist: {self.spec_dir}")
            return False

        pattern = f"{spec_prefix}-*.md"
        logger.debug(f"Looking for pattern: {pattern} in {self.spec_dir}")

        found_files = list(self.spec_dir.glob(pattern))
        logger.debug(f"Found files: {[f.name for f in found_files]}")

        for spec_file in found_files:
            logger.debug(f"Matched spec file: {spec_file.name}")
            return True

        return False

    def _format_report(self, coverage_data: List[Dict], all_priorities: List[Dict]) -> str:
        """Format coverage data as markdown report.

        Args:
            coverage_data: List of coverage items with priority, title, spec_exists
            all_priorities: List of all priorities

        Returns:
            Formatted markdown report
        """
        # Calculate statistics
        total = len(coverage_data)
        with_specs = sum(1 for item in coverage_data if item["spec_exists"])
        without_specs = total - with_specs
        coverage_percent = int(100 * with_specs / total) if total > 0 else 0

        # Build report header
        lines = [
            "# Technical Spec Coverage Report",
            "",
            f"Generated: {Path.cwd().name}",
            "",
            "## Summary",
            "",
            f"- **Total Priorities**: {total}",
            f"- **Specs Exist**: {with_specs} ({coverage_percent}%)",
            f"- **Specs Missing**: {without_specs}",
            "",
        ]

        # If all covered, celebrate!
        if without_specs == 0:
            lines.extend(
                [
                    "### ✅ All priorities have technical specifications!",
                    "",
                    "CFR-008 compliance: EXCELLENT",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    f"### ⚠️  {without_specs} priorities need technical specifications",
                    "",
                ]
            )

        # Coverage table
        lines.extend(
            [
                "## Coverage Details",
                "",
                "| Priority | Title | Spec Status | Action |",
                "|----------|-------|-------------|--------|",
            ]
        )

        for item in coverage_data:
            status = "✅ Exists" if item["spec_exists"] else "❌ Missing"
            action = "N/A" if item["spec_exists"] else "**architect CREATE SPEC**"
            title_short = item["title"][:40] if len(item["title"]) > 40 else item["title"]
            lines.append(f"| {item['priority']} | {title_short} | {status} | {action} |")

        lines.append("")

        # Prioritize missing specs
        missing = [item for item in coverage_data if not item["spec_exists"]]
        if missing:
            lines.extend(
                [
                    "## Priorities Needing Specs",
                    "",
                ]
            )

            for i, item in enumerate(missing, 1):
                spec_prefix = self._get_spec_prefix(item["priority"], item["title"])
                lines.extend(
                    [
                        f"### {i}. {item['priority']}: {item['title']}",
                        "",
                        f"- **Status**: Missing",
                        f"- **Expected Location**: `docs/architecture/specs/{spec_prefix}-<name>.md`",
                        f"- **CFR-008**: code_developer CANNOT create this spec",
                        f"- **Action**: architect must create the specification",
                        "",
                    ]
                )

        # Footer
        lines.extend(
            [
                "---",
                "",
                "**CFR-008 Enforcement**: Only architect creates technical specifications.",
                "",
                "Use this report to identify spec coverage gaps and create missing specs.",
                "",
            ]
        )

        return "\n".join(lines)

    def _get_spec_prefix(self, priority_name: str, priority_title: str = "") -> str:
        """Extract spec prefix from priority name and title.

        Args:
            priority_name: Priority name like "US-047" or "PRIORITY 9"
            priority_title: Priority title, may contain "US-XXX - Description"

        Returns:
            Spec prefix like "SPEC-047" or "SPEC-009"
        """
        # Priority: Check if title contains US-XXX (e.g., "US-047 - Description")
        # This handles cases like "PRIORITY 12: US-047 - ..." where spec is SPEC-047
        if "US-" in priority_title:
            match = re.search(r"US-(\d+)", priority_title)
            if match:
                spec_number = match.group(1)
                return f"SPEC-{spec_number}"

        # Fall back to priority name
        if priority_name.startswith("US-"):
            spec_number = priority_name.split("-")[1]
            return f"SPEC-{spec_number}"
        elif priority_name.startswith("PRIORITY"):
            priority_num = priority_name.replace("PRIORITY", "").strip()
            if "." in priority_num:
                major, minor = priority_num.split(".")
                return f"SPEC-{major.zfill(3)}-{minor}"
            else:
                return f"SPEC-{priority_num.zfill(3)}"
        else:
            return f"SPEC-{priority_name.replace(' ', '-')}"
