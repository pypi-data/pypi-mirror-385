"""
Architecture Skills Module

Provides architectural analysis and design assistance skills:
- architecture_reuse_checker: Detect pattern reuse opportunities
- proactive_refactoring_analyzer: Weekly code health and refactoring analysis
"""

from coffee_maker.skills.architecture.architecture_reuse_checker import (
    ArchitecturalComponent,
    ArchitectureReuseChecker,
    ReuseAnalysisResult,
    ReuseOpportunity,
    check_architecture_reuse,
)
from coffee_maker.skills.architecture.proactive_refactoring_analyzer import (
    CodeHealthReport,
    CodeMetrics,
    ProactiveRefactoringAnalyzer,
    RefactoringOpportunity,
    TrendData,
    analyze_codebase_health,
    generate_weekly_report,
)

__all__ = [
    "ArchitecturalComponent",
    "ArchitectureReuseChecker",
    "ReuseAnalysisResult",
    "ReuseOpportunity",
    "check_architecture_reuse",
    "CodeHealthReport",
    "CodeMetrics",
    "ProactiveRefactoringAnalyzer",
    "RefactoringOpportunity",
    "TrendData",
    "analyze_codebase_health",
    "generate_weekly_report",
]
