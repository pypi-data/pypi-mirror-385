"""
Code Forensics Skill

Deep pattern analysis for understanding code structure, complexity, and architectural patterns.

Capabilities:
- find_patterns: Find code patterns (e.g., error_handling, caching, validation)
- analyze_complexity: Measure code complexity metrics
- identify_duplication: Find duplicate code patterns
- architectural_analysis: Understand component relationships

Used by: architect, code_developer, assistant
"""

import ast
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


class CodeForensics:
    """Deep code pattern analysis."""

    # Pattern definitions for common code patterns
    PATTERNS = {
        "error_handling": {
            "regex": r"(try|except|raise|Exception|Error)",
            "description": "Error handling blocks",
        },
        "caching": {
            "regex": r"(@cache|redis|memcache|@lru_cache|cache\.get)",
            "description": "Caching patterns",
        },
        "validation": {
            "regex": r"(validate|validator|schema|assert|if not|raise ValueError)",
            "description": "Input validation patterns",
        },
        "logging": {
            "regex": r"(logger\.|log\.|print\(|logging\.)",
            "description": "Logging patterns",
        },
        "async": {"regex": r"(async|await|asyncio)", "description": "Async patterns"},
        "database": {
            "regex": r"(query|session|database|\.filter|\.select|\.create)",
            "description": "Database interaction patterns",
        },
        "api": {
            "regex": r"(@app\.|@router\.|@get|@post|@put|@delete|request\.)",
            "description": "API endpoint patterns",
        },
        "testing": {
            "regex": r"(def test_|@pytest|assert |mock\.|patch\()",
            "description": "Testing patterns",
        },
        "security": {
            "regex": r"(encrypt|decrypt|hash|salt|token|signature|jwt)",
            "description": "Security patterns",
        },
        "performance": {
            "regex": r"(@lru_cache|async|batch|parallel|thread|pool)",
            "description": "Performance optimization patterns",
        },
    }

    def __init__(self, codebase_root: str = None):
        """Initialize forensics analyzer."""
        self.codebase_root = Path(codebase_root or Path.cwd())

    def find_patterns(self, pattern_name: str = None) -> Dict[str, Any]:
        """
        Find code patterns across codebase.

        Args:
            pattern_name: Name of pattern (e.g., 'error_handling', 'caching')
                         If None, return all patterns

        Returns:
            {
                "patterns_found": {
                    "error_handling": {
                        "count": 156,
                        "files": ["coffee_maker/auth/jwt.py", ...],
                        "examples": [
                            {
                                "file": "coffee_maker/auth/jwt.py",
                                "line": 45,
                                "snippet": "try:\n    token = jwt.decode(...)"
                            }
                        ]
                    }
                }
            }
        """
        results = {"patterns_found": {}}

        patterns_to_search = (
            {pattern_name: self.PATTERNS[pattern_name]}
            if pattern_name and pattern_name in self.PATTERNS
            else self.PATTERNS
        )

        python_files = self._find_python_files()

        for pattern_key, pattern_info in patterns_to_search.items():
            pattern_matches = {
                "count": 0,
                "files": set(),
                "examples": [],
            }

            pattern_regex = re.compile(pattern_info["regex"], re.IGNORECASE)

            for file_path in python_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue

                lines = content.split("\n")

                for line_no, line in enumerate(lines, 1):
                    if pattern_regex.search(line):
                        pattern_matches["count"] += 1
                        pattern_matches["files"].add(str(file_path.relative_to(self.codebase_root)))

                        # Capture first few examples
                        if len(pattern_matches["examples"]) < 3:
                            snippet = "\n".join(lines[max(0, line_no - 2) : min(len(lines), line_no + 1)])
                            pattern_matches["examples"].append(
                                {
                                    "file": str(file_path.relative_to(self.codebase_root)),
                                    "line": line_no,
                                    "snippet": snippet,
                                }
                            )

            results["patterns_found"][pattern_key] = {
                "count": pattern_matches["count"],
                "files": sorted(pattern_matches["files"]),
                "examples": pattern_matches["examples"],
                "description": pattern_info["description"],
            }

        return results

    def analyze_complexity(self, file_path: str = None) -> Dict[str, Any]:
        """
        Measure code complexity metrics.

        Returns complexity for a file or entire codebase:
        - Cyclomatic complexity
        - Lines of code
        - Number of functions/classes
        - Average function length
        """
        results = {"files": {}}

        files_to_analyze = [Path(file_path)] if file_path else self._find_python_files()

        total_complexity = 0
        total_loc = 0
        total_functions = 0

        for py_file in files_to_analyze:
            if not py_file.exists():
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            # Count functions and classes
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Simple cyclomatic complexity (count branches)
            complexity = self._calculate_cyclomatic_complexity(tree)

            # Lines of code
            loc = len(content.split("\n"))

            file_metrics = {
                "loc": loc,
                "functions": len(functions),
                "classes": len(classes),
                "cyclomatic_complexity": complexity,
                "avg_function_length": (loc // len(functions) if functions else 0),
                "complexity_level": self._rate_complexity(complexity, len(functions)),
            }

            results["files"][str(py_file.relative_to(self.codebase_root))] = file_metrics

            total_complexity += complexity
            total_loc += loc
            total_functions += len(functions)

        results["summary"] = {
            "total_files": len(files_to_analyze),
            "total_loc": total_loc,
            "total_functions": total_functions,
            "avg_complexity": (total_complexity // total_functions if total_functions > 0 else 0),
            "avg_loc": total_loc // len(files_to_analyze) if files_to_analyze else 0,
        }

        return results

    def identify_duplication(self) -> Dict[str, Any]:
        """
        Find duplicate code patterns across codebase.

        Returns:
            {
                "potential_duplicates": {
                    "pattern_hash": [
                        {
                            "file": "coffee_maker/auth/jwt.py",
                            "line": 45,
                            "snippet": "..."
                        },
                        {
                            "file": "coffee_maker/auth/oauth.py",
                            "line": 67,
                            "snippet": "..."
                        }
                    ]
                }
            }
        """
        results = {"potential_duplicates": {}}

        code_snippets = defaultdict(list)
        python_files = self._find_python_files()

        # Extract function/method bodies and look for duplicates
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

            lines = content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = node.lineno - 1
                    end = (node.end_lineno or node.lineno) + 1
                    snippet = "\n".join(lines[start:end])

                    # Create a normalized hash for duplicate detection
                    normalized = self._normalize_code(snippet)
                    code_snippets[normalized].append(
                        {
                            "file": str(py_file.relative_to(self.codebase_root)),
                            "line": node.lineno,
                            "snippet": snippet[:100],  # First 100 chars
                        }
                    )

        # Only report duplicates (2+ occurrences)
        for normalized_code, occurrences in code_snippets.items():
            if len(occurrences) > 1:
                results["potential_duplicates"][hash(normalized_code)] = occurrences

        results["summary"] = {
            "total_duplicate_groups": len(results["potential_duplicates"]),
            "total_duplicated_snippets": sum(len(v) for v in results["potential_duplicates"].values()),
        }

        return results

    def architectural_analysis(self) -> Dict[str, Any]:
        """
        Analyze architectural structure and component relationships.

        Returns:
            {
                "components": {
                    "auth": {
                        "files": [...],
                        "interfaces": [...],
                        "dependencies": [...],
                        "dependents": [...]
                    }
                }
            }
        """
        results = {"components": {}}

        # Group files by directory (component)
        files_by_component = defaultdict(list)
        python_files = self._find_python_files()

        for py_file in python_files:
            rel_path = py_file.relative_to(self.codebase_root)
            parts = rel_path.parts

            # Component is the first directory in coffee_maker
            if len(parts) > 1 and parts[0] == "coffee_maker":
                component = parts[1]
                files_by_component[component].append(str(rel_path))

        # Analyze each component
        for component, files in sorted(files_by_component.items()):
            component_data = {
                "files": files,
                "functions": [],
                "classes": [],
                "imports": set(),
            }

            for file_path in files:
                full_path = self.codebase_root / file_path
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue

                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                # Extract functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        component_data["functions"].append({"name": node.name, "file": file_path})
                    elif isinstance(node, ast.ClassDef):
                        component_data["classes"].append({"name": node.name, "file": file_path})
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            component_data["imports"].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            component_data["imports"].add(node.module)

            component_data["imports"] = sorted(component_data["imports"])
            results["components"][component] = component_data

        return results

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

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity (simple version)."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _rate_complexity(self, complexity: int, func_count: int) -> str:
        """Rate complexity level."""
        if func_count == 0:
            return "unknown"

        avg_complexity = complexity / func_count
        if avg_complexity < 2:
            return "low"
        elif avg_complexity < 5:
            return "medium"
        elif avg_complexity < 10:
            return "high"
        else:
            return "very_high"

    def _normalize_code(self, code: str) -> str:
        """Normalize code for duplicate detection."""
        # Remove whitespace and comments
        lines = code.split("\n")
        normalized = []

        for line in lines:
            # Remove comments
            line = re.sub(r"#.*$", "", line)
            # Remove extra whitespace
            line = " ".join(line.split())
            if line:
                normalized.append(line)

        return "\n".join(normalized)
