"""
PR Monitoring & Analysis Skill

Monitors GitHub pull requests, analyzes status, detects blockers, and generates actionable reports.

Capabilities:
- analyze_prs(): Complete PR health analysis with categorization
- categorize_pr(): Categorize single PR by status
- detect_issues(): Find blockers and issues across all PRs
- calculate_pr_health_score(): Overall PR health (0-100)
- generate_recommendations(): Actionable next steps
- generate_report(): Complete PR analysis report with metrics

Used by: project_manager (daily/hourly PR health checks)
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""

    number: int
    title: str
    author: str
    created_at: datetime
    updated_at: datetime
    is_draft: bool
    labels: List[str] = field(default_factory=list)
    reviews: List[Dict[str, str]] = field(default_factory=list)
    status_checks: List[Dict[str, str]] = field(default_factory=list)
    mergeable: str = "UNKNOWN"  # CONFLICTING, MERGEABLE, UNKNOWN


@dataclass
class PRIssue:
    """Information about a PR issue or blocker."""

    pr_number: int
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    issue_type: str  # "ready_but_not_merged", "failing_checks_too_long", etc.
    description: str
    recommendation: str


@dataclass
class PRHealthMetrics:
    """PR health metrics."""

    health_score: int  # 0-100
    total_prs: int
    ready_to_merge_count: int
    waiting_for_review_count: int
    changes_requested_count: int
    failing_checks_count: int
    merge_conflicts_count: int
    stale_count: int
    draft_count: int


@dataclass
class PRRecommendation:
    """Actionable recommendation for PR management."""

    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    action: str
    details: str
    prs: List[int]
    timeline: str


@dataclass
class PRAnalysisReport:
    """Complete PR analysis report."""

    generated_date: datetime
    repository: str
    health_status: str  # "EXCELLENT", "GOOD", "FAIR", "POOR"
    metrics: PRHealthMetrics
    categorized_prs: Dict[str, List[PullRequest]]
    issues: List[PRIssue]
    recommendations: List[PRRecommendation]
    report_markdown: str
    execution_time_seconds: float = 0.0


class PRMonitoring:
    """
    Monitors GitHub PRs, detects blockers, generates health reports.

    Used by project_manager for daily/hourly PR health checks.
    Generates actionable reports with categorization and recommendations.
    """

    # PR Categories
    CATEGORY_READY_TO_MERGE = "ready_to_merge"
    CATEGORY_WAITING_FOR_REVIEW = "waiting_for_review"
    CATEGORY_CHANGES_REQUESTED = "changes_requested"
    CATEGORY_FAILING_CHECKS = "failing_checks"
    CATEGORY_MERGE_CONFLICTS = "merge_conflicts"
    CATEGORY_STALE = "stale"
    CATEGORY_DRAFT = "draft"

    # Thresholds
    STALE_DAYS_THRESHOLD = 7
    READY_NOT_MERGED_DAYS = 2
    FAILING_CHECKS_HOURS = 24
    MERGE_CONFLICTS_DAYS = 3
    CHANGES_REQUESTED_DAYS = 5
    WAITING_FOR_REVIEW_DAYS = 3
    DRAFT_STALE_DAYS = 14

    def __init__(self, repository: Optional[str] = None, project_root: Optional[Path] = None):
        """
        Initialize PR monitoring.

        Args:
            repository: Repository name (e.g., "user/repo", default: auto-detect from git)
            project_root: Root directory of project (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.repository = repository or self._get_repo_name()

    def _get_repo_name(self) -> str:
        """Get repository name from git config."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )

            if result.returncode == 0:
                # Parse URL: https://github.com/user/repo.git or git@github.com:user/repo.git
                url = result.stdout.strip()
                match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
                if match:
                    return match.group(1)
        except Exception:
            pass

        return "unknown/repo"

    def analyze_prs(self) -> PRAnalysisReport:
        """
        Perform complete PR health analysis.

        Returns:
            PRAnalysisReport with metrics, categorization, issues, and recommendations

        Example:
            >>> monitor = PRMonitoring()
            >>> report = monitor.analyze_prs()
            >>> print(f"Health Score: {report.metrics.health_score}/100")
            >>> print(f"Status: {report.health_status}")
        """
        start_time = datetime.now()

        # Fetch PRs from GitHub
        prs = self._fetch_prs()

        # Categorize PRs
        categorized_prs = self._categorize_prs(prs)

        # Detect issues
        issues = self._detect_issues(categorized_prs)

        # Calculate metrics
        metrics = self._calculate_metrics(categorized_prs, issues)

        # Determine health status
        health_status = self._determine_health_status(metrics.health_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(categorized_prs, issues)

        # Generate report markdown
        report_markdown = self._generate_report_markdown(
            categorized_prs, metrics, issues, recommendations, health_status
        )

        execution_time = (datetime.now() - start_time).total_seconds()

        return PRAnalysisReport(
            generated_date=datetime.now(),
            repository=self.repository,
            health_status=health_status,
            metrics=metrics,
            categorized_prs=categorized_prs,
            issues=issues,
            recommendations=recommendations,
            report_markdown=report_markdown,
            execution_time_seconds=execution_time,
        )

    def _fetch_prs(self) -> List[PullRequest]:
        """Fetch all open PRs using gh CLI."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--state",
                    "open",
                    "--json",
                    "number,title,author,createdAt,updatedAt,isDraft,labels,reviews,statusCheckRollup,mergeable",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30,
            )

            if result.returncode != 0:
                return []

            pr_data = json.loads(result.stdout)
            prs = []

            for pr in pr_data:
                # Parse dates
                created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                updated_at = datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00"))

                # Extract labels
                labels = [label["name"] for label in pr.get("labels", [])]

                # Extract reviews
                reviews = []
                for review in pr.get("reviews", []):
                    reviews.append({"state": review["state"], "author": review["author"]["login"]})

                # Extract status checks
                status_checks = []
                for check in pr.get("statusCheckRollup", []):
                    status_checks.append(
                        {"context": check.get("context", "unknown"), "state": check.get("state", "UNKNOWN")}
                    )

                prs.append(
                    PullRequest(
                        number=pr["number"],
                        title=pr["title"],
                        author=pr["author"]["login"],
                        created_at=created_at,
                        updated_at=updated_at,
                        is_draft=pr["isDraft"],
                        labels=labels,
                        reviews=reviews,
                        status_checks=status_checks,
                        mergeable=pr.get("mergeable", "UNKNOWN"),
                    )
                )

            return prs

        except Exception as e:
            print(f"Error fetching PRs: {e}")
            return []

    def _categorize_prs(self, prs: List[PullRequest]) -> Dict[str, List[PullRequest]]:
        """Categorize all PRs by status."""
        categorized = {
            self.CATEGORY_READY_TO_MERGE: [],
            self.CATEGORY_WAITING_FOR_REVIEW: [],
            self.CATEGORY_CHANGES_REQUESTED: [],
            self.CATEGORY_FAILING_CHECKS: [],
            self.CATEGORY_MERGE_CONFLICTS: [],
            self.CATEGORY_STALE: [],
            self.CATEGORY_DRAFT: [],
        }

        for pr in prs:
            category = self._categorize_single_pr(pr)
            categorized[category].append(pr)

        return categorized

    def _categorize_single_pr(self, pr: PullRequest) -> str:
        """Categorize a single PR by status."""
        now = datetime.now(pr.updated_at.tzinfo)  # Use same timezone

        # Draft
        if pr.is_draft:
            return self.CATEGORY_DRAFT

        # Stale
        days_since_update = (now - pr.updated_at).days
        if days_since_update > self.STALE_DAYS_THRESHOLD:
            return self.CATEGORY_STALE

        # Merge Conflicts
        if pr.mergeable == "CONFLICTING":
            return self.CATEGORY_MERGE_CONFLICTS

        # Failing Checks
        if any(check["state"] == "FAILURE" for check in pr.status_checks):
            return self.CATEGORY_FAILING_CHECKS

        # Changes Requested
        if any(review["state"] == "CHANGES_REQUESTED" for review in pr.reviews):
            return self.CATEGORY_CHANGES_REQUESTED

        # Ready to Merge
        approved = any(review["state"] == "APPROVED" for review in pr.reviews)
        checks_pass = all(check["state"] == "SUCCESS" for check in pr.status_checks) or not pr.status_checks
        no_conflicts = pr.mergeable != "CONFLICTING"

        if approved and checks_pass and no_conflicts:
            return self.CATEGORY_READY_TO_MERGE

        # Waiting for Review
        return self.CATEGORY_WAITING_FOR_REVIEW

    def _detect_issues(self, categorized_prs: Dict[str, List[PullRequest]]) -> List[PRIssue]:
        """Detect blockers and issues across all PRs."""
        issues = []
        now = datetime.now()

        # Ready to merge but not merged for >2 days
        for pr in categorized_prs[self.CATEGORY_READY_TO_MERGE]:
            days_ready = (now - pr.updated_at.replace(tzinfo=None)).days
            if days_ready > self.READY_NOT_MERGED_DAYS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="HIGH",
                        issue_type="ready_but_not_merged",
                        description=f"PR #{pr.number} ready to merge for {days_ready} days",
                        recommendation="Merge immediately or investigate why delayed",
                    )
                )

        # Failing checks for >24 hours
        for pr in categorized_prs[self.CATEGORY_FAILING_CHECKS]:
            hours_failing = (now - pr.updated_at.replace(tzinfo=None)).total_seconds() / 3600
            if hours_failing > self.FAILING_CHECKS_HOURS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="CRITICAL",
                        issue_type="failing_checks_too_long",
                        description=f"PR #{pr.number} has failing checks for {int(hours_failing)} hours",
                        recommendation="Fix failing checks immediately or close PR",
                    )
                )

        # Merge conflicts for >3 days
        for pr in categorized_prs[self.CATEGORY_MERGE_CONFLICTS]:
            days_conflicting = (now - pr.updated_at.replace(tzinfo=None)).days
            if days_conflicting > self.MERGE_CONFLICTS_DAYS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="HIGH",
                        issue_type="merge_conflicts_too_long",
                        description=f"PR #{pr.number} has merge conflicts for {days_conflicting} days",
                        recommendation="Resolve conflicts within 24 hours",
                    )
                )

        # Changes requested for >5 days (no response)
        for pr in categorized_prs[self.CATEGORY_CHANGES_REQUESTED]:
            days_waiting = (now - pr.updated_at.replace(tzinfo=None)).days
            if days_waiting > self.CHANGES_REQUESTED_DAYS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="MEDIUM",
                        issue_type="changes_requested_no_response",
                        description=f"PR #{pr.number} has requested changes for {days_waiting} days (no response)",
                        recommendation="Address reviewer feedback or discuss blockers",
                    )
                )

        # Waiting for review for >3 days
        for pr in categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW]:
            days_waiting = (now - pr.updated_at.replace(tzinfo=None)).days
            if days_waiting > self.WAITING_FOR_REVIEW_DAYS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="MEDIUM",
                        issue_type="waiting_for_review_too_long",
                        description=f"PR #{pr.number} waiting for review for {days_waiting} days",
                        recommendation="Assign reviewer or request review",
                    )
                )

        # Draft for >14 days
        for pr in categorized_prs[self.CATEGORY_DRAFT]:
            days_draft = (now - pr.created_at.replace(tzinfo=None)).days
            if days_draft > self.DRAFT_STALE_DAYS:
                issues.append(
                    PRIssue(
                        pr_number=pr.number,
                        severity="LOW",
                        issue_type="draft_stale",
                        description=f"Draft PR #{pr.number} open for {days_draft} days",
                        recommendation="Close if abandoned or convert to ready for review",
                    )
                )

        return issues

    def _calculate_metrics(
        self, categorized_prs: Dict[str, List[PullRequest]], issues: List[PRIssue]
    ) -> PRHealthMetrics:
        """Calculate PR health metrics."""
        total_prs = sum(len(prs) for prs in categorized_prs.values())

        if total_prs == 0:
            # No PRs = perfect health
            return PRHealthMetrics(
                health_score=100,
                total_prs=0,
                ready_to_merge_count=0,
                waiting_for_review_count=0,
                changes_requested_count=0,
                failing_checks_count=0,
                merge_conflicts_count=0,
                stale_count=0,
                draft_count=0,
            )

        # Calculate health score
        base_score = 100

        # Deductions based on PR status
        ready_ratio = len(categorized_prs[self.CATEGORY_READY_TO_MERGE]) / total_prs
        base_score -= (1 - ready_ratio) * 20  # Penalty if few PRs ready

        failing_ratio = len(categorized_prs[self.CATEGORY_FAILING_CHECKS]) / total_prs
        base_score -= failing_ratio * 30  # Heavy penalty for failing checks

        conflicts_ratio = len(categorized_prs[self.CATEGORY_MERGE_CONFLICTS]) / total_prs
        base_score -= conflicts_ratio * 20  # Penalty for conflicts

        stale_ratio = len(categorized_prs[self.CATEGORY_STALE]) / total_prs
        base_score -= stale_ratio * 15  # Penalty for stale PRs

        # Deductions for issues
        for issue in issues:
            if issue.severity == "CRITICAL":
                base_score -= 15
            elif issue.severity == "HIGH":
                base_score -= 10
            elif issue.severity == "MEDIUM":
                base_score -= 5
            elif issue.severity == "LOW":
                base_score -= 2

        health_score = max(0, min(100, int(base_score)))

        return PRHealthMetrics(
            health_score=health_score,
            total_prs=total_prs,
            ready_to_merge_count=len(categorized_prs[self.CATEGORY_READY_TO_MERGE]),
            waiting_for_review_count=len(categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW]),
            changes_requested_count=len(categorized_prs[self.CATEGORY_CHANGES_REQUESTED]),
            failing_checks_count=len(categorized_prs[self.CATEGORY_FAILING_CHECKS]),
            merge_conflicts_count=len(categorized_prs[self.CATEGORY_MERGE_CONFLICTS]),
            stale_count=len(categorized_prs[self.CATEGORY_STALE]),
            draft_count=len(categorized_prs[self.CATEGORY_DRAFT]),
        )

    def _determine_health_status(self, health_score: int) -> str:
        """Determine health status from score."""
        if health_score >= 90:
            return "EXCELLENT"
        elif health_score >= 70:
            return "GOOD"
        elif health_score >= 50:
            return "FAIR"
        else:
            return "POOR"

    def _generate_recommendations(
        self, categorized_prs: Dict[str, List[PullRequest]], issues: List[PRIssue]
    ) -> List[PRRecommendation]:
        """Generate actionable recommendations."""
        recommendations = []

        # Ready to merge PRs
        if categorized_prs[self.CATEGORY_READY_TO_MERGE]:
            recommendations.append(
                PRRecommendation(
                    priority="HIGH",
                    action="Merge ready PRs",
                    details=f"{len(categorized_prs[self.CATEGORY_READY_TO_MERGE])} PR(s) ready to merge",
                    prs=[pr.number for pr in categorized_prs[self.CATEGORY_READY_TO_MERGE]],
                    timeline="Next 24 hours",
                )
            )

        # Failing checks
        if categorized_prs[self.CATEGORY_FAILING_CHECKS]:
            recommendations.append(
                PRRecommendation(
                    priority="CRITICAL",
                    action="Fix failing CI checks",
                    details=f"{len(categorized_prs[self.CATEGORY_FAILING_CHECKS])} PR(s) with failing checks",
                    prs=[pr.number for pr in categorized_prs[self.CATEGORY_FAILING_CHECKS]],
                    timeline="Immediate",
                )
            )

        # Merge conflicts
        if categorized_prs[self.CATEGORY_MERGE_CONFLICTS]:
            recommendations.append(
                PRRecommendation(
                    priority="HIGH",
                    action="Resolve merge conflicts",
                    details=f"{len(categorized_prs[self.CATEGORY_MERGE_CONFLICTS])} PR(s) with conflicts",
                    prs=[pr.number for pr in categorized_prs[self.CATEGORY_MERGE_CONFLICTS]],
                    timeline="Next 48 hours",
                )
            )

        # Waiting for review
        if len(categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW]) > 3:
            recommendations.append(
                PRRecommendation(
                    priority="MEDIUM",
                    action="Review pending PRs",
                    details=f"{len(categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW])} PR(s) waiting for review",
                    prs=[pr.number for pr in categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW]],
                    timeline="This week",
                )
            )

        # Stale PRs
        if categorized_prs[self.CATEGORY_STALE]:
            recommendations.append(
                PRRecommendation(
                    priority="LOW",
                    action="Close or revive stale PRs",
                    details=f"{len(categorized_prs[self.CATEGORY_STALE])} stale PR(s) (>7 days no update)",
                    prs=[pr.number for pr in categorized_prs[self.CATEGORY_STALE]],
                    timeline="This sprint",
                )
            )

        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(recommendations, key=lambda r: priority_order[r.priority])

    def _generate_report_markdown(
        self,
        categorized_prs: Dict[str, List[PullRequest]],
        metrics: PRHealthMetrics,
        issues: List[PRIssue],
        recommendations: List[PRRecommendation],
        health_status: str,
    ) -> str:
        """Generate markdown PR analysis report."""
        status_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡",
            "FAIR": "🟠",
            "POOR": "🔴",
        }

        report = f"""# Pull Request Monitoring & Analysis Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Repository**: {self.repository}
**Health Score**: {metrics.health_score}/100 {status_emoji.get(health_status, "")}

---

## Executive Summary

- Total Open PRs: {metrics.total_prs}
- Ready to Merge: {metrics.ready_to_merge_count} ✅
- Waiting for Review: {metrics.waiting_for_review_count} ⏳
- Failing Checks: {metrics.failing_checks_count} ❌
- Merge Conflicts: {metrics.merge_conflicts_count} ⚠️
- Stale: {metrics.stale_count} 🕐
- Draft: {metrics.draft_count} 📝

**Overall Health**: {health_status} {status_emoji.get(health_status, "")}

---

## PRs by Category

"""

        # Ready to Merge
        if categorized_prs[self.CATEGORY_READY_TO_MERGE]:
            report += f"### Ready to Merge ✅ ({metrics.ready_to_merge_count} PR{'s' if metrics.ready_to_merge_count != 1 else ''})\n\n"
            report += "**HIGH PRIORITY**: These PRs should be merged ASAP!\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_READY_TO_MERGE], 1):
                days_old = (datetime.now() - pr.created_at.replace(tzinfo=None)).days
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Created: {days_old} day{'s' if days_old != 1 else ''} ago\n"
                report += f"   - **Action**: Merge immediately\n\n"

        # Failing Checks
        if categorized_prs[self.CATEGORY_FAILING_CHECKS]:
            report += f"### Failing Checks ❌ ({metrics.failing_checks_count} PR{'s' if metrics.failing_checks_count != 1 else ''})\n\n"
            report += "**CRITICAL**: These PRs need immediate attention!\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_FAILING_CHECKS], 1):
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Status checks:\n"
                for check in pr.status_checks:
                    emoji = "❌" if check["state"] == "FAILURE" else "✅"
                    report += f"     - {emoji} {check['context']}\n"
                report += f"   - **Action**: Fix failing tests immediately\n\n"

        # Merge Conflicts
        if categorized_prs[self.CATEGORY_MERGE_CONFLICTS]:
            report += f"### Merge Conflicts ⚠️ ({metrics.merge_conflicts_count} PR{'s' if metrics.merge_conflicts_count != 1 else ''})\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_MERGE_CONFLICTS], 1):
                days_old = (datetime.now() - pr.created_at.replace(tzinfo=None)).days
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Created: {days_old} day{'s' if days_old != 1 else ''} ago\n"
                report += f"   - **Action**: Rebase on main and resolve conflicts\n\n"

        # Waiting for Review
        if categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW]:
            report += f"### Waiting for Review ⏳ ({metrics.waiting_for_review_count} PR{'s' if metrics.waiting_for_review_count != 1 else ''})\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_WAITING_FOR_REVIEW], 1):
                days_old = (datetime.now() - pr.created_at.replace(tzinfo=None)).days
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Created: {days_old} day{'s' if days_old != 1 else ''} ago\n"
                report += f"   - Reviews: {len(pr.reviews)} review(s)\n"
                report += f"   - **Action**: Request review from team\n\n"

        # Stale
        if categorized_prs[self.CATEGORY_STALE]:
            report += f"### Stale 🕐 ({metrics.stale_count} PR{'s' if metrics.stale_count != 1 else ''})\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_STALE], 1):
                days_since_update = (datetime.now() - pr.updated_at.replace(tzinfo=None)).days
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Last updated: {days_since_update} day{'s' if days_since_update != 1 else ''} ago\n"
                report += f"   - **Action**: Review and decide: continue, pause, or close\n\n"

        # Draft
        if categorized_prs[self.CATEGORY_DRAFT]:
            report += f"### Draft 📝 ({metrics.draft_count} PR{'s' if metrics.draft_count != 1 else ''})\n\n"
            for i, pr in enumerate(categorized_prs[self.CATEGORY_DRAFT], 1):
                days_old = (datetime.now() - pr.created_at.replace(tzinfo=None)).days
                report += f"{i}. **PR #{pr.number}**: {pr.title}\n"
                report += f"   - Author: {pr.author}\n"
                report += f"   - Created: {days_old} day{'s' if days_old != 1 else ''} ago\n"
                report += f"   - **Action**: Monitor progress\n\n"

        # Issues
        report += f"---\n\n## Issues Found: {len(issues)}\n\n"
        if issues:
            # Group by severity
            critical_issues = [i for i in issues if i.severity == "CRITICAL"]
            high_issues = [i for i in issues if i.severity == "HIGH"]
            medium_issues = [i for i in issues if i.severity == "MEDIUM"]
            low_issues = [i for i in issues if i.severity == "LOW"]

            if critical_issues:
                report += f"### CRITICAL Issues ({len(critical_issues)})\n\n"
                for i, issue in enumerate(critical_issues, 1):
                    report += f"{i}. **PR #{issue.pr_number}: {issue.description}**\n"
                    report += f"   - Recommendation: {issue.recommendation}\n\n"

            if high_issues:
                report += f"### HIGH Issues ({len(high_issues)})\n\n"
                for i, issue in enumerate(high_issues, 1):
                    report += f"{i}. **PR #{issue.pr_number}: {issue.description}**\n"
                    report += f"   - Recommendation: {issue.recommendation}\n\n"

            if medium_issues:
                report += f"### MEDIUM Issues ({len(medium_issues)})\n\n"
                for i, issue in enumerate(medium_issues, 1):
                    report += f"{i}. **PR #{issue.pr_number}: {issue.description}**\n"
                    report += f"   - Recommendation: {issue.recommendation}\n\n"

            if low_issues:
                report += f"### LOW Issues ({len(low_issues)})\n\n"
                for i, issue in enumerate(low_issues, 1):
                    report += f"{i}. **PR #{issue.pr_number}: {issue.description}**\n"
                    report += f"   - Recommendation: {issue.recommendation}\n\n"
        else:
            report += "_No issues identified. All PRs are healthy!_ ✅\n\n"

        # Recommendations
        report += "---\n\n## Recommendations\n\n"
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. **{rec.action}** ({rec.priority})\n"
                report += f"   - {rec.details}\n"
                report += f"   - PRs: {', '.join(f'#{pr}' for pr in rec.prs)}\n"
                report += f"   - Timeline: {rec.timeline}\n\n"
        else:
            report += "1. Continue monitoring - PRs are healthy\n\n"

        report += "---\n\n"
        report += "**Generated by**: project_manager agent (pr-monitoring-analysis skill)\n"

        return report

    def save_report(self, report: PRAnalysisReport, output_path: Optional[Path] = None) -> Path:
        """
        Save PR analysis report to file.

        Args:
            report: PRAnalysisReport to save
            output_path: Where to save (default: evidence/pr-monitoring-{timestamp}.md)

        Returns:
            Path where report was saved
        """
        if output_path is None:
            timestamp = report.generated_date.strftime("%Y%m%d-%H%M%S")
            output_path = self.project_root / "evidence" / f"pr-monitoring-{timestamp}.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.report_markdown, encoding="utf-8")

        return output_path
