"""
Code Index Infrastructure

3-level hierarchical index for fast codebase navigation:
- Level 1: Functional Categories (Payment, Authentication, Notifications, etc.)
- Level 2: Components (Gateway Integration, Validation, Webhooks, etc.)
- Level 3: Implementations (file:line_start:line_end)

Used by: Code analysis skills, functional search, code explanation

Auto-maintained by:
- Git hooks (post-commit, post-merge)
- Manual index rebuild (cron, manual trigger)
"""

from coffee_maker.utils.code_index.indexer import CodeIndexer
from coffee_maker.utils.code_index.query_engine import CodeIndexQueryEngine

__all__ = ["CodeIndexer", "CodeIndexQueryEngine"]
