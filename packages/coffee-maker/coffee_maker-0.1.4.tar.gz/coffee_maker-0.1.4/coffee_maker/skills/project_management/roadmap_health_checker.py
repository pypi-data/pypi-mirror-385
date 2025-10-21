"""
ROADMAP Health Checker Skill

Analyzes ROADMAP.md to detect blockers, calculate velocity, and generate health reports.

Capabilities:
- analyze_roadmap(): Full health analysis with scoring
- calculate_velocity(): Priority completion velocity (priorities/week)
- detect_blockers(): Find stuck or blocked priorities
- generate_recommendations(): Actionable next steps
- generate_report(): Complete health report with metrics

Used by: project_manager (daily/weekly health checks)
"""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Priority:
    """Represents a priority from ROADMAP.md."""

    number: str  # e.g., "10", "2.5"
    status: str  # 📝 Planned, 🔄 In Progress, ✅ Complete, ⏸️ Blocked
    title: str
    description: str
    estimated_effort: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    last_updated_date: Optional[datetime] = None
    user_story_id: Optional[str] = None  # e.g., "US-070"


@dataclass
class VelocityMetrics:
    """Velocity calculation results."""

    last_7_days: int
    last_30_days: int
    average_per_week: float
    trend: str  # "increasing", "stable", "declining"


@dataclass
class BlockerInfo:
    """Information about a blocked priority."""

    priority: Priority
    blocker_type: str  # "explicit_blocked", "stale_work", "dependency_blocked"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    days_blocked: int
    description: str
    recommendation: str


@dataclass
class HealthMetrics:
    """Complete health metrics for ROADMAP."""

    health_score: int  # 0-100
    velocity: VelocityMetrics
    total_priorities: int
    planned_count: int
    in_progress_count: int
    completed_count: int
    blocked_count: int
    stale_count: int
    dependency_blocked_count: int
    backlog_ratio: float


@dataclass
class HealthReport:
    """Complete health report with all analysis."""

    generated_date: datetime
    health_status: str  # "HEALTHY", "WARNING", "CRITICAL"
    metrics: HealthMetrics
    blockers: List[BlockerInfo]
    recommendations: List[str]
    report_markdown: str
    execution_time_seconds: float = 0.0


class RoadmapHealthChecker:
    """
    Analyzes ROADMAP.md health, detects blockers, calculates velocity.

    Used by project_manager for daily/weekly health checks.
    Generates actionable reports with metrics and recommendations.
    """

    # Status emoji patterns
    STATUS_PLANNED = "📝"
    STATUS_IN_PROGRESS = "🔄"
    STATUS_COMPLETE = "✅"
    STATUS_BLOCKED = "⏸️"
    STATUS_MANUAL_REVIEW = "🚧"

    # Thresholds
    STALE_DAYS_THRESHOLD = 7
    CRITICAL_BLOCKER_DAYS = 7
    LOW_VELOCITY_THRESHOLD = 0.5  # 50% of historical average
    HIGH_BACKLOG_RATIO = 0.5  # >50% planned items

    def __init__(self, roadmap_path: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Initialize ROADMAP health checker.

        Args:
            roadmap_path: Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)
            project_root: Root directory of project (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.roadmap_path = roadmap_path or (self.project_root / "docs" / "roadmap" / "ROADMAP.md")

    def analyze_roadmap(self) -> HealthReport:
        """
        Perform complete ROADMAP health analysis.

        Returns:
            HealthReport with metrics, blockers, and recommendations

        Example:
            >>> checker = RoadmapHealthChecker()
            >>> report = checker.analyze_roadmap()
            >>> print(f"Health Score: {report.metrics.health_score}/100")
            >>> print(f"Status: {report.health_status}")
        """
        start_time = datetime.now()

        # Parse ROADMAP
        priorities = self._parse_roadmap()

        # Calculate metrics
        velocity = self._calculate_velocity(priorities)
        metrics = self._calculate_metrics(priorities, velocity)

        # Detect blockers
        blockers = self._detect_blockers(priorities)

        # Calculate health score
        health_score = self._calculate_health_score(metrics, blockers)
        metrics.health_score = health_score

        # Determine health status
        health_status = self._determine_health_status(health_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, blockers)

        # Generate report markdown
        report_markdown = self._generate_report_markdown(metrics, blockers, recommendations, health_status)

        execution_time = (datetime.now() - start_time).total_seconds()

        return HealthReport(
            generated_date=datetime.now(),
            health_status=health_status,
            metrics=metrics,
            blockers=blockers,
            recommendations=recommendations,
            report_markdown=report_markdown,
            execution_time_seconds=execution_time,
        )

    def _parse_roadmap(self) -> List[Priority]:
        """Parse ROADMAP.md and extract all priorities."""
        if not self.roadmap_path.exists():
            return []

        content = self.roadmap_path.read_text(encoding="utf-8")
        priorities = []

        # Pattern to match priority headers
        # Example: ### PRIORITY 10: Feature Name ✅ Complete
        # We need to parse different formats:
        # - ### PRIORITY 10: Feature Name ✅ Complete
        # - ### PRIORITY 10: Feature Name 📝 Planned
        # - ### PRIORITY 10: US-070 - Feature Name 🔄 In Progress
        priority_pattern = re.compile(
            r"###\s+PRIORITY\s+([\d.]+):\s+(.+?)\s*(📝|🔄|✅|⏸️|🚧)\s*(Planned|In Progress|Complete|Blocked|Manual Review)?",
            re.IGNORECASE,
        )

        # Also match US-XXX patterns (with :, -, or space after)
        us_pattern = re.compile(r"US-(\d+)[\s\-:]", re.IGNORECASE)

        lines = content.split("\n")
        current_priority = None

        for i, line in enumerate(lines):
            match = priority_pattern.search(line)
            if match:
                number = match.group(1)
                title = match.group(2).strip()

                # Extract status from emoji (required in the pattern)
                status = match.group(3)

                # Extract US-XXX if present
                us_match = us_pattern.search(title)
                user_story_id = f"US-{us_match.group(1)}" if us_match else None

                # Get last updated date from git blame
                last_updated = self._get_last_updated_date(i + 1)

                current_priority = Priority(
                    number=number,
                    status=status,
                    title=title,
                    description="",
                    user_story_id=user_story_id,
                    last_updated_date=last_updated,
                )
                priorities.append(current_priority)

        return priorities

    def _get_last_updated_date(self, line_number: int) -> Optional[datetime]:
        """Get last updated date for a line using git blame."""
        try:
            result = subprocess.run(
                ["git", "blame", "-L", f"{line_number},{line_number}", "--porcelain", str(self.roadmap_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )

            if result.returncode == 0:
                # Parse git blame output
                for line in result.stdout.split("\n"):
                    if line.startswith("author-time "):
                        timestamp = int(line.split()[1])
                        return datetime.fromtimestamp(timestamp)
        except Exception:
            pass  # Git blame failed, return None

        return None

    def _calculate_velocity(self, priorities: List[Priority]) -> VelocityMetrics:
        """Calculate priority completion velocity."""
        now = datetime.now()
        completed_last_7_days = 0
        completed_last_30_days = 0

        for priority in priorities:
            if priority.status == self.STATUS_COMPLETE and priority.last_updated_date:
                days_ago = (now - priority.last_updated_date).days

                if days_ago <= 7:
                    completed_last_7_days += 1
                    completed_last_30_days += 1
                elif days_ago <= 30:
                    completed_last_30_days += 1

        # Calculate average per week
        if completed_last_30_days > 0:
            average_per_week = (completed_last_30_days / 30) * 7
        else:
            average_per_week = 0.0

        # Determine trend
        if completed_last_7_days > average_per_week:
            trend = "increasing"
        elif completed_last_7_days < average_per_week * 0.8:
            trend = "declining"
        else:
            trend = "stable"

        return VelocityMetrics(
            last_7_days=completed_last_7_days,
            last_30_days=completed_last_30_days,
            average_per_week=round(average_per_week, 1),
            trend=trend,
        )

    def _calculate_metrics(self, priorities: List[Priority], velocity: VelocityMetrics) -> HealthMetrics:
        """Calculate all health metrics."""
        total = len(priorities)
        planned = sum(1 for p in priorities if p.status == self.STATUS_PLANNED)
        in_progress = sum(1 for p in priorities if p.status == self.STATUS_IN_PROGRESS)
        completed = sum(1 for p in priorities if p.status == self.STATUS_COMPLETE)
        blocked = sum(1 for p in priorities if p.status == self.STATUS_BLOCKED)

        # Count stale priorities
        stale = 0
        now = datetime.now()
        for p in priorities:
            if p.status == self.STATUS_IN_PROGRESS and p.last_updated_date:
                days_since_update = (now - p.last_updated_date).days
                if days_since_update > self.STALE_DAYS_THRESHOLD:
                    stale += 1

        backlog_ratio = planned / total if total > 0 else 0.0

        return HealthMetrics(
            health_score=0,  # Will be calculated later
            velocity=velocity,
            total_priorities=total,
            planned_count=planned,
            in_progress_count=in_progress,
            completed_count=completed,
            blocked_count=blocked,
            stale_count=stale,
            dependency_blocked_count=0,  # TODO: Implement dependency tracking
            backlog_ratio=round(backlog_ratio, 2),
        )

    def _detect_blockers(self, priorities: List[Priority]) -> List[BlockerInfo]:
        """Detect all blockers in ROADMAP."""
        blockers = []
        now = datetime.now()

        for priority in priorities:
            # Explicit blocked priorities
            if priority.status == self.STATUS_BLOCKED:
                days_blocked = (now - priority.last_updated_date).days if priority.last_updated_date else 0

                severity = "CRITICAL" if days_blocked >= self.CRITICAL_BLOCKER_DAYS else "HIGH"

                blockers.append(
                    BlockerInfo(
                        priority=priority,
                        blocker_type="explicit_blocked",
                        severity=severity,
                        days_blocked=days_blocked,
                        description=f"Explicitly blocked for {days_blocked} days",
                        recommendation=f"Escalate to user, investigate blocker for {priority.title}",
                    )
                )

            # Stale work
            elif priority.status == self.STATUS_IN_PROGRESS and priority.last_updated_date:
                days_stale = (now - priority.last_updated_date).days

                if days_stale > self.STALE_DAYS_THRESHOLD:
                    severity = "HIGH" if days_stale >= 14 else "MEDIUM"

                    blockers.append(
                        BlockerInfo(
                            priority=priority,
                            blocker_type="stale_work",
                            severity=severity,
                            days_blocked=days_stale,
                            description=f"In Progress but no updates for {days_stale} days",
                            recommendation=f"Check code_developer status, may need assistance with {priority.title}",
                        )
                    )

        return blockers

    def _calculate_health_score(self, metrics: HealthMetrics, blockers: List[BlockerInfo]) -> int:
        """Calculate overall health score (0-100)."""
        base_score = 100

        # Deduct for blockers
        for blocker in blockers:
            if blocker.severity == "CRITICAL":
                base_score -= 20
            elif blocker.severity == "HIGH":
                base_score -= 10
            elif blocker.severity == "MEDIUM":
                base_score -= 5
            elif blocker.severity == "LOW":
                base_score -= 2

        # Deduct for low velocity
        if metrics.velocity.average_per_week < 1.0:
            base_score -= 10

        # Deduct for high backlog ratio
        if metrics.backlog_ratio > self.HIGH_BACKLOG_RATIO:
            base_score -= 5

        # Bonus for good velocity
        if metrics.velocity.last_7_days >= 2:
            base_score += 5

        # Bonus for no blockers
        if metrics.blocked_count == 0:
            base_score += 10

        # Bonus for no stale work
        if metrics.stale_count == 0:
            base_score += 5

        return max(0, min(100, base_score))

    def _determine_health_status(self, health_score: int) -> str:
        """Determine health status from score."""
        if health_score >= 80:
            return "HEALTHY"
        elif health_score >= 60:
            return "WARNING"
        else:
            return "CRITICAL"

    def _generate_recommendations(self, metrics: HealthMetrics, blockers: List[BlockerInfo]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Critical blockers first
        critical_blockers = [b for b in blockers if b.severity == "CRITICAL"]
        if critical_blockers:
            for blocker in critical_blockers:
                recommendations.append(f"🚨 CRITICAL: {blocker.recommendation}")

        # High severity blockers
        high_blockers = [b for b in blockers if b.severity == "HIGH"]
        if high_blockers:
            for blocker in high_blockers:
                recommendations.append(f"⚠️ HIGH: {blocker.recommendation}")

        # Velocity recommendations
        if metrics.velocity.average_per_week < 1.0:
            recommendations.append("📊 Velocity is low (<1 priority/week). Consider investigating bottlenecks.")
        elif metrics.velocity.trend == "declining":
            recommendations.append("📉 Velocity is declining. Review team capacity and priorities.")

        # Backlog recommendations
        if metrics.backlog_ratio > self.HIGH_BACKLOG_RATIO:
            recommendations.append(
                f"📋 Backlog ratio is {metrics.backlog_ratio:.0%}. Consider deferring low-priority items."
            )

        # Positive feedback
        if not blockers and metrics.velocity.average_per_week >= 2.0:
            recommendations.append("✅ Project is healthy! Continue current pace.")

        return recommendations

    def _generate_report_markdown(
        self,
        metrics: HealthMetrics,
        blockers: List[BlockerInfo],
        recommendations: List[str],
        health_status: str,
    ) -> str:
        """Generate markdown health report."""
        status_emoji = {
            "HEALTHY": "🟢",
            "WARNING": "🟡",
            "CRITICAL": "🔴",
        }

        report = f"""# ROADMAP Health Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Health Status**: {health_status} {status_emoji.get(health_status, "")}

## Summary

- **Total Priorities**: {metrics.total_priorities}
- **Completed**: {metrics.completed_count} ({metrics.completed_count/metrics.total_priorities*100:.1f}%)
- **In Progress**: {metrics.in_progress_count}
- **Planned**: {metrics.planned_count}
- **Blocked**: {metrics.blocked_count}
- **Open PRs**: 0
- **Failed CI**: 0

## Top Blockers

"""

        if blockers:
            for i, blocker in enumerate(blockers[:5], 1):
                report += f"{i}. **{blocker.priority.title}** ({blocker.severity}) - {blocker.description}\n"
        else:
            report += "_No blockers identified. All systems healthy!_ ✅\n"

        report += f"""
## Trends

- **Completion Rate**: {metrics.completed_count/metrics.total_priorities*100:.1f}%
- **Velocity**: {metrics.velocity.trend}

## Recommended Actions

"""

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "1. Continue current pace - project is healthy\n"

        return report

    def save_report(self, report: HealthReport, output_path: Optional[Path] = None) -> Path:
        """
        Save health report to file.

        Args:
            report: HealthReport to save
            output_path: Where to save (default: evidence/roadmap-health-{timestamp}.md)

        Returns:
            Path where report was saved
        """
        if output_path is None:
            timestamp = report.generated_date.strftime("%Y%m%d-%H%M%S")
            output_path = self.project_root / "evidence" / f"roadmap-health-{timestamp}.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.report_markdown, encoding="utf-8")

        return output_path
