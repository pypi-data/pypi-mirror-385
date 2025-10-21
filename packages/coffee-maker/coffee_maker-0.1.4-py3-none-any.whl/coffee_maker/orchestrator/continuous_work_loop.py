"""Continuous Work Loop for Orchestrator Agent.

This module implements the main work loop that enables 24/7 autonomous operation
where code_developer and architect continuously work on ROADMAP priorities without
human intervention.

Architecture:
    - Infinite work loop that polls ROADMAP every 30 seconds
    - Maintains 2-3 specs ahead of code_developer (spec backlog)
    - Delegates spec creation to architect proactively
    - Delegates implementation to code_developer when specs ready
    - Monitors task progress and handles errors
    - Graceful shutdown on SIGINT (Ctrl+C)
    - State preservation for crash recovery

CFR Compliance:
    - CFR-009: Sound notifications disabled (sound=False, agent_id="orchestrator")
    - CFR-013: All work happens on roadmap branch only

Related:
    SPEC-104: Technical specification
    US-104: Strategic requirement (PRIORITY 20)
"""

import json
import logging
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from coffee_maker.cli.notifications import NotificationDB
from coffee_maker.orchestrator.architect_coordinator import ArchitectCoordinator

logger = logging.getLogger(__name__)

# Import orchestrator agent management skill
agent_mgmt_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "orchestrator-agent-management"
sys.path.insert(0, str(agent_mgmt_dir))
from agent_management import OrchestratorAgentManagementSkill

sys.path.pop(0)

# Import roadmap management skill (SINGLE SOURCE OF TRUTH for ROADMAP operations)
roadmap_mgmt_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "roadmap-management"
sys.path.insert(0, str(roadmap_mgmt_dir))
from roadmap_management import RoadmapManagementSkill

sys.path.pop(0)

# Import bug tracking skill (database-backed bug tracking)
bug_tracking_dir = Path(__file__).parent.parent.parent / ".claude" / "skills" / "shared" / "bug-tracking"
sys.path.insert(0, str(bug_tracking_dir))
from bug_tracking import BugTrackingSkill

sys.path.pop(0)


@dataclass
class WorkLoopConfig:
    """Configuration for continuous work loop."""

    poll_interval_seconds: int = 30  # How often to check ROADMAP
    spec_backlog_target: int = 3  # Keep 3 specs ahead of code_developer
    max_retry_attempts: int = 3  # Retry failed tasks up to 3 times
    task_timeout_seconds: int = 7200  # 2 hours max per task
    state_file_path: str = "data/orchestrator/work_loop_state.json"
    enable_sound_notifications: bool = False  # CFR-009: Only user_listener uses sound


class ContinuousWorkLoop:
    """
    Continuous work loop for orchestrator agent.

    Responsibilities:
    - Poll ROADMAP every 30 seconds for new priorities
    - Maintain 2-3 specs ahead of code_developer (spec backlog)
    - Delegate spec creation to architect proactively
    - Delegate implementation to code_developer when specs ready
    - Monitor task progress and handle errors
    - Graceful shutdown on SIGINT (Ctrl+C)
    - State preservation for crash recovery

    CFR Compliance:
    - CFR-009: Sound notifications disabled (sound=False, agent_id="orchestrator")
    - CFR-013: All work happens on roadmap branch only
    """

    def __init__(self, config: Optional[WorkLoopConfig] = None):
        """
        Initialize continuous work loop.

        Args:
            config: Configuration for work loop (optional, uses defaults)
        """
        self.config = config or WorkLoopConfig()
        self.notifications = NotificationDB()
        self.running = False
        self.current_state: Dict = {}
        self.last_roadmap_update = 0.0
        self.repo_root = Path.cwd()  # Repository root directory
        self.start_time: Optional[datetime] = None  # Orchestrator start time

        # BUG-074: Track recently completed priorities to prevent immediate re-spawning
        # Maps priority_number → completion_timestamp
        self.recently_completed: Dict[str, float] = {}
        self.completion_cooldown_seconds = 300  # 5 minutes cooldown

        # Initialize agent management skill
        self.agent_mgmt = OrchestratorAgentManagementSkill()

        # Initialize roadmap management skill (SINGLE SOURCE OF TRUTH)
        self.roadmap_skill = RoadmapManagementSkill()

        # Initialize bug tracking skill (database-backed bug tracking)
        self.bug_skill = BugTrackingSkill()

        # Initialize architect coordinator (spec backlog + worktree merging)
        self.architect_coordinator = ArchitectCoordinator(spec_backlog_target=self.config.spec_backlog_target)

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Load previous state if exists (crash recovery)
        self._load_state()

    def start(self):
        """
        Start continuous work loop (runs forever until interrupted).

        Returns:
            None (blocks until graceful shutdown)
        """
        logger.info("🚀 Starting Orchestrator Continuous Work Loop")
        self.running = True
        self.start_time = datetime.now()  # Record orchestrator start time

        self.notifications.create_notification(
            type="info",
            title="Orchestrator Started",
            message="Continuous work loop is now running. Agents will work 24/7 on ROADMAP priorities.",
            priority="normal",
            sound=False,  # CFR-009: Background agent, no sound
            agent_id="orchestrator",
        )

        try:
            while self.running:
                loop_start = time.time()

                # Main work loop cycle
                try:
                    self._work_cycle()
                except Exception as e:
                    logger.error(f"Error in work cycle: {e}", exc_info=True)
                    self._handle_cycle_error(e)

                # Sleep for poll interval (minus cycle time)
                cycle_duration = time.time() - loop_start
                sleep_time = max(0, self.config.poll_interval_seconds - cycle_duration)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self._shutdown()

    def _work_cycle(self):
        """
        Single iteration of work loop.

        Steps:
        1. Poll ROADMAP for changes
        2. Coordinate architect (proactive spec creation)
        3. Coordinate code_developer (implementation)
        4. Monitor task progress
        5. Handle errors and retries
        6. Save state
        """
        # Step 1: Poll ROADMAP
        roadmap_updated = self._poll_roadmap()
        if roadmap_updated:
            logger.info("ROADMAP updated, recalculating work distribution")

        # Step 1.5: Check for high-priority bugs (BUG-065)
        # Bugs are coordinated in parallel with other work
        high_priority_bugs = self._get_high_priority_bugs()
        if high_priority_bugs:
            bug = high_priority_bugs[0]
            logger.info(f"🐛 High-priority bug detected: {bug['number']} - {bug['title']}")
            logger.info(f"   Priority: {bug['priority']}, Status: {bug['status']}")
            self._coordinate_bug_fix(bug)
            # Continue with other work (async/parallel execution)

        # Step 2: Architect coordination (proactive spec creation)
        self._coordinate_architect()

        # Step 2.5: Architect refactoring analysis (weekly)
        # RE-ENABLED: BUG-064 fixed - added --force flag
        self._coordinate_refactoring_analysis()

        # Step 2.6: project_manager auto-planning (weekly)
        self._coordinate_planning()

        # Step 2.7: code-reviewer coordination (post-commit reviews)
        self._coordinate_code_reviewer()

        # Step 2.8: Check for completed worktrees and notify architect for merge
        self._check_worktree_merges()

        # Step 3: code_developer coordination (implementation)
        self._coordinate_code_developer()

        # Step 4: Monitor task progress
        self._monitor_tasks()

        # Step 5: Save state
        self._save_state()

    def _poll_roadmap(self) -> bool:
        """
        Poll ROADMAP.md for changes.

        NOTE: With roadmap-management skill, we don't cache - skill reads file directly.
        This method only checks if file changed to log updates.

        Returns:
            True if ROADMAP was updated since last check, False otherwise
        """
        roadmap_path = Path("docs/roadmap/ROADMAP.md")

        if not roadmap_path.exists():
            logger.warning("ROADMAP.md not found!")
            return False

        # Check file modification time
        current_mtime = roadmap_path.stat().st_mtime

        if current_mtime > self.last_roadmap_update:
            # ROADMAP was modified
            logger.info(f"ROADMAP.md updated (mtime: {current_mtime})")
            self.last_roadmap_update = current_mtime
            return True

        return False

    def _coordinate_architect(self):
        """
        Coordinate architect to maintain spec backlog.

        Logic:
        1. Use RoadmapParser to get ALL priorities (handles all ROADMAP formats)
        2. Use ArchitectCoordinator to identify missing specs
        3. Spawn architect instances for first N missing specs (parallel execution)
        4. Target: Always have 2-3 specs ahead of code_developer
        """
        # Load all priorities from ROADMAP using skill (SINGLE SOURCE OF TRUTH)
        result = self.roadmap_skill.execute(operation="get_all_priorities")

        if result.get("error"):
            logger.error(f"Failed to get priorities: {result['error']}")
            return

        priorities = result.get("result", [])

        if not priorities:
            logger.debug("No priorities found in ROADMAP")
            return

        # Use ArchitectCoordinator to get all missing specs
        missing_specs = self.architect_coordinator.get_missing_specs(priorities)

        if not missing_specs:
            logger.debug("No missing specs, architect idle")
            return

        # Log how many specs are missing
        logger.info(f"📋 Found {len(missing_specs)} priorities without specs")

        # Prioritize: Create specs for first N missing (spec backlog target)
        for priority in missing_specs[: self.config.spec_backlog_target]:
            # Check if already creating this spec
            if self._is_spec_in_progress(priority["number"]):
                # Construct name from us_id or number for logging
                priority_name = priority.get("us_id") or f"PRIORITY {priority['number']}"
                logger.debug(f"Spec for {priority_name} already in progress")
                continue

            # Spawn architect to create spec
            # Skill returns: us_id (e.g., "US-059") and number (e.g., "59")
            priority_name = priority.get("us_id") or f"PRIORITY {priority['number']}"
            priority_number = priority["number"]  # e.g., "59" or "1.5"
            logger.info(f"🏗️  Spawning architect for {priority_name} spec creation")

            result = self.agent_mgmt.execute(
                action="spawn_architect",
                priority_number=priority_number,
                priority_name=priority_name,
                task_type="create_spec",
                auto_approve=True,
            )

            if result["error"]:
                logger.error(f"Failed to spawn architect for {priority_name}: {result['error']}")
                continue

            # Track that we're working on this spec
            agent_info = result["result"]
            self._track_spec_task(priority_number, agent_info["task_id"], agent_info["pid"])
            logger.info(
                f"✅ Architect spawned for {priority_name} (PID: {agent_info['pid']}, task: {agent_info['task_id']})"
            )

    def _coordinate_refactoring_analysis(self):
        """
        Coordinate architect for weekly refactoring analysis.

        Logic:
        1. Check if 7 days since last analysis
        2. If yes: notify user to run codebase analysis (requires interactive input)
        3. User runs: poetry run architect analyze-codebase
        4. Architect analyzes codebase and reports refactoring opportunities
        """
        # Check last refactoring analysis time
        last_analysis = self.current_state.get("last_refactoring_analysis", 0)
        days_since_analysis = (time.time() - last_analysis) / 86400  # seconds to days

        if days_since_analysis < 7:
            # Not time yet
            logger.debug(f"Refactoring analysis not needed (last run {days_since_analysis:.1f} days ago)")
            return

        # Check if we already sent a notification recently (avoid spam)
        last_notification = self.current_state.get("last_analysis_notification", 0)
        hours_since_notification = (time.time() - last_notification) / 3600

        if hours_since_notification < 24:
            logger.debug("Analysis notification already sent recently")
            return

        logger.info("📢 Weekly codebase analysis is due - notifying user")

        # Send notification asking user to run analysis
        self.notifications.create_notification(
            type="action_required",
            title="Weekly Codebase Analysis Due",
            message=f"Architect codebase analysis is overdue ({days_since_analysis:.1f} days since last run).\n\n"
            f"Please run: poetry run architect analyze-codebase\n\n"
            f"This will:\n"
            f"- Analyze complexity metrics (radon)\n"
            f"- Detect large files (>500 LOC)\n"
            f"- Check test coverage\n"
            f"- Extract TODO/FIXME comments\n\n"
            f"After running, the analysis report will be saved to docs/architecture/",
            priority="normal",
            sound=False,  # CFR-009
            agent_id="orchestrator",
        )

        # Track that we sent the notification
        self.current_state["last_analysis_notification"] = time.time()
        logger.info("✅ User notified to run codebase analysis")

    def _coordinate_planning(self):
        """
        Coordinate project_manager for weekly auto-planning.

        Logic:
        1. Check ROADMAP health
        2. If health < 80: spawn project_manager for planning
        3. If 7 days since last planning: spawn for weekly review
        4. project_manager analyzes gaps, creates new priorities
        """
        # Check last planning time
        last_planning = self.current_state.get("last_planning", 0)
        days_since_planning = (time.time() - last_planning) / 86400

        # Weekly planning OR low health
        needs_planning = days_since_planning >= 7

        if not needs_planning:
            logger.debug(f"Auto-planning not needed (last run {days_since_planning:.1f} days ago)")
            return

        logger.info("📋 Spawning project_manager for auto-planning")

        result = self.agent_mgmt.execute(
            action="spawn_project_manager",
            task_type="auto_planning",
            auto_approve=True,
        )

        if result["error"]:
            logger.error(f"Failed to spawn project_manager for planning: {result['error']}")
            return

        # Update last planning time
        self.current_state["last_planning"] = time.time()
        logger.info(f"✅ project_manager spawned for planning (PID: {result['result']['pid']})")

    def _coordinate_code_reviewer(self):
        """
        Coordinate code-reviewer to review recent commits.

        Logic:
        1. Get list of recent commits (last 24 hours)
        2. Check which commits have been reviewed (docs/code-reviews/REVIEW-{commit}.md)
        3. Spawn code-reviewer for unreviewed commits
        4. Limit to 3 reviews at a time to avoid overwhelming
        """
        try:
            # Get commits from last 24 hours on roadmap branch
            result = subprocess.run(
                ["git", "log", "--since='24 hours ago'", "--format=%H", "roadmap"],
                capture_output=True,
                text=True,
                check=True,
            )

            recent_commits = [sha.strip() for sha in result.stdout.strip().split("\n") if sha.strip()]

            if not recent_commits:
                logger.debug("No recent commits to review")
                return

            # Filter for unreviewed commits
            unreviewed_commits = []
            reviews_dir = Path("docs/code-reviews")
            reviews_dir.mkdir(parents=True, exist_ok=True)

            for commit_sha in recent_commits:
                review_file = reviews_dir / f"REVIEW-{commit_sha[:8]}.md"
                if not review_file.exists():
                    unreviewed_commits.append(commit_sha)

            if not unreviewed_commits:
                logger.debug(f"All {len(recent_commits)} recent commits have been reviewed")
                return

            logger.info(f"📝 Found {len(unreviewed_commits)} unreviewed commits")

            # Limit to 3 reviews at a time
            for commit_sha in unreviewed_commits[:3]:
                # Check if already reviewing this commit
                task_id = f"review-{commit_sha[:8]}"
                if task_id in self.current_state.get("active_tasks", {}):
                    logger.debug(f"Already reviewing commit {commit_sha[:8]}")
                    continue

                logger.info(f"📝 Spawning code-reviewer for commit {commit_sha[:8]}")

                result = self.agent_mgmt.execute(
                    action="spawn_code_reviewer",
                    commit_sha=commit_sha,
                    auto_approve=True,
                )

                if result["error"]:
                    logger.error(f"Failed to spawn code-reviewer for {commit_sha[:8]}: {result['error']}")
                    continue

                # Track that we're reviewing this commit
                if "active_tasks" not in self.current_state:
                    self.current_state["active_tasks"] = {}

                self.current_state["active_tasks"][task_id] = {
                    "task_id": task_id,
                    "pid": result["result"]["pid"],
                    "started_at": time.time(),
                    "type": "code_review",
                    "commit_sha": commit_sha,
                }

                logger.info(f"✅ code-reviewer spawned for commit {commit_sha[:8]} (PID: {result['result']['pid']})")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get recent commits: {e}")
        except Exception as e:
            logger.error(f"Error coordinating code-reviewer: {e}", exc_info=True)

    def _check_worktree_merges(self):
        """
        Check for completed worktrees and notify architect when merges are needed.

        Logic:
        1. Detect all roadmap-* branches with completed work (commits ahead of roadmap)
        2. For each completed worktree:
           a. Extract US number from commit message
           b. Create high-priority notification for architect
           c. Include merge command in notification
        3. Architect receives notification and uses merge-worktree-branches skill
        4. After merge, architect notifies orchestrator
        5. Orchestrator can then clean up worktree
        """
        # Use ArchitectCoordinator to check and notify
        notifications_sent = self.architect_coordinator.check_and_notify_merges()

        if notifications_sent > 0:
            logger.info(f"📬 Sent {notifications_sent} merge notification(s) to architect")

    def _coordinate_code_developer(self):
        """
        Coordinate code_developer to implement next priority.

        NEW: Attempts parallel execution when possible!

        Logic:
        1. Get next 2-3 PLANNED priorities with specs
        2. Check task-separator skill for independence
        3. If independent: spawn parallel code_developers in worktrees
        4. If not independent: fall back to sequential execution
        """
        # Use roadmap-management skill (SINGLE SOURCE OF TRUTH)
        result = self.roadmap_skill.execute(operation="get_all_priorities")

        if result.get("error"):
            logger.error(f"Failed to get priorities: {result['error']}")
            return

        priorities = result.get("result", [])

        if not priorities:
            return

        # Filter for planned priorities with specs
        # NOTE: Skill returns: status may include emoji and text like "📝 PLANNED - AWAITING ARCHITECT TECHNICAL SPEC"
        planned_priorities = []
        for p in priorities:
            # Check if planned (flexible matching for "Planned" or "PLANNED" in status)
            status = p.get("status", "").upper()
            if "PLANNED" not in status and "PLAN" not in status:
                continue

            # Check if spec exists
            # Use US number for spec lookup (e.g., "US-104" -> "SPEC-104-*.md")
            # Skill returns: number="20" (PRIORITY number), us_id="US-104"
            # Specs are named with US number, not PRIORITY number
            us_id = p.get("us_id")
            spec_number = None

            if us_id:
                # Extract number from us_id (e.g., "US-104" -> "104")
                spec_number = us_id.replace("US-", "")
            else:
                # Fallback to priority number if no us_id
                spec_number = p.get("number")

            if spec_number:
                spec_pattern = f"SPEC-{spec_number}-*.md"
                spec_dir = Path("docs/architecture/specs")
                spec_files = list(spec_dir.glob(spec_pattern))
                if len(spec_files) > 0:
                    p["has_spec"] = True
                    p["spec_path"] = str(spec_files[0])
                    planned_priorities.append(p)

        # BUG-074: Filter out recently completed priorities (cooldown period)
        current_time = time.time()
        filtered_priorities = []
        for p in planned_priorities:
            priority_num = str(p.get("number"))
            if priority_num in self.recently_completed:
                completion_time = self.recently_completed[priority_num]
                elapsed = current_time - completion_time
                if elapsed < self.completion_cooldown_seconds:
                    logger.debug(
                        f"Skipping priority {priority_num} (recently completed {elapsed:.0f}s ago, cooldown: {self.completion_cooldown_seconds}s)"
                    )
                    continue
                else:
                    # Cooldown expired, remove from tracking
                    del self.recently_completed[priority_num]
            filtered_priorities.append(p)

        planned_priorities = filtered_priorities

        if not planned_priorities:
            logger.info("No planned priorities with specs (after cooldown filter), code_developer idle")
            return

        # Check if any work already in progress (query database, not in-memory state)
        # BUG-070 fix: Must query database because in-memory state clears on restart
        result = self.agent_mgmt.execute(action="list_active_agents", include_completed=False)

        if result.get("error"):
            logger.error(f"Failed to check active agents: {result['error']}")
            return

        active_agents = result.get("result", {}).get("active_agents", [])
        active_impl_count = sum(1 for agent in active_agents if agent.get("task_type") == "implementation")

        if active_impl_count > 0:
            logger.debug(f"{active_impl_count} implementations already in progress (database check)")
            return

        # Try parallel execution (2-3 priorities)
        max_parallel = min(3, len(planned_priorities))

        if max_parallel >= 2:
            # Attempt parallel execution
            candidate_priorities = planned_priorities[:max_parallel]
            candidate_ids = [p["number"] for p in candidate_priorities]

            logger.info(f"🔍 Checking if {len(candidate_ids)} priorities can run in parallel...")

            # Call task-separator skill
            parallel_result = self._check_parallel_viability(candidate_ids)

            if parallel_result["valid"] and len(parallel_result["independent_pairs"]) > 0:
                # Parallel execution possible!
                logger.info(f"✅ Found {len(parallel_result['independent_pairs'])} independent pairs!")
                logger.info(f"🚀 Spawning parallel code_developers in worktrees...")

                # Use ParallelExecutionCoordinator
                self._spawn_parallel_execution(candidate_ids)
                return

            else:
                logger.info(f"❌ Cannot parallelize: {parallel_result.get('reason', 'file conflicts')}")
                logger.info("📝 Falling back to sequential execution...")

        # Fall back to sequential execution (with MANDATORY worktree - CFR-013)
        next_priority = planned_priorities[0]

        # Check if already implementing
        if self._is_implementation_in_progress(next_priority["number"]):
            logger.debug(f"Implementation for PRIORITY {next_priority['number']} already in progress")
            return

        # CFR-013 MANDATORY ISOLATION: Create worktree for code_developer
        # NO TWO code_developers can EVER work in the same directory
        priority_name = next_priority.get("us_id") or f"PRIORITY {next_priority['number']}"
        logger.info(f"⚙️  Creating worktree for {priority_name} implementation (CFR-013 compliance)")

        # Generate unique worktree ID
        worktree_id = self._generate_worktree_id()
        worktree_path = f"../worktree-{worktree_id}"
        worktree_branch = f"roadmap-{worktree_id}"

        # Create worktree
        try:
            result = subprocess.run(
                ["git", "worktree", "add", worktree_path, "-b", worktree_branch],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"✅ Created worktree: {worktree_path} (branch: {worktree_branch})")

            # CRITICAL: Symlink data/ directory to share databases across worktrees
            # Without this, each worktree has isolated databases and can't coordinate
            worktree_abs = Path(self.repo_root) / worktree_path
            worktree_data = worktree_abs / "data"
            main_data = Path(self.repo_root) / "data"

            if worktree_data.exists() and not worktree_data.is_symlink():
                # Remove copied data directory
                shutil.rmtree(worktree_data)
                logger.debug(f"Removed copied data directory: {worktree_data}")

            if not worktree_data.exists():
                # Create symlink to main repo's data directory
                worktree_data.symlink_to(main_data, target_is_directory=True)
                logger.info(f"✅ Symlinked data/ directory: {worktree_data} → {main_data}")

            # CRITICAL: Copy .env file to worktree (required for environment variables)
            env_file = Path(self.repo_root) / ".env"
            worktree_env = worktree_abs / ".env"
            if env_file.exists() and not worktree_env.exists():
                shutil.copy2(env_file, worktree_env)
                logger.info(f"✅ Copied .env file to worktree: {worktree_env}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worktree: {e.stderr}")
            return
        except Exception as e:
            logger.error(f"Failed to setup worktree data symlink: {e}")
            # Try to cleanup worktree on setup failure
            try:
                subprocess.run(["git", "worktree", "remove", worktree_path, "--force"], cwd=self.repo_root)
                subprocess.run(["git", "branch", "-D", worktree_branch], cwd=self.repo_root)
            except Exception:
                pass
            return

        # Spawn code_developer IN worktree
        logger.info(f"⚙️  Spawning code_developer for {priority_name} in worktree {worktree_path}")

        result = self.agent_mgmt.execute(
            action="spawn_code_developer",
            priority_number=next_priority["number"],
            worktree_path=worktree_path,
            auto_approve=True,
        )

        if result.get("error"):
            logger.error(f"Failed to spawn code_developer for {priority_name}: {result['error']}")
            # Cleanup worktree on spawn failure
            try:
                subprocess.run(["git", "worktree", "remove", worktree_path, "--force"], cwd=self.repo_root)
                subprocess.run(["git", "branch", "-D", worktree_branch], cwd=self.repo_root)
            except Exception:
                pass
            return

        agent_info = result["result"]

        # Track implementation task (with worktree info)
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        task_key = f"impl_{next_priority['number']}"
        self.current_state["active_tasks"][task_key] = {
            "task_id": agent_info["task_id"],
            "pid": agent_info["pid"],
            "started_at": time.time(),
            "type": "implementation",
            "priority_number": next_priority["number"],
            "worktree_path": worktree_path,
            "worktree_branch": worktree_branch,
        }

        logger.info(
            f"✅ code_developer spawned for {priority_name} (PID: {agent_info['pid']}, worktree: {worktree_path})"
        )

    def _monitor_tasks(self):
        """
        Monitor in-progress tasks and handle timeouts/failures.

        Checks:
        - Task completion (move from in_progress to completed)
        - Timeouts (task running > 2 hours)
        - Failures (task failed, retry or escalate)
        """
        # Get active agents from database (auto-cleans completed agents)
        result = self.agent_mgmt.execute(action="list_active_agents", include_completed=False)

        if result.get("error"):
            logger.error(f"Failed to list active agents: {result['error']}")
            return

        active_agents = result.get("result", {}).get("active_agents", [])
        active_pids = {agent["pid"] for agent in active_agents}

        # Clean up completed tasks from active_tasks
        active_tasks = self.current_state.get("active_tasks", {})
        completed_tasks = []

        for task_key, task_info in list(active_tasks.items()):
            # Check if PID is still active
            task_pid = task_info.get("pid")

            if task_pid and task_pid not in active_pids:
                # Task completed, remove from active_tasks
                completed_tasks.append(task_key)
                logger.debug(f"✅ Task {task_key} completed (PID {task_pid} finished)")

                # CFR-013: Clean up worktree if task had one
                worktree_path = task_info.get("worktree_path")
                worktree_branch = task_info.get("worktree_branch")

                if worktree_path and worktree_branch:
                    logger.info(f"🧹 Cleaning up worktree for completed task {task_key}")
                    self._cleanup_worktree(worktree_path, worktree_branch)

                del active_tasks[task_key]
                continue

            # Check timeout for still-running tasks
            started_at = task_info.get("started_at")
            if started_at is None:
                # Skip if no started_at timestamp (shouldn't happen, but defensive)
                continue

            task_age = time.time() - started_at

            if task_age > self.config.task_timeout_seconds:
                logger.warning(f"⚠️  Task timeout: {task_key} ({task_age:.0f}s)")

                self.notifications.create_notification(
                    type="warning",
                    title="Task Timeout Detected",
                    message=f"Task {task_key} running for {task_age / 3600:.1f} hours",
                    priority="high",
                    sound=False,  # CFR-009
                    agent_id="orchestrator",
                )

        if completed_tasks:
            logger.info(f"🧹 Cleaned up {len(completed_tasks)} completed tasks from active_tasks")

    def _get_high_priority_bugs(self) -> List[Dict[str, Any]]:
        """
        Query bug tickets for open Critical/High priority bugs using database.

        Returns:
            List of bug dictionaries sorted by priority (Critical first)
        """
        try:
            # Query open Critical/High priority bugs from database
            critical_bugs = self.bug_skill.query_bugs(status="open", priority="Critical", limit=10)

            high_bugs = self.bug_skill.query_bugs(status="open", priority="High", limit=10)

            # Combine and convert to expected format
            bugs = []
            for bug in critical_bugs + high_bugs:
                bugs.append(
                    {
                        "number": bug["bug_number"],
                        "file": bug["ticket_file_path"],
                        "title": bug["title"],
                        "status": bug["status"],
                        "priority": bug["priority"],
                    }
                )

            # Sort by priority (Critical first, then High)
            bugs.sort(key=lambda b: (0 if b["priority"] == "Critical" else 1, b["number"]))

            return bugs

        except Exception as e:
            logger.error(f"Failed to query high-priority bugs: {e}", exc_info=True)
            return []

    def _coordinate_bug_fix(self, bug: Dict[str, Any]):
        """
        Coordinate code_developer to fix a bug.

        Args:
            bug: Bug dictionary with number, title, priority, etc.
        """
        bug_number = bug["number"]

        # Check if bug fix already in progress
        task_key = f"bug_{bug_number}"
        if task_key in self.current_state.get("active_tasks", {}):
            logger.debug(f"Bug fix for BUG-{bug_number:03d} already in progress")
            return

        logger.info(f"🔧 Delegating bug fix to code_developer: BUG-{bug_number:03d}")
        logger.info(f"   Title: {bug['title']}")
        logger.info(f"   Priority: {bug['priority']}")

        # Update bug status to "in_progress" using bug tracking skill
        self.bug_skill.update_bug_status(
            bug_number=bug_number, status="in_progress", notes="Spawned code_developer agent"
        )

        # Create notification
        self.notifications.create_notification(
            type="info",
            title="Bug Fix Started",
            message=f"code_developer working on BUG-{bug_number:03d}: {bug['title']}",
            priority="high" if bug["priority"] == "Critical" else "normal",
            sound=False,  # CFR-009
            agent_id="orchestrator",
        )

        # Spawn code_developer for bug fix
        result = self.agent_mgmt.execute(
            action="spawn_code_developer_bug_fix",
            bug_number=bug_number,
            bug_title=bug["title"],
            auto_approve=True,
        )

        if result["error"]:
            logger.error(f"Failed to spawn code_developer for BUG-{bug_number:03d}: {result['error']}")
            # Revert bug status to open if spawn failed
            self.bug_skill.update_bug_status(
                bug_number=bug_number, status="open", notes=f"Failed to spawn agent: {result['error']}"
            )
            return

        # Track that we're working on this bug
        agent_info = result["result"]
        self.current_state.setdefault("active_tasks", {})[task_key] = {
            "task_id": f"bug-{bug_number}",
            "started_at": time.time(),
            "type": "bug_fix",
            "bug_number": bug_number,
            "pid": agent_info["pid"],
        }

        logger.info(f"✅ code_developer spawned for BUG-{bug_number:03d} (PID: {agent_info['pid']})")

    def _is_spec_in_progress(self, priority_number: int) -> bool:
        """Check if spec creation is already in progress for priority."""
        return f"spec_{priority_number}" in self.current_state.get("active_tasks", {})

    def _is_implementation_in_progress(self, priority_number: int) -> bool:
        """Check if implementation is already in progress for priority."""
        return f"impl_{priority_number}" in self.current_state.get("active_tasks", {})

    def _generate_worktree_id(self) -> str:
        """Generate unique worktree ID.

        CFR-013 compliance: Ensures each code_developer gets isolated worktree.

        Returns:
            Unique worktree ID (e.g., "wt1", "wt2", "wt3")

        Note:
            Checks BOTH database and git branches to avoid conflicts with orphaned branches
            (BUG-071 fix)
        """
        # Query database for existing worktrees
        result = self.agent_mgmt.execute(action="list_active_agents", include_completed=False)

        if result.get("error"):
            # Fallback: use timestamp-based ID
            import time

            return f"wt-{int(time.time())}"

        active_agents = result.get("result", {}).get("active_agents", [])

        # Find highest existing worktree number from database
        max_wt_num = 0
        for agent in active_agents:
            worktree_path = agent.get("worktree_path", "")
            if worktree_path and "worktree-wt" in worktree_path:
                try:
                    # Extract number from "../worktree-wt5" -> 5
                    wt_num = int(worktree_path.split("worktree-wt")[1].split("/")[0])
                    max_wt_num = max(max_wt_num, wt_num)
                except (ValueError, IndexError):
                    pass

        # BUG-071 FIX: Also check git branches for orphaned worktree branches
        try:
            result = subprocess.run(
                ["git", "branch", "--list", "roadmap-wt*"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    # Extract number from "  roadmap-wt5" or "+ roadmap-wt5"
                    match = re.search(r"roadmap-wt(\d+)", line.strip())
                    if match:
                        wt_num = int(match.group(1))
                        max_wt_num = max(max_wt_num, wt_num)
        except Exception as e:
            logger.warning(f"Failed to check git branches for worktree IDs: {e}")

        # Return next available ID
        next_id = max_wt_num + 1
        return f"wt{next_id}"

    def _cleanup_worktree(self, worktree_path: str, worktree_branch: str):
        """Clean up worktree after code_developer completes.

        CFR-013 compliance: Remove worktree directory and branch after task completion.

        Args:
            worktree_path: Path to worktree (e.g., "../worktree-wt1")
            worktree_branch: Branch name (e.g., "roadmap-wt1")
        """
        try:
            # Step 1: Remove worktree directory
            result = subprocess.run(
                ["git", "worktree", "remove", worktree_path, "--force"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info(f"✅ Removed worktree: {worktree_path}")
            else:
                logger.warning(f"⚠️  Failed to remove worktree {worktree_path}: {result.stderr}")

            # Step 2: Delete branch
            result = subprocess.run(
                ["git", "branch", "-D", worktree_branch],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info(f"✅ Deleted branch: {worktree_branch}")
            else:
                logger.warning(f"⚠️  Failed to delete branch {worktree_branch}: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout cleaning up worktree {worktree_path}")
        except Exception as e:
            logger.error(f"❌ Error cleaning up worktree {worktree_path}: {e}")

    def _track_spec_task(self, priority_number: int, task_id: str, pid: Optional[int] = None):
        """Track spec creation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"spec_{priority_number}"] = {
            "task_id": task_id,
            "pid": pid,
            "started_at": time.time(),
            "type": "spec_creation",
        }

    def _track_implementation_task(self, priority_number: int, task_id: str):
        """Track implementation task."""
        if "active_tasks" not in self.current_state:
            self.current_state["active_tasks"] = {}

        self.current_state["active_tasks"][f"impl_{priority_number}"] = {
            "task_id": task_id,
            "started_at": time.time(),
            "type": "implementation",
        }

    def _check_parallel_viability(self, priority_ids: List[int]) -> Dict[str, Any]:
        """Check if priorities can run in parallel using task-separator skill.

        Args:
            priority_ids: List of PRIORITY numbers to check

        Returns:
            Dict with validation result from task-separator skill
        """
        try:
            # Import and execute task-separator skill
            import importlib.util

            skill_path = self.repo_root / ".claude" / "skills" / "architect" / "task-separator" / "task_separator.py"

            if not skill_path.exists():
                return {"valid": False, "reason": f"task-separator skill not found: {skill_path}"}

            spec = importlib.util.spec_from_file_location("task_separator", skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call skill
            result = module.main({"priority_ids": priority_ids})
            return result

        except Exception as e:
            logger.error(f"Error running task-separator skill: {e}", exc_info=True)
            return {"valid": False, "reason": f"Error: {e}"}

    def _spawn_parallel_execution(self, priority_ids: List[int]):
        """Spawn parallel code_developer instances in worktrees.

        Args:
            priority_ids: List of PRIORITY numbers to execute in parallel
        """
        try:
            from coffee_maker.orchestrator.parallel_execution_coordinator import ParallelExecutionCoordinator

            logger.info(f"🚀 Launching ParallelExecutionCoordinator for {len(priority_ids)} priorities")

            # Create coordinator
            coordinator = ParallelExecutionCoordinator(
                repo_root=self.repo_root, max_instances=min(len(priority_ids), 3), auto_merge=True
            )

            # Execute parallel batch
            result = coordinator.execute_parallel_batch(priority_ids, auto_approve=True)

            if result["success"]:
                logger.info(f"✅ Parallel execution completed!")
                logger.info(f"   Priorities executed: {result['priorities_executed']}")
                logger.info(f"   Duration: {result['duration_seconds']:.1f}s")
                logger.info(f"   Merge results: {result['merge_results']}")

                # Track completed implementations
                for priority_id in result["priorities_executed"]:
                    task_key = f"impl_{priority_id}"
                    if task_key in self.current_state.get("active_tasks", {}):
                        del self.current_state["active_tasks"][task_key]

                    # BUG-074: Mark as recently completed to prevent immediate re-spawning
                    self.recently_completed[str(priority_id)] = time.time()
                    logger.info(
                        f"  Marked priority {priority_id} as recently completed (cooldown: {self.completion_cooldown_seconds}s)"
                    )

            else:
                logger.error(f"❌ Parallel execution failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Error spawning parallel execution: {e}", exc_info=True)

    def _handle_cycle_error(self, error: Exception):
        """
        Handle errors during work cycle.

        Args:
            error: Exception that occurred
        """
        logger.error(f"Work cycle error: {error}", exc_info=True)

        # Log to error recovery file
        error_log_path = Path("data/orchestrator/error_recovery.log")
        error_log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(error_log_path, "a") as f:
            f.write(f"{time.time()}: {error}\n")

        # Notify user for critical errors
        if isinstance(error, (IOError, PermissionError)):
            self.notifications.create_notification(
                type="error",
                title="Orchestrator Error",
                message=f"Critical error: {error}. Work loop may need manual restart.",
                priority="critical",
                sound=False,  # CFR-009
                agent_id="orchestrator",
            )

    def _handle_shutdown(self, signum, frame):
        """
        Handle shutdown signals (SIGINT, SIGTERM).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.running = False

    def _shutdown(self):
        """Graceful shutdown: save state and stop orchestrator."""
        logger.info("🛑 Shutting down Orchestrator Work Loop")

        # Save final state
        self._save_state()

        self.notifications.create_notification(
            type="info",
            title="Orchestrator Stopped",
            message="Continuous work loop has been stopped. State saved for recovery.",
            priority="normal",
            sound=False,  # CFR-009
            agent_id="orchestrator",
        )

        logger.info("✅ Graceful shutdown complete")

    def _save_state(self):
        """Save orchestrator state to database for crash recovery (CFR-014 compliant)."""
        try:
            import sqlite3

            db_path = Path("data/orchestrator.db")
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # Save configuration state to orchestrator_state table
            config_keys = [
                ("last_roadmap_update", str(self.last_roadmap_update)),
                ("last_refactoring_analysis", str(self.current_state.get("last_refactoring_analysis", 0))),
                ("last_analysis_notification", str(self.current_state.get("last_analysis_notification", 0))),
                ("last_planning", str(self.current_state.get("last_planning", 0))),
            ]

            # Save orchestrator start time if set
            if self.start_time:
                config_keys.append(("orchestrator_start_time", self.start_time.isoformat()))

            for key, value in config_keys:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO orchestrator_state (key, value, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (key, value, now),
                )

            # Save active_tasks as JSON blob (temporary until full migration)
            active_tasks_json = json.dumps(self.current_state.get("active_tasks", {}))
            cursor.execute(
                """
                INSERT OR REPLACE INTO orchestrator_state (key, value, updated_at)
                VALUES (?, ?, ?)
                """,
                ("active_tasks", active_tasks_json, now),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to save state to database: {e}", exc_info=True)

    def _load_state(self):
        """Load orchestrator state from database after crash/restart (CFR-014 compliant)."""
        try:
            import sqlite3

            db_path = Path("data/orchestrator.db")

            if not db_path.exists():
                logger.info("No database found, starting fresh")
                return

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Load configuration state from orchestrator_state table
            cursor.execute("SELECT key, value FROM orchestrator_state")
            rows = cursor.fetchall()

            for row in rows:
                key = row["key"]
                value = row["value"]

                if key == "last_roadmap_update":
                    self.last_roadmap_update = float(value)
                elif key == "active_tasks":
                    # Load active_tasks from JSON blob
                    self.current_state["active_tasks"] = json.loads(value)
                elif key == "orchestrator_start_time":
                    # Load start time for crash recovery
                    self.start_time = datetime.fromisoformat(value)
                elif key in ["last_refactoring_analysis", "last_analysis_notification", "last_planning"]:
                    self.current_state[key] = float(value)

            conn.close()

            logger.info(f"Loaded previous state from database (last_roadmap_update: {self.last_roadmap_update})")

        except Exception as e:
            logger.warning(f"Failed to load state from database: {e}, starting fresh")
            self.current_state = {}
