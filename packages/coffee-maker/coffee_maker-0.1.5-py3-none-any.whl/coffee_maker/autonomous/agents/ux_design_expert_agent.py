"""UXDesignExpertAgent - UI/UX design guidance and recommendations.

This agent is responsible for providing design guidance, reviewing UI/UX decisions,
and recommending design improvements using Tailwind CSS and modern patterns.

Architecture:
    BaseAgent
      └── UXDesignExpertAgent
            ├── _do_background_work(): Proactive design reviews
            └── _handle_message(): Handle design requests

Related:
    SPEC-057: Multi-agent orchestrator technical specification
    CFR-013: All agents work on roadmap branch only
    US-057: Strategic requirement for multi-agent system

Continuous Work Loop:
    1. Pull latest from roadmap branch
    2. Review recently completed features for design
    3. Check for design inconsistencies
    4. Recommend Tailwind CSS improvements
    5. Provide accessibility guidance
    6. Sleep for check_interval seconds (default: 1 hour)

Message Handling:
    - design_review: Request design review for feature
    - design_decision: Request guidance on design choice
    - accessibility_review: Accessibility audit

Key Responsibilities:
    - Provide design specifications and recommendations
    - Review UI/UX consistency
    - Recommend Tailwind CSS patterns
    - Ensure accessibility compliance
    - Does NOT implement code (recommendations only)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.autonomous.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class UXDesignExpertAgent(BaseAgent):
    """UX Design Expert agent - UI/UX design guidance and recommendations.

    Responsibilities:
    - Provide design specifications and recommendations
    - Review UI/UX for consistency and best practices
    - Recommend Tailwind CSS patterns
    - Ensure accessibility compliance
    - Provide design system guidance

    Key Point: Recommendations, Not Implementation
        This agent provides design guidance and specs.
        Code_developer implements based on recommendations.
        Designer does NOT write code.

    Example:
        >>> agent = UXDesignExpertAgent(
        ...     status_dir=Path("data/agent_status"),
        ...     message_dir=Path("data/agent_messages"),
        ...     check_interval=3600  # 1 hour
        ... )
        >>> agent.run_continuous()  # Runs forever
    """

    def __init__(
        self,
        status_dir: Path,
        message_dir: Path,
        check_interval: int = 3600,  # 1 hour for design reviews
    ):
        """Initialize UXDesignExpertAgent.

        Args:
            status_dir: Directory for agent status files
            message_dir: Directory for inter-agent messages
            check_interval: Seconds between design reviews (default: 1 hour)
        """
        super().__init__(
            agent_type=AgentType.UX_DESIGN_EXPERT,
            status_dir=status_dir,
            message_dir=message_dir,
            check_interval=check_interval,
        )

        logger.info("✅ UXDesignExpertAgent initialized (design guidance)")

    def _do_background_work(self):
        """UX Designer's background work: proactive design reviews.

        Workflow:
        1. Check for recently completed features
        2. Review UI/UX consistency
        3. Check for accessibility compliance
        4. Identify design improvements
        5. Recommend Tailwind CSS patterns
        6. Provide design guidance

        Future (Phase 3):
        - Automated design consistency checking
        - Accessibility compliance auditing
        - Design pattern recommendations
        - Tailwind CSS optimization
        """
        logger.info("🎨 UX Designer: Reviewing design consistency...")

        # TODO: Implement proactive design reviews
        # For now, just log and continue
        logger.info("ℹ️  Design reviews not yet implemented")

        # Update metrics
        self.metrics["reviews_performed"] = self.metrics.get("reviews_performed", 0)
        self.metrics["recommendations_provided"] = self.metrics.get("recommendations_provided", 0)
        self.metrics["last_check"] = datetime.now().isoformat()

        # Update current task
        self.current_task = {
            "type": "design_review",
            "status": "reviewing",
            "last_check": datetime.now().isoformat(),
        }

    def _handle_message(self, message: Dict):
        """Handle inter-agent messages.

        Message types:
        - design_review: Request design review
        - design_decision: Request design guidance
        - accessibility_review: Accessibility audit

        Args:
            message: Message dictionary with 'type' and 'content'
        """
        msg_type = message.get("type")

        if msg_type == "design_review":
            # Design review request
            design_info = message.get("content", {})
            feature = design_info.get("feature", "unknown")

            logger.info(f"🎨 Design review requested for {feature}")

            # TODO: Perform design review and provide recommendations
            # In Phase 3: Implement design review logic

        elif msg_type == "design_decision":
            # Design decision guidance
            decision_info = message.get("content", {})
            question = decision_info.get("question", "design question")

            logger.info(f"🤔 Design question: {question}")

            # TODO: Provide design guidance
            # In Phase 3: Implement design guidance

        elif msg_type == "accessibility_review":
            # Accessibility audit
            message.get("content", {})
            logger.info(f"♿ Accessibility review requested")

            # TODO: Perform accessibility audit
            # In Phase 3: Implement accessibility checking

        else:
            logger.warning(f"Unknown message type: {msg_type}")
