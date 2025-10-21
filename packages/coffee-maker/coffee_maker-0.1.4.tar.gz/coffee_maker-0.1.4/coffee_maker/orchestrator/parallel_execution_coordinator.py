"""
Parallel Execution Coordinator for orchestrator.

Manages parallel code_developer instances using git worktrees.

Author: code_developer (implementing SPEC-108)
Date: 2025-10-19
Related: SPEC-108, US-108, PRIORITY 23
"""

import logging
import psutil
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class WorktreeConfig:
    """Configuration for a git worktree.

    Attributes:
        priority_id: PRIORITY number being worked on
        worktree_path: Path to worktree directory
        branch_name: Git branch name
        process: Subprocess handle for code_developer instance
        status: Current status (pending, running, completed, failed)
        start_time: When work started
        end_time: When work completed
    """

    priority_id: int
    worktree_path: Path
    branch_name: str
    process: Optional[subprocess.Popen] = None
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ResourceMonitor:
    """Monitor system resources (CPU, memory).

    Prevents system exhaustion from too many parallel instances.
    """

    def __init__(self, max_cpu_percent: float = 80.0, max_memory_percent: float = 80.0):
        """Initialize resource monitor.

        Args:
            max_cpu_percent: Maximum CPU usage threshold (0-100)
            max_memory_percent: Maximum memory usage threshold (0-100)
        """
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent

    def check_resources_available(self) -> Tuple[bool, str]:
        """Check if resources are available to spawn new instance.

        Returns:
            Tuple of (available: bool, reason: str)
        """
        # Check CPU
        cpu_percent = psutil.cpu_percent(interval=1.0)
        if cpu_percent > self.max_cpu_percent:
            return False, f"CPU usage too high: {cpu_percent:.1f}% > {self.max_cpu_percent}%"

        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > self.max_memory_percent:
            return False, f"Memory usage too high: {memory.percent:.1f}% > {self.max_memory_percent}%"

        return True, "Resources available"

    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource usage.

        Returns:
            Dict with CPU, memory, disk usage
        """
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3),
        }


class ParallelExecutionCoordinator:
    """Coordinate parallel code_developer instances using git worktrees.

    Key Responsibilities:
    1. Validate task separation (ask architect skill)
    2. Create git worktrees for parallel tasks
    3. Spawn code_developer instances in each worktree
    4. Monitor progress
    5. Merge completed work to roadmap branch
    6. Clean up worktrees
    """

    def __init__(self, repo_root: Optional[Path] = None, max_instances: int = 3, auto_merge: bool = True):
        """Initialize parallel execution coordinator.

        Args:
            repo_root: Root directory of git repository (default: current directory)
            max_instances: Maximum parallel instances (1-3)
            auto_merge: Automatically merge completed work if no conflicts
        """
        self.repo_root = repo_root or Path.cwd()
        self.max_instances = min(max_instances, 3)  # Hard limit: 3 instances
        self.auto_merge = auto_merge
        self.resource_monitor = ResourceMonitor()
        self.worktrees: List[WorktreeConfig] = []

        # Validate git repository
        if not (self.repo_root / ".git").exists():
            raise ValueError(f"Not a git repository: {self.repo_root}")

    def execute_parallel_batch(self, priority_ids: List[int], auto_approve: bool = False) -> Dict[str, Any]:
        """Execute a batch of priorities in parallel.

        Args:
            priority_ids: List of PRIORITY numbers to execute
            auto_approve: Pass --auto-approve to code_developer instances

        Returns:
            Dict with execution results
        """
        start_time = datetime.now()
        logger.info(f"Starting parallel execution for priorities: {priority_ids}")

        # Step 1: Validate task separation
        logger.info("Step 1: Validating task separation...")
        validation_result = self._validate_task_separation(priority_ids)

        if not validation_result["valid"]:
            logger.error(f"Task separation validation failed: {validation_result['reason']}")
            return {
                "success": False,
                "error": validation_result["reason"],
                "conflicts": validation_result.get("conflicts", {}),
            }

        independent_pairs = validation_result["independent_pairs"]
        logger.info(f"Found {len(independent_pairs)} independent priority pairs")

        # Step 2: Select priorities to run in parallel
        selected_priorities = self._select_parallel_priorities(
            priority_ids, independent_pairs, max_count=self.max_instances
        )
        logger.info(f"Selected {len(selected_priorities)} priorities for parallel execution")

        # Step 3: Create worktrees
        logger.info("Step 2: Creating git worktrees...")
        worktrees = self._create_worktrees(selected_priorities)

        if not worktrees:
            return {
                "success": False,
                "error": "Failed to create worktrees",
            }

        self.worktrees = worktrees
        logger.info(f"Created {len(worktrees)} worktrees")

        # Step 4: Spawn code_developer instances
        logger.info("Step 3: Spawning code_developer instances...")
        self._spawn_instances(worktrees, auto_approve=auto_approve)

        # Step 5: Monitor instances
        logger.info("Step 4: Monitoring instances...")
        monitoring_result = self._monitor_instances(worktrees)

        # Step 6: Merge completed work
        logger.info("Step 5: Merging completed work...")
        merge_results = self._merge_completed_work(worktrees)

        # Step 7: Cleanup worktrees
        logger.info("Step 6: Cleaning up worktrees...")
        self._cleanup_worktrees(worktrees)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "success": True,
            "priorities_executed": selected_priorities,
            "worktrees_created": len(worktrees),
            "monitoring_result": monitoring_result,
            "merge_results": merge_results,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

    def _validate_task_separation(self, priority_ids: List[int]) -> Dict[str, Any]:
        """Validate task separation using architect task-separator skill.

        Args:
            priority_ids: List of PRIORITY numbers

        Returns:
            Dict with validation result
        """
        # Import task-separator skill
        skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"

        if not skill_path.exists():
            return {
                "valid": False,
                "reason": f"Task-separator skill not found: {skill_path}",
            }

        # Load skill dynamically
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("task_separator", skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call main function
            result = module.main({"priority_ids": priority_ids})

            # Check if we have independent pairs
            independent_pairs = result.get("independent_pairs", [])
            conflicts = result.get("conflicts", {})

            if not independent_pairs:
                return {
                    "valid": False,
                    "reason": "No independent priority pairs found - all tasks have file conflicts",
                    "conflicts": conflicts,
                }

            return {
                "valid": True,
                "independent_pairs": independent_pairs,
                "conflicts": conflicts,
                "task_file_map": result.get("task_file_map", {}),
            }

        except Exception as e:
            logger.error(f"Error running task-separator skill: {e}")
            return {
                "valid": False,
                "reason": f"Error running task-separator skill: {e}",
            }

    def _select_parallel_priorities(
        self, priority_ids: List[int], independent_pairs: List[Tuple[int, int]], max_count: int
    ) -> List[int]:
        """Select priorities to run in parallel.

        Args:
            priority_ids: List of PRIORITY numbers
            independent_pairs: List of (priority_a, priority_b) independent pairs
            max_count: Maximum number of priorities to select

        Returns:
            List of selected priority IDs
        """
        # Simple greedy selection: pick first N priorities that form independent pairs
        selected = []

        # Try to find a set of N priorities where all pairs are independent
        for priority in priority_ids:
            if len(selected) >= max_count:
                break

            # Check if this priority is independent of all selected priorities
            is_independent = True
            for other_priority in selected:
                pair = tuple(sorted([priority, other_priority]))
                if pair not in independent_pairs:
                    is_independent = False
                    break

            if is_independent:
                selected.append(priority)

        return selected

    def _create_worktrees(self, priority_ids: List[int]) -> List[WorktreeConfig]:
        """Create git worktrees for priorities.

        Args:
            priority_ids: List of PRIORITY numbers

        Returns:
            List of WorktreeConfig objects
        """
        worktrees = []

        for priority_id in priority_ids:
            # Create worktree path: ../MonolithicCoffeeMakerAgent-wt{N}
            worktree_name = f"{self.repo_root.name}-wt{priority_id}"
            worktree_path = self.repo_root.parent / worktree_name

            # Create branch name: roadmap-{priority_id} (CFR-013 compliant)
            # CFR-013 requires all agents to work on roadmap or roadmap-* branches
            branch_name = f"roadmap-{priority_id}"

            # Check if worktree already exists
            if worktree_path.exists():
                logger.warning(f"Worktree already exists: {worktree_path}, removing...")
                self._remove_worktree(worktree_path)

            # Create worktree
            try:
                # Create branch from current roadmap branch
                subprocess.run(
                    ["git", "worktree", "add", "-b", branch_name, str(worktree_path), "roadmap"],
                    cwd=self.repo_root,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                # Copy .env file from main repo to worktree
                env_file = self.repo_root / ".env"
                if env_file.exists():
                    import shutil

                    shutil.copy2(env_file, worktree_path / ".env")
                    logger.info(f"Copied .env file to worktree: {worktree_path}")

                # CRITICAL: Symlink data/ directory to share databases across worktrees
                # Without this, each worktree has isolated databases and can't coordinate
                worktree_data = worktree_path / "data"
                main_data = self.repo_root / "data"

                if worktree_data.exists() and not worktree_data.is_symlink():
                    # Remove copied data directory
                    shutil.rmtree(worktree_data)
                    logger.debug(f"Removed copied data directory: {worktree_data}")

                if not worktree_data.exists():
                    # Create symlink to main repo's data directory
                    worktree_data.symlink_to(main_data, target_is_directory=True)
                    logger.info(f"✅ Symlinked data/ directory: {worktree_data} → {main_data}")

                worktree = WorktreeConfig(
                    priority_id=priority_id, worktree_path=worktree_path, branch_name=branch_name, status="created"
                )
                worktrees.append(worktree)
                logger.info(f"Created worktree: {worktree_path} (branch: {branch_name})")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create worktree for PRIORITY {priority_id}: {e.stderr}")

        return worktrees

    def _spawn_instances(self, worktrees: List[WorktreeConfig], auto_approve: bool = False):
        """Spawn code_developer instances in worktrees.

        Args:
            worktrees: List of WorktreeConfig objects
            auto_approve: Pass --auto-approve to code_developer
        """
        # Get the poetry virtualenv Python path
        venv_result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        venv_path = venv_result.stdout.strip()
        python_bin = f"{venv_path}/bin/python"

        for worktree in worktrees:
            # Build command using direct Python interpreter
            cmd = [python_bin, "-m", "coffee_maker.autonomous.daemon_cli", f"--priority={worktree.priority_id}"]
            if auto_approve:
                cmd.append("--auto-approve")

            # Create log files for stdout/stderr
            log_file = worktree.worktree_path / f"code_developer_priority_{worktree.priority_id}.log"
            error_log_file = worktree.worktree_path / f"code_developer_priority_{worktree.priority_id}_error.log"

            # Spawn process
            try:
                with open(log_file, "w") as stdout_f, open(error_log_file, "w") as stderr_f:
                    process = subprocess.Popen(
                        cmd, cwd=worktree.worktree_path, stdout=stdout_f, stderr=stderr_f, text=True
                    )

                worktree.process = process
                worktree.status = "running"
                worktree.start_time = datetime.now()
                logger.info(f"Spawned code_developer for PRIORITY {worktree.priority_id} (PID: {process.pid})")
                logger.info(f"  Logs: {log_file}")
                logger.info(f"  Error logs: {error_log_file}")

            except Exception as e:
                logger.error(f"Failed to spawn code_developer for PRIORITY {worktree.priority_id}: {e}")
                worktree.status = "failed"

    def _monitor_instances(self, worktrees: List[WorktreeConfig], poll_interval: int = 10) -> Dict[str, Any]:
        """Monitor running instances.

        Args:
            worktrees: List of WorktreeConfig objects
            poll_interval: How often to check status (seconds)

        Returns:
            Dict with monitoring results
        """
        completed_count = 0
        failed_count = 0

        while True:
            all_done = True

            for worktree in worktrees:
                if worktree.status == "running" and worktree.process:
                    # Check if process is still running
                    poll_result = worktree.process.poll()

                    if poll_result is not None:
                        # Process finished
                        worktree.end_time = datetime.now()

                        # Read log files
                        log_file = worktree.worktree_path / f"code_developer_priority_{worktree.priority_id}.log"
                        error_log_file = (
                            worktree.worktree_path / f"code_developer_priority_{worktree.priority_id}_error.log"
                        )

                        if poll_result == 0:
                            worktree.status = "completed"
                            completed_count += 1
                            duration = (worktree.end_time - worktree.start_time).total_seconds()
                            logger.info(
                                f"PRIORITY {worktree.priority_id} completed successfully (duration: {duration:.1f}s)"
                            )

                            # Log last 50 lines of output for debugging
                            if log_file.exists():
                                with open(log_file, "r") as f:
                                    lines = f.readlines()
                                    last_lines = "".join(lines[-50:])
                                    logger.info(f"  Last 50 lines of output:\n{last_lines}")
                        else:
                            worktree.status = "failed"
                            failed_count += 1
                            logger.error(f"PRIORITY {worktree.priority_id} failed with code {poll_result}")

                            # Read and log error output
                            if error_log_file.exists():
                                with open(error_log_file, "r") as f:
                                    stderr_output = f.read()
                                    logger.error(f"  STDERR:\n{stderr_output[:2000]}")

                            if log_file.exists():
                                with open(log_file, "r") as f:
                                    stdout_output = f.read()
                                    logger.error(f"  STDOUT:\n{stdout_output[:2000]}")

                if worktree.status == "running":
                    all_done = False

            if all_done:
                break

            # Wait before next poll
            time.sleep(poll_interval)

        return {
            "completed": completed_count,
            "failed": failed_count,
            "total": len(worktrees),
        }

    def _merge_completed_work(self, worktrees: List[WorktreeConfig]) -> Dict[int, str]:
        """Merge completed work to roadmap branch.

        Args:
            worktrees: List of WorktreeConfig objects

        Returns:
            Dict mapping priority_id to merge result
        """
        merge_results = {}

        for worktree in worktrees:
            if worktree.status != "completed":
                merge_results[worktree.priority_id] = f"skipped (status: {worktree.status})"
                continue

            # Attempt merge
            try:
                # Switch to roadmap branch
                subprocess.run(
                    ["git", "checkout", "roadmap"], cwd=self.repo_root, check=True, capture_output=True, text=True
                )

                # Merge feature branch
                result = subprocess.run(
                    [
                        "git",
                        "merge",
                        "--no-ff",
                        worktree.branch_name,
                        "-m",
                        f"Merge PRIORITY {worktree.priority_id} from parallel execution",
                    ],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    merge_results[worktree.priority_id] = "merged successfully"
                    logger.info(f"Merged PRIORITY {worktree.priority_id} successfully")
                else:
                    merge_results[worktree.priority_id] = f"merge conflict: {result.stderr}"
                    logger.error(f"Merge conflict for PRIORITY {worktree.priority_id}: {result.stderr}")

            except subprocess.CalledProcessError as e:
                merge_results[worktree.priority_id] = f"merge failed: {e.stderr}"
                logger.error(f"Failed to merge PRIORITY {worktree.priority_id}: {e.stderr}")

        return merge_results

    def _cleanup_worktrees(self, worktrees: List[WorktreeConfig]):
        """Clean up git worktrees.

        Args:
            worktrees: List of WorktreeConfig objects
        """
        for worktree in worktrees:
            self._remove_worktree(worktree.worktree_path, worktree.branch_name)
            logger.info(f"Cleaned up worktree: {worktree.worktree_path}")

        # Prune any remaining worktree references
        try:
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("✅ Pruned stale worktree references")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to prune worktrees: {e.stderr}")

    def _remove_worktree(self, worktree_path: Path, branch_name: str):
        """Remove a git worktree and its branch.

        Args:
            worktree_path: Path to worktree directory
            branch_name: Name of the branch to delete
        """
        # Step 1: Remove worktree using git
        try:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree_path)],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"✅ Removed worktree: {worktree_path}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git worktree remove failed: {e.stderr}, trying manual cleanup...")
            # Fallback: manual cleanup of directory
            if worktree_path.exists():
                try:
                    shutil.rmtree(worktree_path)
                    logger.info(f"✅ Manually removed directory: {worktree_path}")
                except Exception as dir_error:
                    logger.error(f"Failed to remove directory {worktree_path}: {dir_error}")

        # Step 2: Delete the branch
        try:
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"✅ Deleted branch: {branch_name}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to delete branch {branch_name}: {e.stderr}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of parallel execution.

        Returns:
            Dict with status information
        """
        return {
            "max_instances": self.max_instances,
            "active_worktrees": len([w for w in self.worktrees if w.status == "running"]),
            "worktrees": [
                {
                    "priority_id": w.priority_id,
                    "status": w.status,
                    "branch": w.branch_name,
                    "worktree_path": str(w.worktree_path),
                    "start_time": w.start_time.isoformat() if w.start_time else None,
                    "end_time": w.end_time.isoformat() if w.end_time else None,
                }
                for w in self.worktrees
            ],
            "resources": self.resource_monitor.get_resource_status(),
        }
