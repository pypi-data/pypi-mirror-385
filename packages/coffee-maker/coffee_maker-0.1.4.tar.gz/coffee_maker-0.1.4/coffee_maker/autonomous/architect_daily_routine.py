"""Architect daily routine for integrating code-searcher findings.

This module implements CFR-011 enforcement: architect MUST read code-searcher
analysis reports daily AND analyze the codebase weekly before creating specs.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from coffee_maker.utils.file_io import read_json_file, write_json_file

logger = logging.getLogger(__name__)


class CFR011ViolationError(Exception):
    """Raised when architect violates CFR-011.

    CFR-011 requires architect to:
    1. Read ALL code-searcher reports before creating specs
    2. Analyze codebase weekly (max 7 days between analyses)
    """


class ArchitectDailyRoutine:
    """Manages architect's daily integration of code-searcher findings.

    This class enforces CFR-011 by:
    - Tracking which code-searcher reports have been read
    - Tracking when codebase was last analyzed
    - Blocking spec creation if violations detected

    Usage:
        >>> routine = ArchitectDailyRoutine()
        >>>
        >>> # Check compliance before creating spec
        >>> routine.enforce_cfr_011()  # Raises CFR011ViolationError if violations
        >>>
        >>> # Daily integration workflow
        >>> unread = routine.get_unread_reports()
        >>> routine.mark_reports_read(unread)
        >>>
        >>> # Weekly codebase analysis
        >>> if routine.is_codebase_analysis_due():
        >>>     # Perform analysis...
        >>>     routine.mark_codebase_analyzed()
    """

    TRACKING_FILE = Path("data/architect_integration_status.json")
    REPORTS_DIR = Path("docs/code-searcher")
    MAX_DAYS_BETWEEN_ANALYSIS = 7

    def __init__(self):
        """Initialize with tracking data from JSON file."""
        self.status = self._load_status()

    def _load_status(self) -> Dict:
        """Load tracking data from JSON file.

        Returns:
            Dict with tracking data (creates default if file doesn't exist)
        """
        default_status = {
            "last_code_searcher_read": None,
            "last_codebase_analysis": None,
            "reports_read": [],
            "refactoring_specs_created": 0,
            "specs_updated": 0,
            "next_analysis_due": None,
        }

        # Ensure data directory exists
        self.TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)

        return read_json_file(self.TRACKING_FILE, default=default_status)

    def _save_status(self):
        """Save tracking data to JSON file (atomic write)."""
        write_json_file(self.TRACKING_FILE, self.status)

    def get_unread_reports(self) -> List[Path]:
        """Find all code-searcher reports not yet read.

        Returns:
            List of unread report file paths, sorted by modification time
        """
        if not self.REPORTS_DIR.exists():
            return []

        all_reports = list(self.REPORTS_DIR.glob("*.md"))
        read_reports = set(self.status["reports_read"])

        unread = [report for report in all_reports if report.name not in read_reports]

        return sorted(unread, key=lambda p: p.stat().st_mtime)

    def mark_reports_read(self, reports: List[Path]):
        """Mark reports as read and update tracking.

        Args:
            reports: List of report file paths that were read
        """
        for report in reports:
            if report.name not in self.status["reports_read"]:
                self.status["reports_read"].append(report.name)

        self.status["last_code_searcher_read"] = datetime.now().strftime("%Y-%m-%d")
        self._save_status()

        logger.info(f"Marked {len(reports)} report(s) as read")

    def is_codebase_analysis_due(self) -> bool:
        """Check if weekly codebase analysis is due.

        Returns:
            True if analysis is due (never analyzed or >7 days since last)
        """
        if not self.status["last_codebase_analysis"]:
            return True  # Never analyzed, due now

        last_analysis = datetime.strptime(self.status["last_codebase_analysis"], "%Y-%m-%d")
        days_since = (datetime.now() - last_analysis).days

        return days_since >= self.MAX_DAYS_BETWEEN_ANALYSIS

    def mark_codebase_analyzed(self):
        """Mark codebase as analyzed and update tracking."""
        today = datetime.now()
        self.status["last_codebase_analysis"] = today.strftime("%Y-%m-%d")
        self.status["next_analysis_due"] = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        self._save_status()

        logger.info(f"Marked codebase as analyzed, next due: {self.status['next_analysis_due']}")

    def enforce_cfr_011(self):
        """Enforce CFR-011 before spec creation.

        Raises:
            CFR011ViolationError: If violations detected (unread reports or overdue analysis)
        """
        violations = []

        # Check for unread reports
        unread = self.get_unread_reports()
        if unread:
            violations.append(f"Unread code-searcher reports: {', '.join(r.name for r in unread)}")

        # Check if weekly analysis due
        if self.is_codebase_analysis_due():
            last = self.status["last_codebase_analysis"] or "NEVER"
            violations.append(f"Weekly codebase analysis overdue (last: {last})")

        if violations:
            error_msg = (
                "CFR-011 violation detected! Cannot create spec until resolved:\n"
                + "\n".join(f"  - {v}" for v in violations)
                + "\n\nActions required:"
                + "\n  1. Run: architect daily-integration"
                + "\n  2. Run: architect analyze-codebase"
            )
            logger.error(f"CFR-011 violation: {violations}")
            raise CFR011ViolationError(error_msg)

    def get_compliance_status(self) -> Dict:
        """Get current CFR-011 compliance status.

        Returns:
            Dict with compliance status and metrics
        """
        unread = self.get_unread_reports()
        analysis_due = self.is_codebase_analysis_due()

        return {
            "compliant": len(unread) == 0 and not analysis_due,
            "last_code_searcher_read": self.status["last_code_searcher_read"],
            "last_codebase_analysis": self.status["last_codebase_analysis"],
            "unread_reports": [r.name for r in unread],
            "analysis_due": analysis_due,
            "next_analysis_due": self.status["next_analysis_due"],
            "reports_read": len(self.status["reports_read"]),
            "refactoring_specs_created": self.status["refactoring_specs_created"],
            "specs_updated": self.status["specs_updated"],
        }

    def increment_refactoring_specs(self, count: int = 1):
        """Increment count of refactoring specs created.

        Args:
            count: Number of specs created (default: 1)
        """
        self.status["refactoring_specs_created"] += count
        self._save_status()

    def increment_specs_updated(self, count: int = 1):
        """Increment count of specs updated.

        Args:
            count: Number of specs updated (default: 1)
        """
        self.status["specs_updated"] += count
        self._save_status()
