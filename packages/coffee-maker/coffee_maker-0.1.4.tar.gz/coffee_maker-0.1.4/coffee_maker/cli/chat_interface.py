"""Chat Interface - Interactive chat session with Rich UI.

This module provides an interactive REPL-style chat interface for managing
the roadmap with Claude AI assistance and rich terminal UI.

IMPORTANT: Communication Guidelines
    See docs/COLLABORATION_METHODOLOGY.md Section 4.6:
    - Use plain language, NOT technical shorthand (no "US-012")
    - Say "the email notification feature" not "US-012"
    - Always explain features descriptively to users

Example:
    >>> from coffee_maker.cli.chat_interface import ChatSession
    >>> from coffee_maker.cli.ai_service import AIService
    >>> from coffee_maker.cli.roadmap_editor import RoadmapEditor
    >>>
    >>> editor = RoadmapEditor(roadmap_path)
    >>> ai_service = AIService()
    >>> session = ChatSession(ai_service, editor)
    >>> session.start()
"""

import json
import logging
import os
import re
import threading
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.utils.file_io import read_json_file, write_json_file

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.assistant_bridge import AssistantBridge
from coffee_maker.cli.commands import get_command_handler, list_commands
from coffee_maker.cli.notifications import NotificationDB, NOTIF_PRIORITY_HIGH
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.process_manager import ProcessManager
from coffee_maker.autonomous.standup_generator import StandupGenerator
from coffee_maker.utils.bug_tracking_helper import get_bug_skill

logger = logging.getLogger(__name__)


class DeveloperStatusMonitor:
    """Background monitor for developer status.

    Polls developer_status.json file and maintains current status data
    for display in a persistent status bar above the prompt.

    Status is displayed as a multi-line toolbar showing:
    - Current task title and priority
    - Iteration count
    - Time elapsed and ETA
    - Progress bar
    """

    def __init__(self, poll_interval: float = 2.0):
        """Initialize status monitor.

        Args:
            poll_interval: Seconds between status checks (default: 2)
        """
        self.poll_interval = poll_interval
        # Use the same status file path as the /status command
        self.status_file = Path.home() / ".coffee_maker" / "daemon_status.json"
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Current status data (thread-safe access)
        self._status_lock = threading.Lock()
        self._current_status: Optional[Dict] = None

    def start(self):
        """Start background monitoring thread."""
        if self.is_running:
            logger.warning("Status monitor already running")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Developer status monitor started")

    def stop(self):
        """Stop background monitoring thread."""
        self.is_running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.info("Developer status monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)."""
        while self.is_running:
            try:
                self._check_status()
            except Exception as e:
                logger.error(f"Status monitor error: {e}", exc_info=True)

            time.sleep(self.poll_interval)

    def _check_status(self):
        """Check developer status file and update internal state."""
        if not self.status_file.exists():
            # File doesn't exist yet, daemon probably not running
            with self._status_lock:
                self._current_status = None
            return

        try:
            with open(self.status_file, "r") as f:
                status_data = json.load(f)

            # Store the full status data
            with self._status_lock:
                self._current_status = status_data

        except json.JSONDecodeError:
            # File might be mid-write, skip this check
            pass
        except Exception as e:
            logger.debug(f"Error checking status: {e}")

    def get_formatted_status(self) -> str:
        """Get formatted status text for toolbar display.

        Returns:
            Multi-line formatted status string for bottom toolbar
        """
        with self._status_lock:
            status_data = self._current_status

        if not status_data:
            return "⚫ code_developer: Not running"

        daemon_status = status_data.get("status", "unknown")
        current_priority = status_data.get("current_priority")
        iteration = status_data.get("iteration", 0)

        # Daemon not working on anything
        if daemon_status != "running" or not current_priority:
            return f"⚪ code_developer: Idle (iteration {iteration})"

        # Extract priority info
        priority_name = current_priority.get("name", "Unknown")
        priority_title = current_priority.get("title", "Unknown Task")
        started_at = current_priority.get("started_at")

        # Calculate time and progress
        elapsed_str = "0m"
        progress = 0
        eta_str = "unknown"

        if started_at:
            try:
                from datetime import datetime

                start_time = datetime.fromisoformat(started_at)
                elapsed = (datetime.now() - start_time).total_seconds()

                # Format elapsed time
                hours = int(elapsed / 3600)
                minutes = int((elapsed % 3600) / 60)
                if hours > 0:
                    elapsed_str = f"{hours}h {minutes}m"
                else:
                    elapsed_str = f"{minutes}m"

                # Calculate progress (assume 8 hours per task)
                progress = min(100, int((elapsed / (8 * 3600)) * 100))

                # Calculate ETA
                if progress > 0:
                    total_estimated = elapsed / (progress / 100)
                    remaining = total_estimated - elapsed
                    eta_hours = int(remaining / 3600)
                    eta_minutes = int((remaining % 3600) / 60)
                    if eta_hours > 0:
                        eta_str = f"~{eta_hours}h {eta_minutes}m"
                    else:
                        eta_str = f"~{eta_minutes}m"
            except (ValueError, ZeroDivisionError) as e:
                logger.debug(f"ETA calculation failed: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error in ETA calculation: {e}", exc_info=True)

        # Create progress bar
        bar_length = 20
        filled = int(bar_length * progress / 100)
        progress_bar = "█" * filled + "░" * (bar_length - filled)

        # Format multi-line status
        lines = [
            f"🟢 {priority_title}",
            f"▸ {priority_name} | Iteration {iteration} | Time: {elapsed_str} | ETA: {eta_str}",
        ]

        # Add subtasks if available
        subtasks = status_data.get("subtasks", [])
        if subtasks:
            lines.append("▸ Tasks:")
            for subtask in subtasks:
                name = subtask.get("name", "Unknown task")
                status = subtask.get("status", "unknown")
                duration = subtask.get("duration_seconds", 0)
                estimated = subtask.get("estimated_seconds", 0)

                # Choose emoji based on status
                if status == "completed":
                    emoji = "✓"
                elif status == "in_progress":
                    emoji = "🔄"
                elif status == "failed":
                    emoji = "❌"
                else:  # pending
                    emoji = "⏳"

                # Format duration and estimated time
                def format_time(seconds):
                    if seconds >= 60:
                        mins = seconds // 60
                        secs = seconds % 60
                        return f"{mins}m{secs}s" if secs > 0 else f"{mins}m"
                    else:
                        return f"{seconds}s"

                # Build subtask line
                if status in ["completed", "failed"]:
                    # Show actual vs estimated for finished tasks
                    actual_str = format_time(duration)
                    est_str = format_time(estimated) if estimated > 0 else "?"
                    lines.append(f"   {emoji} {name}: {actual_str} (est: {est_str})")
                elif status == "in_progress":
                    # Show current elapsed and estimated
                    if duration > 0:
                        actual_str = format_time(duration)
                        est_str = format_time(estimated) if estimated > 0 else "?"
                        lines.append(f"   {emoji} {name}: {actual_str} / {est_str}")
                    else:
                        est_str = format_time(estimated) if estimated > 0 else "?"
                        lines.append(f"   {emoji} {name} (est: {est_str})")
                else:  # pending
                    # Show only estimated
                    est_str = format_time(estimated) if estimated > 0 else "?"
                    lines.append(f"   {emoji} {name} (est: {est_str})")

        # Add progress bar at the end
        lines.append(f"▸ Progress: [{progress_bar}] {progress}%")

        return "\n".join(lines)


class ProjectManagerCompleter(Completer):
    """Auto-completer for project-manager chat.

    Provides Tab completion for:
    - Slash commands (/help, /view, /add, etc.)
    - Priority names (PRIORITY 1, PRIORITY 2, etc.)
    - File paths (when relevant)
    """

    def __init__(self, editor: RoadmapEditor):
        """Initialize completer.

        Args:
            editor: RoadmapEditor instance for priority completion
        """
        self.editor = editor
        self.commands = [
            "help",
            "view",
            "add",
            "update",
            "status",
            "start",
            "stop",
            "restart",
            "standup",
            "exit",
            "quit",
            "notifications",
        ]

    def get_completions(self, document, complete_event):
        """Generate completions based on current input.

        Args:
            document: Current document being edited
            complete_event: Completion event

        Yields:
            Completion objects
        """
        word_before_cursor = document.get_word_before_cursor()
        text_before_cursor = document.text_before_cursor

        # Complete slash commands
        if text_before_cursor.startswith("/") or (text_before_cursor == "" and word_before_cursor == ""):
            for cmd in self.commands:
                if cmd.startswith(word_before_cursor.lstrip("/")):
                    yield Completion(
                        cmd if text_before_cursor.startswith("/") else f"/{cmd}",
                        start_position=-len(word_before_cursor),
                        display_meta=f"command",
                    )

        # Complete priority names when relevant
        elif any(keyword in text_before_cursor.lower() for keyword in ["priority", "PRIORITY", "view", "update"]):
            try:
                priorities = self.editor.list_priorities()
                for priority in priorities[:15]:  # Limit to 15 for performance
                    priority_name = priority["name"]
                    if priority_name.lower().startswith(word_before_cursor.lower()):
                        yield Completion(
                            priority_name,
                            start_position=-len(word_before_cursor),
                            display_meta=f"{priority['title'][:40]}...",
                        )
            except Exception as e:
                logger.debug(f"Priority completion failed: {e}")


class ChatSession:
    """Interactive chat session manager.

    Manages the interactive REPL loop, command routing, and rich terminal UI
    for the project manager CLI.

    NOTE: When used in user_listener context, this class will be mixed with
    MessageHandlerMixin to enable orchestrator-based agent communication.

    Attributes:
        ai_service: AIService instance for natural language processing
        editor: RoadmapEditor instance for roadmap manipulation
        console: Rich console for terminal output
        history: Conversation history
        active: Session active flag

    Example:
        >>> session = ChatSession(ai_service, editor)
        >>> session.start()  # Starts interactive session
    """

    def __init__(
        self,
        ai_service: AIService,
        editor: RoadmapEditor,
        enable_streaming: bool = True,
    ):
        """Initialize chat session.

        Args:
            ai_service: AIService instance
            editor: RoadmapEditor instance
            enable_streaming: If True, use streaming responses (default: True)
        """
        self.ai_service = ai_service
        self.editor = editor
        self.console = Console()
        self.history: List[Dict] = []
        self.active = False

        # Check for streaming environment variable
        env_no_streaming = os.environ.get("PROJECT_MANAGER_NO_STREAMING", "").lower() in ["1", "true", "yes"]
        self.enable_streaming = enable_streaming and not env_no_streaming

        # Initialize process manager for daemon status
        self.process_manager = ProcessManager()
        self.daemon_status_text = ""
        self._update_status_display()

        # Initialize notification database for bidirectional communication
        self.notif_db = NotificationDB()

        # Initialize bug tracking skill for integrated bug fixing workflow (PRIORITY 2.11)
        self.bug_skill = get_bug_skill()

        # Initialize LangChain-powered assistant for complex questions (PRIORITY 2.9.5)
        # Assistant uses tools to help with analysis, debugging, code search, etc.
        self.assistant = AssistantBridge(action_callback=self._display_assistant_action)

        # Initialize developer status monitor for real-time updates
        self.status_monitor = DeveloperStatusMonitor(poll_interval=2.0)

        # Initialize User Story Command Handler for /US command (US-012)
        from coffee_maker.cli.commands.user_story_command import UserStoryCommandHandler

        self.us_handler = UserStoryCommandHandler(ai_service=self.ai_service, roadmap_editor=self.editor)

        # Setup prompt-toolkit for advanced input
        self._setup_prompt_session()

        # Setup session persistence
        self.session_dir = Path.home() / ".project_manager" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / "default.json"

        # Load previous session if exists
        self._load_session()

        logger.debug(f"ChatSession initialized (streaming={'enabled' if self.enable_streaming else 'disabled'})")

    def _setup_prompt_session(self):
        """Setup prompt-toolkit session with history, completion, and key bindings."""
        # History file location
        history_dir = Path.home() / ".project_manager"
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / "chat_history.txt"

        # Key bindings for multi-line input
        bindings = KeyBindings()

        @bindings.add("enter")
        def _(event):
            """Submit on Enter."""
            event.current_buffer.validate_and_handle()

        @bindings.add("escape", "enter")  # Alt+Enter for multi-line
        def _(event):
            """Insert newline on Alt+Enter."""
            event.current_buffer.insert_text("\n")

        # Create prompt session with better multi-line support and status bar
        self.prompt_session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=ProjectManagerCompleter(self.editor),
            complete_while_typing=False,  # Complete only on Tab
            multiline=False,  # Will be controlled by key bindings
            key_bindings=bindings,
            enable_history_search=True,  # Ctrl+R for reverse search
            prompt_continuation="... ",  # Continuation indicator for multi-line (like claude-cli)
            bottom_toolbar=lambda: self.status_monitor.get_formatted_status(),  # Persistent status bar
            refresh_interval=2,  # Refresh toolbar every 2 seconds
        )

    def _display_assistant_action(self, action: str):
        """Display assistant action in real-time.

        PRIORITY 2.9.5: Transparent Assistant Integration

        Called by AssistantBridge when assistant uses a tool.
        Shows user what the assistant is doing.

        Args:
            action: Action description (e.g., "🔧 read_file: daemon.py")
        """
        self.console.print(f"[dim]{action}[/]")

    def _load_session(self):
        """Load previous conversation history from file."""
        if self.session_file.exists():
            try:
                data = read_json_file(self.session_file, default={"history": []})
                self.history = data.get("history", [])
                logger.info(f"Loaded {len(self.history)} messages from previous session")
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")
                self.history = []

    def _save_session(self):
        """Save conversation history to file."""
        try:
            write_json_file(
                self.session_file,
                {
                    "history": self.history,
                    "last_updated": datetime.now().isoformat(),
                },
            )
            logger.debug(f"Saved {len(self.history)} messages to session")
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")

    def _update_status_display(self):
        """Update daemon status text for display."""
        status = self.process_manager.get_daemon_status()

        if status["running"]:
            if status["current_task"]:
                emoji = "🟢"
                text = f"Daemon: Active - Working on {status['current_task']}"
            else:
                emoji = "🟡"
                text = "Daemon: Idle - Waiting for tasks"
        else:
            emoji = "🔴"
            text = "Daemon: Stopped"

        self.daemon_status_text = f"{emoji} {text}"
        logger.debug(f"Status updated: {self.daemon_status_text}")

    def _cmd_daemon_status(self) -> str:
        """Show detailed daemon status with progress bar and work information.

        PRIORITY 2.11: Enhanced status reporting
        - Shows what daemon is working on
        - Progress bar for current priority
        - Time elapsed on current work
        - Iteration count
        - Crash history
        """
        from datetime import datetime
        from pathlib import Path

        self._update_status_display()

        # Read daemon status file directly for detailed info
        status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

        if not status_file.exists():
            return (
                "❌ **Daemon Status: NOT FOUND**\n\n"
                "The daemon status file doesn't exist.\n\n"
                "The daemon may not be running or hasn't been started yet.\n\n"
                "Use `/start` to launch the daemon."
            )

        try:
            daemon_status = read_json_file(status_file)
        except Exception as e:
            return f"❌ **Error Reading Status**: {str(e)}"

        if daemon_status["status"] != "running":
            return (
                "❌ **Daemon Status: STOPPED**\n\n"
                "The code_developer daemon is not currently running.\n\n"
                "Use `/start` to launch it."
            )

        # Get process info
        status = self.process_manager.get_daemon_status()

        # Parse timestamps
        started_at = datetime.fromisoformat(daemon_status["started_at"])
        uptime = datetime.now() - started_at

        # Build status message
        lines = []
        lines.append("🟢 **code_developer is running!**\n")

        # Current work section
        current_priority = daemon_status.get("current_priority")
        if current_priority and current_priority.get("name"):
            lines.append("**📋 Current Work:**")
            lines.append(f"- **Priority**: {current_priority['name']}")
            lines.append(f"- **Title**: {current_priority['title']}")

            # Calculate time on current priority
            if current_priority.get("started_at"):
                priority_start = datetime.fromisoformat(current_priority["started_at"])
                time_on_priority = datetime.now() - priority_start
                hours = int(time_on_priority.total_seconds() / 3600)
                minutes = int((time_on_priority.total_seconds() % 3600) / 60)

                lines.append(f"- **Time Elapsed**: {hours}h {minutes}m")

                # Progress bar based on time (assuming typical priority takes 4-8 hours)
                # Show progress up to 8 hours, then just show it's ongoing
                max_hours = 8
                progress_pct = min(
                    100,
                    int((time_on_priority.total_seconds() / 3600 / max_hours) * 100),
                )

                # Create progress bar
                bar_length = 20
                filled = int(bar_length * progress_pct / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                lines.append(f"- **Progress**: [{bar}] {progress_pct}%")

                if progress_pct >= 100:
                    lines.append("  _(This is a complex task taking longer than usual)_")

            # Iteration count
            iteration = daemon_status.get("iteration", 0)
            lines.append(f"- **Iterations**: {iteration}")

        else:
            lines.append("**Status**: Idle (waiting for work)")

        lines.append("")

        # Process health section
        lines.append("**⚙️  Process Health:**")
        lines.append(f"- **PID**: {daemon_status['pid']}")
        lines.append(f"- **Uptime**: {str(uptime).split('.')[0]}")
        lines.append(f"- **CPU**: {status['cpu_percent']:.1f}%")
        lines.append(f"- **Memory**: {status['memory_mb']:.1f} MB")

        # Crash history
        crashes = daemon_status.get("crashes", {})
        crash_count = crashes.get("count", 0)
        if crash_count > 0:
            max_crashes = crashes.get("max", 3)
            lines.append(f"- **Crashes**: {crash_count}/{max_crashes} ⚠️")

            history = crashes.get("history", [])
            if history:
                lines.append(f"  _Last crash: {history[-1]}_")
        else:
            lines.append(f"- **Crashes**: 0 ✓")

        lines.append("")

        # Context management
        context = daemon_status.get("context", {})
        if context:
            iterations_since_compact = context.get("iterations_since_compact", 0)
            compact_interval = context.get("compact_interval", 10)
            lines.append("**🔄 Context Management:**")
            lines.append(f"- **Next refresh**: {compact_interval - iterations_since_compact} iterations")

        lines.append("")
        lines.append("_Use `/stop` to shut down the daemon, or just let him work!_")

        return "\n".join(lines)

    def _cmd_daemon_start(self) -> str:
        """Start the daemon."""
        if self.process_manager.is_daemon_running():
            self._update_status_display()
            return "✅ Daemon is already running!"

        self.console.print("[cyan]Starting code_developer daemon...[/]")

        success = self.process_manager.start_daemon(background=True)

        if success:
            self._update_status_display()
            return (
                "✅ **Daemon Started Successfully!**\n\n"
                "The code_developer daemon is now running in the background.\n\n"
                "He'll start working on priorities from the roadmap and will\n"
                "respond to your messages when he has time.\n\n"
                "⏰ **Response Time**: May take 12+ hours (needs focus time)\n\n"
                "Use `/status` to check what he's working on."
            )
        else:
            return (
                "❌ **Failed to Start Daemon**\n\n"
                "Could not start the code_developer daemon.\n\n"
                "**Troubleshooting**:\n"
                "- Check that you have a valid ANTHROPIC_API_KEY in .env\n"
                "- Ensure no other daemon is running\n"
                "- Check logs for errors\n\n"
                "Try running manually: `poetry run code-developer`"
            )

    def _cmd_daemon_stop(self) -> str:
        """Stop the daemon."""
        if not self.process_manager.is_daemon_running():
            self._update_status_display()
            return "⚠️  Daemon is not running."

        self.console.print("[cyan]Stopping daemon gracefully...[/]")

        success = self.process_manager.stop_daemon(timeout=10)

        if success:
            self._update_status_display()
            return (
                "✅ **Daemon Stopped Successfully**\n\n"
                "The code_developer daemon has been shut down gracefully.\n\n"
                "Use `/start` to launch it again when needed."
            )
        else:
            return (
                "❌ **Failed to Stop Daemon**\n\n"
                "Could not stop the daemon gracefully.\n\n"
                "You may need to kill the process manually:\n"
                "1. Run `/status` to get the PID\n"
                "2. Run `kill <PID>` in terminal"
            )

    def _cmd_daemon_restart(self) -> str:
        """Restart the daemon."""
        import time

        self.console.print("[cyan]Restarting daemon...[/]")

        # Stop if running
        if self.process_manager.is_daemon_running():
            self.console.print("[cyan]Stopping current daemon...[/]")
            self.process_manager.stop_daemon()
            time.sleep(2)

        # Start fresh
        self.console.print("[cyan]Starting daemon...[/]")
        success = self.process_manager.start_daemon()

        self._update_status_display()

        if success:
            return "✅ Daemon restarted successfully!"
        else:
            return "❌ Failed to restart daemon. Check logs."

    def _auto_start_daemon_if_needed(self):
        """Automatically start daemon if not running.

        PRIORITY: Automatic Daemon Management (Priority #3)

        This method is called at project-manager startup to ensure
        the code_developer daemon is always running when the user
        interacts with the project-manager.

        No user approval required - just makes sure daemon is live.

        Behavior:
        - Checks if daemon is running
        - If not, starts it automatically in background
        - Shows brief status message
        - No long explanations or approval dialogs

        Example:
            >>> session._auto_start_daemon_if_needed()
            # Silently starts daemon if needed
        """
        # Check if daemon is already running
        if self.process_manager.is_daemon_running():
            # Already running - nothing to do
            logger.debug("Daemon already running - no action needed")
            self._update_status_display()
            return

        # Daemon not running - start it automatically
        logger.info("Daemon not running - auto-starting...")
        self.console.print("\n[dim]Starting code_developer daemon...[/]", end=" ")

        success = self.process_manager.start_daemon(background=True)

        if success:
            self.console.print("[green]✓[/]")
            logger.info("Daemon auto-started successfully")
        else:
            self.console.print("[yellow]⚠[/]")
            logger.warning("Failed to auto-start daemon")
            # Don't block the user - they can manually start later if needed

        self._update_status_display()

    def start(self):
        """Start interactive chat session.

        Displays welcome message and enters REPL loop.
        Handles user input, routes commands, and displays responses.

        PRIORITY 9: Enhanced Communication & Daily Standup
        Shows daily standup report on first chat of the day (>12 hours since last chat).

        PRIORITY: Automatic Daemon Management (Priority #3)
        Automatically checks if daemon is running and starts it if needed.
        No user approval required - just make it work.

        Example:
            >>> session.start()
            # Enters interactive mode
            # Daemon auto-starts if not running
        """
        self.active = True

        # Auto-check and start daemon if needed
        self._auto_start_daemon_if_needed()

        # Start real-time status monitoring
        self.status_monitor.start()

        self._display_welcome()
        self._load_roadmap_context()

        # PRIORITY 9: Show daily standup on first chat of day
        if self._should_show_daily_standup():
            self._generate_and_display_standup()
            self._update_last_chat_timestamp()

        self._run_repl_loop()

    def _run_repl_loop(self):
        """Main REPL loop with periodic status updates and daemon question checking.

        Continuously reads user input and processes it until
        the session is terminated. Uses prompt-toolkit for advanced
        input features (multi-line, history, auto-completion).

        Checks for daemon questions on startup and every 10 messages.
        Updates daemon status every 10 messages.
        """
        # Check for daemon questions on startup
        self._check_daemon_questions()

        message_count = 0

        try:
            while self.active:
                try:
                    # Show prompt in a clean, claude-cli style
                    self.console.print("\n[bold]You[/]")

                    # Get user input with prompt-toolkit
                    # (supports: ↑/↓ history, Tab completion, Alt+Enter multi-line)
                    user_input = self.prompt_session.prompt("› ")

                    if not user_input.strip():
                        continue

                    # Check for exit commands
                    if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                        self._display_goodbye()
                        break

                    # Check for help command
                    if user_input.lower() in ["/help", "help"]:
                        self._display_help()
                        continue

                    # Process input
                    response = self._process_input(user_input)

                    # Display response
                    self._display_response(response)

                    # Add to history
                    self.history.append({"role": "user", "content": user_input})
                    self.history.append({"role": "assistant", "content": response})

                    # Auto-save session after each interaction
                    self._save_session()

                    # Update status and check for daemon questions every 10 messages
                    message_count += 1
                    if message_count % 10 == 0:
                        # Update daemon status
                        old_status = self.daemon_status_text
                        self._update_status_display()

                        # Alert if status changed
                        if old_status != self.daemon_status_text:
                            self.console.print(f"\n[cyan]📊 Status Update: {self.daemon_status_text}[/]\n")

                        # Check for new daemon questions
                        self._check_daemon_questions()

                except KeyboardInterrupt:
                    self.console.print("\n\n[yellow]Interrupted. Type /exit to quit.[/]")
                except EOFError:
                    self._display_goodbye()
                    break
                except Exception as e:
                    logger.error(f"Error in REPL loop: {e}", exc_info=True)
                    self.console.print(f"\n[red]Error: {e}[/]")
        finally:
            # Ensure status monitor is stopped on any exit
            self.status_monitor.stop()

    def _process_input(self, user_input: str) -> str:
        """Process user input (command or natural language).

        Routes input to appropriate handler based on whether it's
        a slash command or natural language.

        US-012: If we're in a user story validation loop, route responses to handler.

        Args:
            user_input: User input string

        Returns:
            Response message

        Example:
            >>> response = session._process_input("/help")
            >>> response = session._process_input("What should we do next?")
        """
        # US-012: If we're in a user story validation loop, route to handler
        if self.us_handler.current_draft and not user_input.startswith("/"):
            result = self.us_handler.handle_validation_response(user_input)
            return result.get("message", "")

        # Check if it's a slash command
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        else:
            # Natural language - use AI
            return self._handle_natural_language(user_input)

    def _handle_command(self, command: str) -> str:
        """Handle slash command.

        Parses command and arguments, then routes to appropriate
        command handler.

        Args:
            command: Command string (e.g., "/add New Priority")

        Returns:
            Response message

        Example:
            >>> response = session._handle_command("/view 3")
        """
        # Parse command and args
        parts = command.split(maxsplit=1)
        cmd_name = parts[0][1:].lower()  # Remove '/'
        args_str = parts[1] if len(parts) > 1 else ""
        args = args_str.split() if args_str else []

        logger.debug(f"Handling command: {cmd_name} with args: {args}")

        # US-012: Handle /US command for user story creation
        if cmd_name == "us":
            result = self.us_handler.handle_command(command)
            return result.get("message", "")

        # Handle daemon control commands
        if cmd_name == "status":
            return self._cmd_daemon_status()
        elif cmd_name == "start":
            return self._cmd_daemon_start()
        elif cmd_name == "stop":
            return self._cmd_daemon_stop()
        elif cmd_name == "restart":
            return self._cmd_daemon_restart()
        elif cmd_name == "standup":
            # PRIORITY 9: Force generation of daily standup report
            return self._cmd_standup_force()

        # Get command handler for other commands
        handler = get_command_handler(cmd_name)

        if handler:
            try:
                return handler.execute(args, self.editor)
            except Exception as e:
                logger.error(f"Command execution failed: {e}", exc_info=True)
                return f"❌ Command failed: {str(e)}"
        else:
            return f"❌ Unknown command: /{cmd_name}\n" f"Type /help to see available commands."

    def _handle_natural_language(self, text: str) -> str:
        """Handle natural language input with AI.

        Uses AIService to process natural language and optionally
        execute extracted actions. Supports streaming responses.

        Args:
            text: Natural language input

        Returns:
            Response message

        Example:
            >>> response = session._handle_natural_language(
            ...     "Add a priority for authentication"
            ... )
        """
        try:
            # Build context from current roadmap
            context = self._build_context()

            logger.debug(f"Processing natural language: {text[:100]}...")

            # Use streaming if enabled
            if self.enable_streaming:
                return self._handle_natural_language_stream(text, context)
            else:
                # Get AI response (blocking)
                response = self.ai_service.process_request(
                    user_input=text, context=context, history=self.history, stream=False
                )

                # If AI suggests an action, ask for confirmation
                if response.action:
                    action_desc = self._describe_action(response.action)
                    confirmation = self.console.input(
                        f"\n[yellow]Action suggested: {action_desc}[/]\n" f"[yellow]Execute this action? [y/n]:[/] "
                    )

                    if confirmation.lower() in ["y", "yes"]:
                        result = self._execute_action(response.action)
                        return f"{response.message}\n\n{result}"

                return response.message

        except Exception as e:
            logger.error(f"Natural language processing failed: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def _handle_natural_language_stream(self, text: str, context: Dict) -> str:
        """Handle natural language with streaming response and daemon awareness.

        PRIORITY 2.11: Integrated bug fixing workflow
        Detects bug reports and creates tickets automatically.

        PRIORITY 2.9.5: Transparent Assistant Integration
        Uses LangChain assistant for complex questions requiring analysis.

        Args:
            text: Natural language input
            context: Roadmap context

        Returns:
            Complete response message
        """
        try:
            # PRIORITY 2.11: Detect bug reports
            if self._detect_bug_report(text):
                return self._handle_bug_report(text)

            # Detect daemon-related commands
            daemon_keywords = [
                "ask daemon",
                "tell daemon",
                "daemon implement",
                "daemon work on",
                "daemon start working",
                "daemon please",
                "ask code_developer",
                "tell code_developer",
            ]

            if any(keyword in text.lower() for keyword in daemon_keywords):
                return self._send_command_to_daemon(text)

            # Detect status queries
            status_keywords = [
                "daemon status",
                "what is daemon doing",
                "is daemon working",
                "daemon progress",
                "what's daemon working on",
                "code_developer status",
            ]

            if any(keyword in text.lower() for keyword in status_keywords):
                return self._cmd_daemon_status()

            # PRIORITY 2.9.5: Check if assistant should help with complex question
            if self.assistant.is_available() and self.assistant.should_invoke_for_question(text):
                return self._invoke_assistant(text)

            # Normal AI-powered response with streaming
            return self._get_normal_ai_response(text)

        except Exception as e:
            logger.error(f"Streaming natural language processing failed: {e}", exc_info=True)
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def _build_context(self) -> Dict:
        """Build context dictionary from current roadmap.

        Returns:
            Context dictionary with roadmap summary

        Example:
            >>> context = session._build_context()
            >>> print(context['roadmap_summary']['total'])
            9
        """
        summary = self.editor.get_priority_summary()

        return {
            "roadmap_summary": summary,
            "current_session": len(self.history),
        }

    def _describe_action(self, action: Dict) -> str:
        """Describe an action in human-readable format.

        Args:
            action: Action dictionary

        Returns:
            Human-readable description

        Example:
            >>> desc = session._describe_action({
            ...     'type': 'add_priority',
            ...     'priority': '10',
            ...     'title': 'Authentication'
            ... })
        """
        action_type = action.get("type", "unknown")

        if action_type == "add_priority":
            return f"Add new priority: {action.get('title', 'Unknown')}"
        elif action_type == "update_priority":
            return (
                f"Update {action.get('priority', 'Unknown')} "
                f"{action.get('field', 'status')} to {action.get('value', 'Unknown')}"
            )
        elif action_type == "start_daemon":
            return f"Start daemon on {action.get('priority', 'next priority')}"
        else:
            return f"Execute {action_type}"

    def _execute_action(self, action: Dict) -> str:
        """Execute an action extracted from AI response.

        Args:
            action: Action dictionary

        Returns:
            Result message

        Example:
            >>> result = session._execute_action({
            ...     'type': 'update_priority',
            ...     'priority': '3',
            ...     'field': 'status',
            ...     'value': '✅ Complete'
            ... })
        """
        try:
            action_type = action.get("type")

            if action_type == "add_priority":
                # Use add command
                handler = get_command_handler("add")
                if handler:
                    title = action.get("title", "New Priority")
                    return handler.execute([title], self.editor)

            elif action_type == "update_priority":
                # Use update command
                handler = get_command_handler("update")
                if handler:
                    priority = action.get("priority", "")
                    field = action.get("field", "status")
                    value = action.get("value", "")
                    return handler.execute([priority, field, value], self.editor)

            return "❌ Action execution not implemented yet"

        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            return f"❌ Failed to execute action: {str(e)}"

    def _display_welcome(self):
        """Display welcome message with clean, claude-cli inspired formatting."""
        # Clean, minimal welcome similar to claude-cli
        self.console.print()
        self.console.print("[bold]Coffee Maker[/] [dim]·[/] AI Project Manager")
        self.console.print("[dim]Powered by Claude AI[/]")
        self.console.print()

        # Show keyboard shortcuts in a clean way
        self.console.print("[dim]Keyboard shortcuts:[/]")
        self.console.print("[dim]  /help[/] [dim]- Show commands[/]")
        self.console.print("[dim]  Alt+Enter[/] [dim]- Multi-line input[/]")
        self.console.print(
            "[dim]  ↑↓[/] [dim]- History    [/][dim]Tab[/] [dim]- Complete    [/][dim]/exit[/] [dim]- Quit[/]"
        )
        self.console.print()

        # Show daemon status in a subtle way
        status_icon = (
            "🟢" if "Active" in self.daemon_status_text else "🔴" if "Stopped" in self.daemon_status_text else "🟡"
        )
        self.console.print(
            f"[dim]{status_icon} code_developer: {self.daemon_status_text.split(': ')[1] if ': ' in self.daemon_status_text else self.daemon_status_text}[/]"
        )
        self.console.print()
        self.console.print("[dim]" + "─" * 60 + "[/]")
        self.console.print()

    def _display_goodbye(self):
        """Display goodbye message and save session."""
        self.active = False

        # Stop status monitoring
        self.status_monitor.stop()

        self._save_session()  # Final save on exit
        self.console.print("\n[dim]Session saved. Goodbye![/]")
        self.console.print()

    def _display_response(self, response: str):
        """Display AI response with enhanced syntax highlighting.

        Args:
            response: Response text (supports markdown)

        Example:
            >>> session._display_response("**Success!** Priority added.")
        """
        # Clean, claude-cli style header
        self.console.print("\n[bold]Claude[/]")

        # Extract and render code blocks with syntax highlighting
        try:
            self._display_response_with_syntax(response)
        except Exception as e:
            logger.warning(f"Syntax highlighting failed: {e}, falling back to markdown")
            # Fallback to basic markdown
            try:
                md = Markdown(response)
                self.console.print(md)
            except Exception:
                # Final fallback to plain text
                self.console.print(response)

    def _display_response_with_syntax(self, response: str):
        """Display response with enhanced code syntax highlighting.

        Args:
            response: Response text with markdown code blocks
        """
        # Pattern to match code blocks: ```language\ncode\n```
        code_block_pattern = r"```(\w+)?\n(.*?)```"

        last_end = 0
        parts = []

        # Find all code blocks
        for match in re.finditer(code_block_pattern, response, re.DOTALL):
            # Add text before code block
            if match.start() > last_end:
                text_part = response[last_end : match.start()]
                if text_part.strip():
                    parts.append(("text", text_part))

            # Add code block
            language = match.group(1) or "python"  # Default to python
            code = match.group(2).strip()
            parts.append(("code", code, language))

            last_end = match.end()

        # Add remaining text after last code block
        if last_end < len(response):
            remaining = response[last_end:]
            if remaining.strip():
                parts.append(("text", remaining))

        # Render parts
        if not parts:
            # No code blocks found, render as markdown
            md = Markdown(response)
            self.console.print(md)
        else:
            for part in parts:
                if part[0] == "text":
                    # Render text as markdown
                    md = Markdown(part[1])
                    self.console.print(md)
                elif part[0] == "code":
                    # Render code with syntax highlighting
                    code, language = part[1], part[2]
                    syntax = Syntax(
                        code,
                        language,
                        theme="monokai",
                        line_numbers=True,
                        word_wrap=False,
                    )
                    self.console.print(syntax)

    def _display_help(self):
        """Display help with all available commands."""
        table = Table(
            title="Available Commands",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        # Get all registered commands
        commands = list_commands()

        # Add commands to table
        for command in sorted(commands, key=lambda c: c.name):
            table.add_row(f"/{command.name}", command.description)

        # Add built-in commands
        table.add_row("/help", "Show this help message")
        table.add_row("/exit", "Exit chat session")

        self.console.print(table)
        self.console.print("\n[italic]You can also use natural language![/]")
        self.console.print('[dim]Example: "Add a priority for user authentication"[/]\n')

    def _invoke_assistant(self, question: str) -> str:
        """Invoke LangChain assistant for complex question.

        PRIORITY 2.9.5: Transparent Assistant Integration

        Args:
            question: User's complex question

        Returns:
            Assistant's answer with transparent action steps
        """
        try:
            # Show indicator that assistant is working
            self.console.print("\n[cyan]🔍 Using intelligent assistant to analyze...[/]\n")

            # Invoke assistant (actions will be displayed via callback)
            result = self.assistant.invoke(question)

            if result["success"]:
                # Display final answer
                return result["answer"]
            else:
                # Fall back to normal AI if assistant fails
                error_msg = result.get("error", "Unknown error")
                logger.warning(f"Assistant failed: {error_msg}, falling back to Claude AI")
                self.console.print(f"[yellow]Assistant unavailable ({error_msg}), using Claude AI instead...[/]\n")

                # Continue to normal AI response (will be handled by caller)
                return self._get_normal_ai_response(question)

        except Exception as e:
            logger.error(f"Assistant invocation failed: {e}", exc_info=True)
            # Fall back to normal AI
            return self._get_normal_ai_response(question)

    def _get_normal_ai_response(self, text: str) -> str:
        """Get normal Claude AI streaming response.

        Args:
            text: User input

        Returns:
            Complete AI response
        """
        context = self._build_context()

        # Show thinking indicator briefly (very subtle, like claude-cli)
        self.console.print("\n[dim]...[/]", end="\r")  # Will be overwritten
        import time

        time.sleep(0.2)  # Brief pause

        # Stream response with clean header
        self.console.print("\n[bold]Claude[/]")

        full_response = ""
        for chunk in self.ai_service.process_request_stream(user_input=text, context=context, history=self.history):
            self.console.print(chunk, end="")
            full_response += chunk

        self.console.print()  # Final newline

        return full_response

    def _handle_bug_report(self, bug_description: str) -> str:
        """Handle user bug report.

        PRIORITY 2.11: Integrated Bug Fixing Workflow

        Args:
            bug_description: User's description of the bug

        Returns:
            Ticket creation confirmation and next steps

        Workflow:
            1. Generate ticket number (BUG-xxx)
            2. Create ticket file with description and DoD
            3. Notify code_developer via notification
            4. Return ticket info to user
        """
        try:
            # Create bug ticket using bug tracking skill
            result = self.bug_skill.report_bug(
                title=bug_description[:80],  # Use first 80 chars as title
                description=bug_description,
                reporter="user",
                priority=None,  # Auto-assessed
                category=None,
                reproduction_steps=None,
            )

            bug_number = result["bug_number"]
            ticket_path = result["ticket_file_path"]

            # Get bug details from database
            bug = self.bug_skill.get_bug_by_number(bug_number)
            title = bug["title"]
            priority = bug["priority"]

            # Create notification for code_developer
            notif_id = self.notif_db.create_notification(
                type="bug",
                title=f"BUG-{bug_number:03d}: {title}",
                message=f"New bug reported. See {ticket_path} for details.\n\n{bug_description}",
                priority=(NOTIF_PRIORITY_HIGH if priority in ["Critical", "High"] else "normal"),
                context={
                    "bug_number": bug_number,
                    "ticket_path": str(ticket_path),
                    "priority": priority,
                },
            )

            logger.info(f"Bug ticket {bug_number} created, notification #{notif_id} sent to daemon")

            # Format response for user
            # Format response
            priority_emoji = {
                "Critical": "🚨",
                "High": "⚠️",
                "Medium": "🔸",
                "Low": "🔹",
            }.get(priority, "🔸")

            return f"""🐛 **Bug Ticket Created**

**{priority_emoji} BUG-{bug_number:03d}**: {title}
**Priority**: {priority}
**Ticket**: `{ticket_path}`

✅ code_developer has been notified and will:
1. 🔍 Analyze the bug and reproduce it
2. 📝 Write a technical specification
3. 🔧 Implement the fix with tests
4. 🧪 Verify all tests pass
5. 📤 Create a PR for review

You can track progress in the ticket file or ask me for updates!
"""

        except Exception as e:
            logger.error(f"Failed to create bug ticket: {e}", exc_info=True)
            return f"❌ Failed to create bug ticket: {str(e)}"

    def _send_command_to_daemon(self, command: str) -> str:
        """Send command to daemon via notifications.

        Args:
            command: Natural language command for daemon

        Returns:
            Confirmation message
        """
        # Check if daemon is running
        if not self.process_manager.is_daemon_running():
            return (
                "⚠️  **Daemon Not Running**\n\n"
                "I can't send commands to the daemon because it's not running.\n\n"
                "Would you like me to start it? Use `/start` to launch the daemon."
            )

        # Create notification for daemon
        notif_id = self.notif_db.create_notification(
            type="command",
            title="Command from project-manager",
            message=command,
            priority=NOTIF_PRIORITY_HIGH,
            context={
                "timestamp": datetime.now().isoformat(),
                "source": "project_manager_chat",
            },
        )

        return (
            f"✅ **Command Sent to Daemon** (Notification #{notif_id})\n\n"
            f"Your message has been delivered to code_developer.\n\n"
            f"⏰ **Response Time**: He may take 12+ hours to respond.\n"
            f"   Like a human developer, he needs focus time and rest periods.\n\n"
            f"💡 **Tip**: Use `/notifications` to check for his response later."
        )

    def _check_daemon_questions(self):
        """Check for pending questions from daemon and display them."""
        try:
            questions = self.notif_db.get_pending_notifications()

            # Filter for questions from daemon (type="question")
            daemon_questions = [q for q in questions if q.get("type") == "question"]

            if daemon_questions:
                self.console.print("\n[yellow]📋 Daemon Has Questions:[/]\n")

                for q in daemon_questions[:5]:  # Show top 5
                    created = q.get("created_at", "Unknown time")
                    self.console.print(f"  [bold]#{q['id']}[/]: {q['title']}")
                    self.console.print(f"  [dim]{created}[/]")
                    # Truncate message if too long
                    msg = q["message"]
                    if len(msg) > 100:
                        msg = msg[:100] + "..."
                    self.console.print(f"  {msg}")
                    self.console.print()

                if len(daemon_questions) > 5:
                    self.console.print(f"[dim]  ...and {len(daemon_questions) - 5} more[/]\n")

                self.console.print("[dim]Use /notifications to view and respond[/]\n")

        except Exception as e:
            logger.error(f"Failed to check daemon questions: {e}")

    def _load_roadmap_context(self):
        """Load roadmap context at session start.

        Loads roadmap summary and displays brief status.
        """
        try:
            summary = self.editor.get_priority_summary()

            self.console.print(
                f"\n[dim]Loaded roadmap: {summary['total']} priorities "
                f"({summary['completed']} completed, "
                f"{summary['in_progress']} in progress, "
                f"{summary['planned']} planned)[/]\n"
            )

        except Exception as e:
            logger.warning(f"Failed to load roadmap context: {e}")
            self.console.print("\n[yellow]Warning: Could not load roadmap summary[/]\n")

    def _should_show_daily_standup(self) -> bool:
        """Check if daily standup should be shown.

        Shows standup if more than 12 hours have passed since last chat.

        Returns:
            True if standup should be shown, False otherwise
        """
        config_dir = Path.home() / ".project_manager"
        config_dir.mkdir(parents=True, exist_ok=True)
        last_chat_file = config_dir / "last_chat.json"

        if not last_chat_file.exists():
            # First time running
            return True

        try:
            config = read_json_file(last_chat_file, default={})
            last_chat_time_str = config.get("last_chat_timestamp")

            if not last_chat_time_str:
                return True

            last_chat_time = datetime.fromisoformat(last_chat_time_str)
            hours_elapsed = (datetime.now() - last_chat_time).total_seconds() / 3600

            # Show standup if more than 12 hours have passed
            return hours_elapsed > 12

        except Exception as e:
            logger.warning(f"Error checking last chat time: {e}")
            return False

    def _update_last_chat_timestamp(self):
        """Update the last chat timestamp in config."""
        config_dir = Path.home() / ".project_manager"
        config_dir.mkdir(parents=True, exist_ok=True)
        last_chat_file = config_dir / "last_chat.json"

        try:
            write_json_file(
                last_chat_file,
                {
                    "last_chat_timestamp": datetime.now().isoformat(),
                    "date": date.today().isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to update last chat timestamp: {e}")

    def _generate_and_display_standup(self):
        """Generate and display daily standup report.

        Called at session start if it's the first chat of the day.
        """
        try:
            self.console.print("\n[cyan]Generating daily standup report...[/]\n")

            # Generate standup for yesterday
            yesterday = date.today() - timedelta(days=1)
            generator = StandupGenerator()
            summary = generator.generate_daily_standup(yesterday)

            # Display the standup
            self.console.print("[bold]═" * 30 + "═[/]")
            md = Markdown(summary.summary_text)
            self.console.print(md)
            self.console.print("[bold]═" * 30 + "═[/]\n")

        except Exception as e:
            logger.error(f"Failed to generate standup: {e}")
            self.console.print(f"\n[yellow]Warning: Could not generate standup report ({str(e)})[/]\n")

    def _cmd_standup_force(self) -> str:
        """Force generation of daily standup report.

        This can be invoked with /standup command at any time.

        Returns:
            Response message
        """
        try:
            yesterday = date.today() - timedelta(days=1)
            generator = StandupGenerator()
            summary = generator.generate_daily_standup(yesterday, force_regenerate=True)

            return summary.summary_text

        except Exception as e:
            logger.error(f"Failed to generate standup: {e}")
            return f"❌ Failed to generate standup: {str(e)}"
