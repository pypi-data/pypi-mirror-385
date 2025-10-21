"""Status and monitoring commands for project manager CLI.

SPEC-050: Modularized command modules - Phase 3

This module contains all status commands extracted from roadmap_cli.py:
- cmd_status: Show daemon status
- cmd_developer_status: Show developer status dashboard
- cmd_metrics: Show estimation metrics and velocity
- cmd_summary: Show delivery summary
- cmd_calendar: Show upcoming deliverables calendar
- cmd_dev_report: Show daily developer report

Module Pattern:
    setup_parser(subparsers): Configure command-line arguments
    execute(args): Route to appropriate command handler
    cmd_*(): Individual command implementations
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

from coffee_maker.config import ROADMAP_PATH

logger = logging.getLogger(__name__)


def cmd_status(args: argparse.Namespace) -> int:
    """Show daemon status.

    PRIORITY 2.8: Daemon Status Reporting

    Reads ~/.coffee_maker/daemon_status.json and displays current daemon status.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager status

        Daemon Status: Running
        PID: 12345
        Started: 2025-10-11 10:30:00
        Current Priority: PRIORITY 2.8 - Daemon Status Reporting
        Iteration: 5
        Crashes: 0/3
    """
    from coffee_maker.utils.file_io import FileOperationError, read_json_file

    print("\n" + "=" * 80)
    print("Code Developer Daemon Status")
    print("=" * 80 + "\n")

    # Read status file
    status_file = Path.home() / ".coffee_maker" / "daemon_status.json"

    if not status_file.exists():
        print("❌ Daemon status file not found")
        print("\nThe daemon is either:")
        print("  - Not running")
        print("  - Never been started")
        print("\n💡 Start the daemon with: poetry run code-developer")
        return 1

    try:
        status = read_json_file(status_file)

        # Display daemon status
        daemon_status = status.get("status", "unknown")
        if daemon_status == "running":
            print("Status: 🟢 Running")
        elif daemon_status == "stopped":
            print("Status: 🔴 Stopped")
        else:
            print(f"Status: ⚪ {daemon_status}")

        # PID and process info
        pid = status.get("pid")
        if pid:
            print(f"PID: {pid}")

            # Check if process is actually running
            import psutil

            try:
                process = psutil.Process(pid)
                if process.is_running():
                    print(
                        f"Process: ✅ Running (CPU: {process.cpu_percent()}%, Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB)"
                    )
                else:
                    print("Process: ⚠️  Not running (stale status file)")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print("Process: ⚠️  Not found (stale status file)")

        # Start time
        started_at = status.get("started_at")
        if started_at:
            try:
                start_dt = datetime.fromisoformat(started_at)
                print(f"Started: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")

                # Calculate uptime
                uptime = datetime.now() - start_dt
                hours = int(uptime.total_seconds() // 3600)
                minutes = int((uptime.total_seconds() % 3600) // 60)
                print(f"Uptime: {hours}h {minutes}m")
            except ValueError:
                print(f"Started: {started_at}")

        # Current priority
        current_priority = status.get("current_priority")
        if current_priority:
            name = current_priority.get("name", "Unknown")
            title = current_priority.get("title", "")
            print(f"\nCurrent Priority: {name}")
            if title:
                print(f"  {title}")

            priority_started = current_priority.get("started_at")
            if priority_started:
                try:
                    priority_dt = datetime.fromisoformat(priority_started)
                    elapsed = datetime.now() - priority_dt
                    minutes = int(elapsed.total_seconds() // 60)
                    print(f"  Working on this for: {minutes} minutes")
                except ValueError:
                    pass
        else:
            print("\nCurrent Priority: None (idle)")

        # Iteration count
        iteration = status.get("iteration", 0)
        print(f"\nIteration: {iteration}")

        # Crash info
        crashes = status.get("crashes", {})
        crash_count = crashes.get("count", 0)
        max_crashes = crashes.get("max", 3)
        print(f"Crashes: {crash_count}/{max_crashes}")

        if crash_count > 0:
            print("⚠️  Recent crashes detected!")
            crash_history = crashes.get("history", [])
            if crash_history:
                print("\nRecent crash history:")
                for i, crash in enumerate(crash_history[-3:], 1):
                    timestamp = crash.get("timestamp", "Unknown")
                    exception_type = crash.get("exception_type", "Unknown")
                    print(f"  {i}. {timestamp} - {exception_type}")

        # Context management info
        context = status.get("context", {})
        iterations_since_compact = context.get("iterations_since_compact", 0)
        compact_interval = context.get("compact_interval", 10)
        last_compact = context.get("last_compact")

        print(f"\nContext Management:")
        print(f"  Iterations since last compact: {iterations_since_compact}/{compact_interval}")
        if last_compact:
            try:
                compact_dt = datetime.fromisoformat(last_compact)
                print(f"  Last compact: {compact_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except ValueError:
                print(f"  Last compact: {last_compact}")
        else:
            print("  Last compact: Never")

        # Last update time
        last_update = status.get("last_update")
        if last_update:
            try:
                update_dt = datetime.fromisoformat(last_update)
                time_since = datetime.now() - update_dt
                seconds = int(time_since.total_seconds())
                print(f"\nLast update: {seconds}s ago ({update_dt.strftime('%H:%M:%S')})")
            except ValueError:
                print(f"\nLast update: {last_update}")

        return 0

    except FileOperationError as e:
        print("❌ Status file is corrupted")
        print(f"\nFile: {status_file}")
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error reading status: {e}")
        return 1


def cmd_developer_status(args: argparse.Namespace) -> int:
    """Show developer status dashboard.

    PRIORITY 4: Developer Status Dashboard

    Displays real-time developer status including current task, progress,
    activities, and metrics.

    Args:
        args: Parsed command-line arguments with optional --watch flag

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager developer-status
        $ project-manager developer-status --watch
    """
    from coffee_maker.cli.developer_status_display import DeveloperStatusDisplay

    display = DeveloperStatusDisplay()

    if hasattr(args, "watch") and args.watch:
        # Continuous watch mode
        display.watch(interval=args.interval if hasattr(args, "interval") else 5)
    else:
        # One-time display
        if not display.show():
            return 1

    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    """Show estimation metrics and velocity tracking.

    US-015: Estimation Metrics & Velocity Tracking

    Displays comprehensive metrics including:
    - Current velocity (stories/week, points/week)
    - Estimation accuracy trends
    - Category-specific accuracy
    - Spec vs no-spec comparison
    - Recent completed stories

    Args:
        args: Parsed command-line arguments with optional filters

    Returns:
        0 on success, 1 on error

    Example:
        $ project-manager metrics
        $ project-manager metrics --period 14
        $ project-manager metrics --category feature
    """
    from coffee_maker.autonomous.story_metrics import StoryMetricsDB

    try:
        print("\n" + "=" * 80)
        print("📊 ESTIMATION METRICS & VELOCITY TRACKING (US-015)")
        print("=" * 80 + "\n")

        metrics_db = StoryMetricsDB()

        # Get period from args (default: 7 days for weekly)
        period_days = args.period if hasattr(args, "period") else 7

        # Current Velocity
        print("📈 CURRENT VELOCITY")
        print("-" * 80)
        velocity = metrics_db.get_current_velocity(period_days=period_days)

        print(f"Period: Last {period_days} days")
        print(f"Stories per week: {velocity['stories_per_week']:.2f}")
        print(f"Story points per week: {velocity['points_per_week']:.2f}")
        print(f"Average days per story: {velocity['avg_days_per_story']:.2f}")
        print(f"Average accuracy: {velocity['avg_accuracy_pct']:.1f}%")
        print()

        # Accuracy Trends
        print("🎯 ACCURACY TRENDS (Recent 10 Stories)")
        print("-" * 80)
        trends = metrics_db.get_accuracy_trends(limit=10)

        if trends:
            print(f"{'Story':<15} {'Estimated':<12} {'Actual':<10} {'Error':<10} {'Accuracy':>10}")
            print("-" * 80)
            for trend in trends:
                story_id = trend["story_id"]
                est_min = trend["estimated_min_days"]
                est_max = trend["estimated_max_days"]
                actual = trend["actual_days"]
                error = trend["estimation_error"]
                accuracy = trend["estimation_accuracy_pct"]

                est_str = f"{est_min}-{est_max}"
                error_str = f"{error:+.1f}d" if error else "N/A"
                accuracy_str = f"{accuracy:.1f}%" if accuracy else "N/A"

                # Color coding based on accuracy
                if accuracy and accuracy >= 90:
                    marker = "✅"
                elif accuracy and accuracy >= 75:
                    marker = "⚠️ "
                else:
                    marker = "❌"

                print(f"{story_id:<15} {est_str:<12} {actual:<10.1f} {error_str:<10} {marker} {accuracy_str:>8}")
        else:
            print("No completed stories yet")
        print()

        # Category Accuracy
        print("📂 ACCURACY BY CATEGORY")
        print("-" * 80)
        category_stats = metrics_db.get_category_accuracy()

        if category_stats:
            print(f"{'Category':<15} {'Stories':<10} {'Avg Accuracy':<15} {'Avg Actual':<12} {'Avg Estimated':<15}")
            print("-" * 80)
            for stat in category_stats:
                category = stat["category"]
                count = stat["story_count"]
                accuracy = stat["avg_accuracy_pct"]
                actual = stat["avg_actual_days"]
                estimated = stat["avg_estimated_days"]

                print(f"{category:<15} {count:<10} {accuracy:<15.1f}% {actual:<12.1f} {estimated:<15.1f}")
        else:
            print("No category data yet")
        print()

        # Spec vs No-Spec Comparison
        print("📋 TECHNICAL SPEC COMPARISON")
        print("-" * 80)
        spec_comparison = metrics_db.get_spec_comparison()

        with_spec = spec_comparison["with_spec"]
        without_spec = spec_comparison["without_spec"]

        print(f"{'Type':<20} {'Stories':<10} {'Avg Accuracy':<15} {'Avg Days':<12}")
        print("-" * 80)
        print(
            f"{'With Spec':<20} {with_spec['count']:<10} {with_spec['avg_accuracy_pct']:<15.1f}% {with_spec['avg_actual_days']:<12.1f}"
        )
        print(
            f"{'Without Spec':<20} {without_spec['count']:<10} {without_spec['avg_accuracy_pct']:<15.1f}% {without_spec['avg_actual_days']:<12.1f}"
        )

        if with_spec["count"] > 0 and without_spec["count"] > 0:
            accuracy_diff = with_spec["avg_accuracy_pct"] - without_spec["avg_accuracy_pct"]
            if accuracy_diff > 0:
                print(f"\n✅ Stories with technical specs are {accuracy_diff:.1f}% more accurate!")
            elif accuracy_diff < 0:
                print(f"\n⚠️  Stories without specs are {abs(accuracy_diff):.1f}% more accurate")
            else:
                print("\n➡️  No significant difference")
        print()

        # Tips
        print("💡 TIPS")
        print("-" * 80)
        if velocity["avg_accuracy_pct"] < 75:
            print("⚠️  Accuracy below 75% - consider creating more detailed technical specs")
        elif velocity["avg_accuracy_pct"] >= 90:
            print("✅ Excellent estimation accuracy! Keep up the good work!")
        else:
            print("✅ Good estimation accuracy - room for improvement")

        if with_spec["count"] > 0 and with_spec["avg_accuracy_pct"] > without_spec["avg_accuracy_pct"]:
            print("✅ Technical specs improve accuracy - keep using them!")

        print()
        print(f"Database: {metrics_db.db_path}")
        print(f"Use 'project-manager metrics --period 14' to see 2-week velocity")
        print()

        return 0

    except Exception as e:
        logger.error(f"Failed to show metrics: {e}", exc_info=True)
        print(f"❌ Error showing metrics: {e}")
        return 1


def cmd_summary(args: argparse.Namespace) -> int:
    """Show delivery summary for recently completed stories.

    US-017 Phase 2: CLI Integration - /summary command
    US-017 Phase 4: Manual update trigger - /summary --update

    Args:
        args: Parsed command-line arguments with optional --days, --format, --update

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.reports.status_report_generator import StatusReportGenerator
    from coffee_maker.reports.status_tracking_updater import check_and_update_if_needed

    try:
        # Check if update flag is set (Phase 4)
        force_update = args.update if hasattr(args, "update") else False

        if force_update:
            print("\n" + "=" * 80)
            print("🔄 FORCING STATUS_TRACKING.md UPDATE")
            print("=" * 80 + "\n")

            result = check_and_update_if_needed(force=True)

            if result["updated"]:
                print(f"✅ STATUS_TRACKING.md updated successfully!")
                print(f"   Reason: {result['reason']}")
                print()
            else:
                print(f"⚠️  Update skipped: {result['reason']}")
                print()
        else:
            # Auto-check if update is needed (3-day schedule or estimate changes)
            result = check_and_update_if_needed(force=False)

            if result["updated"]:
                print("\n" + "=" * 80)
                print("✅ STATUS_TRACKING.md AUTO-UPDATE")
                print("=" * 80)
                print(f"Reason: {result['reason']}")
                print()

        # Get parameters from args
        days = args.days if hasattr(args, "days") else 14
        output_format = args.format if hasattr(args, "format") else "markdown"

        # Validate parameters
        if days <= 0:
            print("❌ Error: --days must be greater than 0")
            return 1

        if output_format not in ["text", "markdown"]:
            print(f"❌ Error: Invalid format '{output_format}'. Use 'text' or 'markdown'")
            return 1

        # Initialize generator
        generator = StatusReportGenerator(str(ROADMAP_PATH))

        # Get recent completions
        completions = generator.get_recent_completions(days=days)

        if not completions:
            print("\n" + "=" * 80)
            print(f"📦 DELIVERY SUMMARY (Last {days} days)")
            print("=" * 80 + "\n")
            print(f"No deliveries completed in the last {days} days.")
            print("\nTip: Try increasing the time period with --days N")
            print()
            return 0

        # Format summary
        summary = generator.format_delivery_summary(completions)

        # Display based on format
        if output_format == "markdown":
            print("\n" + summary)
        else:
            # Text format: Remove markdown formatting
            text_summary = summary.replace("# ", "").replace("## ", "").replace("**", "").replace("---", "-" * 80)
            print("\n" + text_summary)

        # Footer
        print()
        print(f"💡 TIP: Use 'project-manager summary --days N' to change time period")
        print(f"   Use 'project-manager summary --update' to force STATUS_TRACKING.md update")
        print(f"   Use 'project-manager calendar' to see upcoming deliverables")
        print()

        return 0

    except FileNotFoundError:
        print(f"❌ Error: ROADMAP not found at {ROADMAP_PATH}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}", exc_info=True)
        print(f"❌ Error generating summary: {e}")
        return 1


def cmd_calendar(args: argparse.Namespace) -> int:
    """Show calendar of upcoming deliverables with estimated completion dates.

    US-017 Phase 2: CLI Integration - /calendar command

    Args:
        args: Parsed command-line arguments with optional --limit, --format, --update

    Returns:
        0 on success, 1 on error
    """
    from coffee_maker.reports.status_report_generator import StatusReportGenerator
    from coffee_maker.reports.status_tracking_updater import check_and_update_if_needed

    try:
        # Check if update flag is set (Phase 4)
        force_update = args.update if hasattr(args, "update") else False

        if force_update:
            print("\n" + "=" * 80)
            print("🔄 FORCING STATUS_TRACKING.md UPDATE")
            print("=" * 80 + "\n")

            result = check_and_update_if_needed(force=True)

            if result["updated"]:
                print(f"✅ STATUS_TRACKING.md updated successfully!")
                print(f"   Reason: {result['reason']}")
                print()
            else:
                print(f"⚠️  Update skipped: {result['reason']}")
                print()
        else:
            # Auto-check if update is needed (3-day schedule or estimate changes)
            result = check_and_update_if_needed(force=False)

            if result["updated"]:
                print("\n" + "=" * 80)
                print("✅ STATUS_TRACKING.md AUTO-UPDATE")
                print("=" * 80)
                print(f"Reason: {result['reason']}")
                print()

        # Get parameters from args
        limit = args.limit if hasattr(args, "limit") else 3
        output_format = args.format if hasattr(args, "format") else "markdown"

        # Validate parameters
        if limit <= 0:
            print("❌ Error: --limit must be greater than 0")
            return 1

        if output_format not in ["text", "markdown"]:
            print(f"❌ Error: Invalid format '{output_format}'. Use 'text' or 'markdown'")
            return 1

        # Initialize generator
        generator = StatusReportGenerator(str(ROADMAP_PATH))

        # Get upcoming deliverables
        upcoming = generator.get_upcoming_deliverables(limit=limit)

        if not upcoming:
            print("\n" + "=" * 80)
            print("📅 UPCOMING DELIVERABLES CALENDAR")
            print("=" * 80 + "\n")
            print("No upcoming deliverables with time estimates found.")
            print("\nTip: Add estimated effort to stories in ROADMAP.md")
            print("   Format: **Estimated Effort**: X-Y days")
            print()
            return 0

        # Format calendar
        calendar = generator.format_calendar_report(upcoming)

        # Display based on format
        if output_format == "markdown":
            print("\n" + calendar)
        else:
            # Text format: Remove markdown formatting
            text_calendar = calendar.replace("# ", "").replace("## ", "").replace("**", "").replace("---", "-" * 80)
            print("\n" + text_calendar)

        # Footer
        print()
        print(f"💡 TIP: Use 'project-manager calendar --limit N' to see more/fewer items")
        print(f"   Use 'project-manager calendar --update' to force STATUS_TRACKING.md update")
        print(f"   Use 'project-manager summary' to see recent deliveries")
        print()

        return 0

    except FileNotFoundError:
        print(f"❌ Error: ROADMAP not found at {ROADMAP_PATH}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate calendar: {e}", exc_info=True)
        print(f"❌ Error generating calendar: {e}")
        return 1


def cmd_dev_report(args: argparse.Namespace) -> int:
    """Show daily or weekly developer report.

    PRIORITY 9: Enhanced code_developer Communication & Daily Standup

    Args:
        args: Parsed arguments with optional --days flag

    Returns:
        0 on success, 1 on error
    """
    from rich.markdown import Markdown
    from rich.panel import Panel

    from coffee_maker.cli.console_ui import console
    from coffee_maker.cli.daily_report_generator import DailyReportGenerator

    try:
        # Get days from args (default: 1 for yesterday)
        days = args.days if hasattr(args, "days") else 1
        since_date = datetime.now() - timedelta(days=days)

        generator = DailyReportGenerator()
        report = generator.generate_report(since_date=since_date)

        # Display with rich
        panel = Panel(
            Markdown(report),
            title="[bold cyan]📊 DEVELOPER REPORT[/bold cyan]",
            style="cyan",
        )
        console.print(panel)
        console.print()

        return 0

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        from coffee_maker.cli.console_ui import error

        error(f"Failed to generate report: {e}")
        return 1


def setup_parser(subparsers):
    """Configure status-related subcommands.

    Args:
        subparsers: argparse subparsers object
    """
    # Status command
    subparsers.add_parser("status", help="Show daemon status")

    # Developer status command (PRIORITY 4)
    dev_status_parser = subparsers.add_parser("developer-status", help="Show developer status dashboard")
    dev_status_parser.add_argument("--watch", action="store_true", help="Continuous watch mode")
    dev_status_parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)",
    )

    # Metrics command (US-015)
    metrics_parser = subparsers.add_parser("metrics", help="Show estimation metrics and velocity tracking (US-015)")
    metrics_parser.add_argument(
        "--period",
        type=int,
        default=7,
        help="Period in days for velocity calculation (default: 7)",
    )

    # Summary command (US-017 Phase 2 + Phase 4)
    summary_parser = subparsers.add_parser("summary", help="Show delivery summary for recent completions (US-017)")
    summary_parser.add_argument("--days", type=int, default=14, help="Number of days to look back (default: 14)")
    summary_parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["text", "markdown"],
        help="Output format (default: markdown)",
    )
    summary_parser.add_argument(
        "--update",
        action="store_true",
        help="Force regenerate STATUS_TRACKING.md (Phase 4)",
    )

    # Calendar command (US-017 Phase 2 + Phase 4)
    calendar_parser = subparsers.add_parser("calendar", help="Show calendar of upcoming deliverables (US-017)")
    calendar_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of upcoming items to show (default: 3)",
    )
    calendar_parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["text", "markdown"],
        help="Output format (default: markdown)",
    )
    calendar_parser.add_argument(
        "--update",
        action="store_true",
        help="Force regenerate STATUS_TRACKING.md (Phase 4)",
    )

    # Dev-report command (PRIORITY 9)
    dev_report_parser = subparsers.add_parser("dev-report", help="Show developer daily report (PRIORITY 9)")
    dev_report_parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Days to look back (default: 1 for yesterday)",
    )


def execute(args: argparse.Namespace) -> int:
    """Execute status commands based on args.command.

    Args:
        args: Parsed command-line arguments

    Returns:
        0 on success, 1 on error
    """
    commands = {
        "status": cmd_status,
        "developer-status": cmd_developer_status,
        "metrics": cmd_metrics,
        "summary": cmd_summary,
        "calendar": cmd_calendar,
        "dev-report": cmd_dev_report,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown status command: {args.command}")
        return 1
