"""User Listener CLI - Primary user interface for MonolithicCoffeeMakerAgent.

This module provides the standalone `poetry run user-listener` command that serves
as the PRIMARY USER INTERFACE for the MonolithicCoffeeMakerAgent system.

SPEC-010: User-Listener UI Command (SIMPLIFIED)
- Reuses 100% of ChatSession infrastructure from project-manager chat
- Enforces singleton pattern via AgentRegistry
- Minimal code: ~250 lines, mostly copy-paste from roadmap_cli.py

ENHANCED (2025-10-19): Orchestrator Integration
- Automatically starts orchestrator in background (--with-team flag, default ON)
- Orchestrator launches and manages all 6 agents
- ALL messages routed through orchestrator (no direct agent communication)
- Velocity tracking and bottleneck detection via orchestrator metrics
- Graceful shutdown stops orchestrator (which stops all 6 agents)

Architecture:
    User runs: poetry run user-listener (or poetry run user-listener --with-team)
       ↓
    user_listener.py main()
       ↓
    Start ORCHESTRATOR in background subprocess
       ↓
    Orchestrator launches 6 agents (architect, code_developer, project_manager, etc.)
       ↓
    Register as USER_LISTENER (singleton)
       ↓
    Create UserListenerSession (ChatSession + MessageHandlerMixin)
       ↓
    Start chat loop with orchestrator message routing:
       - User input → orchestrator (USER_REQUEST)
       - Orchestrator analyzes → routes to best agent
       - Agent completes → orchestrator (TASK_RESPONSE)
       - Orchestrator → user_listener (USER_RESPONSE)
       - Display to user
       ↓
    On exit: Stop orchestrator gracefully (stops all agents)

Orchestrator Benefits:
    - Central routing & load balancing (picks best available agent)
    - Bottleneck detection (measures all task durations)
    - Velocity metrics (tracks team performance)
    - Flexibility (can override agent suggestions)

Key Features:
    - Interactive REPL for user input
    - Rich terminal output with markdown and syntax highlighting
    - Singleton enforcement (only one instance at a time)
    - All slash commands work (/help, /exit, etc.)
    - NEW: Message queue integration (MessageHandlerMixin)
    - NEW: Background message polling for agent responses
    - NEW: Orchestrator-centric architecture (all messages routed centrally)

References:
    - SPEC-010: User-Listener UI Command
    - SPEC-057: Multi-Agent Orchestrator Architecture
    - ADR-003: Simplification-First Approach
    - roadmap_cli.py: Source for cmd_chat() function (REUSED)
"""

import atexit
import click
import logging
import os
import shutil
import signal
import subprocess
import sys
import time

from coffee_maker.autonomous.agent_registry import (
    AgentAlreadyRunningError,
    AgentRegistry,
    AgentType,
)
from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.chat_interface import ChatSession
from coffee_maker.cli.message_handler_mixin import MessageHandlerMixin
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.config import ROADMAP_PATH, ConfigManager

# Configure logging BEFORE imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Global team daemon process (for cleanup on exit)
_team_daemon_process = None


def _detect_and_validate_mode() -> tuple[bool, str]:
    """Detect Claude CLI vs API mode and validate availability.

    Returns:
        Tuple of (use_cli: bool, claude_path: str)

    Raises:
        RuntimeError: If neither Claude CLI nor API key is available
    """
    inside_claude_cli = bool(os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"))

    if inside_claude_cli:
        logger.info("Detected running inside Claude Code - forcing API mode to avoid nesting")

    # Auto-detect mode: CLI vs API (same logic as daemon)
    claude_path = "/opt/homebrew/bin/claude"
    has_cli = shutil.which("claude") or os.path.exists(claude_path)
    has_api_key = ConfigManager.has_anthropic_api_key()

    use_claude_cli = False

    if inside_claude_cli:
        # We're already in Claude CLI - MUST use API to avoid nesting
        if has_api_key:
            print("=" * 70)
            print("ℹ️  Detected: Running inside Claude Code")
            print("=" * 70)
            print("🔄 Using Anthropic API to avoid CLI nesting")
            print("💡 TIP: CLI nesting is not recommended")
            print("=" * 70 + "\n")
            use_claude_cli = False
        else:
            # No API key - can't proceed
            print("=" * 70)
            print("❌ ERROR: Running inside Claude Code without API key")
            print("=" * 70)
            print("\nYou're running user-listener from within Claude Code.")
            print("To avoid CLI nesting, we need to use API mode.")
            print("\n🔧 SOLUTION:")
            print("  1. Get your API key from: https://console.anthropic.com/")
            print("  2. Set the environment variable:")
            print("     export ANTHROPIC_API_KEY='your-api-key-here'")
            print("  3. Or add it to your .env file")
            print("\n💡 ALTERNATIVE: Run from a regular terminal (not Claude Code)")
            print("=" * 70 + "\n")
            raise RuntimeError("No API key available in Claude Code mode")
    elif has_cli:
        # CLI available - use it as default (free with subscription!)
        print("=" * 70)
        print("ℹ️  Auto-detected: Using Claude CLI (default)")
        print("=" * 70)
        print("💡 TIP: Claude CLI is free with your subscription!")
        print("=" * 70 + "\n")
        use_claude_cli = True
    elif has_api_key:
        # No CLI but has API key - use API
        print("=" * 70)
        print("ℹ️  Auto-detected: Using Anthropic API (no CLI found)")
        print("=" * 70)
        print("💡 TIP: Install Claude CLI for free usage!")
        print("    Get it from: https://claude.ai/")
        print("=" * 70 + "\n")
        use_claude_cli = False
    else:
        # Neither available - error
        print("=" * 70)
        print("❌ ERROR: No Claude access available!")
        print("=" * 70)
        print("\nThe chat requires either:")
        print("  1. Claude CLI installed (recommended - free with subscription), OR")
        print("  2. Anthropic API key (requires credits)")
        print("\n🔧 SOLUTION 1 (CLI Mode - Recommended):")
        print("  1. Install Claude CLI from: https://claude.ai/")
        print("  2. Run: poetry run user-listener")
        print("\n🔧 SOLUTION 2 (API Mode):")
        print("  1. Get your API key from: https://console.anthropic.com/")
        print("  2. Set the environment variable:")
        print("     export ANTHROPIC_API_KEY='your-api-key-here'")
        print("  3. Run: poetry run user-listener")
        print("\n" + "=" * 70 + "\n")
        raise RuntimeError("No Claude CLI or API key available")

    return use_claude_cli, claude_path


def _initialize_chat_components(use_claude_cli: bool, claude_path: str) -> tuple:
    """Initialize editor and AI service components.

    Args:
        use_claude_cli: Whether to use Claude CLI
        claude_path: Path to Claude CLI executable

    Returns:
        Tuple of (editor, ai_service)

    Raises:
        RuntimeError: If AI service is not available
    """
    # Initialize components (REUSED from project-manager chat)
    editor = RoadmapEditor(ROADMAP_PATH)
    ai_service = AIService(use_claude_cli=use_claude_cli, claude_cli_path=claude_path)

    # Check AI service availability
    if not ai_service.check_available():
        print("❌ AI service not available")
        print("\nPlease check:")
        if use_claude_cli:
            print("  - Claude CLI is installed and working")
        else:
            print("  - ANTHROPIC_API_KEY is valid")
        print("  - Internet connection is active")
        raise RuntimeError("AI service not available")

    return editor, ai_service


def _start_team_daemon() -> subprocess.Popen:
    """Start orchestrator in background subprocess (launches all 6 agents).

    The orchestrator is the 7th agent that manages and coordinates all other agents:
    - Launches all 6 agents in priority order
    - Monitors agent health and restarts crashed agents
    - Routes ALL inter-agent messages
    - Measures task durations for velocity tracking
    - Detects bottlenecks through centralized metrics

    Returns:
        Popen object for the orchestrator process

    Raises:
        RuntimeError: If orchestrator fails to start
    """
    global _team_daemon_process

    print("=" * 70)
    print("🚀 Starting Multi-Agent Orchestrator...")
    print("=" * 70)
    print("Orchestrator will launch 6 agents in priority order:")
    print("  1. architect (creates specs)")
    print("  2. code_developer (implements features)")
    print("  3. project_manager (monitors GitHub)")
    print("  4. assistant (creates demos, reports bugs)")
    print("  5. code_searcher (code analysis)")
    print("  6. ux_design_expert (design reviews)")
    print("")
    print("Architecture: ALL agents communicate through orchestrator")
    print("Benefits: Load balancing, bottleneck detection, velocity metrics")
    print("")

    try:
        # Start orchestrator as background subprocess
        # Orchestrator will launch all 6 agents and manage them
        process = subprocess.Popen(
            ["python", "-m", "coffee_maker.autonomous.orchestrator"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )

        # Wait a few seconds for orchestrator to initialize and launch agents
        print("⏳ Orchestrator initializing and launching agents (5 seconds)...")
        time.sleep(5)

        # Check if process is still running
        if process.poll() is not None:
            # Process already exited - something went wrong
            stdout, stderr = process.communicate()
            print(f"❌ Orchestrator failed to start!")
            print(f"\nStdout:\n{stdout}")
            print(f"\nStderr:\n{stderr}")
            raise RuntimeError("Orchestrator exited immediately")

        _team_daemon_process = process

        print("✅ Orchestrator started successfully (PID: {})".format(process.pid))
        print("   All 6 agents should now be running in background")
        print("=" * 70)
        print("")

        # Register cleanup handler
        atexit.register(_stop_team_daemon)

        # Handle SIGTERM/SIGINT for graceful shutdown
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)

        return process

    except FileNotFoundError:
        print("❌ Error: 'python' command not found")
        print("\n💡 TIP: Ensure Python is in PATH")
        raise RuntimeError("Python not available")

    except Exception as e:
        print(f"❌ Error starting orchestrator: {e}")
        raise


def _stop_team_daemon():
    """Stop orchestrator gracefully (which will stop all 6 agents)."""
    global _team_daemon_process

    if _team_daemon_process is None:
        return

    if _team_daemon_process.poll() is not None:
        # Already stopped
        return

    print("\n" + "=" * 70)
    print("🛑 Stopping Multi-Agent Orchestrator...")
    print("=" * 70)
    print("Orchestrator will shutdown all 6 agents gracefully...")

    try:
        # Send SIGTERM for graceful shutdown
        _team_daemon_process.terminate()

        # Wait up to 15 seconds for graceful shutdown (longer since it needs to stop 6 agents)
        try:
            _team_daemon_process.wait(timeout=15)
            print("✅ Orchestrator and all agents stopped gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if still alive
            print("⚠️  Timeout - force killing orchestrator...")
            _team_daemon_process.kill()
            _team_daemon_process.wait()
            print("✅ Orchestrator force killed")

    except Exception as e:
        logger.error(f"Error stopping orchestrator: {e}")

    finally:
        _team_daemon_process = None

    print("=" * 70)
    print("")


def _signal_handler(signum, frame):
    """Handle SIGTERM/SIGINT for graceful shutdown."""
    print("\n\n⚠️  Received shutdown signal...")
    _stop_team_daemon()
    sys.exit(0)


class UserListenerSession(MessageHandlerMixin, ChatSession):
    """Chat session with orchestrator message queue integration.

    This class combines ChatSession (interactive REPL) with MessageHandlerMixin
    (orchestrator communication) to create a user_listener that can:
    - Accept user input via console UI
    - Send requests to orchestrator for routing to appropriate agents
    - Receive and display responses from agents
    - Poll for messages in the background

    Multiple inheritance order matters: MessageHandlerMixin first for proper MRO.
    """

    def __init__(self, ai_service: AIService, editor: RoadmapEditor, enable_streaming: bool = True):
        """Initialize user listener session with message queue support.

        Args:
            ai_service: AIService for natural language processing
            editor: RoadmapEditor for roadmap manipulation
            enable_streaming: Enable streaming responses (default: True)
        """
        # Initialize both parent classes (MessageHandlerMixin calls super().__init__)
        super().__init__(ai_service, editor, enable_streaming)
        logger.info("UserListenerSession initialized with orchestrator communication")

        # Track pending responses (for async orchestrator responses)
        self._pending_responses = {}

    def start(self):
        """Start interactive session with message polling.

        This overrides ChatSession.start() to add background message polling.
        """
        logger.info("Starting user_listener session with orchestrator integration...")

        # Start polling for messages in a background thread
        import threading

        self._polling_active = True

        def poll_loop():
            """Background thread for polling orchestrator messages."""
            while self._polling_active and self.active:
                try:
                    self.poll_messages(timeout=0.5)
                except Exception as e:
                    logger.error(f"Error polling messages: {e}")
                time.sleep(0.1)  # Poll every 100ms

        self._poll_thread = threading.Thread(target=poll_loop, daemon=True)
        self._poll_thread.start()
        logger.info("Background message polling started")

        # Call parent start() to run REPL
        try:
            super().start()
        finally:
            # Stop polling when session ends
            self._polling_active = False
            if hasattr(self, "_poll_thread"):
                self._poll_thread.join(timeout=2.0)

    def _handle_natural_language(self, text: str) -> str:
        """Override parent method to route requests through orchestrator.

        This intercepts natural language input and sends it to the orchestrator
        for intelligent routing to appropriate agents. Orchestrator will analyze
        the request and delegate to the best agent (assistant, code_developer,
        project_manager, architect, etc.).

        Args:
            text: Natural language input from user

        Returns:
            Response message (may be from orchestrator or delegated agent)
        """
        logger.info(f"Sending user request to orchestrator: {text[:50]}...")

        # Send request to orchestrator (which will route to appropriate agent)
        # The orchestrator may route to assistant, code_developer, project_manager, etc.
        # based on the content and context of the request
        self.send_user_request(
            user_input=text,
            suggested_recipient="assistant",  # Suggest assistant as default (orchestrator may override)
        )

        # For now, return a confirmation message
        # In future, we could wait for response or use async pattern
        return "🔄 Request sent to orchestrator for processing. Response will arrive shortly..."


@click.command()
@click.option(
    "--with-team/--no-team",
    default=True,
    help="Start multi-agent team daemon in background (default: enabled)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def main(with_team: bool, debug: bool) -> int:
    """Main entry point for user-listener CLI.

    Command: poetry run user-listener [--with-team] [--no-team] [--debug]

    This function:
    1. Optionally starts team daemon in background (default: ON)
    2. Registers as USER_LISTENER singleton
    3. Detects and validates Claude CLI vs API mode
    4. Sets up ChatSession with AI service
    5. Starts interactive REPL loop
    6. Gracefully shuts down team daemon on exit

    Args:
        with_team: Start team daemon in background (default: True)
        debug: Enable debug logging (default: False)

    Returns:
        0 on success, 1 on error

    SPEC-010 Implementation:
        - Copy cmd_chat() logic from roadmap_cli.py
        - Add singleton registration (AgentType.USER_LISTENER)
        - Update welcome banner ("User Listener · Primary Interface")
        - Reuse all ChatSession infrastructure

    ENHANCED (2025-10-19):
        - Add --with-team flag (default ON) for background team daemon
        - Automatic daemon lifecycle management
        - /team and /agents commands for orchestrator queries
    """

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    team_process = None

    try:
        # Start team daemon in background (if requested)
        if with_team:
            try:
                team_process = _start_team_daemon()
            except Exception as e:
                print(f"\n⚠️  Warning: Could not start team daemon: {e}")
                print("Continuing with user-listener only...\n")
                # Continue anyway - user can still interact without team

        # US-035: Register user_listener in singleton registry
        with AgentRegistry.register(AgentType.USER_LISTENER):
            logger.info("✅ user_listener registered in singleton registry")

            # Detect and validate Claude CLI vs API mode
            use_claude_cli, claude_path = _detect_and_validate_mode()

            # Initialize components (REUSED from project-manager chat)
            editor, ai_service = _initialize_chat_components(use_claude_cli, claude_path)

            # Display welcome banner (SPEC-010: Update to identify as user_listener)
            print("\n" + "=" * 70)
            print("User Listener · Primary Interface")
            print("=" * 70)
            print("Powered by Claude AI")
            if with_team and team_process:
                print("Multi-Agent Orchestrator: RUNNING")
                print("  ✓ 6 agents launched in background")
                print("  ✓ All messages routed through orchestrator")
                print("  ✓ Velocity tracking enabled")
                print("")
                print("Architecture:")
                print("  user_listener (you) → orchestrator → agents")
                print("  Benefits: Load balancing, bottleneck detection")
            else:
                print("Multi-Agent Orchestrator: NOT RUNNING")
                print("  Run with --with-team to enable")
            print("=" * 70 + "\n")

            # Start chat session with orchestrator integration
            session = UserListenerSession(ai_service, editor)
            session.start()

            return 0

    except AgentAlreadyRunningError as e:
        print(f"\n❌ Error: {e}\n")
        return 1

    except KeyboardInterrupt:
        print("\n\nGoodbye!\n")
        if with_team:
            _stop_team_daemon()
        return 0

    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        if with_team:
            _stop_team_daemon()
        return 1

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        if "ANTHROPIC_API_KEY" in str(e):
            print("\n💡 TIP: Install Claude CLI for free usage (no API key needed)!")
            print("   Get it from: https://claude.ai/")
        if with_team:
            _stop_team_daemon()
        return 1

    except Exception as e:
        logger.error(f"Chat session failed: {e}")
        import traceback

        traceback.print_exc()
        if with_team:
            _stop_team_daemon()
        return 1

    finally:
        # Ensure team daemon is stopped on any exit
        if with_team and team_process:
            _stop_team_daemon()


if __name__ == "__main__":
    sys.exit(main())
