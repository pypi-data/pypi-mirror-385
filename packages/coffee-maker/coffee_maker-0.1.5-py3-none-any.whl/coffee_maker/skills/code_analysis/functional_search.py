"""
Functional Search Skill

Find all code related to a specific functional area using the 3-level code index.

Capabilities:
- search(query): Find code by functional keyword
- browse_category(category): Browse a functional category
- browse_component(category, component): Browse a specific component

Used by: architect (for spec creation), assistant (for demos and documentation)
"""

from typing import Any, Dict

from coffee_maker.utils.code_index.query_engine import CodeIndexQueryEngine


class FunctionalSearch:
    """Search code by functional area using the code index."""

    def __init__(self, query_engine: CodeIndexQueryEngine = None):
        """
        Initialize functional search.

        Args:
            query_engine: Optional CodeIndexQueryEngine instance
                         (creates new one if not provided)
        """
        self.query_engine = query_engine or CodeIndexQueryEngine()

    def search(self, query: str, expand: bool = True) -> Dict[str, Any]:
        """
        Search code by functional keyword.

        Example:
            results = searcher.search("authentication")
            # Returns all code related to authentication

        Args:
            query: Search query (e.g., "authentication", "payment")
            expand: If True, expand to show individual implementations

        Returns:
            {
                "query": "authentication",
                "results_count": 15,
                "categories": {
                    "Authentication": {
                        "component_count": 3,
                        "implementation_count": 8,
                        "components": {
                            "JWT Validation": {
                                "implementations": [
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
            }
        """
        search_results = self.query_engine.functional_search(query)

        result = {
            "query": query,
            "results_count": 0,
            "categories": {},
        }

        for category, category_data in search_results.get("results", {}).items():
            category_info = {
                "component_count": len(category_data.get("components", {})),
                "implementation_count": 0,
                "components": {},
            }

            for comp_name, comp_data in category_data.get("components", {}).items():
                impls = comp_data.get("implementations", [])
                category_info["implementation_count"] += len(impls)

                if expand:
                    category_info["components"][comp_name] = {"implementations": impls}
                else:
                    category_info["components"][comp_name] = {"implementation_count": len(impls)}

            result["categories"][category] = category_info
            result["results_count"] += category_info["implementation_count"]

        return result

    def browse_category(self, category: str) -> Dict[str, Any]:
        """
        Browse a functional category.

        Args:
            category: Category name (e.g., "Authentication", "Payment")

        Returns:
            {
                "category": "Authentication",
                "components": {
                    "JWT Validation": {
                        "implementation_count": 3,
                        "implementations": [...]
                    }
                },
                "summary": {
                    "total_implementations": 8,
                    "files_affected": [...]
                }
            }
        """
        implementations = self.query_engine.find_implementations(category)

        if not implementations:
            return {
                "category": category,
                "error": f"Category '{category}' not found",
                "available_categories": self.query_engine.get_categories(),
            }

        # Group by component
        components = {}
        for impl in implementations:
            # Try to infer component from file path
            file_path = impl.get("file", "")
            file_path.split("/")

            # Use impl's component info if available, otherwise infer
            component = impl.get("component", "General")

            if component not in components:
                components[component] = []

            components[component].append(impl)

        # Build result
        result = {"category": category, "components": {}, "summary": {}}

        all_files = set()
        total_impls = 0

        for comp_name in sorted(components.keys()):
            result["components"][comp_name] = {
                "implementation_count": len(components[comp_name]),
                "implementations": components[comp_name],
            }
            total_impls += len(components[comp_name])
            for impl in components[comp_name]:
                all_files.add(impl.get("file"))

        result["summary"] = {
            "total_implementations": total_impls,
            "files_affected": sorted(all_files),
            "component_count": len(components),
        }

        return result

    def browse_component(self, category: str, component: str) -> Dict[str, Any]:
        """
        Browse a specific component.

        Args:
            category: Category name (e.g., "Authentication")
            component: Component name (e.g., "JWT Validation")

        Returns:
            {
                "category": "Authentication",
                "component": "JWT Validation",
                "implementations": [
                    {
                        "file": "coffee_maker/auth/jwt.py",
                        "line_start": 45,
                        "line_end": 89,
                        "name": "validate_jwt",
                        "type": "function",
                        "snippet": "def validate_jwt(token):\n    ..."
                    }
                ],
                "summary": {
                    "implementation_count": 3,
                    "files": ["coffee_maker/auth/jwt.py"],
                    "complexity": "medium"
                }
            }
        """
        implementations = self.query_engine.find_implementations(category, component)

        if not implementations:
            return {
                "error": f"Component '{component}' not found in '{category}'",
                "available_components": self.query_engine.get_components(category),
            }

        # Analyze implementations
        files = set()
        for impl in implementations:
            files.add(impl.get("file"))

        # Calculate average complexity
        avg_lines = (
            sum(impl.get("line_end", 0) - impl.get("line_start", 0) for impl in implementations) / len(implementations)
            if implementations
            else 0
        )

        complexity_level = "low" if avg_lines < 30 else ("medium" if avg_lines < 100 else "high")

        result = {
            "category": category,
            "component": component,
            "implementations": implementations,
            "summary": {
                "implementation_count": len(implementations),
                "files": sorted(files),
                "complexity": complexity_level,
                "total_lines": sum(impl.get("line_end", 0) - impl.get("line_start", 0) for impl in implementations),
            },
        }

        return result

    def search_by_pattern(self, pattern: str, regex: bool = False) -> Dict[str, Any]:
        """
        Search implementations by pattern.

        Args:
            pattern: String pattern or regex
            regex: If True, treat pattern as regex

        Returns:
            {
                "query": "pattern",
                "regex": false,
                "results_count": 5,
                "matches": [
                    {
                        "file": "coffee_maker/auth/jwt.py",
                        "implementations": [...]
                    }
                ]
            }
        """
        matches = self.query_engine.search_by_pattern(pattern, regex=regex)

        result = {
            "query": pattern,
            "regex": regex,
            "results_count": 0,
            "matches": [],
        }

        for category, impls in sorted(matches.items()):
            result["matches"].append(
                {
                    "category": category,
                    "implementation_count": len(impls),
                    "implementations": impls,
                }
            )
            result["results_count"] += len(impls)

        return result

    def get_related_code(self, file_path: str) -> Dict[str, Any]:
        """
        Get code related to a specific file (same component).

        Args:
            file_path: Path to file

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "related_files": [
                    "coffee_maker/auth/oauth.py",
                    "coffee_maker/auth/validators.py"
                ],
                "summary": {
                    "related_count": 2,
                    "category": "Authentication"
                }
            }
        """
        related_files = self.query_engine.get_related_files(file_path)

        # Try to find category for this file
        self.query_engine.get_components("Authentication")

        result = {
            "file": file_path,
            "related_files": sorted(related_files),
            "summary": {
                "related_count": len(related_files),
            },
        }

        return result

    def get_categories(self) -> Dict[str, Any]:
        """
        Get list of all functional categories.

        Returns:
            {
                "categories": ["Authentication", "Payment", ...],
                "total_categories": 8
            }
        """
        categories = self.query_engine.get_categories()

        result = {
            "categories": sorted(categories),
            "total_categories": len(categories),
        }

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            {
                "total_categories": 8,
                "total_components": 25,
                "total_implementations": 156,
                "categories": {
                    "Authentication": {
                        "components": 3,
                        "implementations": 8
                    }
                }
            }
        """
        stats = self.query_engine.get_statistics()

        # Add category breakdowns
        category_stats = {}
        for category in self.query_engine.get_categories():
            impls = self.query_engine.find_implementations(category)
            components = self.query_engine.get_components(category)
            category_stats[category] = {
                "components": len(components),
                "implementations": len(impls),
            }

        result = {
            "total_categories": stats["total_categories"],
            "total_components": stats["total_components"],
            "total_implementations": stats["total_implementations"],
            "categories": category_stats,
        }

        return result
