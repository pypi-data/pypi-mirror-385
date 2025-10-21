"""Migration: Add orchestrator_state table for CFR-014 compliance.

This migration creates the orchestrator_state table to replace work_loop_state.json.

Author: code_developer
Date: 2025-10-20
Related: BUG-068 (CFR-014 violation)
"""

import sqlite3
from pathlib import Path


def migrate():
    """Add orchestrator_state table to store configuration state."""
    db_path = Path("data/orchestrator.db")

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrator_state'")
    if cursor.fetchone():
        print("✅ orchestrator_state table already exists")
        conn.close()
        return

    # Create orchestrator_state table
    cursor.execute(
        """
        CREATE TABLE orchestrator_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # Create index for faster lookups
    cursor.execute("CREATE INDEX idx_orchestrator_state_key ON orchestrator_state(key)")

    # Initialize with default values
    from datetime import datetime

    now = datetime.now().isoformat()

    default_values = [
        ("last_roadmap_update", "0", now),
        ("last_refactoring_analysis", "0", now),
        ("last_analysis_notification", "0", now),
        ("last_planning", "0", now),
    ]

    cursor.executemany(
        "INSERT INTO orchestrator_state (key, value, updated_at) VALUES (?, ?, ?)",
        default_values,
    )

    conn.commit()
    conn.close()

    print("✅ Created orchestrator_state table")
    print("   - Stores orchestrator configuration (last_roadmap_update, etc.)")
    print("   - Replaces work_loop_state.json for CFR-014 compliance")


if __name__ == "__main__":
    migrate()
