"""
Skill Loader: Unified API for accessing all code analysis skills

This module provides functions to instantiate and use skills throughout the codebase.

Usage:
    from coffee_maker.skills import functional_search, code_forensics, security_audit

    # Search code by functional area
    results = functional_search("authentication")

    # Find code patterns
    patterns = code_forensics("find_patterns", {"pattern": "error_handling"})

    # Run security audit
    issues = security_audit("check_vulnerabilities")

Skills available:
- functional_search: Find code by feature/function using 3-level index
- code_forensics: Pattern analysis, complexity, duplication detection
- security_audit: Vulnerability scanning, dependency analysis
- dependency_tracer: Trace dependencies, impact analysis
- code_explainer: Explain code functionality

All skills are initialized with codebase_root (defaults to current directory).
"""

from pathlib import Path
from typing import Any, Dict

from coffee_maker.skills.code_analysis.code_explainer import CodeExplainer
from coffee_maker.skills.code_analysis.code_forensics import CodeForensics
from coffee_maker.skills.code_analysis.dependency_tracer import DependencyTracer
from coffee_maker.skills.code_analysis.functional_search import FunctionalSearch
from coffee_maker.skills.code_analysis.security_audit import SecurityAudit
from coffee_maker.skills.code_analysis.test_failure_analyzer import TestFailureAnalyzerSkill
from coffee_maker.skills.dod_verification.criteria_parser import CriteriaParser
from coffee_maker.skills.dod_verification.automated_checks import AutomatedChecks
from coffee_maker.skills.dod_verification.code_quality_checker import CodeQualityChecker
from coffee_maker.skills.dod_verification.functionality_tester import FunctionalityTester
from coffee_maker.skills.dod_verification.documentation_checker import DocumentationChecker
from coffee_maker.skills.dod_verification.integration_verifier import IntegrationVerifier
from coffee_maker.skills.dod_verification.report_generator import ReportGenerator
from coffee_maker.utils.code_index.indexer import CodeIndexer
from coffee_maker.utils.code_index.query_engine import CodeIndexQueryEngine


class SkillLoader:
    """Unified loader for code analysis skills."""

    # Global instances (lazy-loaded)
    _forensics = None
    _security = None
    _tracer = None
    _search = None
    _explainer = None
    _test_failure_analyzer = None
    _dod_verifier = None
    _indexer = None
    _query_engine = None

    @classmethod
    def get_forensics(cls, codebase_root: str = None) -> CodeForensics:
        """Get code forensics skill instance."""
        if cls._forensics is None or (codebase_root and str(cls._forensics.codebase_root) != codebase_root):
            cls._forensics = CodeForensics(codebase_root)
        return cls._forensics

    @classmethod
    def get_security_audit(cls, codebase_root: str = None) -> SecurityAudit:
        """Get security audit skill instance."""
        if cls._security is None or (codebase_root and str(cls._security.codebase_root) != codebase_root):
            cls._security = SecurityAudit(codebase_root)
        return cls._security

    @classmethod
    def get_dependency_tracer(cls, codebase_root: str = None) -> DependencyTracer:
        """Get dependency tracer skill instance."""
        if cls._tracer is None or (codebase_root and str(cls._tracer.codebase_root) != codebase_root):
            cls._tracer = DependencyTracer(codebase_root)
        return cls._tracer

    @classmethod
    def get_functional_search(
        cls, codebase_root: str = None, query_engine: CodeIndexQueryEngine = None
    ) -> FunctionalSearch:
        """Get functional search skill instance."""
        if query_engine is None and cls._query_engine is None:
            index_path = Path(codebase_root or Path.cwd()) / "data" / "code_index" / "index.json"
            cls._query_engine = CodeIndexQueryEngine(str(index_path))

        engine = query_engine or cls._query_engine

        if cls._search is None:
            cls._search = FunctionalSearch(engine)

        return cls._search

    @classmethod
    def get_code_explainer(cls, codebase_root: str = None) -> CodeExplainer:
        """Get code explainer skill instance."""
        if cls._explainer is None or (codebase_root and str(cls._explainer.codebase_root) != codebase_root):
            cls._explainer = CodeExplainer(codebase_root)
        return cls._explainer

    @classmethod
    def get_test_failure_analyzer(cls, codebase_root: str = None) -> TestFailureAnalyzerSkill:
        """Get test failure analyzer skill instance."""
        if cls._test_failure_analyzer is None or (
            codebase_root and str(cls._test_failure_analyzer.codebase_root) != codebase_root
        ):
            cls._test_failure_analyzer = TestFailureAnalyzerSkill(codebase_root)
        return cls._test_failure_analyzer

    @classmethod
    def get_dod_verifier(cls, codebase_root: str = None) -> Dict[str, Any]:
        """
        Get DoD verifier components.

        Returns a dictionary of DoD verification components.
        """
        from pathlib import Path

        root = Path(codebase_root or Path.cwd())

        return {
            "criteria_parser": CriteriaParser(),
            "automated_checks": AutomatedChecks(root),
            "code_quality": CodeQualityChecker(root),
            "functionality_tester": FunctionalityTester(root),
            "documentation_checker": DocumentationChecker(root),
            "integration_verifier": IntegrationVerifier(root),
            "report_generator": ReportGenerator(),
        }

    @classmethod
    def get_indexer(cls, codebase_root: str = None) -> CodeIndexer:
        """Get code indexer instance."""
        if cls._indexer is None or (codebase_root and str(cls._indexer.codebase_root) != codebase_root):
            cls._indexer = CodeIndexer(codebase_root)
        return cls._indexer

    @classmethod
    def rebuild_index(cls, codebase_root: str = None) -> Dict[str, Any]:
        """
        Rebuild the code index (should be run after git commits).

        Returns:
            Status of index rebuild
        """
        indexer = cls.get_indexer(codebase_root)
        indexer.rebuild_index()
        indexer.save_index()

        return {
            "status": "success",
            "message": "Code index rebuilt",
            "index_path": str(indexer.index_path),
            "categories": len(indexer.index.get("categories", {})),
        }

    @classmethod
    def reset_cache(cls) -> None:
        """Reset all cached skill instances."""
        cls._forensics = None
        cls._security = None
        cls._tracer = None
        cls._search = None
        cls._explainer = None
        cls._test_failure_analyzer = None
        cls._dod_verifier = None
        cls._indexer = None
        cls._query_engine = None


# Convenience functions for direct skill access
def functional_search(query: str, codebase_root: str = None) -> Dict[str, Any]:
    """
    Search code by functional area.

    Args:
        query: Search query (e.g., "authentication", "payment")
        codebase_root: Optional codebase root (defaults to current dir)

    Returns:
        Search results with hierarchical code locations
    """
    skill = SkillLoader.get_functional_search(codebase_root)
    return skill.search(query)


def code_forensics(operation: str, params: Dict[str, Any] = None, codebase_root: str = None) -> Dict[str, Any]:
    """
    Run code forensics analysis.

    Args:
        operation: Operation to perform:
            - "find_patterns": Find code patterns (e.g., error_handling)
            - "analyze_complexity": Measure code complexity
            - "identify_duplication": Find duplicate code
            - "architectural_analysis": Analyze component structure
        params: Parameters for operation (e.g., {"pattern": "caching"})
        codebase_root: Optional codebase root

    Returns:
        Analysis results
    """
    skill = SkillLoader.get_forensics(codebase_root)
    params = params or {}

    if operation == "find_patterns":
        return skill.find_patterns(params.get("pattern"))
    elif operation == "analyze_complexity":
        return skill.analyze_complexity(params.get("file_path"))
    elif operation == "identify_duplication":
        return skill.identify_duplication()
    elif operation == "architectural_analysis":
        return skill.architectural_analysis()
    else:
        return {"error": f"Unknown operation: {operation}"}


def security_audit(operation: str = "check_vulnerabilities", codebase_root: str = None) -> Dict[str, Any]:
    """
    Run security audit.

    Args:
        operation: Operation to perform:
            - "check_vulnerabilities": Scan for security vulnerabilities
            - "analyze_dependencies": Analyze third-party dependencies
            - "find_security_patterns": Find security-related patterns
            - "generate_report": Generate comprehensive security report
        codebase_root: Optional codebase root

    Returns:
        Security audit results
    """
    skill = SkillLoader.get_security_audit(codebase_root)

    if operation == "check_vulnerabilities":
        return skill.check_vulnerabilities()
    elif operation == "analyze_dependencies":
        return skill.analyze_dependencies()
    elif operation == "find_security_patterns":
        return skill.find_security_patterns()
    elif operation == "generate_report":
        return skill.generate_security_report()
    else:
        return {"error": f"Unknown operation: {operation}"}


def dependency_tracer(operation: str, params: Dict[str, Any] = None, codebase_root: str = None) -> Dict[str, Any]:
    """
    Trace and analyze dependencies.

    Args:
        operation: Operation to perform:
            - "trace_imports": Find all imports in a file
            - "find_dependents": Find files that import a module
            - "impact_analysis": Analyze impact of changes
            - "circular_dependencies": Find circular imports
            - "dependency_graph": Get complete dependency graph
        params: Parameters for operation (e.g., {"file_path": "..."})
        codebase_root: Optional codebase root

    Returns:
        Dependency analysis results
    """
    skill = SkillLoader.get_dependency_tracer(codebase_root)
    params = params or {}

    if operation == "trace_imports":
        return skill.trace_imports(params.get("file_path", ""))
    elif operation == "find_dependents":
        return skill.find_dependents(
            params.get("module_path", ""),
            internal_only=params.get("internal_only", True),
        )
    elif operation == "impact_analysis":
        return skill.impact_analysis(params.get("file_path", ""))
    elif operation == "circular_dependencies":
        return skill.circular_dependencies()
    elif operation == "dependency_graph":
        return skill.dependency_graph()
    else:
        return {"error": f"Unknown operation: {operation}"}


def code_explainer(operation: str, params: Dict[str, Any] = None, codebase_root: str = None) -> Dict[str, Any]:
    """
    Explain code functionality.

    Args:
        operation: Operation to perform:
            - "explain_file": Summarize a file
            - "explain_function": Explain a function
            - "explain_class": Explain a class
            - "explain_pattern": Explain a code pattern
        params: Parameters for operation (e.g., {"file_path": "...", "function_name": "..."})
        codebase_root: Optional codebase root

    Returns:
        Code explanation
    """
    skill = SkillLoader.get_code_explainer(codebase_root)
    params = params or {}

    if operation == "explain_file":
        return skill.explain_file(params.get("file_path", ""))
    elif operation == "explain_function":
        return skill.explain_function(params.get("file_path", ""), params.get("function_name", ""))
    elif operation == "explain_class":
        return skill.explain_class(params.get("file_path", ""), params.get("class_name", ""))
    elif operation == "explain_pattern":
        return skill.explain_pattern(params.get("pattern_name", ""))
    else:
        return {"error": f"Unknown operation: {operation}"}


def test_failure_analysis(
    test_output: str,
    files_changed: list = None,
    priority_name: str = None,
    codebase_root: str = None,
) -> Dict[str, Any]:
    """
    Analyze pytest test failures and suggest fixes.

    Args:
        test_output: Full pytest output (stdout + stderr)
        files_changed: List of files changed in current implementation
        priority_name: Current priority being implemented
        codebase_root: Optional codebase root

    Returns:
        Analysis results with failures and fix recommendations
    """
    skill = SkillLoader.get_test_failure_analyzer(codebase_root)
    result = skill.analyze(test_output, files_changed or [], priority_name)

    # Convert to dict for JSON serialization
    return {
        "total_failures": result.total_failures,
        "critical_failures": result.critical_failures,
        "high_failures": result.high_failures,
        "medium_failures": result.medium_failures,
        "low_failures": result.low_failures,
        "estimated_total_time_min": result.estimated_total_time_min,
        "recommended_fix_order": result.recommended_fix_order,
        "failures": [
            {
                "test_name": f.test_name,
                "file": f.file,
                "line": f.line,
                "error_type": f.error_type,
                "message": f.message,
                "category": f.category.value,
                "correlation": f.correlation,
                "priority": f.priority,
            }
            for f in result.failures
        ],
        "recommendations": [
            {
                "test_name": r.failure.test_name,
                "root_cause": r.root_cause,
                "quick_fix": r.quick_fix,
                "quick_fix_time_min": r.quick_fix_time_min,
                "deep_fix": r.deep_fix,
                "deep_fix_time_min": r.deep_fix_time_min,
            }
            for r in result.recommendations
        ],
        "report": skill.format_analysis_report(result, priority_name),
    }


def dod_verification(
    priority: str,
    description: str,
    files_changed: list = None,
    check_types: list = None,
    app_url: str = None,
    codebase_root: str = None,
) -> Dict[str, Any]:
    """
    Verify Definition of Done for a priority.

    Args:
        priority: Priority identifier (e.g., "US-066")
        description: Full priority description with acceptance criteria
        files_changed: List of files changed in implementation
        check_types: Types of checks to run (default: ["all"])
        app_url: Application URL for Puppeteer testing
        codebase_root: Optional codebase root

    Returns:
        DoD verification results with status and report
    """
    from pathlib import Path

    Path(codebase_root or Path.cwd())
    files_changed = files_changed or []
    check_types = check_types or ["all"]

    # Get DoD verifier components
    components = SkillLoader.get_dod_verifier(codebase_root)

    # Parse criteria
    criteria = components["criteria_parser"].parse_criteria(description)

    # Run checks
    results = {"priority": priority, "criteria": len(criteria), "checks": {}}

    if "all" in check_types or "automated" in check_types:
        results["checks"]["automated"] = components["automated_checks"].run_all_checks()

    if "all" in check_types or "code_quality" in check_types:
        results["checks"]["code_quality"] = components["code_quality"].check_quality(files_changed)

    if "all" in check_types or "functionality" in check_types:
        results["checks"]["functionality"] = components["functionality_tester"].test_criteria(criteria, app_url)

    if "all" in check_types or "documentation" in check_types:
        results["checks"]["documentation"] = components["documentation_checker"].check_documentation(files_changed)

    if "all" in check_types or "integration" in check_types:
        results["checks"]["integration"] = components["integration_verifier"].verify_integration(files_changed)

    # Determine overall status
    all_pass = all(check.get("status") == "PASS" for check in results["checks"].values())
    results["status"] = "PASS" if all_pass else "FAIL"

    return results


def rebuild_code_index(codebase_root: str = None) -> Dict[str, Any]:
    """
    Rebuild the code index.

    Should be called:
    - After major code changes
    - Via git hooks (post-commit, post-merge)
    - Periodically via cron

    Args:
        codebase_root: Optional codebase root

    Returns:
        Status of rebuild
    """
    return SkillLoader.rebuild_index(codebase_root)
