"""
Code Analysis Skills

6 high-performance skills for deep codebase analysis:
- code_forensics: Pattern detection, complexity analysis, duplication
- security_audit: Vulnerability scanning, dependency analysis
- dependency_tracer: Dependency relationships, impact analysis
- functional_search: Find code by functional area (uses code index)
- code_explainer: Explain code in accessible terms
- test_failure_analyzer: Analyze pytest failures and suggest fixes

All skills execute in <200ms for fast, deterministic results.
"""

from coffee_maker.skills.code_analysis.code_explainer import CodeExplainer
from coffee_maker.skills.code_analysis.code_forensics import CodeForensics
from coffee_maker.skills.code_analysis.dependency_tracer import DependencyTracer
from coffee_maker.skills.code_analysis.functional_search import FunctionalSearch
from coffee_maker.skills.code_analysis.security_audit import SecurityAudit
from coffee_maker.skills.code_analysis.test_failure_analyzer import (
    TestFailureAnalyzerSkill as TestFailureAnalyzer,
    AnalysisResult,
    TestFailure,
    FailureCategory,
    FixRecommendation,
)

__all__ = [
    "CodeForensics",
    "SecurityAudit",
    "DependencyTracer",
    "FunctionalSearch",
    "CodeExplainer",
    "TestFailureAnalyzer",
    "AnalysisResult",
    "TestFailure",
    "FailureCategory",
    "FixRecommendation",
]
