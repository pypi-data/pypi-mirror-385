"""CLI tools for Coffee Maker Agent.

This package provides command-line interfaces for:
- Roadmap management (project-manager CLI)
- Daemon control and monitoring
- Notification system

Modules:
    roadmap_cli: Main roadmap management CLI
    notifications: Notification database and management
"""

from typing import List

__all__: List[str] = ["roadmap_cli", "notifications"]
