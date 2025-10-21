"""Proactive Refactoring Analysis Skill.

This module provides comprehensive code health analysis and refactoring recommendations.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from radon.complexity import cc_visit
from radon.metrics import mi_visit


class CodeComplexityAnalyzer:
    """Analyzes code complexity metrics."""

    def __init__(self, codebase_path: Path):
        """Initialize analyzer.

        Args:
            codebase_path: Root path of the codebase to analyze
        """
        self.codebase_path = codebase_path

    def analyze(self) -> Dict[str, any]:
        """Analyze code complexity across the codebase.

        Returns:
            Dictionary with complexity metrics:
            - files_over_500_loc: List of files with >500 lines
            - files_over_1000_loc: List of files with >1000 lines
            - complex_functions: List of functions with cyclomatic complexity >10
            - average_complexity: Average cyclomatic complexity
            - maintainability_index: Average maintainability index
        """
        metrics = {
            "files_over_500_loc": [],
            "files_over_1000_loc": [],
            "complex_functions": [],
            "average_complexity": 0.0,
            "maintainability_index": 0.0,
        }

        python_files = list(self.codebase_path.rglob("*.py"))
        if not python_files:
            return metrics

        total_complexity = 0
        total_mi = 0
        function_count = 0

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Analyze file size
                loc = len(content.splitlines())
                if loc > 1000:
                    metrics["files_over_1000_loc"].append({"file": str(py_file), "loc": loc})
                elif loc > 500:
                    metrics["files_over_500_loc"].append({"file": str(py_file), "loc": loc})

                # Analyze complexity
                cc_results = cc_visit(content)
                for result in cc_results:
                    total_complexity += result.complexity
                    function_count += 1

                    if result.complexity > 10:
                        metrics["complex_functions"].append(
                            {
                                "file": str(py_file),
                                "function": result.name,
                                "complexity": result.complexity,
                                "line": result.lineno,
                            }
                        )

                # Maintainability index
                mi_results = mi_visit(content, multi=True)
                if mi_results:
                    total_mi += mi_results

            except (SyntaxError, UnicodeDecodeError, Exception):
                # Skip files that can't be parsed
                continue

        # Calculate averages
        if function_count > 0:
            metrics["average_complexity"] = round(total_complexity / function_count, 2)
        if python_files:
            metrics["maintainability_index"] = round(total_mi / len(python_files), 2)

        return metrics


class CodeDuplicationDetector:
    """Detects code duplication."""

    def __init__(self, codebase_path: Path):
        """Initialize detector.

        Args:
            codebase_path: Root path of the codebase to analyze
        """
        self.codebase_path = codebase_path

    def analyze(self) -> Dict[str, any]:
        """Detect code duplication using simple pattern matching.

        Returns:
            Dictionary with duplication metrics:
            - duplicated_blocks: List of duplicated code patterns
            - duplication_percentage: Estimated percentage of duplicated code
        """
        metrics = {"duplicated_blocks": [], "duplication_percentage": 0.0}

        # Use simple grep-based detection for common patterns
        patterns = [
            r"api_key\s*=\s*os\.getenv",
            r"if\s+not\s+.*:\s*raise",
            r"with\s+open\([^)]+\)\s+as",
        ]

        total_lines = 0
        duplicated_lines = 0

        for pattern in patterns:
            try:
                result = subprocess.run(
                    ["grep", "-r", "-n", pattern, str(self.codebase_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                matches = result.stdout.strip().split("\n") if result.stdout else []
                if len(matches) > 3:  # More than 3 instances suggests duplication
                    metrics["duplicated_blocks"].append(
                        {"pattern": pattern, "count": len(matches), "instances": matches[:5]}
                    )
                    duplicated_lines += len(matches) * 3  # Estimate 3 lines per match

            except (subprocess.TimeoutExpired, Exception):
                continue

        # Count total lines
        for py_file in self.codebase_path.rglob("*.py"):
            try:
                total_lines += len(py_file.read_text(encoding="utf-8").splitlines())
            except (UnicodeDecodeError, Exception):
                continue

        if total_lines > 0:
            metrics["duplication_percentage"] = round((duplicated_lines / total_lines) * 100, 2)

        return metrics


class TestCoverageAnalyzer:
    """Analyzes test coverage."""

    def __init__(self, codebase_path: Path):
        """Initialize analyzer.

        Args:
            codebase_path: Root path of the codebase to analyze
        """
        self.codebase_path = codebase_path

    def analyze(self) -> Dict[str, any]:
        """Analyze test coverage using pytest-cov.

        Returns:
            Dictionary with coverage metrics:
            - overall_coverage: Overall coverage percentage
            - files_under_80: List of files with <80% coverage
            - untested_files: List of files with no tests
        """
        metrics = {
            "overall_coverage": 0.0,
            "files_under_80": [],
            "untested_files": [],
        }

        try:
            # Run pytest with coverage
            result = subprocess.run(
                ["pytest", "--cov=coffee_maker", "--cov-report=json", "--cov-report=term-missing", "-q"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                cwd=str(self.codebase_path),
            )

            # Parse coverage.json
            coverage_file = self.codebase_path / ".coverage.json"
            if coverage_file.exists():
                coverage_data = json.loads(coverage_file.read_text())
                metrics["overall_coverage"] = coverage_data.get("totals", {}).get("percent_covered", 0.0)

                # Find files under 80%
                for file_path, file_data in coverage_data.get("files", {}).items():
                    coverage_pct = file_data.get("summary", {}).get("percent_covered", 0.0)
                    if coverage_pct < 80:
                        metrics["files_under_80"].append({"file": file_path, "coverage": coverage_pct})
                    if coverage_pct == 0:
                        metrics["untested_files"].append(file_path)

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, Exception):
            # If pytest fails, return empty metrics
            pass

        return metrics


class DependencyAnalyzer:
    """Analyzes project dependencies."""

    def __init__(self, codebase_path: Path):
        """Initialize analyzer.

        Args:
            codebase_path: Root path of the codebase to analyze
        """
        self.codebase_path = codebase_path

    def analyze(self) -> Dict[str, any]:
        """Analyze dependencies for issues.

        Returns:
            Dictionary with dependency metrics:
            - unused_dependencies: List of installed but unused dependencies
            - outdated_dependencies: List of outdated dependencies
            - circular_dependencies: List of circular import issues
        """
        metrics = {
            "unused_dependencies": [],
            "outdated_dependencies": [],
            "circular_dependencies": [],
        }

        # Check for unused imports
        try:
            result = subprocess.run(
                ["autoflake", "--check", "--remove-all-unused-imports", "-r", "coffee_maker/"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.codebase_path),
            )

            # Parse output for unused imports
            if result.stdout:
                for line in result.stdout.splitlines():
                    if "import" in line.lower():
                        metrics["unused_dependencies"].append(line.strip())

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Check for outdated dependencies
        try:
            result = subprocess.run(
                ["poetry", "show", "--outdated"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.codebase_path),
            )

            # Parse output
            if result.stdout:
                for line in result.stdout.splitlines()[2:]:  # Skip header lines
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            metrics["outdated_dependencies"].append(
                                {
                                    "package": parts[0],
                                    "current": parts[1],
                                    "latest": parts[2],
                                }
                            )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        return metrics


class ROICalculator:
    """Calculates ROI for refactoring opportunities."""

    def calculate_roi(self, effort_hours: float, time_saved_hours: float) -> Dict[str, any]:
        """Calculate ROI for a refactoring.

        Args:
            effort_hours: Estimated effort in hours
            time_saved_hours: Estimated time saved in future in hours

        Returns:
            Dictionary with ROI metrics:
            - roi_percentage: ROI as percentage
            - roi_category: HIGH/MEDIUM/LOW
            - break_even_months: Months to break even
        """
        if effort_hours <= 0:
            return {"roi_percentage": 0, "roi_category": "UNKNOWN", "break_even_months": 0}

        roi_percentage = ((time_saved_hours - effort_hours) / effort_hours) * 100

        # Categorize ROI
        if roi_percentage >= 200:
            roi_category = "VERY HIGH"
        elif roi_percentage >= 100:
            roi_category = "HIGH"
        elif roi_percentage >= 50:
            roi_category = "MEDIUM"
        else:
            roi_category = "LOW"

        # Calculate break-even (assuming monthly usage)
        break_even_months = round(effort_hours / max(time_saved_hours, 0.1), 1)

        return {
            "roi_percentage": round(roi_percentage, 1),
            "roi_category": roi_category,
            "break_even_months": break_even_months,
        }


class WeeklyReportGenerator:
    """Generates weekly refactoring analysis reports."""

    def __init__(self, codebase_path: Path):
        """Initialize generator.

        Args:
            codebase_path: Root path of the codebase to analyze
        """
        self.codebase_path = codebase_path
        self.complexity_analyzer = CodeComplexityAnalyzer(codebase_path)
        self.duplication_detector = CodeDuplicationDetector(codebase_path)
        self.coverage_analyzer = TestCoverageAnalyzer(codebase_path)
        self.dependency_analyzer = DependencyAnalyzer(codebase_path)
        self.roi_calculator = ROICalculator()

    def generate_report(self) -> str:
        """Generate comprehensive refactoring analysis report.

        Returns:
            Markdown-formatted report
        """
        # Collect all metrics
        complexity_metrics = self.complexity_analyzer.analyze()
        duplication_metrics = self.duplication_detector.analyze()
        coverage_metrics = self.coverage_analyzer.analyze()
        dependency_metrics = self.dependency_analyzer.analyze()

        # Generate recommendations
        recommendations = self._generate_recommendations(
            complexity_metrics, duplication_metrics, coverage_metrics, dependency_metrics
        )

        # Format report
        report = self._format_report(
            complexity_metrics,
            duplication_metrics,
            coverage_metrics,
            dependency_metrics,
            recommendations,
        )

        return report

    def _generate_recommendations(
        self,
        complexity_metrics: Dict,
        duplication_metrics: Dict,
        coverage_metrics: Dict,
        dependency_metrics: Dict,
    ) -> List[Dict]:
        """Generate top refactoring recommendations with ROI.

        Returns:
            List of recommendations sorted by ROI
        """
        recommendations = []

        # Recommendation 1: Split large files
        if complexity_metrics["files_over_1000_loc"]:
            for file_data in complexity_metrics["files_over_1000_loc"][:3]:
                effort = 10  # 10 hours to split large file
                time_saved = 20  # 20 hours saved in future
                roi = self.roi_calculator.calculate_roi(effort, time_saved)

                recommendations.append(
                    {
                        "title": f"Split large file: {Path(file_data['file']).name}",
                        "issue": f"File has {file_data['loc']} lines (critical)",
                        "effort_hours": effort,
                        "time_saved_hours": time_saved,
                        "roi": roi,
                        "priority": "HIGH",
                    }
                )

        # Recommendation 2: Reduce function complexity
        if complexity_metrics["complex_functions"]:
            func_data = complexity_metrics["complex_functions"][0]
            effort = 2
            time_saved = 5
            roi = self.roi_calculator.calculate_roi(effort, time_saved)

            recommendations.append(
                {
                    "title": f"Refactor complex function: {func_data['function']}",
                    "issue": f"Cyclomatic complexity {func_data['complexity']} (threshold: 10)",
                    "effort_hours": effort,
                    "time_saved_hours": time_saved,
                    "roi": roi,
                    "priority": "MEDIUM",
                }
            )

        # Recommendation 3: Extract duplicated code
        if duplication_metrics["duplicated_blocks"]:
            block = duplication_metrics["duplicated_blocks"][0]
            effort = 3
            time_saved = 15
            roi = self.roi_calculator.calculate_roi(effort, time_saved)

            recommendations.append(
                {
                    "title": f"Extract duplicated pattern",
                    "issue": f"Pattern '{block['pattern']}' duplicated {block['count']} times",
                    "effort_hours": effort,
                    "time_saved_hours": time_saved,
                    "roi": roi,
                    "priority": "HIGH",
                }
            )

        # Recommendation 4: Improve test coverage
        if coverage_metrics["files_under_80"]:
            file_data = coverage_metrics["files_under_80"][0]
            effort = 4
            time_saved = 8
            roi = self.roi_calculator.calculate_roi(effort, time_saved)

            recommendations.append(
                {
                    "title": f"Add tests for: {Path(file_data['file']).name}",
                    "issue": f"Coverage: {file_data['coverage']:.1f}% (target: 80%)",
                    "effort_hours": effort,
                    "time_saved_hours": time_saved,
                    "roi": roi,
                    "priority": "MEDIUM",
                }
            )

        # Recommendation 5: Update dependencies
        if dependency_metrics["outdated_dependencies"]:
            dep_count = len(dependency_metrics["outdated_dependencies"])
            effort = 2
            time_saved = 4
            roi = self.roi_calculator.calculate_roi(effort, time_saved)

            recommendations.append(
                {
                    "title": f"Update {dep_count} outdated dependencies",
                    "issue": f"{dep_count} packages have newer versions",
                    "effort_hours": effort,
                    "time_saved_hours": time_saved,
                    "roi": roi,
                    "priority": "MEDIUM",
                }
            )

        # Sort by ROI
        recommendations.sort(key=lambda x: x["roi"]["roi_percentage"], reverse=True)

        return recommendations[:5]  # Top 5

    def _format_report(
        self,
        complexity_metrics: Dict,
        duplication_metrics: Dict,
        coverage_metrics: Dict,
        dependency_metrics: Dict,
        recommendations: List[Dict],
    ) -> str:
        """Format the report as Markdown."""
        report = f"""# Proactive Refactoring Analysis Report

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Generated by**: proactive-refactoring-analysis skill
**Codebase**: MonolithicCoffeeMakerAgent

---

## Executive Summary

**Code Health Score**: {self._calculate_health_score(complexity_metrics, coverage_metrics)}/100

**Key Metrics**:
- Average Complexity: {complexity_metrics['average_complexity']}
- Maintainability Index: {complexity_metrics['maintainability_index']}
- Test Coverage: {coverage_metrics['overall_coverage']:.1f}%
- Code Duplication: {duplication_metrics['duplication_percentage']:.1f}%

**Refactoring Opportunities**: {len(recommendations)}

---

## Top Recommendations (Sorted by ROI)

"""

        for i, rec in enumerate(recommendations, 1):
            report += f"""### {i}. {rec['title']} ({rec['roi']['roi_category']} ROI)

**Issue**: {rec['issue']}

**Effort**: {rec['effort_hours']} hours
**Time Saved**: {rec['time_saved_hours']} hours (future)
**ROI**: {rec['roi']['roi_percentage']:.1f}%
**Break-even**: {rec['roi']['break_even_months']} months
**Priority**: {rec['priority']}

---

"""

        # Add detailed metrics
        report += f"""## Detailed Metrics

### Code Complexity

- Files >1000 LOC: {len(complexity_metrics['files_over_1000_loc'])}
- Files >500 LOC: {len(complexity_metrics['files_over_500_loc'])}
- Complex Functions (>10): {len(complexity_metrics['complex_functions'])}
- Average Complexity: {complexity_metrics['average_complexity']}
- Maintainability Index: {complexity_metrics['maintainability_index']}

### Code Duplication

- Duplication Percentage: {duplication_metrics['duplication_percentage']:.1f}%
- Duplicated Patterns: {len(duplication_metrics['duplicated_blocks'])}

### Test Coverage

- Overall Coverage: {coverage_metrics['overall_coverage']:.1f}%
- Files <80% Coverage: {len(coverage_metrics['files_under_80'])}
- Untested Files: {len(coverage_metrics['untested_files'])}

### Dependencies

- Outdated Dependencies: {len(dependency_metrics['outdated_dependencies'])}
- Circular Dependencies: {len(dependency_metrics['circular_dependencies'])}

---

## Next Steps

1. **project_manager**: Review this report
2. **project_manager**: Add top 3-5 priorities to ROADMAP
3. **architect**: Create technical specs for approved refactorings
4. **code_developer**: Implement refactorings in priority order

---

*Report generated by proactive-refactoring-analysis skill*
"""

        return report

    def _calculate_health_score(self, complexity_metrics: Dict, coverage_metrics: Dict) -> int:
        """Calculate overall code health score (0-100).

        Args:
            complexity_metrics: Complexity analysis results
            coverage_metrics: Coverage analysis results

        Returns:
            Health score from 0-100
        """
        score = 100

        # Deduct for large files
        score -= len(complexity_metrics["files_over_1000_loc"]) * 10
        score -= len(complexity_metrics["files_over_500_loc"]) * 5

        # Deduct for complex functions
        score -= len(complexity_metrics["complex_functions"]) * 2

        # Deduct for low coverage
        if coverage_metrics["overall_coverage"] < 80:
            score -= 80 - coverage_metrics["overall_coverage"]

        return max(0, min(100, score))


class TrendTracker:
    """Tracks code health trends over time."""

    def __init__(self, codebase_path: Path):
        """Initialize tracker.

        Args:
            codebase_path: Root path of the codebase
        """
        self.codebase_path = codebase_path
        self.trends_file = codebase_path / "data" / "refactoring_trends.json"

    def record_metrics(self, metrics: Dict) -> None:
        """Record metrics for trend analysis.

        Args:
            metrics: Current metrics to record
        """
        # Load existing trends
        trends = self._load_trends()

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }

        trends.append(entry)

        # Keep only last 12 weeks
        trends = trends[-12:]

        # Save trends
        self._save_trends(trends)

    def get_trends(self) -> Dict[str, List]:
        """Get historical trends.

        Returns:
            Dictionary with trend data for each metric
        """
        trends = self._load_trends()

        if not trends:
            return {}

        # Extract time series for each metric
        return {
            "timestamps": [entry["timestamp"] for entry in trends],
            "health_scores": [entry["metrics"].get("health_score", 0) for entry in trends],
            "coverage": [entry["metrics"].get("coverage", 0) for entry in trends],
            "complexity": [entry["metrics"].get("complexity", 0) for entry in trends],
        }

    def _load_trends(self) -> List[Dict]:
        """Load trends from file."""
        if not self.trends_file.exists():
            return []

        try:
            return json.loads(self.trends_file.read_text())
        except (json.JSONDecodeError, Exception):
            return []

    def _save_trends(self, trends: List[Dict]) -> None:
        """Save trends to file."""
        self.trends_file.parent.mkdir(parents=True, exist_ok=True)
        self.trends_file.write_text(json.dumps(trends, indent=2))


def main(codebase_path: Optional[Path] = None) -> str:
    """Main entry point for proactive refactoring analysis.

    Args:
        codebase_path: Path to codebase (defaults to current directory)

    Returns:
        Generated report as markdown string
    """
    if codebase_path is None:
        codebase_path = Path.cwd()

    # Generate report
    generator = WeeklyReportGenerator(codebase_path)
    report = generator.generate_report()

    # Save report
    report_dir = codebase_path / "evidence"
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = report_dir / f"refactoring-analysis-{timestamp}.md"
    report_file.write_text(report)

    print(f"Report generated: {report_file}")

    return report


if __name__ == "__main__":
    main()
