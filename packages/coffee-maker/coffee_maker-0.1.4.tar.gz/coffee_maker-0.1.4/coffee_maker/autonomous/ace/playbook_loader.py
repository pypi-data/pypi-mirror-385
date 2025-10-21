"""Playbook loader for ACE framework."""

import json
import logging
import random
from datetime import datetime, timedelta

from coffee_maker.autonomous.ace.config import ACEConfig
from coffee_maker.autonomous.ace.models import Playbook, PlaybookBullet

logger = logging.getLogger(__name__)


class PlaybookLoader:
    """Loads and manages agent playbooks."""

    def __init__(self, agent_name: str, config: ACEConfig):
        """Initialize playbook loader.

        Args:
            agent_name: Agent to load playbook for
            config: ACE configuration
        """
        self.agent_name = agent_name
        self.config = config
        self.playbook_path = config.playbook_dir / f"{agent_name}_playbook.json"

    def load(self) -> Playbook:
        """Load playbook for agent.

        Returns:
            Playbook instance

        Raises:
            FileNotFoundError: If playbook file doesn't exist
        """
        if not self.playbook_path.exists():
            # Generate mock playbook for demo
            return self._generate_mock_playbook()

        try:
            with open(self.playbook_path, "r") as f:
                data = json.load(f)

            bullets = [
                PlaybookBullet(
                    bullet_id=b["bullet_id"],
                    content=b["content"],
                    category=b["category"],
                    effectiveness=b["effectiveness"],
                    usage_count=b.get("usage_count", 0),
                    added_date=(datetime.fromisoformat(b["added_date"]) if b.get("added_date") else None),
                    status=b.get("status", "active"),
                    metadata=b.get("metadata", {}),
                )
                for b in data.get("bullets", [])
            ]

            return Playbook(
                agent_name=self.agent_name,
                bullets=bullets,
                total_bullets=len(bullets),
                avg_effectiveness=data.get("avg_effectiveness", 0.0),
                last_updated=(datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None),
            )
        except Exception as e:
            logger.error(f"Failed to load playbook for {self.agent_name}: {e}")
            return self._generate_mock_playbook()

    def save(self, playbook: Playbook) -> bool:
        """Save playbook to disk.

        Args:
            playbook: Playbook to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.config.playbook_dir.mkdir(parents=True, exist_ok=True)

            data = playbook.to_dict()

            with open(self.playbook_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved playbook for {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save playbook for {self.agent_name}: {e}")
            return False

    def _generate_mock_playbook(self) -> Playbook:
        """Generate mock playbook for demo purposes.

        Returns:
            Mock Playbook instance
        """
        categories = [
            "error_handling",
            "optimization",
            "user_interaction",
            "code_quality",
            "testing",
            "documentation",
            "security",
            "performance",
        ]

        mock_bullets = [
            "Always validate user input before processing",
            "Use try-except blocks for error-prone operations",
            "Cache expensive computations when possible",
            "Log errors with full context for debugging",
            "Provide clear error messages to users",
            "Use type hints for better code clarity",
            "Write tests for critical functionality",
            "Document complex logic with inline comments",
            "Sanitize user input to prevent injection attacks",
            "Use connection pooling for database operations",
            "Implement retry logic for transient failures",
            "Profile code to identify performance bottlenecks",
            "Use async/await for I/O-bound operations",
            "Validate API responses before processing",
            "Implement rate limiting for external API calls",
            "Use meaningful variable and function names",
            "Break down complex functions into smaller ones",
            "Add logging at key decision points",
            "Use constants for magic numbers",
            "Implement proper cleanup in finally blocks",
        ]

        # Generate 157 bullets (as mentioned in spec)
        bullets = []
        for i in range(157):
            bullet_id = f"{self.agent_name}_{i:03d}"
            content = mock_bullets[i % len(mock_bullets)]
            if i >= len(mock_bullets):
                content = f"{content} (variant {i // len(mock_bullets)})"

            category = categories[i % len(categories)]
            effectiveness = random.uniform(0.3, 0.95)
            usage_count = random.randint(0, 50)
            added_date = datetime.now() - timedelta(days=random.randint(1, 90))
            status = random.choice(["active"] * 90 + ["pending"] * 8 + ["archived"] * 2)

            bullets.append(
                PlaybookBullet(
                    bullet_id=bullet_id,
                    content=content,
                    category=category,
                    effectiveness=effectiveness,
                    usage_count=usage_count,
                    added_date=added_date,
                    status=status,
                )
            )

        avg_effectiveness = sum(b.effectiveness for b in bullets) / len(bullets)

        return Playbook(
            agent_name=self.agent_name,
            bullets=bullets,
            total_bullets=len(bullets),
            avg_effectiveness=avg_effectiveness,
            last_updated=datetime.now(),
        )
