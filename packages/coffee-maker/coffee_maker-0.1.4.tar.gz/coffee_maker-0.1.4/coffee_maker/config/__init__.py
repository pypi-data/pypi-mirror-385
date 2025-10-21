"""Configuration management for Coffee Maker Agent.

This package provides centralized configuration management for:
- API keys (Anthropic, OpenAI, Gemini, GitHub)
- Environment variable validation
- Configuration defaults and schemas
- Database and file paths

Main entry points:
- ConfigManager: Centralized configuration access
- DATABASE_PATHS: Database file paths (for backward compatibility)
- ROADMAP_PATH: Path to ROADMAP.md file
- PROJECT_ROOT: Project root directory
"""

from pathlib import Path
from typing import Dict, Final

from coffee_maker.config.manager import ConfigManager

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directory (shared between user environment and daemon)
DATA_DIR = PROJECT_ROOT / "data"

# ROADMAP.md path (single source of truth)
ROADMAP_PATH = PROJECT_ROOT / "docs" / "ROADMAP.md"

# Database paths (shared between user environment and daemon)
# This is re-exported from the package for backward compatibility
# while we migrate to ConfigManager
DATABASE_PATHS: Final[Dict[str, Path]] = {
    "analytics": DATA_DIR / "analytics.db",
    "notifications": DATA_DIR / "notifications.db",
    "langfuse_export": DATA_DIR / "langfuse_export.db",
}

__all__ = ["ConfigManager", "DATABASE_PATHS", "ROADMAP_PATH", "PROJECT_ROOT"]
