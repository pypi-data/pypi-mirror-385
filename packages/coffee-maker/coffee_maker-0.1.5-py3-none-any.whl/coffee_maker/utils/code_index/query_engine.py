"""
Code Index Query Engine

Provides fast queries against the 3-level hierarchical code index.
Used by all code analysis skills for consistent, deterministic results.

Query Types:
- functional_search(query): Find code by functional area (e.g., "authentication")
- find_implementations(category, component): Get all code in a specific component
- get_complexity_metrics(file_path): Get code complexity metrics
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class CodeIndexQueryEngine:
    """Query engine for the 3-level code index."""

    def __init__(self, index_path: str = None):
        """
        Initialize query engine with index.

        Args:
            index_path: Path to index.json (defaults to data/code_index/index.json)
        """
        if index_path is None:
            index_path = Path.cwd() / "data" / "code_index" / "index.json"
        else:
            index_path = Path(index_path)

        self.index_path = index_path
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load index from disk."""
        if not self.index_path.exists():
            return {"categories": {}, "metadata": {}}

        try:
            with open(self.index_path) as f:
                return json.load(f)
        except Exception:
            return {"categories": {}, "metadata": {}}

    def functional_search(self, query: str) -> Dict[str, Any]:
        """
        Search code by functional area.

        Example:
            results = engine.functional_search("authentication")
            # Returns all code related to authentication

        Args:
            query: Search query (e.g., "authentication", "payment")

        Returns:
            Hierarchical results:
            {
                "matching_categories": ["Authentication", "Logging"],
                "results": {
                    "Authentication": {
                        "components": {
                            "JWT Validation": [
                                {
                                    "file": "coffee_maker/auth/jwt.py",
                                    "line_start": 45,
                                    "line_end": 89,
                                    "name": "validate_jwt",
                                    "type": "function"
                                }
                            ]
                        }
                    }
                }
            }
        """
        query_lower = query.lower()
        results = {"matching_categories": [], "results": {}}

        # Search category names
        for category_name, category_data in self.index.get("categories", {}).items():
            if query_lower in category_name.lower():
                results["matching_categories"].append(category_name)
                results["results"][category_name] = category_data

        # If no category match, search within all categories
        if not results["matching_categories"]:
            for category_name, category_data in self.index.get("categories", {}).items():
                matching_components = {}
                for comp_name, comp_data in category_data.get("components", {}).items():
                    matching_impls = [
                        impl for impl in comp_data.get("implementations", []) if query_lower in str(impl).lower()
                    ]
                    if matching_impls:
                        matching_components[comp_name] = {"implementations": matching_impls}

                if matching_components:
                    results["matching_categories"].append(category_name)
                    results["results"][category_name] = {"components": matching_components}

        return results

    def find_implementations(self, category: str, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all implementations in a category or component.

        Args:
            category: Category name (e.g., "Authentication")
            component: Optional component name (e.g., "JWT Validation")

        Returns:
            List of implementations with file, line numbers, etc.
        """
        implementations = []

        if category not in self.index.get("categories", {}):
            return implementations

        category_data = self.index["categories"][category]

        if component:
            # Return specific component
            if component in category_data.get("components", {}):
                implementations = category_data["components"][component].get("implementations", [])
        else:
            # Return all components in category
            for comp_data in category_data.get("components", {}).values():
                implementations.extend(comp_data.get("implementations", []))

        return implementations

    def get_file_implementations(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get all implementations in a specific file.

        Args:
            file_path: Path to file (relative to codebase root)

        Returns:
            List of implementations in the file
        """
        implementations = []

        for category_data in self.index.get("categories", {}).values():
            for comp_data in category_data.get("components", {}).values():
                for impl in comp_data.get("implementations", []):
                    if impl.get("file") == file_path:
                        implementations.append(impl)

        return implementations

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.index.get("categories", {}).keys())

    def get_components(self, category: str) -> List[str]:
        """Get all components in a category."""
        if category not in self.index.get("categories", {}):
            return []

        return list(self.index["categories"][category].get("components", {}).keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        stats = {
            "total_categories": len(self.index.get("categories", {})),
            "total_components": 0,
            "total_implementations": 0,
        }

        for category_data in self.index.get("categories", {}).values():
            stats["total_components"] += len(category_data.get("components", {}))
            for comp_data in category_data.get("components", {}).values():
                stats["total_implementations"] += len(comp_data.get("implementations", []))

        return stats

    def search_by_pattern(self, pattern: str, regex: bool = False) -> Dict[str, Any]:
        """
        Search implementations by pattern.

        Args:
            pattern: String pattern or regex pattern
            regex: If True, treat pattern as regex

        Returns:
            Matching implementations grouped by category
        """
        results = {}

        if regex:
            try:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
            except re.error:
                return results
        else:
            pattern = pattern.lower()

        for category_name, category_data in self.index.get("categories", {}).items():
            matching_impls = []

            for comp_data in category_data.get("components", {}).values():
                for impl in comp_data.get("implementations", []):
                    search_text = f"{impl.get('name', '')} {impl.get('snippet', '')}".lower()

                    if regex:
                        if compiled_pattern.search(search_text):
                            matching_impls.append(impl)
                    else:
                        if pattern in search_text:
                            matching_impls.append(impl)

            if matching_impls:
                results[category_name] = matching_impls

        return results

    def get_related_files(self, file_path: str, same_component: bool = True) -> List[str]:
        """
        Find files related to a given file.

        Args:
            file_path: Path to file
            same_component: If True, find files in same component

        Returns:
            List of related file paths
        """
        related_files = set()

        for category_data in self.index.get("categories", {}).values():
            for comp_data in category_data.get("components", {}).values():
                file_in_component = any(impl.get("file") == file_path for impl in comp_data.get("implementations", []))

                if file_in_component and same_component:
                    # Get all files in this component
                    for impl in comp_data.get("implementations", []):
                        related_files.add(impl.get("file"))

        return sorted(related_files)

    def get_dependency_map(self) -> Dict[str, List[str]]:
        """
        Get a map of file dependencies based on component structure.

        Returns:
            Map of file -> related_files
        """
        dep_map = {}

        for file_path in self._get_all_files():
            dep_map[file_path] = self.get_related_files(file_path)

        return dep_map

    def _get_all_files(self) -> set:
        """Get all files in the index."""
        files = set()

        for category_data in self.index.get("categories", {}).values():
            for comp_data in category_data.get("components", {}).values():
                for impl in comp_data.get("implementations", []):
                    files.add(impl.get("file"))

        return files
