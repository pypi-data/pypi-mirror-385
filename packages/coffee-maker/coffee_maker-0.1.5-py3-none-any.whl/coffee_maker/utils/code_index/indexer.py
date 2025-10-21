"""
Code Indexer: Builds and maintains 3-level hierarchical codebase index

Architecture:
- Level 1: Functional Categories (e.g., "Authentication", "Payment Processing")
- Level 2: Components (e.g., "JWT Validation", "Rate Limiting")
- Level 3: Implementations (file:line_start:line_end with code snippets)

Features:
- Full rebuild: Analyzes entire codebase structure
- Incremental update: Updates only changed files
- Git hook integration: Triggered by commits
- Automatic categorization: Uses patterns to identify categories

Index Format:
{
    "categories": {
        "Authentication": {
            "components": {
                "JWT Validation": {
                    "implementations": [
                        {
                            "file": "coffee_maker/auth/jwt.py",
                            "line_start": 45,
                            "line_end": 89,
                            "snippet": "def validate_jwt(...)",
                            "complexity": "medium",
                            "dependencies": ["PyJWT", "cryptography"]
                        }
                    ]
                }
            }
        }
    }
}
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import ast


class CodeIndexer:
    """Builds and maintains the 3-level hierarchical code index."""

    # Default functional categories and their patterns
    CATEGORY_PATTERNS = {
        "Authentication": [
            r"auth",
            r"jwt",
            r"oauth",
            r"token",
            r"login",
            r"password",
            r"credential",
        ],
        "Database": [
            r"database",
            r"sqlalchemy",
            r"orm",
            r"query",
            r"migration",
            r"schema",
        ],
        "API": [
            r"endpoint",
            r"route",
            r"request",
            r"response",
            r"rest",
            r"graphql",
        ],
        "Payment": [
            r"payment",
            r"stripe",
            r"transaction",
            r"billing",
            r"invoice",
            r"charge",
        ],
        "Notifications": [
            r"email",
            r"notification",
            r"alert",
            r"message",
            r"slack",
            r"webhook",
        ],
        "Logging": [
            r"log",
            r"logger",
            r"debug",
            r"trace",
            r"observability",
            r"langfuse",
        ],
        "Configuration": [
            r"config",
            r"settings",
            r"environment",
            r"env",
            r"dotenv",
        ],
        "Testing": [r"test", r"pytest", r"mock", r"fixture"],
        "Utilities": [r"util", r"helper", r"common", r"base"],
        "CLI": [r"cli", r"command", r"argparse", r"typer"],
        "Autonomous": [
            r"daemon",
            r"agent",
            r"autonomous",
            r"orchestr",
            r"workflow",
        ],
    }

    # Component patterns for secondary classification
    COMPONENT_PATTERNS = {
        "Validation": r"validate|validator|schema|constraint",
        "Error Handling": r"exception|error|try|except|raise",
        "Caching": r"cache|redis|memcache",
        "Security": r"security|encrypt|decrypt|hash|salt",
        "Performance": r"optimize|cache|batch|parallel|async",
        "Integration": r"integrate|gateway|adapter|bridge",
        "Monitoring": r"monitor|metric|trace|observe",
    }

    def __init__(self, codebase_root: str = None):
        """
        Initialize the code indexer.

        Args:
            codebase_root: Root directory of codebase (defaults to project root)
        """
        self.codebase_root = Path(codebase_root or os.getcwd())
        self.index_path = self.codebase_root / "data" / "code_index" / "index.json"
        self.index: Dict[str, Any] = {"categories": {}, "metadata": {}}

    def rebuild_index(self) -> None:
        """Perform full rebuild of code index for entire codebase."""
        self.index = {"categories": {}, "metadata": {"last_updated": None}}

        python_files = self._find_python_files()
        total_files = len(python_files)

        for idx, file_path in enumerate(python_files):
            try:
                self._index_file(file_path)
            except Exception as e:
                # Log error but continue indexing
                print(f"Error indexing {file_path}: {e}")

        # Update metadata
        self.index["metadata"]["last_updated"] = str(Path(python_files[0]).stat().st_mtime if python_files else None)
        self.index["metadata"]["total_files"] = total_files
        self.index["metadata"]["total_categories"] = len(self.index["categories"])

    def update_index_incremental(self, changed_files: List[str]) -> None:
        """
        Update index incrementally for only changed files.

        Args:
            changed_files: List of file paths that changed
        """
        # Load existing index
        if self.index_path.exists():
            with open(self.index_path) as f:
                self.index = json.load(f)
        else:
            self.index = {"categories": {}, "metadata": {}}

        # Re-index only changed files
        for file_path in changed_files:
            if file_path.endswith(".py"):
                try:
                    self._index_file(file_path)
                except Exception as e:
                    print(f"Error updating index for {file_path}: {e}")

    def save_index(self) -> None:
        """Save index to disk (data/code_index/index.json)."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(self.index, f, indent=2)

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in codebase (excluding tests for now)."""
        python_files = []
        for root, dirs, files in os.walk(self.codebase_root):
            # Skip common non-code directories
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
                    "node_modules",
                }
            ]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return sorted(python_files)

    def _index_file(self, file_path: str) -> None:
        """
        Index a single Python file.

        Extracts:
        - Classes and functions with their locations
        - Categorizes by functional area
        - Identifies components and implementation details
        """
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.suffix == ".py":
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        # Extract functions and classes
        definitions = self._extract_definitions(tree, content, file_path)

        if not definitions:
            return

        # Determine categories for this file
        categories = self._categorize_file(file_path, content)

        if not categories:
            categories = ["Utilities"]  # Default category

        # Add to index
        for category in categories:
            if category not in self.index["categories"]:
                self.index["categories"][category] = {"components": {}}

            # Determine component
            component = self._determine_component(file_path, content, definitions)

            if component not in self.index["categories"][category]["components"]:
                self.index["categories"][category]["components"][component] = {"implementations": []}

            # Add implementations
            for definition in definitions:
                impl = {
                    "file": str(file_path.relative_to(self.codebase_root)),
                    "line_start": definition["line_start"],
                    "line_end": definition["line_end"],
                    "name": definition["name"],
                    "type": definition["type"],
                    "snippet": definition["snippet"],
                }
                self.index["categories"][category]["components"][component]["implementations"].append(impl)

    def _extract_definitions(self, tree: ast.AST, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract function and class definitions from AST."""
        definitions = []
        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                line_start = node.lineno
                line_end = node.end_lineno or node.lineno

                # Get snippet (first 3 lines)
                snippet_lines = lines[line_start - 1 : min(line_start + 2, len(lines))]
                snippet = "\n".join(snippet_lines)

                definitions.append(
                    {
                        "name": node.name,
                        "type": "class" if isinstance(node, ast.ClassDef) else "function",
                        "line_start": line_start,
                        "line_end": line_end,
                        "snippet": snippet,
                    }
                )

        return definitions

    def _categorize_file(self, file_path: Path, content: str) -> Set[str]:
        """Determine functional categories for a file."""
        categories = set()
        file_str = str(file_path).lower() + "\n" + content.lower()  # Search file path and content

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, file_str):
                    categories.add(category)
                    break

        return categories

    def _determine_component(self, file_path: Path, content: str, definitions: List[Dict]) -> str:
        """Determine component name for this file."""
        # Check file name
        file_name = file_path.stem.lower()

        for component, pattern in self.COMPONENT_PATTERNS.items():
            if re.search(pattern, file_name):
                return component

        # Check content
        for component, pattern in self.COMPONENT_PATTERNS.items():
            if re.search(pattern, content.lower()):
                return component

        # Use file name as component
        return file_name.replace("_", " ").title()
