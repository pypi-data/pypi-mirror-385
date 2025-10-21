"""
Security Audit Skill

Vulnerability scanning, dependency analysis, and security pattern detection.

Capabilities:
- check_vulnerabilities: Scan for common security vulnerabilities
- analyze_dependencies: Analyze third-party dependencies for security issues
- find_security_patterns: Identify security-related patterns and practices

Used by: architect, code_developer (during implementation)
"""

import ast
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


class SecurityAudit:
    """Security vulnerability and pattern analysis."""

    # Common vulnerability patterns
    VULNERABILITY_PATTERNS = {
        "sql_injection": {
            "patterns": [
                r"execute\s*\(\s*f['\"]",  # f-string SQL
                r"execute\s*\(\s*\+\s*",  # String concatenation in SQL
                r"query\s*=\s*f['\"]",
            ],
            "severity": "critical",
            "description": "Potential SQL injection vulnerability",
        },
        "hardcoded_secrets": {
            "patterns": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][A-Za-z0-9]+["\']',
            ],
            "severity": "critical",
            "description": "Hardcoded credentials or secrets",
        },
        "unsafe_deserialization": {
            "patterns": [
                r"pickle\.load",
                r"yaml\.load\s*\(",
                r"json\.loads.*untrusted",
            ],
            "severity": "high",
            "description": "Unsafe deserialization of untrusted data",
        },
        "weak_crypto": {
            "patterns": [
                r"hashlib\.md5",
                r"hashlib\.sha1",
                r"random\.random",
                r"os\.urandom.*short",
            ],
            "severity": "high",
            "description": "Weak cryptographic algorithm",
        },
        "missing_validation": {
            "patterns": [
                r"request\.args\[",
                r"request\.form\[",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
            "severity": "medium",
            "description": "Missing input validation or dangerous eval usage",
        },
        "insecure_random": {
            "patterns": [
                r"random\.choice",
                r"random\.randint",
                r"random\.seed",
            ],
            "severity": "medium",
            "description": "Use of insecure random for security-sensitive operations",
        },
    }

    # Suspicious patterns that may indicate security issues
    SECURITY_PATTERNS = {
        "custom_crypto": {
            "regex": r"(def.*encrypt|def.*decrypt|def.*hash)",
            "severity": "medium",
            "description": "Custom cryptographic implementation (use standard libraries)",
        },
        "exception_suppression": {
            "regex": r"except\s*:(?:\s*pass|[\r\n]\s*pass)",
            "severity": "low",
            "description": "Bare except clause suppressing all exceptions",
        },
        "debug_mode": {
            "regex": r"(DEBUG\s*=\s*True|debug\s*=\s*True|app\.run.*debug\s*=\s*True)",
            "severity": "medium",
            "description": "Debug mode enabled in production",
        },
        "unprotected_routes": {
            "regex": r"@app\.route.*\n\s*def\s+\w+\(\):",
            "severity": "medium",
            "description": "API route without authentication/authorization check",
        },
    }

    def __init__(self, codebase_root: str = None):
        """Initialize security auditor."""
        self.codebase_root = Path(codebase_root or Path.cwd())

    def check_vulnerabilities(self) -> Dict[str, Any]:
        """
        Scan codebase for common security vulnerabilities.

        Returns:
            {
                "vulnerabilities": {
                    "critical": [...],
                    "high": [...],
                    "medium": [...],
                    "low": [...]
                },
                "summary": {
                    "total_issues": 0,
                    "by_severity": {...}
                }
            }
        """
        vulnerabilities = defaultdict(list)
        python_files = self._find_python_files()

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.split("\n")

            # Check each vulnerability pattern
            for vuln_name, vuln_info in self.VULNERABILITY_PATTERNS.items():
                for pattern in vuln_info["patterns"]:
                    try:
                        pattern_regex = re.compile(pattern, re.IGNORECASE)
                    except re.error:
                        continue

                    for line_no, line in enumerate(lines, 1):
                        if pattern_regex.search(line):
                            severity = vuln_info["severity"]
                            vulnerabilities[severity].append(
                                {
                                    "file": str(py_file.relative_to(self.codebase_root)),
                                    "line": line_no,
                                    "type": vuln_name,
                                    "description": vuln_info["description"],
                                    "snippet": line.strip()[:100],
                                }
                            )

        # Convert to regular dict with summary
        result = {"vulnerabilities": dict(vulnerabilities), "summary": {}}

        # Calculate summary
        summary_by_severity = {}
        total_issues = 0

        for severity, issues in result["vulnerabilities"].items():
            summary_by_severity[severity] = len(issues)
            total_issues += len(issues)

        result["summary"] = {
            "total_issues": total_issues,
            "by_severity": summary_by_severity,
        }

        return result

    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analyze third-party dependencies.

        Returns:
            {
                "dependencies": {
                    "PyJWT": {
                        "usage_count": 5,
                        "files": ["coffee_maker/auth/jwt.py", ...],
                        "imported_as": ["jwt", "PyJWT"],
                        "security_notes": "Ensure using latest secure version"
                    }
                }
            }
        """
        dependencies = defaultdict(
            lambda: {
                "usage_count": 0,
                "files": set(),
                "imported_as": set(),
            }
        )

        python_files = self._find_python_files()

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_name = alias.name.split(".")[0]
                        alias_name = alias.asname or alias.name
                        dependencies[dep_name]["usage_count"] += 1
                        dependencies[dep_name]["files"].add(str(py_file.relative_to(self.codebase_root)))
                        dependencies[dep_name]["imported_as"].add(alias_name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep_name = node.module.split(".")[0]
                        dependencies[dep_name]["usage_count"] += 1
                        dependencies[dep_name]["files"].add(str(py_file.relative_to(self.codebase_root)))

        # Convert sets to lists and add security notes
        result = {"dependencies": {}}

        for dep_name, dep_info in sorted(dependencies.items()):
            result["dependencies"][dep_name] = {
                "usage_count": dep_info["usage_count"],
                "files": sorted(dep_info["files"]),
                "imported_as": sorted(dep_info["imported_as"]),
                "security_notes": self._get_security_notes(dep_name),
            }

        result["summary"] = {
            "total_dependencies": len(result["dependencies"]),
            "external_only": self._count_external_deps(result["dependencies"]),
        }

        return result

    def find_security_patterns(self) -> Dict[str, Any]:
        """
        Find security-related patterns and practices.

        Returns:
            {
                "patterns": {
                    "custom_crypto": {
                        "count": 2,
                        "findings": [...]
                    }
                }
            }
        """
        results = {"patterns": {}}
        python_files = self._find_python_files()

        for pattern_name, pattern_info in self.SECURITY_PATTERNS.items():
            findings = []
            pattern_regex = re.compile(pattern_info["regex"], re.IGNORECASE | re.MULTILINE)

            for py_file in python_files:
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue

                lines = content.split("\n")

                for line_no, line in enumerate(lines, 1):
                    if pattern_regex.search(line):
                        findings.append(
                            {
                                "file": str(py_file.relative_to(self.codebase_root)),
                                "line": line_no,
                                "snippet": line.strip()[:100],
                                "severity": pattern_info["severity"],
                            }
                        )

            if findings:
                results["patterns"][pattern_name] = {
                    "count": len(findings),
                    "severity": pattern_info["severity"],
                    "description": pattern_info["description"],
                    "findings": findings[:5],  # First 5 examples
                }

        return results

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        vulns = self.check_vulnerabilities()
        deps = self.analyze_dependencies()
        patterns = self.find_security_patterns()

        return {
            "report_type": "security_audit",
            "vulnerabilities": vulns,
            "dependencies": deps,
            "patterns": patterns,
            "severity_summary": {
                "critical": sum(1 for v in vulns["vulnerabilities"].get("critical", [])),
                "high": sum(1 for v in vulns["vulnerabilities"].get("high", [])),
                "medium": sum(1 for v in vulns["vulnerabilities"].get("medium", [])),
                "low": sum(1 for v in vulns["vulnerabilities"].get("low", [])),
            },
            "recommendations": self._generate_recommendations(vulns, deps, patterns),
        }

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in codebase."""
        python_files = []
        for root, dirs, files in os.walk(self.codebase_root):
            dirs[:] = [
                d
                for d in dirs
                if d
                not in {
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "venv",
                    ".venv",
                }
            ]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return sorted(python_files)

    def _get_security_notes(self, dep_name: str) -> str:
        """Get security notes for a dependency."""
        security_notes = {
            "PyJWT": "Ensure using latest version with security patches",
            "cryptography": "Good: Using standard cryptographic library",
            "sqlalchemy": "Use parameterized queries to prevent SQL injection",
            "requests": "Ensure verifying SSL certificates",
            "flask": "Keep up to date with security patches",
            "django": "Keep up to date with security patches",
        }
        return security_notes.get(dep_name, "Review dependency for known vulnerabilities")

    def _count_external_deps(self, deps: Dict) -> int:
        """Count external (non-standard library) dependencies."""
        stdlib_mods = {
            "os",
            "sys",
            "re",
            "json",
            "ast",
            "pathlib",
            "collections",
            "defaultdict",
            "typing",
        }
        return len([d for d in deps.keys() if d not in stdlib_mods])

    def _generate_recommendations(self, vulns: Dict, deps: Dict, patterns: Dict) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        if vulns["summary"]["total_issues"] > 0:
            recommendations.append(f"Fix {vulns['summary']['total_issues']} security vulnerabilities identified")

        if vulns["vulnerabilities"].get("critical"):
            recommendations.append("URGENT: Address critical vulnerabilities before deployment")

        if patterns.get("patterns"):
            recommendations.append(f"Review {len(patterns['patterns'])} security patterns")

        recommendations.append("Keep all dependencies up to date")
        recommendations.append("Enable security scanning in CI/CD pipeline")

        return recommendations
