"""Autonomous development daemon.

This package provides the autonomous development daemon that continuously
reads ROADMAP.md and implements features via Claude CLI.

Modules:
    daemon: Main daemon implementation
    roadmap_parser: Parse ROADMAP.md for tasks
    claude_cli_interface: Subprocess wrapper for Claude CLI
    git_manager: Basic Git operations

Vision:
    The daemon enables Claude to autonomously implement the roadmap
    while you plan. It creates a self-improving system where the framework
    builds itself.
"""

from typing import List

__all__: List[str] = ["daemon", "roadmap_parser", "claude_cli_interface", "git_manager"]
