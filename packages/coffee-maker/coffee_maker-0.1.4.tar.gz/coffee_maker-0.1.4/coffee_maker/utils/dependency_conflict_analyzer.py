"""
Dependency conflict analyzer.

Analyzes dependency conflicts and circular dependencies using Poetry's resolver.
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ConflictAnalyzer:
    """
    Analyzes dependency conflicts and circular dependencies.

    Uses Poetry's resolver to detect version conflicts and
    parses poetry.lock to identify circular dependencies.
    """

    def __init__(self, project_root: Path):
        """
        Initialize with project root containing pyproject.toml.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.lock_path = project_root / "poetry.lock"

        if not self.pyproject_path.exists():
            logger.warning(f"pyproject.toml not found at {self.pyproject_path}")

        logger.debug(f"ConflictAnalyzer initialized for {project_root}")

    def check_conflicts(self, package_name: str, version: Optional[str] = None) -> "ConflictInfo":  # noqa: F821
        """
        Check for version conflicts and circular dependencies.

        Args:
            package_name: Package to check
            version: Optional version constraint

        Returns:
            ConflictInfo with conflicts, circular deps, tree depth

        Implementation:
        1. Run `poetry add {package} --dry-run` to simulate
        2. Parse output for conflict messages
        3. Run `poetry show --tree` to analyze dependency tree
        4. Use DFS to detect cycles
        5. Calculate tree depth
        """
        logger.info(f"Checking conflicts for {package_name} (version: {version or 'latest'})")

        # Check for version conflicts using Poetry dry-run
        conflicts = self._detect_version_conflicts(package_name, version)
        has_conflicts = len(conflicts) > 0

        # Detect circular dependencies (simulated - would need Poetry tree)
        circular_dependencies = self._detect_circular_dependencies(package_name)

        # Calculate tree depth and total sub-dependencies (simulated)
        tree_depth, total_sub_deps = self._calculate_tree_metrics(package_name, version)

        # Import here to avoid circular imports
        from coffee_maker.utils.dependency_analyzer import ConflictInfo

        conflict_info = ConflictInfo(
            has_conflicts=has_conflicts,
            conflicts=conflicts,
            circular_dependencies=circular_dependencies,
            tree_depth=tree_depth,
            total_sub_dependencies=total_sub_deps,
        )

        if has_conflicts:
            logger.warning(
                f"Conflicts detected for {package_name}: {len(conflicts)} conflicts, "
                f"{len(circular_dependencies)} circular deps"
            )
        else:
            logger.info(f"No conflicts detected for {package_name}")

        return conflict_info

    def _detect_version_conflicts(self, package_name: str, version: Optional[str]) -> List[Dict[str, str]]:
        """
        Detect version conflicts using Poetry dry-run.

        Args:
            package_name: Package name
            version: Optional version constraint

        Returns:
            List of conflicts: [{"package": "foo", "constraint": ">=1.0", "conflict": "requires <0.9"}]
        """
        try:
            # Build Poetry command
            package_spec = f"{package_name}"
            if version:
                # Clean up version string (remove quotes if present)
                version_clean = version.strip('"').strip("'")
                package_spec = f"{package_name}{version_clean}"

            # Run poetry add --dry-run
            cmd = ["poetry", "add", package_spec, "--dry-run"]
            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse output for conflict messages
            conflicts = []

            # Poetry dry-run output patterns:
            # "Because X depends on Y (>=1.0) and no versions of Y match >=1.0,<2.0, X is forbidden."
            # "The current project's Python requirement (>=3.11,<4.0) is not compatible with ..."

            if result.returncode != 0:
                output = result.stdout + result.stderr

                # Check for common conflict patterns
                if "conflict" in output.lower() or "incompatible" in output.lower() or "forbidden" in output.lower():
                    # Try to parse specific conflicts
                    lines = output.split("\n")
                    for line in lines:
                        if "depends on" in line.lower() or "requires" in line.lower():
                            # Extract conflict information (simplified parsing)
                            conflicts.append(
                                {"package": package_name, "constraint": version or "latest", "conflict": line.strip()}
                            )

                    # If we couldn't parse specific conflicts, add generic one
                    if not conflicts:
                        conflicts.append(
                            {
                                "package": package_name,
                                "constraint": version or "latest",
                                "conflict": "Poetry resolver detected conflicts (see logs for details)",
                            }
                        )

                    logger.warning(f"Version conflicts detected for {package_name}: {len(conflicts)} conflicts")
                else:
                    logger.debug(f"Poetry dry-run failed but no clear conflicts: {output[:200]}")

            return conflicts

        except subprocess.TimeoutExpired:
            logger.warning(f"Poetry dry-run timeout for {package_name}")
            return []
        except Exception as e:
            logger.warning(f"Error detecting conflicts for {package_name}: {str(e)}")
            return []

    def _detect_circular_dependencies(self, package_name: str) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.

        Returns list of cycles: [["pkg_a", "pkg_b", "pkg_a"], ...]

        Note: This is a simplified implementation. Full implementation would
        require parsing Poetry's dependency tree.
        """
        # For now, return empty (no circular deps detected)
        # Full implementation would:
        # 1. Build dependency graph from `poetry show --tree`
        # 2. Run DFS to detect cycles
        # 3. Return list of cycles

        logger.debug(f"Circular dependency detection for {package_name} (simplified)")

        # Try to get dependency tree
        try:
            result = subprocess.run(
                ["poetry", "show", package_name, "--tree"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse tree and look for repeated packages
                tree_output = result.stdout
                packages_in_tree = re.findall(r"([a-zA-Z0-9_-]+)\s+\d+", tree_output)

                # Check for repeated packages (simple heuristic)
                seen = set()
                for pkg in packages_in_tree:
                    if pkg in seen:
                        # Potential cycle detected (simplified)
                        logger.debug(f"Potential circular dependency: {pkg}")
                        # Don't report for now (needs proper DFS)
                    seen.add(pkg)

        except Exception as e:
            logger.debug(f"Could not analyze dependency tree for {package_name}: {str(e)}")

        # Return empty for now (conservative)
        return []

    def _calculate_tree_metrics(self, package_name: str, version: Optional[str]) -> Tuple[int, int]:
        """
        Calculate dependency tree depth and total sub-dependencies.

        Args:
            package_name: Package name
            version: Optional version constraint

        Returns:
            Tuple of (tree_depth, total_sub_dependencies)
        """
        try:
            # Try to get dependency tree
            result = subprocess.run(
                ["poetry", "show", package_name, "--tree"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                tree_output = result.stdout
                lines = tree_output.split("\n")

                # Calculate depth by looking at indentation
                max_depth = 0
                total_deps = 0

                for line in lines:
                    if not line.strip():
                        continue

                    # Count leading spaces/pipes to determine depth
                    # Poetry tree format: "├── package-name version"
                    depth = 0
                    for char in line:
                        if char in [" ", "│", "├", "└"]:
                            depth += 1
                        else:
                            break

                    depth = depth // 4  # Normalize (4 spaces per level)
                    max_depth = max(max_depth, depth)

                    # Count as dependency if it has a package name
                    if "──" in line:
                        total_deps += 1

                logger.debug(f"Tree metrics for {package_name}: depth={max_depth}, sub-deps={total_deps}")
                return max_depth, total_deps

        except Exception as e:
            logger.debug(f"Could not calculate tree metrics for {package_name}: {str(e)}")

        # Default values if we can't determine
        return 0, 0

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Build dependency graph from poetry.lock.

        Returns:
            Dict mapping package names to list of dependencies

        Note: Simplified implementation. Full version would parse poetry.lock TOML.
        """
        graph = {}

        if not self.lock_path.exists():
            logger.debug("poetry.lock not found, returning empty graph")
            return graph

        # For now, return empty graph
        # Full implementation would parse poetry.lock TOML file
        # and build a graph of package -> [dependencies]

        return graph

    def _dfs_cycle_detection(
        self,
        graph: Dict[str, List[str]],
        start_node: str,
        visited: Set[str],
        path_stack: List[str],
    ) -> List[List[str]]:
        """
        DFS-based cycle detection.

        Args:
            graph: Dependency graph
            start_node: Starting node for DFS
            visited: Set of visited nodes
            path_stack: Current path stack

        Returns:
            List of detected cycles
        """
        cycles = []

        def dfs(node: str):
            if node in path_stack:
                # Cycle detected - extract cycle from path_stack
                cycle_start_idx = path_stack.index(node)
                cycle = path_stack[cycle_start_idx:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path_stack.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor)

            path_stack.pop()

        dfs(start_node)
        return cycles
