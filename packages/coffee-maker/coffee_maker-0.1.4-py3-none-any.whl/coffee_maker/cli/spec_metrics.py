"""Spec Metrics Tracker for CFR-010: Continuous Spec Improvement.

Tracks architect's spec improvement activities and generates weekly reports.

This module provides:
- Spec creation and update tracking
- Complexity reduction metrics
- Reuse opportunity identification
- Weekly improvement reports

Data is stored in data/spec_metrics.json for persistence.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.utils.file_io import read_json_file, write_json_file


class SpecMetricsTracker:
    """Track spec improvement metrics for CFR-010."""

    def __init__(self):
        """Initialize the metrics tracker.

        Loads existing metrics from data/spec_metrics.json if available.
        """
        self.metrics_file = Path("/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent/data/spec_metrics.json")
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file or create empty structure.

        Returns:
            Metrics dictionary with 'specs' and 'weekly_summaries' keys
        """
        if self.metrics_file.exists():
            try:
                return read_json_file(self.metrics_file)
            except Exception:
                # If file is corrupted, start fresh
                return self._create_empty_metrics()
        else:
            return self._create_empty_metrics()

    @staticmethod
    def _create_empty_metrics() -> Dict[str, Any]:
        """Create empty metrics structure.

        Returns:
            Empty metrics dictionary
        """
        return {"specs": {}, "weekly_summaries": []}

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        write_json_file(self.metrics_file, self.metrics)

    def record_spec_created(
        self,
        spec_name: str,
        complexity_score: int,
        estimated_days: float,
    ) -> None:
        """Record new spec creation.

        Args:
            spec_name: Spec identifier (e.g., "SPEC-049")
            complexity_score: Estimated lines of documentation
            estimated_days: Implementation timeline in days
        """
        if spec_name not in self.metrics["specs"]:
            self.metrics["specs"][spec_name] = {
                "created": datetime.now().isoformat(),
                "complexity_score": complexity_score,
                "estimated_days": estimated_days,
                "actual_days": None,
                "updates": [],
            }
            self._save_metrics()

    def record_spec_updated(
        self,
        spec_name: str,
        changes: str,
        complexity_reduction: int = 0,
    ) -> None:
        """Record spec improvement.

        Args:
            spec_name: Spec identifier
            changes: Description of what was changed
            complexity_reduction: Lines of documentation reduced (default: 0)
        """
        if spec_name not in self.metrics["specs"]:
            # Initialize if not yet tracked
            self.record_spec_created(spec_name, 0, 0)

        update = {
            "date": datetime.now().isoformat(),
            "changes": changes,
            "complexity_reduction": complexity_reduction,
        }

        self.metrics["specs"][spec_name]["updates"].append(update)
        self._save_metrics()

    def record_spec_completed(
        self,
        spec_name: str,
        actual_days: float,
    ) -> None:
        """Record spec completion (after code_developer finishes implementation).

        Args:
            spec_name: Spec identifier
            actual_days: Actual implementation time in days
        """
        if spec_name in self.metrics["specs"]:
            self.metrics["specs"][spec_name]["actual_days"] = actual_days
            self._save_metrics()

    def get_spec_accuracy(self, spec_name: str) -> Optional[float]:
        """Get estimation accuracy for a spec.

        Accuracy = (actual / estimated) * 100
        100% = perfect estimate
        > 100% = overestimated (built faster than expected)
        < 100% = underestimated (took longer than expected)

        Args:
            spec_name: Spec identifier

        Returns:
            Accuracy percentage (0-200+) or None if no actual_days recorded
        """
        if spec_name not in self.metrics["specs"]:
            return None

        spec = self.metrics["specs"][spec_name]
        if spec["actual_days"] is None or spec["estimated_days"] == 0:
            return None

        accuracy = (spec["actual_days"] / spec["estimated_days"]) * 100
        return accuracy

    def get_weekly_complexity_reduction(self, weeks_back: int = 1) -> int:
        """Get total complexity reduction for a week.

        Args:
            weeks_back: How many weeks back (0=this week, 1=last week, etc.)

        Returns:
            Total lines reduced
        """
        now = datetime.now()
        week_start = now - timedelta(weeks=weeks_back + 1)
        week_end = now - timedelta(weeks=weeks_back)

        total = 0
        for spec_info in self.metrics["specs"].values():
            for update in spec_info.get("updates", []):
                update_date = datetime.fromisoformat(update["date"])
                if week_start <= update_date < week_end:
                    total += update.get("complexity_reduction", 0)

        return total

    def get_specs_created_this_week(self) -> List[Dict[str, Any]]:
        """Get specs created in the current week.

        Returns:
            List of specs created this week with details
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())  # Monday

        created = []
        for spec_name, spec_info in self.metrics["specs"].items():
            created_date = datetime.fromisoformat(spec_info["created"])
            if created_date >= week_start:
                created.append(
                    {
                        "name": spec_name,
                        "created": spec_info["created"],
                        "complexity": spec_info["complexity_score"],
                        "estimated_days": spec_info["estimated_days"],
                    }
                )

        return sorted(created, key=lambda x: x["created"])

    def get_specs_updated_this_week(self) -> List[Dict[str, Any]]:
        """Get specs updated in the current week.

        Returns:
            List of specs with updates this week
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())  # Monday

        updated = []
        for spec_name, spec_info in self.metrics["specs"].items():
            week_updates = [u for u in spec_info.get("updates", []) if datetime.fromisoformat(u["date"]) >= week_start]

            if week_updates:
                total_reduction = sum(u.get("complexity_reduction", 0) for u in week_updates)
                updated.append(
                    {
                        "name": spec_name,
                        "updates": week_updates,
                        "total_reduction": total_reduction,
                    }
                )

        return updated

    def get_reuse_opportunities_identified(self) -> List[str]:
        """Get list of reuse opportunities identified in specs.

        (Placeholder for future enhancement with pattern detection)

        Returns:
            List of identified patterns/opportunities
        """
        return []

    def generate_weekly_report(self) -> str:
        """Generate weekly improvement report.

        Returns:
            Markdown report showing:
            - Specs created this week
            - Specs updated this week
            - Total complexity reduction
            - Reuse opportunities identified
            - Trends (vs previous weeks)
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())  # Monday
        week_end = week_start + timedelta(days=7)

        report = "# Weekly Spec Improvement Report\n\n"
        report += f"Week of: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}\n\n"

        # Summary
        created = self.get_specs_created_this_week()
        updated = self.get_specs_updated_this_week()
        complexity_reduction = self.get_weekly_complexity_reduction(weeks_back=0)

        report += "## Summary\n"
        report += f"- Specs Created: {len(created)}\n"
        report += f"- Specs Updated: {len(updated)}\n"
        report += f"- Complexity Reduced: {complexity_reduction} lines\n"
        report += "\n"

        # Specs created this week
        if created:
            report += "## Specs Created This Week\n"
            for i, spec in enumerate(created, 1):
                report += f"{i}. {spec['name']}: {spec['complexity']} lines, {spec['estimated_days']} days\n"
            report += "\n"

        # Specs improved this week
        if updated:
            report += "## Specs Improved This Week\n"
            for spec in updated:
                report += f"- {spec['name']}\n"
                report += f"  - Total reduction: {spec['total_reduction']} lines\n"
                for update in spec["updates"]:
                    report += f"  - {update['changes']} ({update.get('complexity_reduction', 0)} lines)\n"
            report += "\n"

        # Complexity trends
        report += "## Complexity Reduction Trends\n"
        this_week = self.get_weekly_complexity_reduction(weeks_back=0)
        last_week = self.get_weekly_complexity_reduction(weeks_back=1)

        report += f"- This week: {this_week} lines\n"
        report += f"- Last week: {last_week} lines\n"

        if last_week > 0 and this_week > last_week:
            improvement = ((this_week - last_week) / last_week) * 100
            report += f"- Trend: ✅ Up {improvement:.0f}% (improving)\n"
        elif last_week > 0 and this_week < last_week:
            decline = ((last_week - this_week) / last_week) * 100
            report += f"- Trend: ⚠️  Down {decline:.0f}% (declining)\n"
        else:
            report += "- Trend: ➡️  Stable\n"
        report += "\n"

        # Estimation accuracy
        report += "## Estimation Accuracy\n"
        completed_specs = [
            (name, spec) for name, spec in self.metrics["specs"].items() if spec.get("actual_days") is not None
        ]

        if completed_specs:
            accuracies = []
            for name, spec in completed_specs:
                accuracy = self.get_spec_accuracy(name)
                if accuracy is not None:
                    accuracies.append(accuracy)

            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                report += f"- Average accuracy: {avg_accuracy:.0f}%\n"
                report += f"- Specs with actuals: {len(completed_specs)}\n"
                if avg_accuracy > 100:
                    report += "- Status: ✅ Consistently estimating shorter than actual (conservative)\n"
                elif avg_accuracy < 100:
                    report += "- Status: ⚠️  Consistently overestimating (can improve)\n"
                else:
                    report += "- Status: ✅ Excellent estimation accuracy\n"
            else:
                report += "- No completed specs yet\n"
        else:
            report += "- No completed specs yet\n"

        report += "\n"

        # Tips
        report += "## Tips for Next Week\n"
        if len(created) == 0:
            report += "- Create specs proactively (try 2-3 this week)\n"
        if complexity_reduction == 0:
            report += "- Review existing specs for simplification opportunities\n"
        if len(updated) == 0:
            report += "- Update specs based on recent implementations\n"

        report += "\n"
        report += f"Report generated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"

        return report

    def show_spec_status(self) -> str:
        """Generate spec status report.

        Returns:
            Markdown report showing all specs and their status
        """
        report = "# Spec Status Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if not self.metrics["specs"]:
            report += "No specs tracked yet.\n"
            return report

        report += "| Spec | Created | Status | Complexity | Est. Days | Actual Days | Accuracy |\n"
        report += "|------|---------|--------|------------|-----------|-------------|----------|\n"

        for spec_name in sorted(self.metrics["specs"].keys()):
            spec = self.metrics["specs"][spec_name]

            # Status
            if spec.get("actual_days") is not None:
                status = "✅ Complete"
            elif spec.get("updates"):
                status = "🔄 Active"
            else:
                status = "📋 New"

            # Accuracy
            accuracy = self.get_spec_accuracy(spec_name)
            accuracy_str = f"{accuracy:.0f}%" if accuracy is not None else "N/A"

            # Actual days
            actual_str = f"{spec.get('actual_days', 'N/A')}"

            report += f"| {spec_name} | {spec['created'][:10]} | {status} | {spec['complexity_score']} | {spec['estimated_days']} | {actual_str} | {accuracy_str} |\n"

        report += "\n"

        # Summary statistics
        report += "## Summary Statistics\n"
        total_specs = len(self.metrics["specs"])
        complete_specs = sum(1 for s in self.metrics["specs"].values() if s.get("actual_days") is not None)
        total_complexity = sum(s["complexity_score"] for s in self.metrics["specs"].values())
        total_updates = sum(len(s.get("updates", [])) for s in self.metrics["specs"].values())
        total_reduction = sum(
            sum(u.get("complexity_reduction", 0) for u in s.get("updates", [])) for s in self.metrics["specs"].values()
        )

        report += f"- Total specs: {total_specs}\n"
        report += f"- Complete specs: {complete_specs}\n"
        report += f"- Total complexity tracked: {total_complexity} lines\n"
        report += f"- Total improvements: {total_updates} updates\n"
        report += f"- Total reduction: {total_reduction} lines\n"

        return report
