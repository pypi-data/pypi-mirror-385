"""Code Developer Daemon CLI.

This module provides the command-line interface for the code-developer daemon.

Usage:
    code-developer                      # Interactive mode (Claude CLI, default)
    code-developer --auto-approve       # Autonomous mode (Claude CLI, default)
    code-developer --use-api            # Use Anthropic API instead (requires credits)
    code-developer --help               # Show help

By default, the daemon uses Claude CLI (subscription). Use --use-api for Anthropic API mode.
"""

import argparse
import logging
import os
import signal
import sys
from types import FrameType
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, env vars must be set manually

from coffee_maker.autonomous.daemon import DevDaemon
from coffee_maker.cli.console_ui import (
    console,
    create_table,
    error,
    info,
    section_header,
    warning,
)
from coffee_maker.config import ConfigManager
from coffee_maker.process_manager import ProcessManager


def check_claude_session() -> bool:
    """Check if running inside a Claude Code session and warn user.

    Returns:
        bool: True if running inside Claude Code terminal session
    """
    # Check for ACTUAL Claude Code environment variables
    # These are set when running inside a Claude Code terminal session
    claude_env_vars = [
        "CLAUDECODE",  # Set to "1" when inside Claude Code
        "CLAUDE_CODE_ENTRYPOINT",  # Set to "cli" when using Claude Code CLI
    ]

    for var in claude_env_vars:
        if os.environ.get(var):
            return True

    # NOTE: We do NOT check for running processes with pgrep
    # because that's too broad - it matches any Claude process anywhere,
    # not just the terminal session we're running in.
    # Only environment variables reliably indicate we're INSIDE a session.

    return False


def main() -> None:
    """Run the code-developer daemon."""
    parser = argparse.ArgumentParser(
        description="Code Developer Daemon - Autonomous development agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  code-developer                      # Interactive mode (Claude CLI, default)
  code-developer --auto-approve       # Autonomous mode (Claude CLI, default)
  code-developer --use-api            # Use Anthropic API instead (requires credits)
  code-developer --no-pr              # Skip PR creation

The daemon reads your ROADMAP.md file and autonomously implements features.
By default, it uses Claude CLI (subscription). Use --use-api for Anthropic API mode.
        """,
    )

    parser.add_argument(
        "--roadmap",
        default="docs/roadmap/ROADMAP.md",
        help="Path to ROADMAP.md (default: docs/roadmap/ROADMAP.md)",
    )

    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve implementation without asking (autonomous mode)",
    )

    parser.add_argument("--no-pr", action="store_true", help="Skip creating pull requests")

    parser.add_argument(
        "--sleep",
        type=int,
        default=30,
        help="Seconds to sleep between iterations (default: 30)",
    )

    parser.add_argument("--model", default="sonnet", help="Claude model to use (default: sonnet)")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging output")

    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Use Anthropic API instead of Claude CLI (requires API credits)",
    )

    parser.add_argument(
        "--claude-path",
        default="/opt/homebrew/bin/claude",
        help="Path to claude CLI executable (default: /opt/homebrew/bin/claude)",
    )

    parser.add_argument(
        "--priority",
        type=int,
        help="Work on a specific priority only (used by orchestrator for parallel execution)",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Determine mode: CLI is default, API requires --use-api flag
    use_cli_mode = not args.use_api

    # Check for required prerequisites based on mode
    if use_cli_mode:
        # CLI mode (default) - Check if Claude CLI is available
        if not os.path.isfile(args.claude_path):
            console.print()
            warning("Claude CLI not found (default mode)")
            console.print()
            info(f"Claude CLI not found at: [bold]{args.claude_path}[/bold]")
            console.print()
            console.print("The daemon uses Claude CLI by default (uses your Claude subscription).")
            console.print()
            console.print("[bold cyan]📋 CHOOSE AN OPTION:[/bold cyan]")
            console.print()
            console.print("[bold green]  Option A: Install Claude CLI (Recommended)[/bold green]")
            console.print("  ─" * 30)
            console.print("    1. Install from: [link]https://docs.claude.com/docs/claude-cli[/link]")
            console.print("    2. Verify: [cyan]claude --version[/cyan]")
            console.print("    3. Run: [cyan]code-developer --auto-approve[/cyan]")
            console.print()
            console.print("[bold yellow]  Option B: Use Anthropic API (Requires Credits)[/bold yellow]")
            console.print("  ─" * 30)
            console.print("    1. Get API key: [link]https://console.anthropic.com/[/link]")
            console.print("    2. Set: [cyan]export ANTHROPIC_API_KEY='your-key'[/cyan]")
            console.print("    3. Run: [cyan]code-developer --use-api --auto-approve[/cyan]")
            console.print()
            sys.exit(1)
    else:
        # API mode (--use-api flag) - Check if API key is set
        if not ConfigManager.has_anthropic_api_key():
            console.print()
            error("ANTHROPIC_API_KEY not set!")
            console.print()
            info("You're using [bold]--use-api[/bold] but ANTHROPIC_API_KEY is not set.")
            console.print()
            console.print("[bold cyan]🔧 SOLUTION:[/bold cyan]")
            console.print("  1. Get your API key from: [link]https://console.anthropic.com/[/link]")
            console.print("  2. Set the environment variable:")
            console.print("     [cyan]export ANTHROPIC_API_KEY='your-api-key-here'[/cyan]")
            console.print("  3. Run the daemon again with [cyan]--use-api[/cyan]")
            console.print()
            console.print("[dim]OR remove --use-api to use Claude CLI (default, no API key needed)[/dim]")
            console.print()
            sys.exit(1)

    # Check if running inside Claude session (warning only, not blocking)
    if check_claude_session():
        console.print()
        info("Running inside Claude Code session")
        console.print()
        console.print("You're running the daemon from within Claude Code.")
        console.print("This works fine now (we use the Anthropic SDK directly),")
        console.print("but running from a separate terminal provides better isolation.")
        console.print()
        console.print("[dim]💡 TIP: For better debugging, run from a separate terminal.[/dim]")
        console.print()

    # Create and run daemon
    section_header("Code Developer Daemon", "Autonomous development agent")

    # Show configuration in a table
    config_table = create_table(title="Configuration", show_header=False)
    config_table.add_column(style="bold cyan", justify="right", width=20)
    config_table.add_column(width=50)

    config_table.add_row("Roadmap", args.roadmap)
    config_table.add_row(
        "Mode",
        (
            "[bold green]Autonomous[/bold green] (auto-approve)"
            if args.auto_approve
            else "[bold yellow]Interactive[/bold yellow] (requires approval)"
        ),
    )
    config_table.add_row(
        "Pull Requests",
        "[red]Disabled[/red]" if args.no_pr else "[green]Enabled[/green]",
    )
    config_table.add_row(
        "Backend",
        ("[blue]Claude CLI[/blue] (subscription)" if use_cli_mode else "[magenta]Anthropic API[/magenta] (credits)"),
    )
    config_table.add_row("Model", args.model)

    console.print(config_table)
    console.print()
    info("Starting daemon... Press [bold]Ctrl+C[/bold] to stop")
    console.print()

    # Initialize process manager for PID file handling
    process_manager = ProcessManager()

    # Register signal handlers for graceful shutdown
    def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
        """Handle shutdown signals gracefully."""
        logger = logging.getLogger(__name__)
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        process_manager._clean_stale_pid()
        print("\n\n⏹️  Daemon stopped (signal received)")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        daemon = DevDaemon(
            roadmap_path=args.roadmap,
            auto_approve=args.auto_approve,
            create_prs=not args.no_pr,
            sleep_interval=args.sleep,
            model=args.model,
            use_claude_cli=use_cli_mode,
            claude_cli_path=args.claude_path,
            specific_priority=args.priority,
        )

        # Write PID file after daemon is initialized
        process_manager._write_pid_file(os.getpid())
        info(f"Daemon PID: [bold]{os.getpid()}[/bold]")
        console.print(f"[dim]PID file: {process_manager.pid_file}[/dim]")
        console.print()

        # Run daemon main loop
        daemon.run()

    except KeyboardInterrupt:
        console.print()
        console.print()
        info("Daemon stopped by user")
        process_manager._clean_stale_pid()
        sys.exit(0)
    except Exception as e:
        console.print()
        console.print()
        error(str(e), suggestion="Check the logs for more details")
        import traceback

        traceback.print_exc()
        process_manager._clean_stale_pid()
        sys.exit(1)
    finally:
        # Always clean up PID file on exit
        process_manager._clean_stale_pid()


if __name__ == "__main__":
    main()
