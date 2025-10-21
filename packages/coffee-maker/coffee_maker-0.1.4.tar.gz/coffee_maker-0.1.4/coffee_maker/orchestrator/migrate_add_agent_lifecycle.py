"""Migration script to add agent_lifecycle table and analytics views.

This script implements Phase 1 of CFR-014 migration:
- Creates agent_lifecycle table
- Creates analytics views (active_agents, agent_velocity, agent_bottlenecks, priority_timeline)
- Optionally migrates data from agent_state.json to database

Usage:
    poetry run python coffee_maker/orchestrator/migrate_add_agent_lifecycle.py [--migrate-json]

Author: code_developer
Date: 2025-10-20
Related: CFR-014, SPEC-110, US-110
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AgentLifecycleMigration:
    """Migrate orchestrator agent tracking to SQLite database."""

    def __init__(self, db_path: str = "data/orchestrator.db", json_path: str = "data/orchestrator/agent_state.json"):
        """
        Initialize migration.

        Args:
            db_path: Path to SQLite database
            json_path: Path to legacy JSON state file
        """
        self.db_path = Path(db_path)
        self.json_path = Path(json_path)

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self, migrate_json: bool = False) -> bool:
        """
        Run migration.

        Args:
            migrate_json: If True, migrate existing JSON data to database

        Returns:
            True if successful
        """
        try:
            logger.info("Starting agent_lifecycle migration...")

            # Step 1: Create agent_lifecycle table
            self._create_agent_lifecycle_table()

            # Step 2: Create analytics views
            self._create_analytics_views()

            # Step 3: Optionally migrate JSON data
            if migrate_json and self.json_path.exists():
                self._migrate_json_data()

            # Step 4: Verify migration
            self._verify_migration()

            logger.info("✅ Migration completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}", exc_info=True)
            return False

    def _create_agent_lifecycle_table(self):
        """Create agent_lifecycle table with indexes."""
        logger.info("Creating agent_lifecycle table...")

        schema_sql = """
        -- Agent Lifecycle Table (CFR-014 requirement)
        CREATE TABLE IF NOT EXISTS agent_lifecycle (
            agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pid INTEGER NOT NULL,
            agent_type TEXT NOT NULL,           -- architect, code_developer, project_manager
            task_id TEXT NOT NULL,              -- Links to tasks.task_id if applicable
            task_type TEXT,                     -- create_spec, implementation, auto_planning
            priority_number INTEGER,            -- ROADMAP priority (if applicable)

            -- Lifecycle timestamps (ISO8601 format)
            spawned_at TEXT NOT NULL,           -- Process spawn time
            started_at TEXT,                    -- When agent began work
            completed_at TEXT,                  -- When agent finished

            -- Status and metrics
            status TEXT NOT NULL,               -- spawned, running, completed, failed, killed
            exit_code INTEGER,                  -- Process exit code
            duration_ms INTEGER,                -- spawn → complete (milliseconds)
            idle_time_ms INTEGER,               -- spawn → start (milliseconds)

            -- Additional context
            command TEXT NOT NULL,              -- Full CLI command executed
            worktree_path TEXT,                 -- Git worktree path (parallel exec)
            worktree_branch TEXT,               -- Git worktree branch name (e.g., roadmap-wt1)
            merged_at TEXT,                     -- When architect merged to roadmap (CFR-013)
            cleaned_at TEXT,                    -- When orchestrator cleaned up worktree
            merge_duration_ms INTEGER,          -- Time to merge (merged_at - completed_at)
            cleanup_duration_ms INTEGER,        -- Time to cleanup (cleaned_at - merged_at)
            error_message TEXT,                 -- Error details if failed
            metadata TEXT                       -- JSON blob for extras
        );
        """

        # Create table first
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()

        # Then add missing columns if needed (for tables that exist but are missing columns)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(agent_lifecycle)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            new_columns = [
                ("worktree_branch", "TEXT"),
                ("merged_at", "TEXT"),
                ("cleaned_at", "TEXT"),
                ("merge_duration_ms", "INTEGER"),
                ("cleanup_duration_ms", "INTEGER"),
            ]

            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    logger.info(f"Adding missing column: {col_name}")
                    conn.execute(f"ALTER TABLE agent_lifecycle ADD COLUMN {col_name} {col_type}")

            conn.commit()

        # Now create indexes
        index_sql = """
        -- Indexes for fast queries
        CREATE INDEX IF NOT EXISTS idx_agent_type_status ON agent_lifecycle(agent_type, status);
        CREATE INDEX IF NOT EXISTS idx_priority_number ON agent_lifecycle(priority_number);
        CREATE INDEX IF NOT EXISTS idx_spawned_at ON agent_lifecycle(spawned_at);
        CREATE INDEX IF NOT EXISTS idx_duration ON agent_lifecycle(duration_ms DESC);
        CREATE INDEX IF NOT EXISTS idx_task_id ON agent_lifecycle(task_id);
        CREATE INDEX IF NOT EXISTS idx_pid ON agent_lifecycle(pid);
        CREATE INDEX IF NOT EXISTS idx_worktree_branch ON agent_lifecycle(worktree_branch);
        CREATE INDEX IF NOT EXISTS idx_merged_at ON agent_lifecycle(merged_at);
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(index_sql)
            conn.commit()

        logger.info("✅ agent_lifecycle table created")

    def _create_analytics_views(self):
        """Create analytics views for querying agent data."""
        logger.info("Creating analytics views...")

        views_sql = """
        -- Drop existing views if they exist (for idempotency)
        DROP VIEW IF EXISTS active_agents;
        DROP VIEW IF EXISTS agent_velocity;
        DROP VIEW IF EXISTS agent_bottlenecks;
        DROP VIEW IF EXISTS priority_timeline;

        -- Current active agents (running only)
        CREATE VIEW active_agents AS
        SELECT
            agent_id,
            pid,
            agent_type,
            task_id,
            priority_number,
            status,
            spawned_at,
            CAST((julianday('now') - julianday(spawned_at)) * 86400000 AS INTEGER) AS elapsed_ms
        FROM agent_lifecycle
        WHERE status IN ('spawned', 'running')
        ORDER BY spawned_at;

        -- Agent velocity (throughput per agent type)
        CREATE VIEW agent_velocity AS
        SELECT
            agent_type,
            COUNT(*) AS total_agents,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
            AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms,
            AVG(CASE WHEN status = 'completed' THEN idle_time_ms ELSE NULL END) AS avg_idle_ms,
            MAX(duration_ms) AS max_duration_ms,
            MIN(duration_ms) AS min_duration_ms
        FROM agent_lifecycle
        GROUP BY agent_type;

        -- Agent bottlenecks (slowest 100 agents)
        CREATE VIEW agent_bottlenecks AS
        SELECT
            agent_id,
            agent_type,
            task_id,
            priority_number,
            duration_ms,
            idle_time_ms,
            spawned_at,
            completed_at,
            CASE
                WHEN idle_time_ms > duration_ms * 0.5 THEN 'High Idle Time'
                WHEN duration_ms > 1800000 THEN 'Long Duration'  -- >30 minutes
                ELSE 'Normal'
            END AS bottleneck_type
        FROM agent_lifecycle
        WHERE status = 'completed' AND duration_ms IS NOT NULL
        ORDER BY duration_ms DESC
        LIMIT 100;

        -- Priority implementation timeline
        CREATE VIEW priority_timeline AS
        SELECT
            priority_number,
            agent_type,
            MIN(spawned_at) AS first_spawn,
            MAX(completed_at) AS last_completion,
            COUNT(*) AS agent_count,
            SUM(duration_ms) AS total_time_ms,
            AVG(duration_ms) AS avg_time_ms
        FROM agent_lifecycle
        WHERE priority_number IS NOT NULL
        GROUP BY priority_number, agent_type
        ORDER BY priority_number;
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(views_sql)
            conn.commit()

        logger.info("✅ Analytics views created (active_agents, agent_velocity, agent_bottlenecks, priority_timeline)")

    def _migrate_json_data(self):
        """Migrate existing agent data from JSON to database."""
        logger.info(f"Migrating data from {self.json_path}...")

        try:
            with open(self.json_path, "r") as f:
                state = json.load(f)

            active_agents = state.get("active_agents", {})
            completed_agents = state.get("completed_agents", [])

            migrated_count = 0

            with sqlite3.connect(self.db_path) as conn:
                # Migrate active agents
                for pid_str, agent_info in active_agents.items():
                    # Check if already migrated
                    existing = conn.execute("SELECT 1 FROM agent_lifecycle WHERE pid = ?", (int(pid_str),)).fetchone()

                    if existing:
                        logger.debug(f"Skipping already migrated agent PID {pid_str}")
                        continue

                    # Insert agent record
                    conn.execute(
                        """
                        INSERT INTO agent_lifecycle
                        (pid, agent_type, task_id, task_type, priority_number, spawned_at,
                         started_at, completed_at, status, exit_code, command, worktree_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            int(pid_str),
                            agent_info.get("agent_type"),
                            agent_info.get("task_id"),
                            agent_info.get("task_type"),
                            agent_info.get("priority_number"),
                            agent_info.get("started_at") or agent_info.get("spawned_at"),  # Fallback
                            agent_info.get("started_at"),
                            agent_info.get("completed_at"),
                            agent_info.get("status", "running"),
                            agent_info.get("exit_code"),
                            agent_info.get("command", ""),
                            agent_info.get("worktree_path"),
                        ),
                    )
                    migrated_count += 1

                # Migrate completed agents
                for agent_info in completed_agents:
                    pid = agent_info.get("pid")
                    if not pid:
                        continue

                    # Check if already migrated
                    existing = conn.execute("SELECT 1 FROM agent_lifecycle WHERE pid = ?", (pid,)).fetchone()

                    if existing:
                        logger.debug(f"Skipping already migrated agent PID {pid}")
                        continue

                    # Calculate duration if possible
                    duration_ms = None
                    if agent_info.get("spawned_at") and agent_info.get("completed_at"):
                        try:
                            spawned = datetime.fromisoformat(agent_info["spawned_at"])
                            completed = datetime.fromisoformat(agent_info["completed_at"])
                            duration_ms = int((completed - spawned).total_seconds() * 1000)
                        except Exception as e:
                            logger.warning(f"Failed to calculate duration for PID {pid}: {e}")

                    conn.execute(
                        """
                        INSERT INTO agent_lifecycle
                        (pid, agent_type, task_id, task_type, priority_number, spawned_at,
                         started_at, completed_at, status, exit_code, duration_ms, command, worktree_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            pid,
                            agent_info.get("agent_type"),
                            agent_info.get("task_id"),
                            agent_info.get("task_type"),
                            agent_info.get("priority_number"),
                            agent_info.get("started_at") or agent_info.get("spawned_at"),
                            agent_info.get("started_at"),
                            agent_info.get("completed_at"),
                            agent_info.get("status", "completed"),
                            agent_info.get("exit_code"),
                            duration_ms,
                            agent_info.get("command", ""),
                            agent_info.get("worktree_path"),
                        ),
                    )
                    migrated_count += 1

                conn.commit()

            logger.info(f"✅ Migrated {migrated_count} agents from JSON to database")

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON file: {e}")
        except Exception as e:
            logger.warning(f"Failed to migrate JSON data: {e}")

    def _verify_migration(self):
        """Verify migration was successful."""
        logger.info("Verifying migration...")

        with sqlite3.connect(self.db_path) as conn:
            # Check table exists
            table_check = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_lifecycle'"
            ).fetchone()

            if not table_check:
                raise RuntimeError("agent_lifecycle table not found!")

            # Check views exist
            required_views = ["active_agents", "agent_velocity", "agent_bottlenecks", "priority_timeline"]
            for view_name in required_views:
                view_check = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='view' AND name=?", (view_name,)
                ).fetchone()

                if not view_check:
                    raise RuntimeError(f"View {view_name} not found!")

            # Count records
            count = conn.execute("SELECT COUNT(*) FROM agent_lifecycle").fetchone()[0]

            logger.info(f"✅ Verification passed:")
            logger.info(f"   - agent_lifecycle table: EXISTS")
            logger.info(f"   - Analytics views: {len(required_views)} created")
            logger.info(f"   - Agent records: {count}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate agent tracking to SQLite database (CFR-014)")
    parser.add_argument(
        "--migrate-json",
        action="store_true",
        help="Migrate existing JSON data to database",
    )
    parser.add_argument(
        "--db-path",
        default="data/orchestrator.db",
        help="Path to SQLite database (default: data/orchestrator.db)",
    )
    parser.add_argument(
        "--json-path",
        default="data/orchestrator/agent_state.json",
        help="Path to JSON state file (default: data/orchestrator/agent_state.json)",
    )

    args = parser.parse_args()

    # Run migration
    migration = AgentLifecycleMigration(db_path=args.db_path, json_path=args.json_path)
    success = migration.run(migrate_json=args.migrate_json)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
