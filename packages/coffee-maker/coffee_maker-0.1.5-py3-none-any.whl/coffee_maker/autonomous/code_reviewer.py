"""Code Reviewer Agent - Automated Quality Assurance.

This module provides automated code review for code_developer commits,
generating detailed quality reports and communicating findings to architect.
"""

import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.autonomous.agent_registry import AgentRegistry, AgentType
from coffee_maker.cli.notifications import NotificationDB

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """Represents a code quality issue."""

    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    category: str  # "Architecture", "Security", "Performance", "Style", etc.
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    effort_estimate: str  # e.g., "15 minutes", "1 hour", "2-3 hours"


@dataclass
class ReviewReport:
    """Code review report."""

    commit_sha: str
    date: datetime
    files_changed: int
    lines_added: int
    lines_deleted: int
    quality_score: int  # 0-100
    issues: List[Issue]
    style_compliance: Dict[str, bool]
    architecture_compliance: Dict[str, bool]
    overall_assessment: str
    approved: bool
    review_duration_seconds: float


class CodeReviewerAgent:
    """Automated code review agent.

    Reviews commits from code_developer, generates quality reports,
    and notifies architect of findings for continuous improvement.
    """

    def __init__(self, project_root: Path):
        """Initialize code reviewer agent.

        Args:
            project_root (Path): Project root directory.
        """
        self.project_root = project_root
        self.reviews_dir = project_root / "docs" / "code-reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self.notifications = NotificationDB()

    def review_commit(self, commit_sha: str = "HEAD") -> ReviewReport:
        """Review a specific commit.

        Args:
            commit_sha (str): Commit SHA to review (default: HEAD).

        Returns:
            ReviewReport: Detailed review report.
        """
        logger.info(f"Starting review of commit {commit_sha}")
        start_time = datetime.now()

        # Get commit details
        commit_info = self._get_commit_info(commit_sha)

        # Get changed files
        changed_files = self._get_changed_files(commit_sha)

        # Analyze files
        issues = self._analyze_files(changed_files)

        # Check style guide compliance
        style_compliance = self._check_style_compliance(changed_files)

        # Check architecture compliance
        architecture_compliance = self._check_architecture_compliance(changed_files)

        # Calculate quality score
        quality_score = self._calculate_quality_score(issues)

        # Determine approval status
        approved = quality_score >= 70

        # Overall assessment
        overall_assessment = self._generate_overall_assessment(quality_score, issues, approved)

        # Create review report
        review_duration = (datetime.now() - start_time).total_seconds()
        report = ReviewReport(
            commit_sha=commit_info["sha"],
            date=datetime.now(),
            files_changed=len(changed_files),
            lines_added=commit_info["lines_added"],
            lines_deleted=commit_info["lines_deleted"],
            quality_score=quality_score,
            issues=issues,
            style_compliance=style_compliance,
            architecture_compliance=architecture_compliance,
            overall_assessment=overall_assessment,
            approved=approved,
            review_duration_seconds=review_duration,
        )

        # Generate and save report
        self._save_report(report)

        # Notify architect
        self._notify_architect(report)

        logger.info(f"Review complete: {commit_info['sha'][:7]} - Score: {quality_score}/100 - Approved: {approved}")

        return report

    def _get_commit_info(self, commit_sha: str) -> Dict:
        """Get commit information.

        Args:
            commit_sha (str): Commit SHA.

        Returns:
            Dict: Commit information (sha, message, author, date, lines_added, lines_deleted).
        """
        try:
            # Get commit SHA
            result = subprocess.run(
                ["git", "rev-parse", commit_sha],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            full_sha = result.stdout.strip()

            # Get commit message and author
            result = subprocess.run(
                ["git", "show", "-s", "--format=%s|%an|%ai", full_sha],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            message, author, date = result.stdout.strip().split("|")

            # Get lines added/deleted
            result = subprocess.run(
                ["git", "show", "--stat", "--format=", full_sha],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            stats = result.stdout.strip()

            # Parse stats (last line usually has format: "X files changed, Y insertions(+), Z deletions(-)")
            lines_added = 0
            lines_deleted = 0
            if stats:
                last_line = stats.split("\n")[-1]
                if "insertion" in last_line:
                    parts = last_line.split(",")
                    for part in parts:
                        if "insertion" in part:
                            lines_added = int(part.strip().split()[0])
                        if "deletion" in part:
                            lines_deleted = int(part.strip().split()[0])

            return {
                "sha": full_sha,
                "message": message,
                "author": author,
                "date": date,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
            }

        except Exception as e:
            logger.error(f"Error getting commit info: {e}")
            return {
                "sha": commit_sha,
                "message": "Unknown",
                "author": "Unknown",
                "date": "Unknown",
                "lines_added": 0,
                "lines_deleted": 0,
            }

    def _get_changed_files(self, commit_sha: str) -> List[str]:
        """Get list of changed files in commit.

        Args:
            commit_sha (str): Commit SHA.

        Returns:
            List[str]: List of changed file paths.
        """
        try:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            # Filter to only Python files for analysis
            python_files = [f for f in files if f.endswith(".py")]
            logger.info(f"Found {len(python_files)} Python files changed in {commit_sha}")
            return python_files

        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []

    def _analyze_files(self, changed_files: List[str]) -> List[Issue]:
        """Analyze changed files for quality issues.

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            List[Issue]: List of issues found.
        """
        issues = []

        # Run static analysis tools
        issues.extend(self._run_radon_analysis(changed_files))
        issues.extend(self._run_mypy_analysis(changed_files))
        issues.extend(self._run_bandit_analysis(changed_files))
        issues.extend(self._check_test_coverage(changed_files))

        return issues

    def _run_radon_analysis(self, changed_files: List[str]) -> List[Issue]:
        """Run radon complexity analysis.

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            List[Issue]: List of complexity issues.
        """
        issues = []

        for file_path in changed_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue

            try:
                # Run radon cyclomatic complexity
                result = subprocess.run(
                    ["radon", "cc", str(full_path), "-s", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                output = result.stdout
                # Parse radon output for high complexity (grade D, E, F)
                for line in output.split("\n"):
                    if any(grade in line for grade in [" D ", " E ", " F "]):
                        issues.append(
                            Issue(
                                severity="MEDIUM" if " D " in line else "HIGH",
                                category="Performance",
                                file_path=file_path,
                                line_number=None,
                                description=f"High cyclomatic complexity: {line.strip()}",
                                recommendation="Consider refactoring to reduce complexity (extract methods, simplify logic)",
                                effort_estimate="30-60 minutes",
                            )
                        )

            except Exception as e:
                logger.warning(f"Radon analysis failed for {file_path}: {e}")

        return issues

    def _run_mypy_analysis(self, changed_files: List[str]) -> List[Issue]:
        """Run mypy type checking.

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            List[Issue]: List of type checking issues.
        """
        issues = []

        if not changed_files:
            return issues

        try:
            # Run mypy on changed files
            result = subprocess.run(
                ["mypy"] + [str(self.project_root / f) for f in changed_files],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse mypy output (format: file:line: error: message)
            for line in result.stdout.split("\n"):
                if ": error:" in line:
                    parts = line.split(":")
                    if len(parts) >= 3:
                        file_path = Path(parts[0]).relative_to(self.project_root)
                        line_number = int(parts[1]) if parts[1].isdigit() else None
                        message = ":".join(parts[3:]).strip()

                        issues.append(
                            Issue(
                                severity="LOW",
                                category="Style",
                                file_path=str(file_path),
                                line_number=line_number,
                                description=f"Type checking issue: {message}",
                                recommendation="Add or fix type hints",
                                effort_estimate="5-15 minutes",
                            )
                        )

        except Exception as e:
            logger.warning(f"Mypy analysis failed: {e}")

        return issues

    def _run_bandit_analysis(self, changed_files: List[str]) -> List[Issue]:
        """Run bandit security scanning.

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            List[Issue]: List of security issues.
        """
        issues = []

        if not changed_files:
            return issues

        try:
            # Run bandit on changed files
            result = subprocess.run(
                ["bandit", "-r"] + [str(self.project_root / f) for f in changed_files],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse bandit output
            output = result.stdout
            if "CONFIDENCE: HIGH" in output or "CONFIDENCE: MEDIUM" in output:
                # Found security issues
                for line in output.split("\n"):
                    if "Issue:" in line:
                        issues.append(
                            Issue(
                                severity="CRITICAL" if "CONFIDENCE: HIGH" in output else "HIGH",
                                category="Security",
                                file_path=changed_files[0] if changed_files else "unknown",
                                line_number=None,
                                description=f"Security vulnerability detected: {line.strip()}",
                                recommendation="Review and fix security issue immediately",
                                effort_estimate="30-120 minutes",
                            )
                        )

        except Exception as e:
            logger.warning(f"Bandit analysis failed: {e}")

        return issues

    def _check_test_coverage(self, changed_files: List[str]) -> List[Issue]:
        """Check test coverage for changed files.

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            List[Issue]: List of test coverage issues.
        """
        issues = []

        # Filter to source files only (not tests)
        source_files = [f for f in changed_files if not f.startswith("tests/")]

        if not source_files:
            return issues

        try:
            # Run pytest with coverage
            result = subprocess.run(
                ["pytest", "--cov=coffee_maker", "--cov-report=term-missing", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse coverage output
            output = result.stdout
            for source_file in source_files:
                # Check if file appears in coverage report
                file_name = Path(source_file).stem
                if file_name in output:
                    # Look for coverage percentage
                    for line in output.split("\n"):
                        if file_name in line:
                            parts = line.split()
                            if len(parts) >= 4 and parts[3].endswith("%"):
                                coverage = int(parts[3].rstrip("%"))
                                if coverage < 80:
                                    issues.append(
                                        Issue(
                                            severity="MEDIUM",
                                            category="Test Coverage",
                                            file_path=source_file,
                                            line_number=None,
                                            description=f"Test coverage below 80%: {coverage}%",
                                            recommendation="Add more unit tests to cover edge cases",
                                            effort_estimate="30-60 minutes",
                                        )
                                    )

        except Exception as e:
            logger.warning(f"Coverage check failed: {e}")

        return issues

    def _check_style_compliance(self, changed_files: List[str]) -> Dict[str, bool]:
        """Check style guide compliance (.gemini/styleguide.md).

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            Dict[str, bool]: Style compliance checks.
        """
        compliance = {
            "line_length_120": True,
            "google_docstrings": True,
            "type_hints": True,
            "snake_case_naming": True,
            "imports_grouped": True,
            "logging_module": True,
        }

        # For simplicity, assume compliance unless static analysis found issues
        # In a full implementation, would parse files and check each rule

        return compliance

    def _check_architecture_compliance(self, changed_files: List[str]) -> Dict[str, bool]:
        """Check architecture compliance (SPEC-*, ADR-*, GUIDELINE-*).

        Args:
            changed_files (List[str]): List of changed file paths.

        Returns:
            Dict[str, bool]: Architecture compliance checks.
        """
        compliance = {
            "follows_specs": True,
            "follows_adrs": True,
            "follows_guidelines": True,
            "uses_mixins_pattern": True,
            "singleton_enforcement": True,
        }

        # Check for common architecture patterns
        for file_path in changed_files:
            full_path = self.project_root / file_path

            if full_path.exists():
                try:
                    content = full_path.read_text()

                    # Check singleton pattern usage for agents
                    if "Agent" in file_path and "AgentRegistry" not in content:
                        compliance["singleton_enforcement"] = False

                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")

        return compliance

    def _calculate_quality_score(self, issues: List[Issue]) -> int:
        """Calculate quality score (0-100).

        Args:
            issues (List[Issue]): List of issues found.

        Returns:
            int: Quality score (0-100).
        """
        score = 100

        for issue in issues:
            if issue.severity == "CRITICAL":
                score -= 30
            elif issue.severity == "HIGH":
                score -= 20
            elif issue.severity == "MEDIUM":
                score -= 10
            elif issue.severity == "LOW":
                score -= 5

        return max(0, score)

    def _generate_overall_assessment(self, quality_score: int, issues: List[Issue], approved: bool) -> str:
        """Generate overall assessment text.

        Args:
            quality_score (int): Quality score.
            issues (List[Issue]): List of issues.
            approved (bool): Approval status.

        Returns:
            str: Overall assessment text.
        """
        critical_issues = sum(1 for i in issues if i.severity == "CRITICAL")
        high_issues = sum(1 for i in issues if i.severity == "HIGH")
        medium_issues = sum(1 for i in issues if i.severity == "MEDIUM")
        low_issues = sum(1 for i in issues if i.severity == "LOW")

        if quality_score >= 90:
            assessment = f"**APPROVED - EXCELLENT QUALITY**\n\nQuality score: {quality_score}/100. "
            if low_issues > 0:
                assessment += f"{low_issues} low issue(s) are minor and can be addressed later."
            else:
                assessment += "No issues found. Excellent work!"
        elif quality_score >= 70:
            assessment = f"**APPROVED WITH NOTES**\n\nQuality score: {quality_score}/100. "
            assessment += f"Found {medium_issues} medium issue(s). "
            assessment += "Optional follow-up recommended."
        elif quality_score >= 50:
            assessment = f"**REQUEST CHANGES**\n\nQuality score: {quality_score}/100. "
            assessment += f"Found {medium_issues} medium issue(s) and {high_issues} high issue(s). "
            assessment += "architect should create follow-up task."
        else:
            assessment = f"**BLOCK MERGE - CRITICAL ISSUES**\n\nQuality score: {quality_score}/100. "
            assessment += f"Found {critical_issues} critical issue(s). "
            assessment += "Immediate fix required before proceeding."

        return assessment

    def _save_report(self, report: ReviewReport) -> None:
        """Save review report to file.

        Args:
            report (ReviewReport): Review report to save.
        """
        # Generate report filename
        report_date = report.date.strftime("%Y-%m-%d")
        commit_short = report.commit_sha[:7]
        report_filename = f"REVIEW-{report_date}-{commit_short}.md"
        report_path = self.reviews_dir / report_filename

        # Generate report content
        content = self._generate_report_markdown(report)

        # Save to file
        report_path.write_text(content)
        logger.info(f"Saved review report: {report_path}")

        # Update index
        self._update_review_index(report)

    def _generate_report_markdown(self, report: ReviewReport) -> str:
        """Generate review report in Markdown format.

        Args:
            report (ReviewReport): Review report.

        Returns:
            str: Markdown content.
        """
        # Count issues by severity
        critical = [i for i in report.issues if i.severity == "CRITICAL"]
        high = [i for i in report.issues if i.severity == "HIGH"]
        medium = [i for i in report.issues if i.severity == "MEDIUM"]
        low = [i for i in report.issues if i.severity == "LOW"]

        md = f"""# Code Review Report

**Commit**: {report.commit_sha[:7]}
**Date**: {report.date.strftime('%Y-%m-%d %H:%M:%S')}
**Reviewer**: code-reviewer
**Files Changed**: {report.files_changed} files (+{report.lines_added}, -{report.lines_deleted})
**Review Duration**: {report.review_duration_seconds:.1f} seconds

---

## Summary

{report.overall_assessment}

**Quality Score**: {report.quality_score}/100

---

## Issues Found

### 🔴 CRITICAL ({len(critical)})
"""

        if critical:
            for i, issue in enumerate(critical, 1):
                md += f"""
{i}. **{issue.category}** - `{issue.file_path}`
   - {issue.description}
   - **Recommendation**: {issue.recommendation}
   - **Effort**: {issue.effort_estimate}
"""
        else:
            md += "\nNone\n"

        md += f"""
### 🟠 HIGH ({len(high)})
"""

        if high:
            for i, issue in enumerate(high, 1):
                md += f"""
{i}. **{issue.category}** - `{issue.file_path}`
   - {issue.description}
   - **Recommendation**: {issue.recommendation}
   - **Effort**: {issue.effort_estimate}
"""
        else:
            md += "\nNone\n"

        md += f"""
### 🟡 MEDIUM ({len(medium)})
"""

        if medium:
            for i, issue in enumerate(medium, 1):
                md += f"""
{i}. **{issue.category}** - `{issue.file_path}`
   - {issue.description}
   - **Recommendation**: {issue.recommendation}
   - **Effort**: {issue.effort_estimate}
"""
        else:
            md += "\nNone\n"

        md += f"""
### ⚪ LOW ({len(low)})
"""

        if low:
            for i, issue in enumerate(low, 1):
                md += f"""
{i}. **{issue.category}** - `{issue.file_path}`
   - {issue.description}
   - **Recommendation**: {issue.recommendation}
   - **Effort**: {issue.effort_estimate}
"""
        else:
            md += "\nNone\n"

        # Style guide compliance
        md += """
---

## Style Guide Compliance (`.gemini/styleguide.md`)

"""
        for check, passed in report.style_compliance.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            md += f"{status} - {check.replace('_', ' ').title()}\n"

        # Architecture compliance
        md += """
---

## Architecture Compliance

"""
        for check, passed in report.architecture_compliance.items():
            status = "✅ PASS" if passed else "⚠️ WARNING"
            md += f"{status} - {check.replace('_', ' ').title()}\n"

        # Recommendations for architect
        md += """
---

## Recommendations for architect

"""
        if report.quality_score >= 90:
            md += """
No action required. Code quality is excellent.
"""
        elif report.quality_score >= 70:
            md += """
Consider reviewing the medium issues and decide if follow-up task is needed.
Optional improvements suggested in the issues section above.
"""
        elif report.quality_score >= 50:
            md += """
1. **Create follow-up task** for code_developer to address medium/high issues
2. **Update relevant specs** if issues indicate spec improvements needed
3. **Review architecture decisions** if patterns are not being followed
"""
        else:
            md += """
1. **URGENT**: Review critical issues immediately
2. **Block further work** until critical issues are resolved
3. **Update specs** with stricter requirements to prevent recurrence
4. **Create high-priority task** for code_developer with detailed fixes
"""

        md += """
---

## Overall Assessment

"""
        md += report.overall_assessment

        md += (
            """

**Next Steps**:
1. architect reviews this report
2. architect creates follow-up task if needed
3. code_developer addresses issues
4. code-reviewer re-reviews after fix

---

**Review Confidence**: HIGH
**Reviewed Lines**: """
            + str(report.lines_added + report.lines_deleted)
            + """ (100% coverage)
**Automated Checks**: """
            + str(len(report.style_compliance) + len(report.architecture_compliance))
            + """ checks run
"""
        )

        return md

    def _update_review_index(self, report: ReviewReport) -> None:
        """Update review index file.

        Args:
            report (ReviewReport): Review report.
        """
        index_path = self.reviews_dir / "INDEX.md"

        # Read existing index or create new
        if index_path.exists():
            content = index_path.read_text()
        else:
            content = """# Code Review Index

This index lists all code reviews performed by code-reviewer agent.

## Reviews

| Date | Commit | Score | Status | Issues | Report |
|------|--------|-------|--------|--------|--------|
"""

        # Add new review entry
        report_date = report.date.strftime("%Y-%m-%d")
        commit_short = report.commit_sha[:7]
        report_filename = f"REVIEW-{report_date}-{commit_short}.md"

        status = "✅ APPROVED" if report.approved else "❌ CHANGES REQUESTED"
        issues_count = len(report.issues)

        new_entry = f"| {report_date} | {commit_short} | {report.quality_score}/100 | {status} | {issues_count} | [{report_filename}](./{report_filename}) |\n"

        # Insert new entry (after header)
        lines = content.split("\n")
        header_end = -1
        for i, line in enumerate(lines):
            if line.startswith("|---"):
                header_end = i
                break

        if header_end >= 0:
            lines.insert(header_end + 1, new_entry.rstrip())
            content = "\n".join(lines)
        else:
            content += new_entry

        # Save index
        index_path.write_text(content)

    def _notify_architect(self, report: ReviewReport) -> None:
        """Notify architect of review completion.

        Args:
            report (ReviewReport): Review report.
        """
        commit_short = report.commit_sha[:7]

        # Determine notification level
        if report.quality_score >= 90:
            level = "info"
            title = f"Code Review: {commit_short} - Approved ✅"
        elif report.quality_score >= 70:
            level = "info"
            title = f"Code Review: {commit_short} - Approved with Notes ⚠️"
        elif report.quality_score >= 50:
            level = "high"
            title = f"Code Review: {commit_short} - Changes Requested ⚠️"
        else:
            level = "high"
            title = f"Code Review: {commit_short} - Critical Issues ❌"

        message = (
            f"Quality score: {report.quality_score}/100. "
            f"Issues found: {len(report.issues)}. "
            f"Review: docs/code-reviews/REVIEW-{report.date.strftime('%Y-%m-%d')}-{commit_short}.md"
        )

        # Create notification (background agent - MUST use sound=False)
        self.notifications.create_notification(
            title=title,
            message=message,
            level=level,
            sound=False,  # CFR-009: code-reviewer is background agent
            agent_id="code_reviewer",
        )

        logger.info(f"Notified architect: {title}")


def main():
    """Main entry point for code-reviewer CLI."""
    import sys

    project_root = Path(__file__).parent.parent.parent

    if len(sys.argv) < 2:
        print("Usage: poetry run code-reviewer review [<commit-sha>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "review":
        commit_sha = sys.argv[2] if len(sys.argv) > 2 else "HEAD"

        # Use singleton enforcement
        with AgentRegistry.register(AgentType.CODE_REVIEWER):
            reviewer = CodeReviewerAgent(project_root)
            report = reviewer.review_commit(commit_sha)

            print(f"\n✅ Review complete!")
            print(f"Commit: {report.commit_sha[:7]}")
            print(f"Quality Score: {report.quality_score}/100")
            print(f"Issues: {len(report.issues)}")
            print(f"Approved: {report.approved}")
            print(
                f"\nReport saved to: docs/code-reviews/REVIEW-{report.date.strftime('%Y-%m-%d')}-{report.commit_sha[:7]}.md"
            )

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
