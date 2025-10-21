"""Process management for code_developer daemon.

This module provides functionality to detect, start, stop, and monitor
the code_developer daemon process.
"""

import logging
import psutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict

from coffee_maker.utils.file_io import read_json_file, write_json_file

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages code_developer daemon process lifecycle.

    Provides methods to:
    - Detect if daemon is running
    - Get detailed daemon status
    - Start daemon in background
    - Stop daemon gracefully
    - Track current task
    """

    def __init__(self):
        """Initialize process manager with config directory."""
        self.config_dir = Path.home() / ".coffee_maker"
        self.config_dir.mkdir(exist_ok=True)

        self.pid_file = self.config_dir / "daemon.pid"
        self.status_file = self.config_dir / "daemon_status.json"

        logger.debug(f"ProcessManager initialized (config dir: {self.config_dir})")

    def is_daemon_running(self) -> bool:
        """Check if code_developer daemon is running.

        Verifies both that the PID exists and that it's actually
        the autonomous daemon (not just any Claude process).

        IMPORTANT: Only recognizes autonomous daemon with --auto-approve flag.
        This distinguishes the daemon from interactive Claude Code sessions.

        Returns:
            True if daemon is running, False otherwise
        """
        pid = self._read_pid_file()
        if pid is None:
            return False

        try:
            # Check if process exists
            process = psutil.Process(pid)

            # Verify it's actually the daemon (not a recycled PID or interactive session)
            cmdline = " ".join(process.cmdline())

            # Must be code-developer process
            is_code_developer = (
                "code-developer" in cmdline
                or "daemon_cli.py" in cmdline
                or "coffee_maker.autonomous.daemon_cli" in cmdline
            )

            # Should have --auto-approve flag (autonomous mode)
            # This distinguishes daemon from interactive Claude Code sessions
            has_auto_approve = "--auto-approve" in cmdline

            if not is_code_developer:
                logger.warning(f"PID {pid} exists but is not code_developer: {cmdline}")
                self._clean_stale_pid()
                return False

            if not has_auto_approve:
                logger.info(f"PID {pid} is code_developer but not autonomous (missing --auto-approve)")
                # Don't clean PID - it might be an interactive session we don't want to interfere with
                # But report it as "not the daemon"
                return False

            return True

        except psutil.NoSuchProcess:
            logger.debug(f"PID {pid} no longer exists")
            self._clean_stale_pid()
            return False
        except Exception as e:
            logger.error(f"Error checking daemon status: {e}")
            return False

    def get_daemon_status(self) -> Dict:
        """Get detailed daemon status information.

        Returns:
            Dict with keys:
            - running: bool (is daemon running)
            - pid: int or None (process ID)
            - status: str (stopped/idle/working/error)
            - current_task: str or None (current task name)
            - uptime: float or None (timestamp when started)
            - cpu_percent: float (CPU usage percentage)
            - memory_mb: float (memory usage in MB)
        """
        if not self.is_daemon_running():
            return {
                "running": False,
                "status": "stopped",
                "current_task": None,
                "uptime": None,
                "pid": None,
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
            }

        pid = self._read_pid_file()

        try:
            process = psutil.Process(pid)

            # Get current task
            current_task = self._get_current_task()

            return {
                "running": True,
                "pid": pid,
                "status": "working" if current_task else "idle",
                "current_task": current_task,
                "uptime": process.create_time(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
            }
        except Exception as e:
            logger.error(f"Error getting daemon status: {e}")
            return {
                "running": False,
                "status": "error",
                "current_task": None,
                "uptime": None,
                "pid": pid,
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
            }

    def start_daemon(self, background: bool = True) -> bool:
        """Start the code_developer daemon in autonomous mode.

        IMPORTANT: Always starts daemon with --auto-approve flag for autonomous operation.
        This distinguishes the daemon from interactive Claude Code sessions.

        Args:
            background: If True, start in background. If False, run in foreground.

        Returns:
            True if daemon started successfully, False otherwise
        """
        if self.is_daemon_running():
            logger.info("Daemon is already running")
            return True

        logger.info("Starting code_developer daemon in autonomous mode...")

        # Build command with --auto-approve for autonomous operation
        # This flag distinguishes daemon from interactive Claude sessions
        cmd = ["poetry", "run", "code-developer", "--auto-approve"]

        try:
            if background:
                # Start in background (detached from parent)
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,  # Detach from terminal
                    cwd=Path.cwd(),  # Use current working directory
                )

                # Note: PID will be written by daemon itself
                logger.info(f"Daemon spawned with PID {process.pid}")

                # Wait briefly to ensure it started
                time.sleep(2)

                # Verify it's running
                if self.is_daemon_running():
                    logger.info("Daemon started successfully")
                    return True
                else:
                    logger.error("Daemon failed to start")
                    return False
            else:
                # Run in foreground (for debugging)
                subprocess.run(cmd)
                return True

        except FileNotFoundError:
            logger.error("Poetry not found. Is it installed and in PATH?")
            return False
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            return False

    def stop_daemon(self, timeout: int = 10) -> bool:
        """Stop the daemon gracefully.

        Sends SIGTERM for graceful shutdown, waits for timeout,
        then force kills if necessary.

        Args:
            timeout: Seconds to wait for graceful shutdown before force kill

        Returns:
            True if daemon stopped successfully, False otherwise
        """
        if not self.is_daemon_running():
            logger.info("Daemon is not running")
            return True

        pid = self._read_pid_file()

        logger.info(f"Stopping daemon (PID {pid})...")

        try:
            process = psutil.Process(pid)

            # Send SIGTERM for graceful shutdown
            logger.info("Sending SIGTERM for graceful shutdown...")
            process.terminate()

            # Wait for graceful exit
            try:
                process.wait(timeout=timeout)
                logger.info("Daemon stopped gracefully")
            except psutil.TimeoutExpired:
                # Force kill if timeout exceeded
                logger.warning("Graceful shutdown timed out, force killing...")
                process.kill()
                logger.info("Daemon force killed")

            # Clean up PID file
            self._clean_stale_pid()
            return True

        except psutil.NoSuchProcess:
            logger.info("Process already stopped")
            self._clean_stale_pid()
            return True
        except Exception as e:
            logger.error(f"Error stopping daemon: {e}")
            return False

    def _get_current_task(self) -> Optional[str]:
        """Get current task daemon is working on.

        Checks status file first, then falls back to ROADMAP.

        Returns:
            Task name or None if idle
        """
        # Try status file first (most accurate)
        if self.status_file.exists():
            try:
                data = read_json_file(self.status_file, default={})
                task = data.get("current_task")
                if task:
                    return task
            except Exception as e:
                logger.warning(f"Failed to read status file: {e}")

        # Fallback: Check ROADMAP for in-progress priorities
        try:
            from coffee_maker.cli.roadmap_editor import RoadmapEditor

            editor = RoadmapEditor(Path("docs/roadmap/ROADMAP.md"))
            priorities = editor.list_priorities()

            for p in priorities:
                status = p.get("status", "")
                if "🔄" in status or "In Progress" in status:
                    return p.get("name", "Unknown priority")
        except Exception as e:
            logger.warning(f"Failed to check ROADMAP: {e}")

        return None

    def _read_pid_file(self) -> Optional[int]:
        """Read PID from file.

        Returns:
            PID as integer or None if file doesn't exist/is invalid
        """
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file) as f:
                pid_str = f.read().strip()
                return int(pid_str)
        except (ValueError, IOError) as e:
            logger.warning(f"Invalid PID file: {e}")
            return None

    def _write_pid_file(self, pid: int):
        """Write PID to file.

        Args:
            pid: Process ID to write
        """
        try:
            with open(self.pid_file, "w") as f:
                f.write(str(pid))
            logger.info(f"Wrote PID {pid} to {self.pid_file}")
        except IOError as e:
            logger.error(f"Failed to write PID file: {e}")

    def _clean_stale_pid(self):
        """Remove stale PID file."""
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                logger.info("Cleaned stale PID file")
            except Exception as e:
                logger.warning(f"Failed to remove stale PID file: {e}")

    def update_status(self, current_task: Optional[str] = None):
        """Update daemon status file with current task.

        This should be called by the daemon itself.

        Args:
            current_task: Current task name, or None if idle
        """
        from datetime import datetime

        try:
            # Read existing data or create new
            data = read_json_file(self.status_file, default={"started_at": datetime.now().isoformat()})

            # Update fields
            data["current_task"] = current_task
            data["last_updated"] = datetime.now().isoformat()

            # Write back atomically
            write_json_file(self.status_file, data)

            logger.debug(f"Updated status: {current_task or 'idle'}")
        except Exception as e:
            logger.error(f"Failed to update status file: {e}")
