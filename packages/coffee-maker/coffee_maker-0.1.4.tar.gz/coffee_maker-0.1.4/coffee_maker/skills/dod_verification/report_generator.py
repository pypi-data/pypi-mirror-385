"""
Report Generator: Generate comprehensive DoD verification reports.

Creates Markdown and JSON reports with executive summary, detailed results, and recommendations.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coffee_maker.skills.dod_verification.dod_verification import DoDResult


class ReportGenerator:
    """Generate DoD verification reports."""

    def generate_markdown_report(self, result: "DoDResult") -> str:
        """
        Generate Markdown DoD verification report.

        Args:
            result: DoD verification result

        Returns:
            Markdown report content
        """
        report = []

        # Header
        report.append("# Definition of Done (DoD) Verification Report\n")
        report.append(f"**Priority**: {result.priority}\n")
        report.append(f"**Date**: {result.timestamp}\n")
        report.append(f"**Overall Status**: {'✅ PASS' if result.status == 'PASS' else '❌ FAIL'}\n")
        report.append("\n---\n\n")

        # Executive Summary
        report.append("## Executive Summary\n\n")
        report.append(f"- Criteria Tested: {result.criteria_tested}\n")
        report.append(f"- Checks Passed: {result.criteria_passed}/{result.criteria_tested}\n")
        report.append(f"- Checks Failed: {result.criteria_failed}\n")
        report.append(f"- Execution Time: {result.execution_time_seconds:.2f}s\n")
        report.append(f"- **Recommendation**: {result.recommendation}\n")
        report.append("\n")

        # Detailed Results
        report.append("## Detailed Results\n\n")

        # Automated Checks
        if "automated" in result.checks:
            report.append("### Automated Checks\n\n")
            automated = result.checks["automated"]
            report.append(f"**Status**: {automated['status']}\n\n")

            if "tests" in automated:
                tests = automated["tests"]
                report.append(f"- **Tests**: {tests['passed']} passed, {tests['failed']} failed\n")

            if "formatting" in automated:
                fmt = automated["formatting"]
                report.append(f"- **Formatting**: {fmt['status']} ({fmt['tool']})\n")

            if "pre_commit" in automated:
                pre = automated["pre_commit"]
                report.append(f"- **Pre-commit Hooks**: {pre['status']}\n")

            if "security" in automated:
                sec = automated["security"]
                report.append(f"- **Security**: {sec['status']} ({sec['tool']})\n")

            report.append("\n")

        # Code Quality
        if "code_quality" in result.checks:
            report.append("### Code Quality\n\n")
            quality = result.checks["code_quality"]
            report.append(f"**Status**: {quality['status']}\n\n")
            report.append(f"- Files Checked: {quality['files_checked']}\n")
            report.append(f"- Total Issues: {quality.get('total_issues', 0)}\n")

            if quality.get("total_issues", 0) > 0:
                report.append("\n**Issues Found**:\n\n")
                for issue_type, issues in quality.get("issues", {}).items():
                    if issues:
                        report.append(f"- {issue_type}: {len(issues)}\n")
                        for issue in issues[:5]:  # Show first 5
                            report.append(f"  - {issue}\n")
                        if len(issues) > 5:
                            report.append(f"  - ... and {len(issues) - 5} more\n")

            report.append("\n")

        # Functionality
        if "functionality" in result.checks:
            report.append("### Functionality Testing\n\n")
            func = result.checks["functionality"]
            report.append(f"**Status**: {func['status']}\n\n")
            report.append(f"- Criteria Tested: {func['criteria_tested']}\n")
            report.append(f"- Criteria Passed: {func['criteria_passed']}\n")
            report.append(f"- Criteria Failed: {func['criteria_failed']}\n")

            if func.get("screenshots"):
                report.append(f"\n**Evidence Screenshots**: {len(func['screenshots'])} captured\n")
                for screenshot in func["screenshots"][:5]:
                    report.append(f"- {screenshot}\n")

            if func.get("details"):
                report.append("\n**Details**:\n\n")
                for detail in func["details"][:10]:
                    report.append(f"- {detail}\n")

            report.append("\n")

        # Documentation
        if "documentation" in result.checks:
            report.append("### Documentation\n\n")
            docs = result.checks["documentation"]
            report.append(f"**Status**: {docs['status']}\n\n")
            report.append(f"- Code Documentation: {docs['code_docs']}\n")
            report.append(f"- User Documentation: {docs['user_docs']}\n")
            report.append(f"- Technical Documentation: {docs['technical_docs']}\n")

            if docs.get("missing_docs"):
                report.append("\n**Missing Documentation**:\n\n")
                for missing in docs["missing_docs"]:
                    report.append(f"- {missing}\n")

            report.append("\n")

        # Integration
        if "integration" in result.checks:
            report.append("### Integration & Compatibility\n\n")
            integration = result.checks["integration"]
            report.append(f"**Status**: {integration['status']}\n\n")
            report.append(f"- Backward Compatible: {integration['backward_compatible']}\n")
            report.append(f"- Integration Tests: {integration['integration_tests']}\n")
            report.append(f"- Dependencies: {integration['dependencies']}\n")
            report.append(f"- Config Changes: {integration['config_changes']}\n")

            if integration.get("issues"):
                report.append("\n**Issues**:\n\n")
                for issue in integration["issues"]:
                    report.append(f"- {issue}\n")

            report.append("\n")

        # Recommendations
        report.append("## Recommendations\n\n")
        if result.status == "PASS":
            report.append("✅ **All DoD criteria met. Ready to merge.**\n\n")
            report.append("**Next Steps**:\n")
            report.append("1. Create pull request\n")
            report.append("2. Request code review\n")
            report.append("3. Merge to main branch\n")
        else:
            report.append("❌ **DoD criteria not met. Fix issues before merging.**\n\n")
            report.append("**Next Steps**:\n")
            report.append("1. Review failed checks above\n")
            report.append("2. Fix identified issues\n")
            report.append("3. Re-run DoD verification\n")

        report.append("\n---\n\n")
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        report.append("*Tool: DoD Verification Skill (coffee_maker/skills/dod_verification)*\n")

        return "".join(report)
