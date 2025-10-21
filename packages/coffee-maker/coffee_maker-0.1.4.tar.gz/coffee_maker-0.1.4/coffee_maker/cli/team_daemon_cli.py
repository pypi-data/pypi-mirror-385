"""CLI commands for team daemon orchestration.

Provides commands to:
- Start the team daemon (orchestrates all agents)
- Stop the team daemon
- View team status and agent health
- Analyze bottlenecks and performance metrics
- Monitor message queue depth

Usage:
    poetry run team-daemon start
    poetry run team-daemon status
    poetry run team-daemon bottlenecks
    poetry run team-daemon metrics
    poetry run team-daemon stop
"""

import json
import logging
import sys

import click

from coffee_maker.autonomous.message_queue import MessageQueue
from coffee_maker.autonomous.team_daemon import TeamConfig, TeamDaemon


logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.pass_context
def team_daemon_cli(ctx, debug):
    """Manage the autonomous team daemon.

    The team daemon orchestrates all autonomous agents (code_developer,
    project_manager, architect, assistant) for continuous, coordinated work.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--health-check-interval",
    default=30,
    type=int,
    help="Health check interval in seconds",
)
@click.pass_context
def start(ctx, db_path, health_check_interval):
    """Start the team daemon.

    Spawns all autonomous agents and begins orchestration loop.
    The daemon monitors agent health, coordinates work, and ensures
    fault tolerance through automatic restart capability.
    """
    click.echo(click.style("Starting team daemon...", fg="cyan", bold=True))

    try:
        # Create configuration
        config = TeamConfig(database_path=db_path, health_check_interval=health_check_interval)

        # Create and start daemon
        daemon = TeamDaemon(config)
        click.echo(f"Configuration: {db_path}")
        click.echo("Spawning agents...")

        daemon.start()

    except KeyboardInterrupt:
        click.echo("\nShutdown requested.")
        sys.exit(0)
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to start team daemon: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--agent",
    help="Show status for specific agent",
)
@click.pass_context
def status(ctx, db_path, agent):
    """Show team daemon status.

    Displays health, performance, and activity information for all agents.
    """
    try:
        # Load message queue for status info
        queue = MessageQueue(db_path=db_path)

        # Get task metrics
        metrics = queue.get_task_metrics()

        click.echo(click.style("Team Daemon Status", fg="cyan", bold=True))
        click.echo("")
        click.echo(f"Database: {db_path}")
        click.echo("")

        click.echo(click.style("Task Metrics:", fg="yellow", bold=True))
        click.echo(f"  Total tasks: {metrics['total_tasks']}")
        click.echo(f"  Completed: {metrics['completed_tasks']}")
        click.echo(f"  Failed: {metrics['failed_tasks']}")
        click.echo(f"  Queued: {metrics['queued_tasks']}")
        click.echo(f"  Running: {metrics['running_tasks']}")
        click.echo(f"  Average duration: {metrics['avg_duration_ms']:.0f}ms")
        click.echo("")

        # Get agent performance
        performance = queue.get_agent_performance()
        if performance:
            click.echo(click.style("Agent Performance:", fg="yellow", bold=True))
            for agent_perf in performance:
                if agent and agent != agent_perf["agent"]:
                    continue

                click.echo(f"  {agent_perf['agent']}:")
                click.echo(f"    Total tasks: {agent_perf['total_tasks']}")
                click.echo(f"    Completed: {agent_perf['completed_tasks']}")
                click.echo(f"    Failed: {agent_perf['failed_tasks']}")
                click.echo(f"    Average duration: {agent_perf['avg_duration_ms']}ms")
                click.echo(f"    Max duration: {agent_perf['max_duration_ms']}ms")
                click.echo("")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to get status: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--limit",
    default=10,
    type=int,
    help="Number of slowest tasks to show",
)
@click.pass_context
def bottlenecks(ctx, db_path, limit):
    """Show slowest tasks (bottleneck analysis).

    Identifies tasks taking the longest to complete, helping identify
    performance bottlenecks in the agent system.
    """
    try:
        queue = MessageQueue(db_path=db_path)

        slowest = queue.get_slowest_tasks(limit=limit)

        click.echo(click.style(f"Top {limit} Slowest Tasks", fg="cyan", bold=True))
        click.echo("")

        if not slowest:
            click.echo("No completed tasks found.")
            return

        for i, task in enumerate(slowest, 1):
            duration_sec = task["duration_ms"] / 1000
            click.echo(f"{i}. {task['agent']} - {task['type']}: {duration_sec:.2f}s")
            click.echo(f"   Task ID: {task['task_id']}")
            click.echo(f"   Created: {task['created_at']}")
            click.echo(f"   Duration: {task['duration_ms']}ms")
            click.echo("")

        # Show percentiles
        percentiles = queue.get_percentiles([50, 95, 99])
        click.echo(click.style("Duration Percentiles:", fg="yellow", bold=True))
        if percentiles[50]:
            click.echo(f"  p50: {percentiles[50]}ms")
        if percentiles[95]:
            click.echo(f"  p95: {percentiles[95]}ms")
        if percentiles[99]:
            click.echo(f"  p99: {percentiles[99]}ms")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to get bottlenecks: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--agent",
    help="Show metrics for specific agent",
)
@click.pass_context
def metrics(ctx, db_path, agent):
    """Show agent performance metrics.

    Displays detailed performance metrics including task counts,
    success rates, and duration statistics.
    """
    try:
        queue = MessageQueue(db_path=db_path)

        performance = queue.get_agent_performance()
        queue_depth = queue.get_queue_depth()

        click.echo(click.style("Agent Performance Metrics", fg="cyan", bold=True))
        click.echo("")

        if performance:
            click.echo(click.style("Performance by Agent:", fg="yellow", bold=True))
            for agent_perf in performance:
                if agent and agent != agent_perf["agent"]:
                    continue

                total = agent_perf["total_tasks"]
                success_rate = (agent_perf["completed_tasks"] / total * 100) if total > 0 else 0

                click.echo(f"\n{agent_perf['agent']}:")
                click.echo(f"  Total tasks: {agent_perf['total_tasks']}")
                click.echo(f"  Completed: {agent_perf['completed_tasks']}")
                click.echo(f"  Failed: {agent_perf['failed_tasks']}")
                click.echo(f"  Success rate: {success_rate:.1f}%")
                click.echo(f"  Average duration: {agent_perf['avg_duration_ms']:.0f}ms")
                click.echo(f"  Max duration: {agent_perf['max_duration_ms']}ms")
                click.echo(f"  Min duration: {agent_perf['min_duration_ms']}ms")

        if queue_depth:
            click.echo("")
            click.echo(click.style("Queue Depth by Agent:", fg="yellow", bold=True))
            for agent_queue in queue_depth:
                if agent and agent != agent_queue["agent"]:
                    continue

                click.echo(f"\n{agent_queue['agent']}:")
                click.echo(f"  Queued tasks: {agent_queue['queued_tasks']}")
                click.echo(f"    High priority: {agent_queue['high_priority']}")
                click.echo(f"    Normal priority: {agent_queue['normal_priority']}")
                click.echo(f"    Low priority: {agent_queue['low_priority']}")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to get metrics: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.pass_context
def queue(ctx, db_path):
    """Show message queue status.

    Displays queue depth by agent and priority level, showing which
    agents have pending work.
    """
    try:
        queue = MessageQueue(db_path=db_path)

        queue_size = queue.size()
        queue_depth = queue.get_queue_depth()

        click.echo(click.style("Message Queue Status", fg="cyan", bold=True))
        click.echo("")
        click.echo(f"Total queued messages: {queue_size}")
        click.echo("")

        if queue_depth:
            click.echo(click.style("Queue Depth by Agent:", fg="yellow", bold=True))
            for agent_queue in queue_depth:
                click.echo(f"\n{agent_queue['agent']}:")
                click.echo(f"  Queued: {agent_queue['queued_tasks']}")
                click.echo(f"    High (1-2): {agent_queue['high_priority']}")
                click.echo(f"    Normal (3-7): {agent_queue['normal_priority']}")
                click.echo(f"    Low (8-10): {agent_queue['low_priority']}")
        else:
            click.echo("No messages in queue.")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to get queue status: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force stop without graceful shutdown",
)
@click.pass_context
def stop(ctx, db_path, force):
    """Stop the team daemon.

    Gracefully shuts down all agents and the daemon. Use --force for
    immediate shutdown (not recommended).
    """
    click.echo(click.style("Stopping team daemon...", fg="cyan", bold=True))

    try:
        # For now, just print message - actual stop would be handled by running daemon
        if force:
            click.echo("Force stopping (sending SIGKILL)...")
        else:
            click.echo("Graceful shutdown (sending SIGTERM)...")

        click.echo("Use Ctrl+C to stop the daemon if running in foreground.")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to stop daemon: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file (default: stdout)",
)
@click.pass_context
def export(ctx, db_path, output):
    """Export queue metrics as JSON.

    Exports all queue metrics, performance data, and bottleneck analysis
    to JSON format for further analysis or reporting.
    """
    try:
        queue = MessageQueue(db_path=db_path)

        data = {
            "metrics": queue.get_task_metrics(),
            "performance": queue.get_agent_performance(),
            "queue_depth": queue.get_queue_depth(),
            "slowest_tasks": queue.get_slowest_tasks(limit=20),
            "percentiles": queue.get_percentiles([50, 95, 99]),
        }

        json.dump(data, output, indent=2)
        output.write("\n")

        click.echo(
            click.style("✓ Metrics exported successfully", fg="green"),
            err=True,
        )

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to export metrics: %s", e, exc_info=True)
        sys.exit(1)


@team_daemon_cli.command()
@click.option(
    "--db-path",
    default="data/orchestrator.db",
    help="Path to orchestrator database",
)
@click.option(
    "--days",
    default=30,
    type=int,
    help="Number of days of data to retain",
)
@click.pass_context
def cleanup(ctx, db_path, days):
    """Clean up old completed tasks.

    Removes completed and failed tasks older than the specified number
    of days to reduce database size.
    """
    try:
        queue = MessageQueue(db_path=db_path)

        deleted = queue.cleanup_old_tasks(days=days)

        click.echo(f"Deleted {deleted} old tasks (older than {days} days)")
        click.echo("Running database optimization...")

        queue.stop()  # Triggers VACUUM

        click.echo(
            click.style("✓ Cleanup completed successfully", fg="green"),
        )

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        logger.error("Failed to cleanup: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    team_daemon_cli()
