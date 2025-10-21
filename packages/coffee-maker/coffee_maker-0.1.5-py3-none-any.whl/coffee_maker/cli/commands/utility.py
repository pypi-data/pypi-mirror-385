"""Utility and chat commands for project manager CLI.

SPEC-050: Modularized command modules - Phase 5

This module contains:
- cmd_sync: Sync with daemon environment
- cmd_spec: Generate technical specification
- cmd_chat: Interactive chat interface
- cmd_assistant_status: Show assistant status
- cmd_assistant_refresh: Refresh assistant documentation
- cmd_spec_metrics: Show spec metrics
- cmd_spec_status: Show spec status
- cmd_spec_diff: Compare spec to implementation

Module Pattern:
    setup_parser(subparsers): Configure command-line arguments
    execute(args): Route to appropriate command handler
    cmd_*(): Individual command implementations
"""

import argparse
import logging
import os
import shutil
from datetime import datetime

from coffee_maker.config import ROADMAP_PATH, ConfigManager

logger = logging.getLogger(__name__)

# Check if chat features available
try:
    from coffee_maker.cli.ai_service import AIService
    from coffee_maker.cli.chat_interface import ChatSession
    from coffee_maker.cli.roadmap_editor import RoadmapEditor

    CHAT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chat features not available: {e}")
    CHAT_AVAILABLE = False


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync roadmap with daemon environment.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 (always successful for MVP placeholder)
    """
    print("\n" + "=" * 80)
    print("Sync with Daemon Environment")
    print("=" * 80 + "\n")

    # For MVP, this is a placeholder
    print("Sync: Not implemented yet (MVP Phase 1)")
    print("\nSync functionality will be available in Phase 2:")
    print("  - Copy ROADMAP.md to daemon environment")
    print("  - Sync database changes")
    print("  - Verify consistency")

    return 0


def cmd_spec(args: argparse.Namespace) -> int:
    """Generate technical specification for a user story.

    US-016 Phase 5: Interactive Spec Generation Workflow

    This command:
    1. Generates technical spec from user story
    2. Shows delivery estimate with buffer
    3. Prompts for review (approve/reject)
    4. Updates ROADMAP.md on approval

    Args:
        args: Parsed command-line arguments with user_story, feature_type, complexity, etc.

    Returns:
        0 on success, 1 on error
    """
    if not CHAT_AVAILABLE:
        print("❌ Spec generation not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        from coffee_maker.cli.spec_workflow import SpecWorkflow

        print("\n" + "=" * 80)
        print("Technical Specification Generation (US-016 Phase 5)")
        print("=" * 80 + "\n")

        # Initialize AI service and workflow
        ai_service = AIService()
        workflow = SpecWorkflow(ai_service)

        # Get parameters
        user_story = args.user_story
        feature_type = args.type if hasattr(args, "type") else "general"
        complexity = args.complexity if hasattr(args, "complexity") else "medium"
        user_story_id = args.id if hasattr(args, "id") else None

        print(f"Generating specification...")
        print(f"  User Story: {user_story[:60]}...")
        print(f"  Type: {feature_type}")
        print(f"  Complexity: {complexity}")
        print()

        # Generate spec
        result = workflow.generate_and_review_spec(
            user_story=user_story,
            feature_type=feature_type,
            complexity=complexity,
            user_story_id=user_story_id,
        )

        # Show summary
        print(workflow.format_spec_summary(result))
        print()

        # Prompt for review
        response = input("Review the spec? [y/n]: ").strip().lower()

        if response == "y":
            # Show spec file location
            print(f"\nSpec saved to: {result.spec_path}")
            print("\nPlease review the technical specification.")
            print()

            # Show what will be updated in ROADMAP
            if user_story_id:
                print(workflow.format_roadmap_update_example(result, user_story_id))
                print()

            # Approval workflow
            approve_response = input("Approve this specification? [y/n]: ").strip().lower()

            if approve_response == "y":
                # Approve and update ROADMAP
                if user_story_id:
                    workflow.approve_spec(result, user_story_id)
                    print(f"\n✅ Specification approved!")
                    print(f"   ROADMAP.md updated for {user_story_id}")
                    print(f"   Estimated delivery: {result.delivery_estimate['delivery_date']}")
                else:
                    print("\n⚠️  No user story ID provided, cannot update ROADMAP")
                    print("   Spec saved but ROADMAP not updated")

                return 0

            else:
                # Rejected
                reason = input("Reason for rejection (optional): ").strip()
                workflow.reject_spec(result, reason or "User rejected")
                print(f"\n❌ Specification rejected: {reason}")
                print(f"   Spec kept at {result.spec_path} for reference")

                return 0

        else:
            print(f"\nSpec saved to: {result.spec_path}")
            print("   Review later and use 'project-manager spec' to approve")
            return 0

    except Exception as e:
        logger.error(f"Spec generation failed: {e}")
        print(f"\n❌ Error generating spec: {e}")
        return 1


def cmd_chat(args: argparse.Namespace) -> int:
    """Start interactive chat session with AI (Phase 2).

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    if not CHAT_AVAILABLE:
        print("❌ Chat feature not available")
        print("\nMissing dependencies or ANTHROPIC_API_KEY not set.")
        print("\nPlease ensure:")
        print("  1. All dependencies are installed: poetry install")
        print("  2. ANTHROPIC_API_KEY is set in .env file")
        return 1

    try:
        # Check if we're ALREADY running inside Claude CLI (Claude Code)
        # If so, we MUST use API mode to avoid nesting
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
                print("\nYou're running project-manager chat from within Claude Code.")
                print("To avoid CLI nesting, we need to use API mode.")
                print("\n🔧 SOLUTION:")
                print("  1. Get your API key from: https://console.anthropic.com/")
                print("  2. Set the environment variable:")
                print("     export ANTHROPIC_API_KEY='your-api-key-here'")
                print("  3. Or add it to your .env file")
                print("\n💡 ALTERNATIVE: Run from a regular terminal (not Claude Code)")
                print("=" * 70 + "\n")
                return 1
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
            print("  2. Run: poetry run project-manager chat")
            print("\n🔧 SOLUTION 2 (API Mode):")
            print("  1. Get your API key from: https://console.anthropic.com/")
            print("  2. Set the environment variable:")
            print("     export ANTHROPIC_API_KEY='your-api-key-here'")
            print("  3. Run: poetry run project-manager chat")
            print("\n" + "=" * 70 + "\n")
            return 1

        # Initialize components
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
            return 1

        # Start chat session
        session = ChatSession(ai_service, editor)
        session.start()

        return 0

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        if "ANTHROPIC_API_KEY" in str(e):
            print("\n💡 TIP: Install Claude CLI for free usage (no API key needed)!")
            print("   Get it from: https://claude.ai/")
        return 1
    except Exception as e:
        logger.error(f"Chat session failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


def cmd_assistant_status(args):
    """Show assistant status and knowledge state.

    PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    if not CHAT_AVAILABLE:
        print("❌ Assistant feature not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        # Get assistant manager from global context (will be set in main())
        if not hasattr(cmd_assistant_status, "manager"):
            print("❌ Assistant manager not initialized")
            print("\nThe assistant is not running.")
            return 1

        manager = cmd_assistant_status.manager
        status = manager.get_status()

        print("\n" + "=" * 80)
        print("🤖 ASSISTANT STATUS")
        print("=" * 80 + "\n")

        # Online status
        if status["online"]:
            print("Status: 🟢 ONLINE")
        else:
            print("Status: 🔴 OFFLINE")

        # Assistant availability
        if status["assistant_available"]:
            print("Assistant: ✅ Available")
        else:
            print("Assistant: ❌ Not available (no LLM configured)")

        # Refresh info
        if status["last_refresh"]:
            from dateutil.parser import isoparse

            last_refresh = isoparse(status["last_refresh"])
            elapsed = datetime.now() - last_refresh
            minutes = int(elapsed.total_seconds() // 60)

            print(f"\nLast Documentation Refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')} ({minutes} minutes ago)")
        else:
            print("\nLast Documentation Refresh: Never")

        if status["next_refresh"]:
            print(f"Next Refresh: {status['next_refresh']}")

        # Documentation knowledge
        print(f"\nDocumentation Knowledge:")
        print(f"  📚 {status['docs_loaded']} document(s) loaded")

        for doc_info in status["docs_info"]:
            print(f"  ✅ {doc_info['path']}")
            print(f"     Modified: {doc_info['modified']}, Lines: {doc_info['line_count']}")

        # Git history
        if status["git_commits_loaded"] > 0:
            print(f"\n  📝 Git History: {status['git_commits_loaded']} recent commits loaded")

        # Tools
        print("\nTools Available:")
        tool_names = [
            "read_file",
            "search_code",
            "list_files",
            "git_log",
            "git_diff",
            "execute_bash",
        ]
        for tool in tool_names:
            print(f"  ✅ {tool}")

        print("\n✨ Ready to answer questions! 🚀")
        print("\nUse 'project-manager chat' to ask questions")
        print("Use 'project-manager assistant-refresh' to manually refresh documentation")
        print()

        return 0

    except Exception as e:
        logger.error(f"Failed to get assistant status: {e}", exc_info=True)
        print(f"❌ Error getting assistant status: {e}")
        return 1


def cmd_assistant_refresh(args):
    """Manually refresh assistant documentation.

    PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    if not CHAT_AVAILABLE:
        print("❌ Assistant feature not available")
        print("\nMissing dependencies. Install with: poetry install")
        return 1

    try:
        # Get assistant manager from global context
        if not hasattr(cmd_assistant_refresh, "manager"):
            print("❌ Assistant manager not initialized")
            return 1

        manager = cmd_assistant_refresh.manager

        print("\n🔄 Refreshing assistant documentation...")
        print()

        # Trigger manual refresh
        result = manager.manual_refresh()

        if result["success"]:
            print("Reading ROADMAP.md... ✅")
            print("Reading COLLABORATION_METHODOLOGY.md... ✅")
            print("Reading DOCUMENTATION_INDEX.md... ✅")
            print("Reading TUTORIALS.md... ✅")
            print("Reading git history... ✅")
            print()
            print(f"✅ Assistant knowledge refreshed successfully!")
            print(f"   {result['docs_refreshed']} document(s) updated")
            print(f"   Timestamp: {result['timestamp']}")
            print()
        else:
            print(f"❌ Refresh failed: {result['message']}")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Manual refresh failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


def cmd_spec_metrics(args: argparse.Namespace) -> int:
    """Show spec metrics and weekly improvement report.

    US-049: Continuous Spec Improvement Loop (CFR-010)

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.cli.spec_metrics import SpecMetricsTracker

    try:
        print("\n" + "=" * 80)
        print("SPEC IMPROVEMENT METRICS (US-049 - CFR-010)")
        print("=" * 80 + "\n")

        tracker = SpecMetricsTracker()

        # Generate weekly report
        report = tracker.generate_weekly_report()
        print(report)

        return 0

    except Exception as e:
        logger.error(f"Failed to show spec metrics: {e}")
        print(f"❌ Error showing spec metrics: {e}")
        return 1


def cmd_spec_status(args: argparse.Namespace) -> int:
    """Show spec status and coverage report.

    US-049: Continuous Spec Improvement Loop (CFR-010)

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.cli.spec_metrics import SpecMetricsTracker

    try:
        print("\n" + "=" * 80)
        print("SPEC STATUS REPORT (US-049 - CFR-010)")
        print("=" * 80 + "\n")

        tracker = SpecMetricsTracker()

        # Generate status report
        report = tracker.show_spec_status()
        print(report)

        return 0

    except Exception as e:
        logger.error(f"Failed to show spec status: {e}")
        print(f"❌ Error showing spec status: {e}")
        return 1


def cmd_spec_diff(args: argparse.Namespace) -> int:
    """Compare spec to actual implementation.

    US-049: Continuous Spec Improvement Loop (CFR-010)

    Args:
        args: Parsed command-line arguments with priority

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.cli.spec_diff import SpecDiffAnalyzer

    try:
        if not hasattr(args, "priority") or not args.priority:
            print("❌ Error: You must specify a priority")
            print("\nUsage: project-manager spec-diff <priority>")
            print("\nExamples:")
            print("  project-manager spec-diff 'PRIORITY 9'")
            print("  project-manager spec-diff SPEC-049")
            return 1

        print("\n" + "=" * 80)
        print("SPEC vs IMPLEMENTATION ANALYSIS (US-049 - CFR-010)")
        print("=" * 80 + "\n")

        analyzer = SpecDiffAnalyzer()

        # Analyze priority
        report = analyzer.analyze_priority(args.priority)
        print(report)

        return 0

    except Exception as e:
        logger.error(f"Failed to analyze spec diff: {e}")
        print(f"❌ Error analyzing spec diff: {e}")
        return 1


def cmd_spec_review(args: argparse.Namespace) -> int:
    """Show technical spec coverage report for architect.

    US-047 Phase 2: Architect Proactive Workflow

    This command shows which priorities have technical specifications and
    which ones are missing, helping architect proactively create missing specs
    to enforce CFR-008.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.cli.spec_review import SpecReviewReport

    try:
        print("\n" + "=" * 80)
        print("TECHNICAL SPEC COVERAGE REPORT (US-047 - CFR-008)")
        print("=" * 80 + "\n")

        report_gen = SpecReviewReport()
        report = report_gen.generate_report()
        print(report)

        return 0

    except Exception as e:
        logger.error(f"Failed to generate spec review report: {e}")
        print(f"❌ Error generating spec review: {e}")
        return 1


def setup_parser(subparsers):
    """Configure utility-related subcommands.

    Args:
        subparsers: argparse subparsers object
    """
    # Sync command
    subparsers.add_parser("sync", help="Sync with daemon environment")

    # Spec command (US-016 Phase 5)
    spec_parser = subparsers.add_parser("spec", help="Generate technical specification (US-016 Phase 5)")
    spec_parser.add_argument("user_story", help="User story description")
    spec_parser.add_argument(
        "--type",
        default="general",
        help="Feature type (crud, integration, ui, infrastructure, analytics, security)",
    )
    spec_parser.add_argument("--complexity", default="medium", help="Complexity (low, medium, high)")
    spec_parser.add_argument("--id", help="User story ID (e.g., US-016) for ROADMAP update")

    # Chat command (Phase 2)
    subparsers.add_parser("chat", help="Start interactive AI chat session (Phase 2)")

    # Assistant commands (PRIORITY 5)
    subparsers.add_parser("assistant-status", help="Show assistant status and knowledge state")
    subparsers.add_parser("assistant-refresh", help="Manually refresh assistant documentation")

    # Spec-metrics command (US-049: CFR-010)
    subparsers.add_parser("spec-metrics", help="Show spec improvement metrics and weekly report (US-049)")

    # Spec-status command (US-049: CFR-010)
    subparsers.add_parser("spec-status", help="Show spec status and coverage report (US-049)")

    # Spec-diff command (US-049: CFR-010)
    spec_diff_parser = subparsers.add_parser("spec-diff", help="Compare spec to implementation (US-049)")
    spec_diff_parser.add_argument("priority", help="Priority or spec ID to analyze")

    # Spec-review command (US-047: CFR-008)
    subparsers.add_parser("spec-review", help="Show technical spec coverage report (US-047 - CFR-008)")


def execute(args: argparse.Namespace) -> int:
    """Execute utility commands based on args.command.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    commands = {
        "sync": cmd_sync,
        "spec": cmd_spec,
        "chat": cmd_chat,
        "assistant-status": cmd_assistant_status,
        "assistant-refresh": cmd_assistant_refresh,
        "spec-metrics": cmd_spec_metrics,
        "spec-status": cmd_spec_status,
        "spec-diff": cmd_spec_diff,
        "spec-review": cmd_spec_review,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown utility command: {args.command}")
        return 1
