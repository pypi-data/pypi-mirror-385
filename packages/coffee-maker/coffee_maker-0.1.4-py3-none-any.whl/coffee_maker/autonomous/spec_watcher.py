"""ROADMAP Spec Monitoring for Architect - US-047 Phase 3.

This module provides automated monitoring of ROADMAP.md to detect new priorities
that need technical specifications, proactively notifying architect.

The SpecWatcher class:
1. Monitors ROADMAP.md for changes
2. Detects new priorities added
3. Checks if technical specs exist for them
4. Notifies architect when specs are missing

This enables proactive spec creation, enforcing CFR-008.

Usage:
    >>> from coffee_maker.autonomous.spec_watcher import SpecWatcher
    >>> watcher = SpecWatcher()
    >>> new_priorities = watcher.check_for_new_priorities()
    >>> if new_priorities:
    ...     print(f"Found {len(new_priorities)} priorities needing specs")

Integration:
    The daemon calls watcher.check_for_new_priorities() periodically (every 5 minutes)
    to detect new priorities and notify architect.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Set

from coffee_maker.config import ROADMAP_PATH

logger = logging.getLogger(__name__)


class SpecWatcher:
    """Monitor ROADMAP.md for new priorities needing specs.

    This class implements CFR-008 enforcement by proactively detecting when
    new priorities are added to ROADMAP without corresponding technical specs.

    Attributes:
        roadmap_path: Path to ROADMAP.md file
        spec_dir: Path to architecture specs directory
        known_priorities: Set of priority names already seen
        last_check: Timestamp of last check (for logging)
    """

    def __init__(self, roadmap_path: Path = None, spec_dir: Path = None):
        """Initialize spec watcher.

        Args:
            roadmap_path: Path to ROADMAP.md (defaults to project ROADMAP)
            spec_dir: Path to specs directory (defaults to docs/architecture/specs)
        """
        self.roadmap_path = roadmap_path or ROADMAP_PATH
        self.spec_dir = spec_dir or (self.roadmap_path.parent.parent / "architecture" / "specs")
        self.known_priorities: Set[str] = set()
        self.last_check = None

    def check_for_new_priorities(self) -> List[Dict]:
        """Check if new priorities added to ROADMAP that need specs.

        This method:
        1. Parses current ROADMAP priorities
        2. Compares with known priorities
        3. For new priorities, checks if spec exists
        4. Returns list of new priorities needing specs

        Returns:
            List of priority dictionaries needing specs, with fields:
            - name: Priority name (e.g., "US-047", "PRIORITY 12")
            - title: Priority title
            - spec_prefix: Expected spec filename prefix
        """
        current_priorities = self._parse_roadmap()

        if not current_priorities:
            logger.debug("No priorities found in ROADMAP")
            return []

        new_priorities_needing_specs = []

        for priority in current_priorities:
            priority_name = priority["name"]

            # Check if this is a new priority (not seen before)
            if priority_name not in self.known_priorities:
                logger.info(f"Detected new priority: {priority_name}")

                # Check if spec exists
                if not self._spec_exists(priority):
                    spec_prefix = self._get_spec_prefix(priority_name)
                    logger.warning(
                        f"⚠️  New priority {priority_name} missing spec: " f"docs/architecture/specs/{spec_prefix}-*.md"
                    )

                    new_priorities_needing_specs.append(
                        {
                            "name": priority_name,
                            "title": priority.get("title", ""),
                            "spec_prefix": spec_prefix,
                        }
                    )
                else:
                    logger.info(f"✅ New priority {priority_name} has spec")

                # Mark as known (even if missing spec - we've detected it once)
                self.known_priorities.add(priority_name)

        return new_priorities_needing_specs

    def _parse_roadmap(self) -> List[Dict]:
        """Parse ROADMAP.md to extract all priorities.

        Looks for markdown headers like:
        - ### PRIORITY 1: Title
        - ### US-001: Title
        - ### PRIORITY 1.5: Title (decimal notation)

        Returns:
            List of priority dictionaries with name and title
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
            r"^###\s+(PRIORITY\s+[\d.]+):\s+(.+?)(?:\s+[📝✅🔄⏸️🚧].*)?$",  # PRIORITY 1: Title [emoji status]
            r"^###\s+(US-\d+):\s+(.+?)(?:\s+[📝✅🔄⏸️🚧].*)?$",  # US-001: Title [emoji status]
        ]

        for line in content.split("\n"):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    name = match.group(1).strip()
                    title = match.group(2).strip()
                    priorities.append({"name": name, "title": title})
                    break

        logger.debug(f"Parsed {len(priorities)} priorities from ROADMAP")
        return priorities

    def _spec_exists(self, priority: Dict) -> bool:
        """Check if technical spec exists for this priority.

        Args:
            priority: Priority dictionary with name and title

        Returns:
            True if spec exists, False otherwise
        """
        priority_name = priority.get("name", "")
        spec_prefix = self._get_spec_prefix(priority_name)

        # Check if spec file exists
        if not self.spec_dir.exists():
            logger.warning(f"Spec directory does not exist: {self.spec_dir}")
            return False

        # Look for any spec file matching the prefix
        for spec_file in self.spec_dir.glob(f"{spec_prefix}-*.md"):
            logger.debug(f"Found spec for {priority_name}: {spec_file.name}")
            return True

        return False

    def _get_spec_prefix(self, priority_name: str) -> str:
        """Generate expected spec prefix from priority name.

        Args:
            priority_name: Priority name like "US-047" or "PRIORITY 9"

        Returns:
            Spec prefix like "SPEC-047" or "SPEC-009"
        """
        # Extract number from priority name for spec prefix
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

    def reset_known_priorities(self) -> None:
        """Reset known priorities set (for testing).

        This allows re-detection of all priorities.
        Useful for testing or when starting fresh monitoring.
        """
        logger.info("Resetting known priorities set")
        self.known_priorities.clear()

    def get_known_priorities_count(self) -> int:
        """Get count of known priorities.

        Returns:
            Number of priorities currently tracked
        """
        return len(self.known_priorities)
