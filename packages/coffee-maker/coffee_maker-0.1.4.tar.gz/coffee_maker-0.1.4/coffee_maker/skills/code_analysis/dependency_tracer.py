"""
Dependency Tracer Skill

Analyze dependency relationships and impact of changes.

Capabilities:
- trace_imports: Find all imports in a file
- find_dependents: Find all files that depend on a module
- impact_analysis: Analyze impact of changes to a file
- circular_dependencies: Detect circular import dependencies

Used by: architect (for impact analysis before design), code_developer
"""

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class DependencyTracer:
    """Trace and analyze dependency relationships."""

    def __init__(self, codebase_root: str = None):
        """Initialize dependency tracer."""
        self.codebase_root = Path(codebase_root or Path.cwd())
        self._import_cache = None

    def trace_imports(self, file_path: str) -> Dict[str, Any]:
        """
        Find all imports in a file.

        Args:
            file_path: Path to Python file (relative to codebase root)

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "imports": {
                    "standard_library": ["os", "sys", "json"],
                    "third_party": ["PyJWT", "cryptography"],
                    "internal": ["coffee_maker.config", "coffee_maker.utils"]
                },
                "import_details": [
                    {
                        "module": "PyJWT",
                        "imported_as": "jwt",
                        "type": "third_party",
                        "line": 3
                    }
                ]
            }
        """
        full_path = self.codebase_root / file_path
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}

        result = {
            "file": file_path,
            "imports": {
                "standard_library": [],
                "third_party": [],
                "internal": [],
            },
            "import_details": [],
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    import_type = self._classify_import(module_name)
                    result["imports"][import_type].append(module_name)
                    result["import_details"].append(
                        {
                            "module": alias.name,
                            "imported_as": alias.asname or alias.name,
                            "type": import_type,
                            "line": node.lineno,
                        }
                    )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    import_type = self._classify_import(module_name)
                    result["imports"][import_type].append(module_name)
                    result["import_details"].append(
                        {
                            "module": node.module,
                            "imported_as": None,
                            "type": import_type,
                            "line": node.lineno,
                        }
                    )

        # Deduplicate
        for import_type in result["imports"]:
            result["imports"][import_type] = sorted(list(set(result["imports"][import_type])))

        return result

    def find_dependents(self, module_path: str, internal_only: bool = True) -> Dict[str, Any]:
        """
        Find all files that import/depend on a module.

        Args:
            module_path: Path to module (relative to codebase root)
            internal_only: Only return internal dependencies

        Returns:
            {
                "module": "coffee_maker/auth/jwt.py",
                "dependents": [
                    {
                        "file": "coffee_maker/api/routes.py",
                        "import_line": "from coffee_maker.auth.jwt import validate_token",
                        "line_number": 5
                    }
                ],
                "dependency_count": 3
            }
        """
        result = {"module": module_path, "dependents": [], "dependency_count": 0}

        # Convert file path to module name
        module_name = self._path_to_module_name(module_path)
        python_files = self._find_python_files()

        for py_file in python_files:
            if str(py_file.relative_to(self.codebase_root)) == module_path:
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.split("\n")

            # Look for imports of this module
            for line_no, line in enumerate(lines, 1):
                if module_name in line and ("import" in line or "from" in line):
                    result["dependents"].append(
                        {
                            "file": str(py_file.relative_to(self.codebase_root)),
                            "import_line": line.strip(),
                            "line_number": line_no,
                        }
                    )

        result["dependency_count"] = len(result["dependents"])
        return result

    def impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze impact of changes to a file.

        What code could be affected by changes to this file?

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "direct_impact": [...],      # Files that import this
                "indirect_impact": [...],    # Files that import those files
                "impact_level": "medium",
                "affected_modules": ["API", "Authentication", "Admin"],
                "risky_changes": [...]       # High-impact functions
            }
        """
        result = {
            "file": file_path,
            "direct_impact": [],
            "indirect_impact": [],
            "impact_level": "low",
            "affected_modules": set(),
            "risky_changes": [],
        }

        # Find direct dependents
        direct = self.find_dependents(file_path, internal_only=True)
        result["direct_impact"] = direct["dependents"]

        # Find indirect dependents (files that depend on direct dependents)
        indirect_files = set()
        for dependent in result["direct_impact"]:
            indirect = self.find_dependents(dependent["file"], internal_only=True)
            for ind_dep in indirect["dependents"]:
                indirect_files.add(ind_dep["file"])

        result["indirect_impact"] = [{"file": f} for f in sorted(indirect_files)]

        # Determine impact level
        total_affected = len(result["direct_impact"]) + len(result["indirect_impact"])
        if total_affected > 10:
            result["impact_level"] = "high"
        elif total_affected > 3:
            result["impact_level"] = "medium"

        # Extract module names from affected files
        for dep in result["direct_impact"]:
            parts = Path(dep["file"]).parts
            if len(parts) > 1:
                result["affected_modules"].add(parts[1])

        result["affected_modules"] = sorted(result["affected_modules"])

        # Identify risky changes (exported functions/classes)
        risky = self._find_exported_definitions(file_path)
        result["risky_changes"] = risky

        return result

    def circular_dependencies(self) -> Dict[str, Any]:
        """
        Detect circular import dependencies.

        Returns:
            {
                "cycles_found": [
                    {
                        "cycle": ["module_a", "module_b", "module_a"],
                        "files": ["coffee_maker/a.py", "coffee_maker/b.py"]
                    }
                ],
                "circular_count": 1,
                "affected_files": [...]
            }
        """
        result = {
            "cycles_found": [],
            "circular_count": 0,
            "affected_files": set(),
        }

        # Build dependency graph
        graph = self._build_dependency_graph()

        # Find cycles using DFS
        cycles = self._find_cycles_dfs(graph)

        for cycle in cycles:
            cycle_files = [self._module_name_to_path(m) for m in cycle]
            result["cycles_found"].append({"cycle": cycle, "files": [f for f in cycle_files if f]})
            result["affected_files"].update(cycle_files)

        result["circular_count"] = len(result["cycles_found"])
        result["affected_files"] = sorted(result["affected_files"])

        return result

    def dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get complete dependency graph for visualization.

        Returns:
            {
                "coffee_maker/auth/jwt.py": [
                    "coffee_maker/config.py",
                    "coffee_maker/utils.py"
                ]
            }
        """
        return self._build_dependency_graph()

    def _classify_import(self, module_name: str) -> str:
        """Classify import as standard_library, third_party, or internal."""
        stdlib_modules = {
            "os",
            "sys",
            "re",
            "json",
            "ast",
            "pathlib",
            "typing",
            "collections",
            "defaultdict",
            "asyncio",
            "threading",
            "logging",
            "unittest",
            "tempfile",
        }

        if module_name in stdlib_modules:
            return "standard_library"

        if module_name.startswith("coffee_maker"):
            return "internal"

        return "third_party"

    def _path_to_module_name(self, file_path: str) -> str:
        """Convert file path to module name."""
        path = file_path.replace(".py", "").replace("/", ".")
        return path

    def _module_name_to_path(self, module_name: str) -> Optional[str]:
        """Convert module name to file path."""
        path = module_name.replace(".", "/") + ".py"
        full_path = self.codebase_root / path
        if full_path.exists():
            return path
        return None

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

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build complete dependency graph."""
        graph = {}
        python_files = self._find_python_files()

        for py_file in python_files:
            file_path = str(py_file.relative_to(self.codebase_root))
            imports = self.trace_imports(file_path)

            # Get internal dependencies only
            internal_deps = []
            for detail in imports.get("import_details", []):
                if detail["type"] == "internal":
                    mod_path = self._module_name_to_path(detail["module"])
                    if mod_path:
                        internal_deps.append(mod_path)

            if internal_deps:
                graph[file_path] = internal_deps

        return graph

    def _find_cycles_dfs(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find cycles in dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _find_exported_definitions(self, file_path: str) -> List[Dict[str, str]]:
        """Find exported functions and classes (potential breaking changes)."""
        full_path = self.codebase_root / file_path
        exported = []

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return exported

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return exported

        # Find top-level functions and classes (likely exported)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    exported.append(
                        {
                            "name": node.name,
                            "type": "function",
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    exported.append(
                        {
                            "name": node.name,
                            "type": "class",
                            "line": node.lineno,
                        }
                    )

        return exported
