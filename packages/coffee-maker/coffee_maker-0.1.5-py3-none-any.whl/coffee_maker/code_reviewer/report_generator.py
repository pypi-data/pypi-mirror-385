"""Report generator for code review results.

This module generates formatted reports from code review results:
- HTML reports with interactive filtering
- Markdown reports for documentation
- JSON reports for programmatic access
- Plain text reports for CLI output
"""

from pathlib import Path
from typing import List

from coffee_maker.code_reviewer.models import ReviewReport


class ReportGenerator:
    """Generates formatted reports from code review results.

    Supports multiple output formats:
    - HTML: Interactive report with filtering
    - Markdown: Documentation-friendly format
    - JSON: Programmatic access
    - Text: CLI-friendly format

    Example:
        >>> generator = ReportGenerator()
        >>> html = generator.generate_html(report)
        >>> Path("review.html").write_text(html)
    """

    def __init__(self):
        """Initialize report generator."""

    def generate_html(self, report: ReviewReport) -> str:
        """Generate interactive HTML report.

        Args:
            report: Code review report

        Returns:
            HTML string

        Example:
            >>> generator = ReportGenerator()
            >>> html = generator.generate_html(report)
            >>> Path("review.html").write_text(html)
        """
        # Group issues by severity
        critical_issues = report.get_issues_by_severity("critical")
        high_issues = report.get_issues_by_severity("high")
        medium_issues = report.get_issues_by_severity("medium")
        low_issues = report.get_issues_by_severity("low")

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report - {Path(report.file_path).name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}

        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            white-space: pre-line;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .metric-label {{
            color: #7f8c8d;
            font-size: 14px;
        }}

        .severity-critical .metric-value {{ color: #e74c3c; }}
        .severity-high .metric-value {{ color: #e67e22; }}
        .severity-medium .metric-value {{ color: #f39c12; }}
        .severity-low .metric-value {{ color: #3498db; }}

        .issue-section {{
            margin-bottom: 30px;
        }}

        .section-header {{
            font-size: 24px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}

        .issue {{
            background: #fff;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .issue.critical {{ border-left-color: #e74c3c; }}
        .issue.high {{ border-left-color: #e67e22; }}
        .issue.medium {{ border-left-color: #f39c12; }}
        .issue.low {{ border-left-color: #3498db; }}

        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}

        .issue-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }}

        .issue-meta {{
            display: flex;
            gap: 10px;
            font-size: 12px;
        }}

        .badge {{
            padding: 4px 8px;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge.critical {{ background: #e74c3c; color: white; }}
        .badge.high {{ background: #e67e22; color: white; }}
        .badge.medium {{ background: #f39c12; color: white; }}
        .badge.low {{ background: #3498db; color: white; }}
        .badge.category {{ background: #95a5a6; color: white; }}

        .issue-description {{
            margin: 15px 0;
            color: #555;
        }}

        .code-snippet {{
            background: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin: 10px 0;
        }}

        .suggestion {{
            background: #d5f4e6;
            border-left: 3px solid #27ae60;
            padding: 12px;
            margin-top: 10px;
            border-radius: 4px;
        }}

        .suggestion-label {{
            font-weight: 600;
            color: #27ae60;
            margin-bottom: 5px;
        }}

        .no-issues {{
            text-align: center;
            padding: 40px;
            color: #27ae60;
            font-size: 20px;
        }}

        .filter-buttons {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }}

        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .filter-btn:hover {{
            background: #f0f0f0;
        }}

        .filter-btn.active {{
            background: #3498db;
            color: white;
            border-color: #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Review Report</h1>
        <div class="timestamp">
            <strong>File:</strong> {report.file_path}<br>
            <strong>Generated:</strong> {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </div>

        <div class="summary">
            <strong>Summary:</strong><br>
            {report.summary}
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{report.metrics.get('total_issues', 0)}</div>
                <div class="metric-label">Total Issues</div>
            </div>
            <div class="metric-card severity-critical">
                <div class="metric-value">{report.metrics.get('critical', 0)}</div>
                <div class="metric-label">Critical</div>
            </div>
            <div class="metric-card severity-high">
                <div class="metric-value">{report.metrics.get('high', 0)}</div>
                <div class="metric-label">High</div>
            </div>
            <div class="metric-card severity-medium">
                <div class="metric-value">{report.metrics.get('medium', 0)}</div>
                <div class="metric-label">Medium</div>
            </div>
            <div class="metric-card severity-low">
                <div class="metric-value">{report.metrics.get('low', 0)}</div>
                <div class="metric-label">Low</div>
            </div>
        </div>

        {"" if report.issues else '<div class="no-issues">✅ No issues found! Code looks great.</div>'}

        {self._generate_issue_section_html("Critical Issues", critical_issues, "critical")}
        {self._generate_issue_section_html("High Priority Issues", high_issues, "high")}
        {self._generate_issue_section_html("Medium Priority Issues", medium_issues, "medium")}
        {self._generate_issue_section_html("Low Priority Issues", low_issues, "low")}
    </div>
</body>
</html>
"""

        return html

    def _generate_issue_section_html(self, title: str, issues: List, severity: str) -> str:
        """Generate HTML for a section of issues.

        Args:
            title: Section title
            issues: List of issues
            severity: Severity level

        Returns:
            HTML string for the section
        """
        if not issues:
            return ""

        issues_html = []
        for issue in issues:
            code_snippet_html = f'<div class="code-snippet">{issue.code_snippet}</div>' if issue.code_snippet else ""

            suggestion_html = (
                f"""
                <div class="suggestion">
                    <div class="suggestion-label">💡 Suggestion:</div>
                    <div>{issue.suggestion}</div>
                </div>
            """
                if issue.suggestion
                else ""
            )

            line_info = f"Line {issue.line_number}" if issue.line_number else "Multiple lines"

            issues_html.append(
                f"""
                <div class="issue {severity}">
                    <div class="issue-header">
                        <div class="issue-title">{issue.title}</div>
                        <div class="issue-meta">
                            <span class="badge {severity}">{severity}</span>
                            <span class="badge category">{issue.category}</span>
                        </div>
                    </div>
                    <div style="color: #7f8c8d; font-size: 14px; margin-bottom: 10px;">
                        {line_info} • {issue.perspective}
                    </div>
                    <div class="issue-description">{issue.description}</div>
                    {code_snippet_html}
                    {suggestion_html}
                </div>
            """
            )

        return f"""
            <div class="issue-section">
                <h2 class="section-header">{title} ({len(issues)})</h2>
                {"".join(issues_html)}
            </div>
        """

    def generate_markdown(self, report: ReviewReport) -> str:
        """Generate Markdown report.

        Args:
            report: Code review report

        Returns:
            Markdown string

        Example:
            >>> generator = ReportGenerator()
            >>> md = generator.generate_markdown(report)
            >>> Path("review.md").write_text(md)
        """
        lines = [
            f"# Code Review Report: {Path(report.file_path).name}",
            "",
            f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**File:** `{report.file_path}`",
            "",
            "## Summary",
            "",
            report.summary,
            "",
            "## Metrics",
            "",
            f"- **Total Issues:** {report.metrics.get('total_issues', 0)}",
            f"- **Critical:** {report.metrics.get('critical', 0)}",
            f"- **High:** {report.metrics.get('high', 0)}",
            f"- **Medium:** {report.metrics.get('medium', 0)}",
            f"- **Low:** {report.metrics.get('low', 0)}",
            "",
        ]

        if not report.issues:
            lines.append("✅ **No issues found!** Code looks great.")
            return "\n".join(lines)

        # Group by severity
        for severity in ["critical", "high", "medium", "low"]:
            issues = report.get_issues_by_severity(severity)
            if issues:
                lines.extend(self._generate_issue_section_markdown(severity, issues))

        return "\n".join(lines)

    def _generate_issue_section_markdown(self, severity: str, issues: List) -> List[str]:
        """Generate Markdown for issue section.

        Args:
            severity: Severity level
            issues: List of issues

        Returns:
            List of markdown lines
        """
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
        }

        lines = [
            f"## {severity_emoji.get(severity, '')} {severity.title()} Issues ({len(issues)})",
            "",
        ]

        for i, issue in enumerate(issues, 1):
            lines.append(f"### {i}. {issue.title}")
            lines.append("")
            lines.append(f"**Severity:** {severity.upper()} | **Category:** {issue.category}")

            if issue.line_number:
                lines.append(f"**Location:** Line {issue.line_number}")

            lines.append(f"**Found by:** {issue.perspective}")
            lines.append("")
            lines.append(f"{issue.description}")
            lines.append("")

            if issue.code_snippet:
                lines.append("**Code:**")
                lines.append("```python")
                lines.append(issue.code_snippet)
                lines.append("```")
                lines.append("")

            if issue.suggestion:
                lines.append(f"💡 **Suggestion:** {issue.suggestion}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return lines

    def save_html_report(self, report: ReviewReport, output_path: str) -> None:
        """Generate and save HTML report to file.

        Args:
            report: Code review report
            output_path: Path to save HTML file

        Example:
            >>> generator = ReportGenerator()
            >>> generator.save_html_report(report, "report.html")
        """
        html = self.generate_html(report)
        Path(output_path).write_text(html)

    def save_markdown_report(self, report: ReviewReport, output_path: str) -> None:
        """Generate and save Markdown report to file.

        Args:
            report: Code review report
            output_path: Path to save Markdown file

        Example:
            >>> generator = ReportGenerator()
            >>> generator.save_markdown_report(report, "report.md")
        """
        markdown = self.generate_markdown(report)
        Path(output_path).write_text(markdown)
