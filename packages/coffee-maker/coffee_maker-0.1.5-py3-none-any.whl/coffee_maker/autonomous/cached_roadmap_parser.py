"""Cached ROADMAP parser for improved performance.

This module provides a caching layer on top of RoadmapParser to avoid
redundant file reads and parsing when the ROADMAP hasn't changed.

US-021 Phase 4: Performance Optimization
- Implements file mtime checking
- Caches parsed priorities in memory
- Invalidates cache only when file changes
- Expected improvement: 50-80% reduction in parse time

Example:
    >>> from coffee_maker.autonomous.cached_roadmap_parser import CachedRoadmapParser
    >>>
    >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
    >>> priorities = parser.get_priorities()  # Parses file
    >>> priorities = parser.get_priorities()  # Returns cached (fast!)
    >>>
    >>> # File changes...
    >>> priorities = parser.get_priorities()  # Detects change, re-parses
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CachedRoadmapParser:
    """Cached ROADMAP parser with file change detection.

    This parser caches the results of parsing ROADMAP.md and only re-parses
    when the file's modification time changes. This dramatically improves
    performance in the daemon loop where the ROADMAP is checked frequently
    but rarely changes.

    Attributes:
        roadmap_path: Path to ROADMAP.md
        _cached_content: Cached file content
        _cached_priorities: Cached parsed priorities
        _last_mtime: Last modification time of file
        _pattern: Pre-compiled regex pattern for priority headers

    Example:
        >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
        >>> priorities = parser.get_priorities()  # First call: parses
        >>> priorities = parser.get_priorities()  # Second call: cached!
    """

    # Pre-compile regex patterns for priority headers (optimization)
    # Support both PRIORITY X and US-XXX formats
    _PRIORITY_PATTERNS = [
        re.compile(r"^###\s+🔴\s+\*\*PRIORITY\s+(\d+(?:\.\d+)?):([^*]+)\*\*"),  # Strict PRIORITY format
        re.compile(r"^###\s+PRIORITY\s+(\d+(?:\.\d+)?):([^#]+?)(?:\s+(?:📝|🔄|✅|⏸️).*)?$"),  # Flexible PRIORITY format
        re.compile(r"^###\s+US-(\d+):([^#]+?)(?:\s+(?:📝|🔄|✅|⏸️).*)?$"),  # User Story format (US-XXX)
    ]

    def __init__(self, roadmap_path: str):
        """Initialize cached parser with roadmap path.

        Args:
            roadmap_path: Path to ROADMAP.md file
        """
        self.roadmap_path = Path(roadmap_path)

        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {roadmap_path}")

        # Cache state
        self._cached_content: Optional[str] = None
        self._cached_priorities: Optional[List[Dict]] = None
        self._cached_lines: Optional[List[str]] = None
        self._last_mtime: Optional[float] = None

        logger.info(f"Initialized cached parser for {roadmap_path}")

    def _should_reload(self) -> bool:
        """Check if file has changed and cache should be invalidated.

        Returns:
            True if file changed, False if cache is valid
        """
        current_mtime = self.roadmap_path.stat().st_mtime

        if self._last_mtime is None:
            # First load
            return True

        if current_mtime != self._last_mtime:
            logger.info("ROADMAP file changed - invalidating cache")
            return True

        return False

    def _load_file(self) -> str:
        """Load file content and update cache.

        Returns:
            File content as string
        """
        self._cached_content = self.roadmap_path.read_text()
        self._cached_lines = self._cached_content.split("\n")
        self._last_mtime = self.roadmap_path.stat().st_mtime
        logger.debug(f"Loaded roadmap: {len(self._cached_lines)} lines")
        return self._cached_content

    def _parse_priorities(self) -> List[Dict]:
        """Parse priorities from cached content.

        Returns:
            List of priority dictionaries
        """
        if self._should_reload():
            self._load_file()

        priorities = []
        lines = self._cached_lines

        # Track code blocks to skip priorities inside them
        in_code_block = False

        for i, line in enumerate(lines):
            # Check for code fence markers
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip lines inside code blocks
            if in_code_block:
                continue

            # Try each pattern until we find a match
            for pattern in self._PRIORITY_PATTERNS:
                match = pattern.search(line)
                if match:
                    priority_num = match.group(1)
                    title = match.group(2).strip()

                    # Clean up title (remove emojis and status if captured)
                    title = re.sub(r"\s*(📝|🔄|✅|⏸️).*$", "", title).strip()

                    # Look for status in next few lines
                    status = self._extract_status(lines, i)

                    # If status not found in **Status**: lines, try to extract from header
                    if status == "Unknown":
                        status = self._extract_status_from_header(line)

                    # Extract full section content (lazy - only when needed)
                    section_content = self._extract_section(lines, i)

                    # Determine priority name based on format (PRIORITY or US-XXX)
                    if "US-" in line:
                        priority_name = f"US-{priority_num}"
                    else:
                        priority_name = f"PRIORITY {priority_num}"

                    priorities.append(
                        {
                            "name": priority_name,
                            "number": priority_num,
                            "title": title,
                            "status": status,
                            "section_start": i,
                            "content": section_content,
                        }
                    )
                    break  # Found match, move to next line

        logger.debug(f"Parsed {len(priorities)} priorities")
        return priorities

    def get_priorities(self) -> List[Dict]:
        """Get all priorities from roadmap (cached).

        Returns:
            List of priority dictionaries with:
                - name: Priority name (e.g., "PRIORITY 1: Analytics")
                - number: Priority number (e.g., 1)
                - title: Full title
                - status: Status emoji/text (e.g., "📝 Planned")
                - section_start: Line number where section starts
                - content: Full section content

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> priorities = parser.get_priorities()
            >>> len(priorities)
            7
        """
        # Check if cache is valid
        if self._cached_priorities is not None and not self._should_reload():
            logger.debug("Returning cached priorities")
            return self._cached_priorities

        # Cache miss or invalidated - re-parse
        logger.info("Cache miss - parsing ROADMAP")
        self._cached_priorities = self._parse_priorities()
        return self._cached_priorities

    def _extract_status(self, lines: List[str], start_line: int) -> str:
        """Extract status from lines near priority header.

        Args:
            lines: All lines from roadmap
            start_line: Line number of priority header

        Returns:
            Status string (e.g., "📝 Planned", "🔄 In Progress")
        """
        # Look in next 10 lines for **Status**: pattern
        for i in range(start_line, min(start_line + 15, len(lines))):
            line = lines[i]
            if "**Status**:" in line:
                # Extract status after the colon
                status_match = re.search(r"\*\*Status\*\*:\s*(.+?)(?:\n|$)", line)
                if status_match:
                    return status_match.group(1).strip()

        return "Unknown"

    def _extract_status_from_header(self, header_line: str) -> str:
        """Extract status emoji and text from priority header line.

        Args:
            header_line: The priority header line

        Returns:
            Status string (e.g., "complete", "planned", "in_progress", "blocked")
        """
        # Look for status emojis and convert to status strings
        if "✅" in header_line or "Complete" in header_line:
            return "complete"
        elif "🔄" in header_line or "In Progress" in header_line:
            return "in_progress"
        elif "📝" in header_line or "Planned" in header_line:
            return "planned"
        elif "⏸️" in header_line or "Blocked" in header_line:
            return "blocked"

        return "Unknown"

    def _extract_section(self, lines: List[str], start_line: int) -> str:
        """Extract full section content until next priority or end.

        Args:
            lines: All lines from roadmap
            start_line: Line number of priority header

        Returns:
            Section content as string
        """
        section_lines = [lines[start_line]]

        # Continue until we hit another ### heading with PRIORITY
        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Stop at next priority section
            if line.startswith("### 🔴 **PRIORITY"):
                break

            # Stop at major section divider
            if line.startswith("## ") and not line.startswith("###"):
                break

            section_lines.append(line)

        return "\n".join(section_lines)

    def get_next_planned_priority(self) -> Optional[Dict]:
        """Get the next priority that is in Planned status.

        Returns:
            Priority dict or None if no planned priorities

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> next_task = parser.get_next_planned_priority()
            >>> if next_task:
            ...     print(f"Implement: {next_task['title']}")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            status = priority["status"].lower()
            if "planned" in status or "📝" in status:
                logger.info(f"Next planned priority: {priority['name']}")
                return priority

        logger.info("No planned priorities found")
        return None

    def get_in_progress_priorities(self) -> List[Dict]:
        """Get all priorities currently in progress.

        Returns:
            List of priority dictionaries

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> in_progress = parser.get_in_progress_priorities()
            >>> for p in in_progress:
            ...     print(f"Working on: {p['title']}")
        """
        priorities = self.get_priorities()

        in_progress = [p for p in priorities if "🔄" in p["status"] or "in progress" in p["status"].lower()]

        logger.info(f"Found {len(in_progress)} in-progress priorities")
        return in_progress

    def extract_deliverables(self, priority_name: str) -> List[str]:
        """Extract deliverables list from a priority section.

        Args:
            priority_name: Priority name (e.g., "PRIORITY 2")

        Returns:
            List of deliverable descriptions

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> deliverables = parser.extract_deliverables("PRIORITY 2")
            >>> for d in deliverables:
            ...     print(f"- {d}")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            if priority["name"] == priority_name:
                content = priority["content"]

                # Look for deliverables section
                deliverables = []
                lines = content.split("\n")

                in_deliverables = False
                for line in lines:
                    if "**Deliverables**" in line or "deliverables:" in line.lower():
                        in_deliverables = True
                        continue

                    if in_deliverables:
                        # Stop at next major heading
                        if line.startswith("**") and ":" in line and not line.startswith("- "):
                            break

                        # Extract list items
                        if line.strip().startswith("- [ ]") or line.strip().startswith("- "):
                            deliverable = line.strip()[2:].strip()  # Remove "- "
                            if deliverable.startswith("[ ] "):
                                deliverable = deliverable[4:]  # Remove "[ ] "
                            deliverables.append(deliverable)

                return deliverables

        return []

    def is_priority_complete(self, priority_name: str) -> bool:
        """Check if a priority is marked as complete.

        Args:
            priority_name: Priority name (e.g., "PRIORITY 1")

        Returns:
            True if complete, False otherwise

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> if parser.is_priority_complete("PRIORITY 1"):
            ...     print("PRIORITY 1 is done!")
        """
        priorities = self.get_priorities()

        for priority in priorities:
            if priority["name"] == priority_name:
                status = priority["status"].lower()
                return "✅" in priority["status"] or "complete" in status

        return False

    def invalidate_cache(self):
        """Manually invalidate the cache to force re-parsing."""
        logger.info("Manually invalidating cache")
        self._cached_priorities = None
        self._cached_content = None
        self._cached_lines = None
        self._last_mtime = None

    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring.

        Returns:
            Dictionary with cache stats:
                - cached: Whether cache is active
                - priorities_count: Number of cached priorities
                - last_mtime: Last modification time
                - file_size: File size in bytes

        Example:
            >>> parser = CachedRoadmapParser("docs/roadmap/ROADMAP.md")
            >>> stats = parser.get_cache_stats()
            >>> print(f"Cache active: {stats['cached']}")
        """
        return {
            "cached": self._cached_priorities is not None,
            "priorities_count": len(self._cached_priorities) if self._cached_priorities else 0,
            "last_mtime": self._last_mtime,
            "file_size": self.roadmap_path.stat().st_size if self.roadmap_path.exists() else 0,
        }
