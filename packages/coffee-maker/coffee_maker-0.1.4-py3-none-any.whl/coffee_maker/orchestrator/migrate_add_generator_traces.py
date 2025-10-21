"""Migration script to add generator_traces table for ACE Generator agent logging.

This migration adds comprehensive logging for the Generator agent's tool, skill, and command usage,
enabling observability into the first layer of the ACE (Agentic Context Evolving) framework.

Author: architect + code_developer
Date: 2025-10-20
Related: Generator agent (coffee_maker/autonomous/ace/generator.py)
"""

import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path("data/orchestrator.db")


def run_migration():
    """Add generator_traces table to orchestrator database."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Please ensure orchestrator has been initialized")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    print(f"🔄 Migrating {DB_PATH} to add generator_traces table...")

    try:
        # Create generator_traces table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generator_traces (
                -- Primary identification
                trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT NOT NULL,           -- Agent that invoked the operation
                operation_type TEXT NOT NULL,       -- tool, skill, command, file_operation
                operation_name TEXT NOT NULL,       -- Specific tool/skill/command name

                -- Timing
                started_at TEXT NOT NULL,           -- ISO8601 timestamp
                completed_at TEXT,                  -- ISO8601 timestamp (NULL if still running)
                duration_ms INTEGER,                -- Total execution time

                -- Status and result
                status TEXT NOT NULL,               -- running, completed, failed
                exit_code INTEGER,                  -- 0 = success, non-zero = error
                error_message TEXT,                 -- Error details if failed

                -- Operation details
                parameters TEXT,                    -- JSON blob of parameters passed
                result TEXT,                        -- JSON blob of result returned
                delegated BOOLEAN DEFAULT 0,        -- Whether operation was delegated
                delegated_to TEXT,                  -- Agent delegated to (if applicable)

                -- Context
                file_path TEXT,                     -- File being operated on (if applicable)
                task_id TEXT,                       -- Links to tasks.task_id
                priority_number INTEGER,            -- ROADMAP priority (if applicable)

                -- Metadata
                metadata TEXT                       -- JSON blob for additional context
            )
        """
        )

        # Create indexes for fast queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_generator_agent_type
            ON generator_traces(agent_type, operation_type)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_generator_status
            ON generator_traces(status, started_at)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_generator_operation
            ON generator_traces(operation_name, duration_ms DESC)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_generator_errors
            ON generator_traces(status, exit_code)
            WHERE status = 'failed'
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_generator_duration
            ON generator_traces(duration_ms DESC)
        """
        )

        # Create views for analytics

        # View 1: Tool usage statistics
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generator_tool_usage AS
            SELECT
                operation_name AS tool_name,
                agent_type,
                COUNT(*) AS total_uses,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS successful_uses,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_uses,
                AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms,
                MAX(duration_ms) AS max_duration_ms
            FROM generator_traces
            WHERE operation_type = 'tool'
            GROUP BY operation_name, agent_type
            ORDER BY total_uses DESC
        """
        )

        # View 2: Skill usage statistics
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generator_skill_usage AS
            SELECT
                operation_name AS skill_name,
                agent_type,
                COUNT(*) AS total_uses,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS successful_uses,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_uses,
                AVG(CASE WHEN status = 'completed' THEN duration_ms ELSE NULL END) AS avg_duration_ms
            FROM generator_traces
            WHERE operation_type = 'skill'
            GROUP BY operation_name, agent_type
            ORDER BY total_uses DESC
        """
        )

        # View 3: Command failures and errors
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generator_errors AS
            SELECT
                trace_id,
                agent_type,
                operation_type,
                operation_name,
                started_at,
                duration_ms,
                exit_code,
                error_message,
                file_path
            FROM generator_traces
            WHERE status = 'failed'
            ORDER BY started_at DESC
            LIMIT 100
        """
        )

        # View 4: Delegation patterns
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generator_delegations AS
            SELECT
                agent_type AS requesting_agent,
                delegated_to AS owner_agent,
                operation_name,
                file_path,
                COUNT(*) AS delegation_count,
                AVG(duration_ms) AS avg_duration_ms
            FROM generator_traces
            WHERE delegated = 1
            GROUP BY agent_type, delegated_to, operation_name
            ORDER BY delegation_count DESC
        """
        )

        # View 5: Performance bottlenecks
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generator_bottlenecks AS
            SELECT
                trace_id,
                agent_type,
                operation_type,
                operation_name,
                duration_ms,
                started_at,
                completed_at,
                CASE
                    WHEN duration_ms > 60000 THEN 'Very Slow (>1min)'
                    WHEN duration_ms > 30000 THEN 'Slow (>30s)'
                    WHEN duration_ms > 10000 THEN 'Moderate (>10s)'
                    ELSE 'Normal'
                END AS performance_category
            FROM generator_traces
            WHERE status = 'completed' AND duration_ms IS NOT NULL
            ORDER BY duration_ms DESC
            LIMIT 100
        """
        )

        conn.commit()
        print("✅ Migration completed successfully")
        print("\n📊 Created tables:")
        print("   - generator_traces (main trace log)")
        print("\n📈 Created views:")
        print("   - generator_tool_usage (tool usage statistics)")
        print("   - generator_skill_usage (skill usage statistics)")
        print("   - generator_errors (recent errors)")
        print("   - generator_delegations (delegation patterns)")
        print("   - generator_bottlenecks (performance issues)")

        # Show count of existing traces (should be 0 for new migration)
        cursor.execute("SELECT COUNT(*) FROM generator_traces")
        count = cursor.fetchone()[0]
        print(f"\n📝 Current traces in database: {count}")

    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
