"""
Skill Cache for Claude Skills Integration (Phase 3 Optimization).

Caches skill execution results for repeated executions.
Provides instant results for cached skill executions.

Author: architect agent
Date: 2025-10-19
Related: SPEC-057, US-057
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SkillCache:
    """Cache skill execution results for faster repeated executions.

    Phase 3 optimization: Provides instant results for repeated skill executions
    with identical context, reducing execution time from minutes to milliseconds.

    Example:
        >>> cache = SkillCache()
        >>> result = cache.get("test-driven-implementation", "context_hash_123")
        >>> if result is None:
        ...     result = execute_skill()  # Execute skill
        ...     cache.set("test-driven-implementation", "context_hash_123", result)
    """

    def __init__(self, cache_dir: Path = None, ttl: int = 3600):
        """Initialize SkillCache.

        Args:
            cache_dir: Directory for cache storage (default: .cache/skills)
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir or Path(".cache/skills")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def get(self, skill_name: str, context_hash: str) -> Optional[Any]:
        """Get cached result if available and fresh.

        Args:
            skill_name: Name of the skill
            context_hash: Hash of the context (use hash_context() to generate)

        Returns:
            Cached result if available and fresh, None otherwise
        """
        cache_file = self._get_cache_file(skill_name, context_hash)

        if not cache_file.exists():
            logger.debug(f"Cache miss for {skill_name} (hash: {context_hash[:8]}...)")
            return None

        # Check if cache is fresh
        age = time.time() - cache_file.stat().st_mtime

        if age > self.ttl:
            logger.debug(f"Cache expired for {skill_name} (age: {age:.0f}s > TTL: {self.ttl}s)")
            # Optionally delete expired cache
            cache_file.unlink(missing_ok=True)
            return None

        # Load cached result
        try:
            result = json.loads(cache_file.read_text())
            logger.info(f"Cache hit for {skill_name} (age: {age:.0f}s)")
            return result
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load cache for {skill_name}: {e}")
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, skill_name: str, context_hash: str, result: Any) -> None:
        """Cache skill result.

        Args:
            skill_name: Name of the skill
            context_hash: Hash of the context (use hash_context() to generate)
            result: Result to cache (must be JSON-serializable)
        """
        cache_file = self._get_cache_file(skill_name, context_hash)

        try:
            cache_file.write_text(json.dumps(result, indent=2))
            logger.info(f"Cached result for {skill_name} (hash: {context_hash[:8]}...)")
        except (TypeError, OSError) as e:
            logger.warning(f"Failed to cache result for {skill_name}: {e}")

    def hash_context(self, context: dict) -> str:
        """Generate hash for context.

        Args:
            context: Context dictionary

        Returns:
            SHA256 hash of context (deterministic)
        """
        # Sort keys for deterministic hashing
        context_json = json.dumps(context, sort_keys=True)
        return hashlib.sha256(context_json.encode()).hexdigest()

    def clear(self, skill_name: Optional[str] = None) -> int:
        """Clear cache.

        Args:
            skill_name: Skill name to clear (None = clear all)

        Returns:
            Number of cache files deleted
        """
        if skill_name:
            pattern = f"{skill_name}_*.json"
        else:
            pattern = "*.json"

        deleted = 0
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
            deleted += 1

        logger.info(f"Cleared {deleted} cache files" + (f" for {skill_name}" if skill_name else ""))

        return deleted

    def _get_cache_file(self, skill_name: str, context_hash: str) -> Path:
        """Get cache file path.

        Args:
            skill_name: Skill name
            context_hash: Context hash

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{skill_name}_{context_hash}.json"
