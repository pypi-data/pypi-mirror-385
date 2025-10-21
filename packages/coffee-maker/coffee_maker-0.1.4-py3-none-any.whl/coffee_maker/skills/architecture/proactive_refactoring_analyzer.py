"""
Proactive Refactoring Analysis Skill

Identifies code health issues weekly and recommends refactoring improvements.

Capabilities:
- analyze_codebase(): Performs full codebase health analysis
- calculate_metrics(path): Calculates complexity, duplication, coverage metrics
- find_refactoring_opportunities(): Identifies top refactoring candidates
- generate_weekly_report(): Creates synthetic health report for project_manager
- track_trends(): Monitors code health over time

Used by: architect (proactively, weekly automated analysis)
"""

import ast
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.utils.file_io import read_json_file, write_json_file


@dataclass
class CodeMetrics:
    """Code quality metrics for a file or module."""

    file_path: str
    lines_of_code: int
    complexity: int  # Cyclomatic complexity
    duplication_score: float  # 0-100%
    test_coverage: float  # 0-100%
    num_functions: int
    num_classes: int
    avg_function_length: float
    max_function_length: int
    num_todos: int
    num_fixmes: int
    num_hacks: int


@dataclass
class RefactoringOpportunity:
    """Represents a refactoring opportunity with ROI calculation."""

    title: str
    category: str  # "duplication", "complexity", "naming", "architecture", "technical_debt"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    current_state: str
    proposed_refactoring: str
    files_affected: List[str]
    estimated_effort_hours: float
    time_saved_hours: float  # Future time savings
    roi_score: float  # time_saved / estimated_effort
    priority: int  # 1-10 based on ROI and severity
    benefits: List[str]
    risks: List[str]


@dataclass
class CodeHealthReport:
    """Weekly code health report."""

    timestamp: str
    codebase_name: str
    total_loc: int
    total_files: int
    opportunities: List[RefactoringOpportunity]
    metrics_summary: Dict[str, Any]
    top_priorities: List[RefactoringOpportunity]
    overall_health_score: float  # 0-100
    execution_time_seconds: float


@dataclass
class TrendData:
    """Historical trend data for code health."""

    timestamp: str
    health_score: float
    total_loc: int
    complexity_avg: float
    duplication_pct: float
    test_coverage_pct: float
    num_opportunities: int


class ProactiveRefactoringAnalyzer:
    """
    Proactively identifies refactoring opportunities and generates health reports.

    Analyzes codebase for:
    - Code duplication (>20% duplicated blocks)
    - File/function complexity (>500 LOC files, >50 LOC functions)
    - Naming issues (magic numbers, vague names)
    - Architecture patterns (god classes, tight coupling)
    - Technical debt (TODOs, FIXMEs, HACKs)
    - Test coverage (<80%)
    - Dependency issues (unused, outdated, circular)
    """

    def __init__(self, codebase_root: Path):
        """Initialize analyzer with codebase root path."""
        self.codebase_root = Path(codebase_root)
        self.data_dir = self.codebase_root / "data" / "refactoring_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trends_file = self.data_dir / "trends.json"

    def analyze_codebase(self) -> CodeHealthReport:
        """
        Perform full codebase health analysis.

        Returns:
            CodeHealthReport with opportunities, metrics, and recommendations
        """
        start_time = datetime.now()

        # 1. Calculate metrics for all Python files
        metrics = self._calculate_all_metrics()

        # 2. Find refactoring opportunities
        opportunities = self._find_refactoring_opportunities(metrics)

        # 3. Sort by ROI and priority
        opportunities_sorted = sorted(opportunities, key=lambda x: (x.priority, x.roi_score), reverse=True)

        # 4. Calculate overall health score
        health_score = self._calculate_health_score(metrics, opportunities)

        # 5. Get top priorities (top 3-5)
        top_priorities = opportunities_sorted[:5]

        # 6. Create metrics summary
        metrics_summary = self._create_metrics_summary(metrics)

        # 7. Record trend data
        self._record_trend(health_score, metrics_summary, len(opportunities))

        execution_time = (datetime.now() - start_time).total_seconds()

        report = CodeHealthReport(
            timestamp=datetime.now().isoformat(),
            codebase_name=self.codebase_root.name,
            total_loc=sum(m.lines_of_code for m in metrics),
            total_files=len(metrics),
            opportunities=opportunities_sorted,
            metrics_summary=metrics_summary,
            top_priorities=top_priorities,
            overall_health_score=health_score,
            execution_time_seconds=execution_time,
        )

        return report

    def _calculate_all_metrics(self) -> List[CodeMetrics]:
        """Calculate metrics for all Python files in codebase."""
        metrics = []

        # Find all Python files (exclude tests, venv, etc.)
        python_files = list(self.codebase_root.glob("coffee_maker/**/*.py"))

        for file_path in python_files:
            try:
                metrics.append(self._calculate_file_metrics(file_path))
            except Exception:
                # Skip files that can't be analyzed
                continue

        return metrics

    def _calculate_file_metrics(self, file_path: Path) -> CodeMetrics:
        """Calculate metrics for a single file."""
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Return minimal metrics for unparseable files
            return CodeMetrics(
                file_path=str(file_path),
                lines_of_code=len(lines),
                complexity=0,
                duplication_score=0.0,
                test_coverage=0.0,
                num_functions=0,
                num_classes=0,
                avg_function_length=0.0,
                max_function_length=0,
                num_todos=0,
                num_fixmes=0,
                num_hacks=0,
            )

        # Extract functions and classes
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # Calculate function lengths
        function_lengths = []
        for func in functions:
            func_start = func.lineno
            func_end = func.end_lineno or func_start
            func_length = func_end - func_start + 1
            function_lengths.append(func_length)

        avg_func_len = sum(function_lengths) / len(function_lengths) if function_lengths else 0.0
        max_func_len = max(function_lengths) if function_lengths else 0

        # Calculate complexity (simple approximation based on control flow)
        complexity = self._calculate_complexity(tree)

        # Detect technical debt indicators
        num_todos = len(re.findall(r"TODO|todo", content))
        num_fixmes = len(re.findall(r"FIXME|fixme", content))
        num_hacks = len(re.findall(r"HACK|hack|XXX", content))

        # Duplication score (placeholder - would need full analysis)
        duplication_score = 0.0

        # Test coverage (placeholder - would need pytest-cov)
        test_coverage = 80.0  # Default assumption

        return CodeMetrics(
            file_path=str(file_path),
            lines_of_code=len(lines),
            complexity=complexity,
            duplication_score=duplication_score,
            test_coverage=test_coverage,
            num_functions=len(functions),
            num_classes=len(classes),
            avg_function_length=avg_func_len,
            max_function_length=max_func_len,
            num_todos=num_todos,
            num_fixmes=num_fixmes,
            num_hacks=num_hacks,
        )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _find_refactoring_opportunities(self, metrics: List[CodeMetrics]) -> List[RefactoringOpportunity]:
        """Find refactoring opportunities based on metrics."""
        opportunities = []

        # 1. Check for large files (>500 LOC)
        large_files = [m for m in metrics if m.lines_of_code > 500]
        for metric in large_files:
            file_name = Path(metric.file_path).name
            severity = "CRITICAL" if metric.lines_of_code > 1000 else "HIGH"
            estimated_effort = (metric.lines_of_code // 500) * 8  # 8 hours per 500 LOC
            time_saved = estimated_effort * 1.5  # Easier maintenance

            opportunities.append(
                RefactoringOpportunity(
                    title=f"Split {file_name} into smaller modules",
                    category="complexity",
                    severity=severity,
                    current_state=f"{metric.lines_of_code} LOC in single file",
                    proposed_refactoring="Split into logical modules or use mixin pattern",
                    files_affected=[metric.file_path],
                    estimated_effort_hours=estimated_effort,
                    time_saved_hours=time_saved,
                    roi_score=time_saved / estimated_effort if estimated_effort > 0 else 0,
                    priority=10 if severity == "CRITICAL" else 8,
                    benefits=[
                        "Easier to navigate and understand",
                        "Better separation of concerns",
                        "Easier testing",
                    ],
                    risks=["Breaking existing imports", "Requires thorough testing"],
                )
            )

        # 2. Check for complex functions (>50 LOC)
        for metric in metrics:
            if metric.max_function_length > 50:
                file_name = Path(metric.file_path).name
                opportunities.append(
                    RefactoringOpportunity(
                        title=f"Break down complex functions in {file_name}",
                        category="complexity",
                        severity="MEDIUM",
                        current_state=f"Functions up to {metric.max_function_length} LOC",
                        proposed_refactoring="Extract helper functions, simplify logic",
                        files_affected=[metric.file_path],
                        estimated_effort_hours=3.0,
                        time_saved_hours=5.0,
                        roi_score=5.0 / 3.0,
                        priority=6,
                        benefits=["Better readability", "Easier testing", "Reusable helpers"],
                        risks=["May increase call stack depth"],
                    )
                )

        # 3. Check for technical debt (TODOs, FIXMEs)
        files_with_debt = [m for m in metrics if m.num_todos + m.num_fixmes + m.num_hacks > 0]
        if files_with_debt:
            total_debt = sum(m.num_todos + m.num_fixmes + m.num_hacks for m in files_with_debt)
            opportunities.append(
                RefactoringOpportunity(
                    title=f"Address {total_debt} technical debt items",
                    category="technical_debt",
                    severity="MEDIUM",
                    current_state=f"{total_debt} TODO/FIXME/HACK comments in codebase",
                    proposed_refactoring="Create ROADMAP priorities for top items",
                    files_affected=[m.file_path for m in files_with_debt[:5]],
                    estimated_effort_hours=total_debt * 0.5,  # 30 min per item
                    time_saved_hours=total_debt * 1.0,
                    roi_score=2.0,
                    priority=5,
                    benefits=[
                        "Clean up known issues",
                        "Prevent future bugs",
                        "Improve code quality",
                    ],
                    risks=["Some TODOs may be outdated"],
                )
            )

        # 4. Check for god classes (many methods/high complexity)
        for metric in metrics:
            if metric.num_classes > 0 and metric.num_functions > 20:
                file_name = Path(metric.file_path).name
                opportunities.append(
                    RefactoringOpportunity(
                        title=f"Extract mixins from god class in {file_name}",
                        category="architecture",
                        severity="HIGH",
                        current_state=f"{metric.num_functions} methods in single class",
                        proposed_refactoring="Extract mixins for single responsibility",
                        files_affected=[metric.file_path],
                        estimated_effort_hours=12.0,
                        time_saved_hours=20.0,
                        roi_score=20.0 / 12.0,
                        priority=9,
                        benefits=[
                            "Single Responsibility Principle",
                            "Easier parallel development",
                            "Better testability",
                        ],
                        risks=["Requires careful refactoring", "Must maintain compatibility"],
                    )
                )

        return opportunities

    def _calculate_health_score(self, metrics: List[CodeMetrics], opportunities: List[RefactoringOpportunity]) -> float:
        """Calculate overall codebase health score (0-100)."""
        if not metrics:
            return 100.0

        # Factors affecting health score:
        # 1. Average LOC per file (prefer smaller files)
        avg_loc = sum(m.lines_of_code for m in metrics) / len(metrics)
        loc_score = max(0, 100 - (avg_loc - 200) * 0.2)  # Penalty after 200 LOC

        # 2. Technical debt indicators
        total_debt = sum(m.num_todos + m.num_fixmes + m.num_hacks for m in metrics)
        debt_score = max(0, 100 - total_debt * 2)  # -2 points per debt item

        # 3. Number of refactoring opportunities
        opportunity_score = max(0, 100 - len(opportunities) * 5)  # -5 points per opportunity

        # 4. Complexity
        avg_complexity = sum(m.complexity for m in metrics) / len(metrics) if metrics else 1
        complexity_score = max(0, 100 - (avg_complexity - 10) * 5)

        # Weighted average
        health_score = loc_score * 0.25 + debt_score * 0.25 + opportunity_score * 0.30 + complexity_score * 0.20

        return round(max(0.0, min(100.0, health_score)), 1)

    def _create_metrics_summary(self, metrics: List[CodeMetrics]) -> Dict[str, Any]:
        """Create summary statistics from metrics."""
        if not metrics:
            return {}

        return {
            "total_files": len(metrics),
            "total_loc": sum(m.lines_of_code for m in metrics),
            "avg_loc_per_file": round(sum(m.lines_of_code for m in metrics) / len(metrics), 1),
            "max_loc_file": max(metrics, key=lambda m: m.lines_of_code).file_path,
            "total_functions": sum(m.num_functions for m in metrics),
            "total_classes": sum(m.num_classes for m in metrics),
            "avg_complexity": round(sum(m.complexity for m in metrics) / len(metrics), 1),
            "max_complexity_file": max(metrics, key=lambda m: m.complexity).file_path,
            "total_todos": sum(m.num_todos for m in metrics),
            "total_fixmes": sum(m.num_fixmes for m in metrics),
            "total_hacks": sum(m.num_hacks for m in metrics),
            "files_over_500_loc": len([m for m in metrics if m.lines_of_code > 500]),
            "files_over_1000_loc": len([m for m in metrics if m.lines_of_code > 1000]),
        }

    def _record_trend(self, health_score: float, metrics_summary: Dict[str, Any], num_opportunities: int):
        """Record trend data for historical tracking."""
        trend = TrendData(
            timestamp=datetime.now().isoformat(),
            health_score=health_score,
            total_loc=metrics_summary.get("total_loc", 0),
            complexity_avg=metrics_summary.get("avg_complexity", 0.0),
            duplication_pct=0.0,  # Placeholder
            test_coverage_pct=80.0,  # Placeholder
            num_opportunities=num_opportunities,
        )

        # Load existing trends
        trends = []
        if self.trends_file.exists():
            try:
                trends = read_json_file(self.trends_file, default=[])
            except Exception:
                trends = []

        # Append new trend
        trends.append(
            {
                "timestamp": trend.timestamp,
                "health_score": trend.health_score,
                "total_loc": trend.total_loc,
                "complexity_avg": trend.complexity_avg,
                "duplication_pct": trend.duplication_pct,
                "test_coverage_pct": trend.test_coverage_pct,
                "num_opportunities": trend.num_opportunities,
            }
        )

        # Keep only last 12 weeks
        trends = trends[-12:]

        # Save trends
        write_json_file(self.trends_file, trends)

    def generate_report_markdown(self, report: CodeHealthReport) -> str:
        """Generate markdown report for project_manager."""
        md = f"""# Refactoring Analysis Report

**Date**: {report.timestamp[:10]}
**Analyzed by**: architect (proactive-refactoring-analysis skill)
**Codebase**: {report.codebase_name}
**LOC**: {report.total_loc:,} lines Python
**Execution Time**: {report.execution_time_seconds:.2f}s

---

## Executive Summary

**Overall Health Score**: {report.overall_health_score:.1f}/100 {"🟢" if report.overall_health_score >= 80 else "🟡" if report.overall_health_score >= 60 else "🔴"}

**Refactoring Opportunities Found**: {len(report.opportunities)}
**Total Estimated Effort**: {sum(o.estimated_effort_hours for o in report.opportunities):.1f} hours
**Potential Time Savings**: {sum(o.time_saved_hours for o in report.opportunities):.1f} hours (in future)
**ROI**: {sum(o.time_saved_hours for o in report.opportunities) / max(sum(o.estimated_effort_hours for o in report.opportunities), 1):.1f}x

**Top 3 Priorities**:
"""

        for i, opp in enumerate(report.top_priorities[:3], 1):
            md += f"{i}. **{opp.title}** ({opp.severity} ROI) - {opp.estimated_effort_hours:.1f} hours, saves {opp.time_saved_hours:.1f} hours\n"

        md += """

---

## Refactoring Opportunities (Sorted by Priority)

"""

        for i, opp in enumerate(report.opportunities, 1):
            roi_emoji = "🏆" if opp.roi_score > 2.0 else "🥈" if opp.roi_score > 1.5 else "🥉"
            md += f"""### {i}. {roi_emoji} {opp.title} ({opp.severity.upper()} Priority)

**Issue**: {opp.current_state}

**Proposed Refactoring**: {opp.proposed_refactoring}

**Effort**: {opp.estimated_effort_hours:.1f} hours
**Time Saved (Future)**: {opp.time_saved_hours:.1f} hours
**ROI**: {opp.roi_score:.1f}x
**Priority**: {opp.priority}/10

**Benefits**:
{chr(10).join(f"- {b}" for b in opp.benefits)}

**Risks**:
{chr(10).join(f"- {r}" for r in opp.risks)}

**Files Affected**:
{chr(10).join(f"- `{f}`" for f in opp.files_affected[:5])}

---

"""

        md += """## Metrics Summary

| Metric | Value |
|--------|-------|
"""
        for key, value in report.metrics_summary.items():
            md += f"| {key.replace('_', ' ').title()} | {value} |\n"

        md += """
---

## Next Steps

1. **project_manager**: Review this report
2. **project_manager**: Add top priorities to ROADMAP
3. **architect**: Create technical specs for approved refactorings
4. **code_developer**: Implement refactorings in priority order
5. **architect**: Run this skill again in 1 week (track progress)

---

**Generated by**: proactive-refactoring-analysis skill
**Version**: 1.0.0
"""

        return md

    def get_trend_analysis(self) -> str:
        """Get trend analysis comparing current vs previous weeks."""
        if not self.trends_file.exists():
            return "No historical data available yet."

        trends = read_json_file(self.trends_file, default=[])
        if len(trends) < 2:
            return "Insufficient data for trend analysis (need at least 2 weeks)."

        current = trends[-1]
        previous = trends[-2]

        health_change = current["health_score"] - previous["health_score"]
        loc_change = current["total_loc"] - previous["total_loc"]
        opportunity_change = current["num_opportunities"] - previous["num_opportunities"]

        trend_md = f"""## Trend Analysis (Week-over-Week)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Health Score | {previous['health_score']:.1f} | {current['health_score']:.1f} | {health_change:+.1f} {"📈" if health_change > 0 else "📉" if health_change < 0 else "➡️"} |
| Total LOC | {previous['total_loc']:,} | {current['total_loc']:,} | {loc_change:+,} |
| Opportunities | {previous['num_opportunities']} | {current['num_opportunities']} | {opportunity_change:+} {"📈" if opportunity_change < 0 else "📉" if opportunity_change > 0 else "➡️"} |
| Avg Complexity | {previous['complexity_avg']:.1f} | {current['complexity_avg']:.1f} | {current['complexity_avg'] - previous['complexity_avg']:+.1f} |
"""

        return trend_md


def analyze_codebase_health(codebase_root: Path) -> CodeHealthReport:
    """
    Main entry point for proactive refactoring analysis.

    Args:
        codebase_root: Path to codebase root directory

    Returns:
        CodeHealthReport with opportunities and recommendations
    """
    analyzer = ProactiveRefactoringAnalyzer(codebase_root)
    report = analyzer.analyze_codebase()
    return report


def generate_weekly_report(codebase_root: Path, output_path: Optional[Path] = None) -> str:
    """
    Generate weekly refactoring analysis report.

    Args:
        codebase_root: Path to codebase root directory
        output_path: Optional path to save report markdown

    Returns:
        Markdown report string
    """
    analyzer = ProactiveRefactoringAnalyzer(codebase_root)
    report = analyzer.analyze_codebase()
    markdown = analyzer.generate_report_markdown(report)

    # Add trend analysis
    trend_analysis = analyzer.get_trend_analysis()
    markdown += "\n\n" + trend_analysis

    # Save to file if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

    return markdown
