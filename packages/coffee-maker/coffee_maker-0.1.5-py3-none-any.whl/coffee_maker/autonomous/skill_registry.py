"""
Skill Registry for Claude Skills Integration.

Automatic skill discovery based on task triggers with fuzzy matching.
Caches trigger → skill mapping for fast lookups.

Author: architect agent
Date: 2025-10-19
Related: SPEC-055, US-055
"""

import logging
from difflib import get_close_matches
from typing import Dict, List

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.skill_loader import SkillLoader, SkillMetadata

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for agent-specific skill discovery.

    Example:
        >>> registry = SkillRegistry(AgentType.CODE_DEVELOPER)
        >>> skills = registry.find_skills_for_task("implement feature with tests")
        >>> # Returns: [SkillMetadata(test-driven-implementation)]
    """

    def __init__(self, agent_type: AgentType):
        """Initialize SkillRegistry.

        Args:
            agent_type: Type of agent using this registry
        """
        self.agent_type = agent_type
        self.loader = SkillLoader(agent_type)
        self._cache = self._build_cache()

    def _build_cache(self) -> Dict[str, List[SkillMetadata]]:
        """Build trigger → skill mapping cache.

        Returns:
            Dict mapping trigger strings to list of skills
        """
        cache = {}

        try:
            for skill in self.loader.list_available_skills():
                for trigger in skill.triggers:
                    if trigger not in cache:
                        cache[trigger] = []
                    cache[trigger].append(skill)
        except Exception as e:
            logger.warning(f"Failed to build skill cache: {e}")

        return cache

    def find_skills_for_task(self, task: str) -> List[SkillMetadata]:
        """Find skills relevant to a task description (fuzzy matching).

        Args:
            task: Task description (e.g., "implement feature with tests")

        Returns:
            List of SkillMetadata that match the task
        """
        # Exact match first
        if task in self._cache:
            return self._cache[task]

        # Fuzzy match on triggers
        triggers = list(self._cache.keys())
        if not triggers:
            return []

        matches = get_close_matches(task, triggers, n=3, cutoff=0.6)

        skills = []
        for match in matches:
            skills.extend(self._cache[match])

        # Remove duplicates (preserve order)
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.name not in seen:
                seen.add(skill.name)
                unique_skills.append(skill)

        return unique_skills

    def refresh(self):
        """Refresh skill cache (call after adding new skills)."""
        self._cache = self._build_cache()
        logger.info(f"Skill cache refreshed for {self.agent_type.value}: " f"{len(self._cache)} triggers loaded")
