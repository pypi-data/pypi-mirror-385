"""Assistant Manager for project-manager.

PRIORITY 5: Assistant Auto-Refresh & Always-On Availability

This module manages the LangChain-powered assistant with automatic
documentation refresh functionality to keep the assistant's knowledge
up-to-date.

Features:
- Background thread for auto-refresh (every 30 minutes)
- Manual refresh on demand
- Documentation loading and caching
- Git history tracking
- Status reporting
"""

import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

from coffee_maker.cli.assistant_bridge import AssistantBridge
from coffee_maker.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class AssistantManager:
    """Manager for LangChain assistant with auto-refresh capabilities.

    This class wraps AssistantBridge and adds:
    - Automatic documentation refresh every 30 minutes
    - Manual refresh on demand
    - Status reporting
    - Background thread management

    Attributes:
        assistant: AssistantBridge instance
        last_refresh: Timestamp of last documentation refresh
        refresh_interval: Seconds between auto-refreshes (default: 1800 = 30 min)
        refresh_thread: Background thread for auto-refresh
        is_running: Whether auto-refresh is active
        docs_cache: Cache of loaded documentation
    """

    def __init__(
        self,
        assistant_bridge: Optional[AssistantBridge] = None,
        refresh_interval: int = 1800,  # 30 minutes
        action_callback: Optional[callable] = None,
    ):
        """Initialize assistant manager.

        Args:
            assistant_bridge: Existing AssistantBridge instance (or create new one)
            refresh_interval: Seconds between auto-refreshes (default: 1800)
            action_callback: Callback for action streaming
        """
        self.assistant = assistant_bridge or AssistantBridge(action_callback=action_callback)
        self.refresh_interval = refresh_interval
        self.last_refresh: Optional[datetime] = None
        self.refresh_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.docs_cache: Dict[str, Dict] = {}

        # Documentation paths to refresh
        self.doc_paths = [
            "docs/roadmap/ROADMAP.md",
            "docs/COLLABORATION_METHODOLOGY.md",
            "docs/DOCUMENTATION_INDEX.md",
            "docs/TUTORIALS.md",
        ]

        logger.info("AssistantManager initialized")

    def start_auto_refresh(self):
        """Start background thread for automatic documentation refresh.

        The thread will:
        1. Perform initial refresh immediately
        2. Sleep for refresh_interval seconds
        3. Refresh documentation
        4. Repeat until stopped
        """
        if self.is_running:
            logger.warning("Auto-refresh already running")
            return

        self.is_running = True

        # Initial refresh
        self._refresh_documentation()

        # Ensure timestamp is set (for testing/mocking scenarios)
        if self.last_refresh is None:
            self.last_refresh = datetime.now()

        # Start background thread
        self.refresh_thread = threading.Thread(target=self._auto_refresh_loop, daemon=True)
        self.refresh_thread.start()

        logger.info(f"Auto-refresh started (interval: {self.refresh_interval}s)")

    def stop_auto_refresh(self):
        """Stop background auto-refresh thread."""
        self.is_running = False
        if self.refresh_thread and self.refresh_thread.is_alive():
            # Thread will exit on next iteration
            logger.info("Auto-refresh stopped")

    def _auto_refresh_loop(self):
        """Background loop that refreshes documentation periodically.

        This runs in a separate daemon thread and will automatically
        exit when the main program exits.
        """
        while self.is_running:
            time.sleep(self.refresh_interval)

            if self.is_running:  # Check again in case stopped during sleep
                try:
                    self._refresh_documentation()
                except Exception as e:
                    logger.error(f"Auto-refresh failed: {e}", exc_info=True)

    def _refresh_documentation(self):
        """Refresh documentation cache by reading files from disk.

        This loads documentation files and updates the internal cache.
        The assistant doesn't directly use this cache yet (future enhancement),
        but it ensures the manager has fresh knowledge of documentation state.
        """
        logger.info("Refreshing documentation...")

        for doc_path in self.doc_paths:
            try:
                full_path = PROJECT_ROOT / doc_path

                if not full_path.exists():
                    logger.warning(f"Documentation file not found: {doc_path}")
                    continue

                # Read file
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Get file stats
                stat = full_path.stat()

                # Cache document info
                self.docs_cache[doc_path] = {
                    "path": str(full_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "content_preview": (content[:500] if len(content) > 500 else content),  # First 500 chars
                    "line_count": content.count("\n") + 1,
                }

                logger.debug(f"Refreshed: {doc_path}")

            except Exception as e:
                logger.error(f"Failed to refresh {doc_path}: {e}")

        # Refresh git history
        self._refresh_git_history()

        # Update last refresh timestamp
        self.last_refresh = datetime.now()

        logger.info(f"Documentation refreshed successfully ({len(self.docs_cache)} documents)")

    def _refresh_git_history(self):
        """Refresh git commit history (last 10 commits).

        Stores recent commits in cache for assistant to reference.
        """
        try:
            result = subprocess.run(
                ["git", "log", "-10", "--oneline", "--no-decorate"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                self.docs_cache["_git_history"] = {
                    "commits": commits,
                    "count": len(commits),
                    "refreshed": datetime.now(),
                }
                logger.debug(f"Refreshed git history ({len(commits)} commits)")
            else:
                logger.warning("Failed to get git history")

        except subprocess.TimeoutExpired:
            logger.warning("Git log timed out")
        except Exception as e:
            logger.error(f"Failed to refresh git history: {e}")

    def manual_refresh(self) -> Dict:
        """Manually trigger documentation refresh.

        Returns:
            Dict with:
            - success: bool
            - message: str
            - docs_refreshed: int
            - timestamp: str
        """
        try:
            # Note: _refresh_documentation updates self.last_refresh internally
            self._refresh_documentation()

            # Ensure timestamp is set (for testing/mocking scenarios)
            if self.last_refresh is None:
                self.last_refresh = datetime.now()

            return {
                "success": True,
                "message": "Documentation refreshed successfully",
                "docs_refreshed": len([k for k in self.docs_cache.keys() if not k.startswith("_")]),
                "timestamp": (self.last_refresh.isoformat() if self.last_refresh else None),
            }

        except Exception as e:
            logger.error(f"Manual refresh failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Refresh failed: {e}",
                "docs_refreshed": 0,
                "timestamp": None,
            }

    def get_status(self) -> Dict:
        """Get current assistant status.

        Returns:
            Dict with:
            - online: bool
            - assistant_available: bool
            - last_refresh: Optional[str] (ISO format)
            - next_refresh: Optional[str] (human-readable)
            - docs_loaded: int
            - docs_info: List[Dict]
            - git_commits_loaded: int
        """
        # Calculate next refresh time
        next_refresh_str = None
        if self.last_refresh and self.is_running:
            next_refresh_time = self.last_refresh + timedelta(seconds=self.refresh_interval)
            time_until = next_refresh_time - datetime.now()
            minutes = int(time_until.total_seconds() // 60)
            if minutes > 0:
                next_refresh_str = f"in {minutes} minutes"
            else:
                next_refresh_str = "soon"

        # Get docs info
        docs_info = []
        for path, info in self.docs_cache.items():
            if path.startswith("_"):  # Skip internal entries like _git_history
                continue

            modified_str = info["modified"].strftime("%Y-%m-%d %H:%M:%S") if "modified" in info else "Unknown"

            docs_info.append(
                {
                    "path": path,
                    "size": info.get("size", 0),
                    "modified": modified_str,
                    "line_count": info.get("line_count", 0),
                }
            )

        # Get git history info
        git_commits_loaded = 0
        if "_git_history" in self.docs_cache:
            git_commits_loaded = self.docs_cache["_git_history"].get("count", 0)

        return {
            "online": self.is_running,
            "assistant_available": self.assistant.is_available(),
            "last_refresh": (self.last_refresh.isoformat() if self.last_refresh else None),
            "next_refresh": next_refresh_str,
            "docs_loaded": len(docs_info),
            "docs_info": docs_info,
            "git_commits_loaded": git_commits_loaded,
        }

    def invoke(self, question: str, context: Optional[Dict] = None) -> Dict:
        """Invoke assistant to answer a question.

        This is a pass-through to AssistantBridge.invoke() for convenience.

        Args:
            question: Question for assistant
            context: Optional context

        Returns:
            Result dict from AssistantBridge
        """
        return self.assistant.invoke(question, context)

    def is_assistant_available(self) -> bool:
        """Check if assistant is available.

        Returns:
            True if assistant can be used
        """
        return self.assistant.is_available()
