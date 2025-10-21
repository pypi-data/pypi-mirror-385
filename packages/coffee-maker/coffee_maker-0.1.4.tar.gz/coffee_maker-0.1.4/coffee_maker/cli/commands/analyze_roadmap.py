"""Analyze roadmap command - Analyze roadmap health and provide insights.

Example:
    >>> from coffee_maker.cli.commands.analyze_roadmap import AnalyzeRoadmapCommand
    >>> command = AnalyzeRoadmapCommand()
    >>> response = command.execute([], editor)
"""

import logging
from typing import List

from coffee_maker.cli.commands import register_command
from coffee_maker.cli.commands.base import BaseCommand
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


@register_command
class AnalyzeRoadmapCommand(BaseCommand):
    """Analyze roadmap health and provide insights.

    Usage: /analyze

    Provides:
    - Overall health score
    - Progress metrics
    - Bottleneck analysis
    - Recommendations

    Example:
        /analyze
    """

    @property
    def name(self) -> str:
        """Command name."""
        return "analyze"

    @property
    def description(self) -> str:
        """Command description."""
        return "Analyze roadmap health and identify issues"

    def get_usage(self) -> str:
        """Get usage string."""
        return "Usage: /analyze"

    def execute(self, args: List[str], editor: RoadmapEditor) -> str:
        """Execute analyze command.

        Args:
            args: No arguments expected
            editor: RoadmapEditor instance

        Returns:
            Analysis report (markdown formatted)
        """
        try:
            summary = editor.get_priority_summary()

            if summary["total"] == 0:
                return "No priorities to analyze."

            # Build analysis report
            report = "## 📊 Roadmap Health Analysis\n\n"

            # Calculate metrics
            total = summary["total"]
            completed = summary["completed"]
            in_progress = summary["in_progress"]
            planned = summary["planned"]

            completion_rate = (completed / total * 100) if total > 0 else 0

            # Overall progress
            report += f"**Overall Progress**: {completion_rate:.0f}% ({completed}/{total} completed)\n\n"

            # Status breakdown
            report += "**Status Breakdown**:\n"
            report += f"- ✅ Completed: {completed}\n"
            report += f"- 🔄 In Progress: {in_progress}\n"
            report += f"- 📝 Planned: {planned}\n\n"

            # Health score
            health_score = self._calculate_health_score(summary)
            report += f"**Health Score**: {health_score}/100\n\n"

            # Key insights
            insights = self._generate_insights(summary)
            if insights:
                report += "**Key Insights**:\n"
                for insight in insights:
                    report += f"{insight}\n"
                report += "\n"

            # Bottleneck analysis
            bottlenecks = self._identify_bottlenecks(summary)
            if bottlenecks:
                report += "**Potential Bottlenecks**:\n"
                for bottleneck in bottlenecks:
                    report += f"{bottleneck}\n"
                report += "\n"

            # Recommendations
            recommendations = self._generate_recommendations(summary)
            if recommendations:
                report += "**Recommendations**:\n"
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"

            return report

        except Exception as e:
            logger.error(f"Failed to analyze roadmap: {e}", exc_info=True)
            return self.format_error(f"Unexpected error: {str(e)}")

    def _calculate_health_score(self, summary: dict) -> int:
        """Calculate health score (0-100).

        Args:
            summary: Roadmap summary

        Returns:
            Health score
        """
        total = summary["total"]
        completed = summary["completed"]
        in_progress = summary["in_progress"]

        if total == 0:
            return 0

        # Score components
        progress_score = (completed / total) * 50  # Up to 50 points
        momentum_score = min((in_progress / total) * 30, 30)  # Up to 30 points
        structure_score = 20  # Assume good structure (20 points)

        # Penalty for too many in-progress
        if in_progress > 3:
            momentum_score -= 10

        return int(progress_score + momentum_score + structure_score)

    def _generate_insights(self, summary: dict) -> List[str]:
        """Generate insights from summary.

        Args:
            summary: Roadmap summary

        Returns:
            List of insight strings
        """
        insights = []

        total = summary["total"]
        completed = summary["completed"]
        in_progress = summary["in_progress"]
        planned = summary["planned"]

        # No work in progress
        if in_progress == 0 and planned > 0:
            insights.append("⚠️  No priorities in progress - consider starting next priority")

        # Too many in progress
        if in_progress > 3:
            insights.append(f"⚠️  {in_progress} priorities in progress - consider focusing on completing existing work")

        # Good progress
        if completed > total / 2:
            insights.append(f"✅ Great progress! Over {(completed/total*100):.0f}% complete")

        # Low progress
        if completed < total / 4 and total > 4:
            insights.append("⚠️  Low completion rate - review priority complexity")

        # All planned
        if in_progress == 0 and completed == 0:
            insights.append("📝 Project is in planning phase - ready to start implementation")

        return insights

    def _identify_bottlenecks(self, summary: dict) -> List[str]:
        """Identify potential bottlenecks.

        Args:
            summary: Roadmap summary

        Returns:
            List of bottleneck descriptions
        """
        bottlenecks = []

        in_progress = summary["in_progress"]
        planned = summary["planned"]

        # Many priorities waiting
        if planned > 5 and in_progress < 2:
            bottlenecks.append(
                f"1. **Execution bottleneck**: {planned} planned priorities waiting, only {in_progress} in progress"
            )

        # Long-running in-progress items
        if in_progress > 0:
            bottlenecks.append(
                f"2. **Check in-progress items**: Verify {in_progress} in-progress priorities are not blocked"
            )

        return bottlenecks

    def _generate_recommendations(self, summary: dict) -> List[str]:
        """Generate recommendations.

        Args:
            summary: Roadmap summary

        Returns:
            List of recommendation strings
        """
        recommendations = []

        total = summary["total"]
        completed = summary["completed"]
        in_progress = summary["in_progress"]
        planned = summary["planned"]

        # Start next priority
        if planned > 0 and in_progress < 2:
            recommendations.append("**Start next planned priority** to maintain momentum")

        # Focus on completion
        if in_progress > 2:
            recommendations.append("**Focus on completing in-progress items** before starting new work")

        # Review complexity
        if completed < total / 4 and in_progress > 0:
            recommendations.append("**Review priority complexity** - consider breaking down large priorities")

        # Celebrate progress
        if completed > total / 2:
            recommendations.append("**Celebrate progress!** - You're over halfway done")

        # Plan ahead
        if planned < 3 and total > 0:
            recommendations.append("**Plan ahead** - Consider adding more priorities to the roadmap")

        return recommendations
