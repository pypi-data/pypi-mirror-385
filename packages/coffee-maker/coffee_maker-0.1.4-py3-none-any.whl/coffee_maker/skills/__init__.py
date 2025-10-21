"""
Code Skills System

This module provides high-performance code analysis skills used by architect, code_developer,
and other agents for deep codebase analysis, security audits, and code exploration.

Skills replace the retired code-searcher agent with a more performant, accessible approach.
All skills use the shared Code Index infrastructure for fast, consistent results.

Key Skills:
- code_index: 3-level hierarchical codebase map (data/code_index/index.json)
- functional_search: Find all code related to a feature (e.g., "authentication")
- code_forensics: Deep pattern analysis, code complexity, architectural structure
- security_audit: Vulnerability scanning, dependency analysis, security patterns
- dependency_tracer: Dependency impact analysis for changes
- code_explainer: Summarize code functionality in accessible terms

Usage:
    from coffee_maker.skills import functional_search, code_forensics, security_audit

    # Find all authentication-related code
    results = functional_search("authentication")

    # Analyze code patterns
    patterns = code_forensics("find_patterns", {"pattern": "error_handling"})

    # Run security audit
    issues = security_audit("check_vulnerabilities")

    # Trace dependencies
    deps = dependency_tracer("trace_imports", {"file_path": "coffee_maker/auth/jwt.py"})

    # Explain code
    explanation = code_explainer("explain_file", {"file_path": "coffee_maker/auth/jwt.py"})
"""

from coffee_maker.skills.code_analysis import (
    CodeExplainer,
    CodeForensics,
    DependencyTracer,
    FunctionalSearch,
    SecurityAudit,
)
from coffee_maker.utils.code_index import CodeIndexer, CodeIndexQueryEngine
from coffee_maker.skills.analysis_loader import (
    SkillLoader as AnalysisLoader,
    code_explainer,
    code_forensics,
    dependency_tracer,
    functional_search,
    rebuild_code_index,
    security_audit,
    test_failure_analysis,
)
from coffee_maker.skills.skill_loader import (
    StartupSkillLoader,
    SkillResult,
    SkillStep,
    StartupError,
    CFR007ViolationError,
    HealthCheckError,
    ContextLoadError,
    ResourceInitializationError,
)

__all__ = [
    # Skill functions (for direct use)
    "functional_search",
    "code_forensics",
    "security_audit",
    "dependency_tracer",
    "code_explainer",
    "test_failure_analysis",
    "rebuild_code_index",
    # Skill classes (for advanced use)
    "CodeForensics",
    "SecurityAudit",
    "DependencyTracer",
    "FunctionalSearch",
    "CodeExplainer",
    "TestFailureAnalyzer",
    # Infrastructure classes
    "CodeIndexer",
    "CodeIndexQueryEngine",
    # Loader utilities
    "AnalysisLoader",
    "StartupSkillLoader",
    "SkillResult",
    "SkillStep",
    "StartupError",
    "CFR007ViolationError",
    "HealthCheckError",
    "ContextLoadError",
    "ResourceInitializationError",
]
