"""Agent Delegation Router for routing user requests to specialized agents.

This module handles intent classification and delegation to the appropriate
specialized agents (architect, project_manager, code_developer, etc.).

Architecture:
    AgentDelegationRouter: Routes requests based on pattern matching + AI
    Uses keyword-based classification for fast decisions
    Falls back to AI-based classification for ambiguous requests

Usage:
    >>> from coffee_maker.cli.agent_router import AgentDelegationRouter
    >>> from coffee_maker.cli.ai_service import AIService
    >>> ai_service = AIService()
    >>> router = AgentDelegationRouter(ai_service)
    >>> agent_type, confidence = router.classify_intent("Design a caching layer")
    >>> response = router.delegate_to_agent(agent_type, "Design a caching layer", [])
"""

import logging
import re
from typing import Dict, List, Tuple

from coffee_maker.autonomous.agent_registry import AgentType
from coffee_maker.cli.ai_service import AIService

logger = logging.getLogger(__name__)


class AgentDelegationRouter:
    """Routes user requests to appropriate specialized agents.

    Uses pattern matching and AI classification to determine
    which agent should handle each type of request.

    Attributes:
        ai_service: AIService instance for AI-based classification
    """

    def __init__(self, ai_service: AIService):
        """Initialize agent router.

        Args:
            ai_service: AI service for intent classification
        """
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)

        # Pattern-based classification keywords
        self.patterns: Dict[AgentType, List[str]] = {
            AgentType.ARCHITECT: [
                "design",
                "architecture",
                "technical spec",
                "adr",
                "dependency",
                "add package",
                "design pattern",
                "framework",
                "technology",
            ],
            AgentType.PROJECT_MANAGER: [
                "roadmap",
                "priority",
                "github",
                "pr status",
                "strategic",
                "planning",
                "milestone",
                "status",
                "progress",
            ],
            AgentType.CODE_DEVELOPER: [
                "implement",
                "code",
                "pull request",
                "pr",
                "fix bug",
                "write code",
                "develop",
                "bug fix",
            ],
            AgentType.ASSISTANT: [
                "documentation",
                "demo",
                "show me",
                "explain",
                "test",
                "bug report",
                "how does",
                "help",
            ],
            AgentType.CODE_SEARCHER: [
                "find in code",
                "where is",
                "search code",
                "analyze code",
                "code forensics",
                "dependency trace",
                "search",
            ],
            AgentType.UX_DESIGN_EXPERT: [
                "ui",
                "ux",
                "design",
                "tailwind",
                "dashboard",
                "chart",
                "visualization",
                "layout",
                "frontend",
            ],
        }

    def classify_intent(self, user_input: str) -> Tuple[AgentType, float]:
        """Classify user intent to determine appropriate agent.

        Uses keyword matching + AI classification for high accuracy.

        Args:
            user_input: User's message

        Returns:
            Tuple of (agent_type, confidence) where confidence is 0.0-1.0

        Example:
            >>> router.classify_intent("Design a caching layer")
            (AgentType.ARCHITECT, 0.95)
        """
        # Pattern-based classification (fast, no API call)
        lower_input = user_input.lower()
        for agent_type, keywords in self.patterns.items():
            if any(keyword in lower_input for keyword in keywords):
                self.logger.info(f"Intent classified: {agent_type.value} (pattern match)")
                return (agent_type, 0.9)  # High confidence from pattern match

        # Fallback to AI classification for ambiguous cases
        return self._classify_with_ai(user_input)

    def _classify_with_ai(self, user_input: str) -> Tuple[AgentType, float]:
        """Use AI to classify ambiguous intents.

        Args:
            user_input: User's message

        Returns:
            Tuple of (agent_type, confidence)
        """
        prompt = f"""Classify this user request to determine which specialized agent should handle it:

User request: "{user_input}"

Available agents:
- architect: Design, technical specs, ADRs, dependency management, framework selection
- project_manager: Strategic planning, ROADMAP, GitHub monitoring, project status
- code_developer: Implementation, pull requests, bug fixes, code changes
- assistant: Documentation, demos, bug reports, explanations, testing
- code-searcher: Deep code analysis, searching codebase, dependencies
- ux-design-expert: UI/UX design, Tailwind, charts, frontend

Respond ONLY with the agent name and confidence (0.0-1.0):
<classification>
<agent>architect</agent>
<confidence>0.95</confidence>
</classification>
"""

        try:
            response = self.ai_service.process_request(user_input=prompt, context={}, history=[], stream=False)

            # Parse response
            agent_match = re.search(r"<agent>(.+?)</agent>", response.message)
            conf_match = re.search(r"<confidence>(.+?)</confidence>", response.message)

            if agent_match and conf_match:
                agent_name = agent_match.group(1).strip().lower()
                try:
                    confidence = float(conf_match.group(1).strip())
                except ValueError:
                    confidence = 0.5

                # Map name to AgentType
                agent_map = {
                    "architect": AgentType.ARCHITECT,
                    "project_manager": AgentType.PROJECT_MANAGER,
                    "code_developer": AgentType.CODE_DEVELOPER,
                    "assistant": AgentType.ASSISTANT,
                    "code-searcher": AgentType.CODE_SEARCHER,
                    "ux-design-expert": AgentType.UX_DESIGN_EXPERT,
                }

                agent_type = agent_map.get(agent_name, AgentType.ASSISTANT)
                self.logger.info(f"Intent classified: {agent_type.value} (AI, {confidence:.2f})")
                return (agent_type, confidence)

            # Default to assistant for unknown
            self.logger.warning("Failed to parse AI classification, defaulting to assistant")
            return (AgentType.ASSISTANT, 0.5)

        except Exception as e:
            self.logger.error(f"AI classification failed: {e}", exc_info=True)
            return (AgentType.ASSISTANT, 0.5)

    def delegate_to_agent(self, agent_type: AgentType, request: str, conversation_history: List[Dict]) -> str:
        """Delegate request to specified agent.

        Args:
            agent_type: Which agent to delegate to
            request: User's request
            conversation_history: Previous conversation context

        Returns:
            Agent's response

        Note:
            In Phase 1, we simulate delegation by using AI with agent-specific prompts.
            In Phase 2, this would integrate with actual agent instances.
        """
        self.logger.info(f"Delegating to {agent_type.value}: {request[:50]}...")

        # Get delegation prompt for this agent type
        delegation_prompt = self._get_delegation_prompt(agent_type, request)

        # Execute delegation using AI with agent-specific prompt
        response = self.ai_service.process_request(
            user_input=delegation_prompt,
            context={"agent_type": agent_type.value},
            history=conversation_history[-5:] if conversation_history else [],  # Last 5 for context
            stream=False,
        )

        return response.message

    def _get_delegation_prompt(self, agent_type: AgentType, request: str) -> str:
        """Get agent-specific delegation prompt.

        Each agent has a specialized prompt that guides the AI to respond
        as that agent would.

        Args:
            agent_type: Agent to delegate to
            request: User's request

        Returns:
            Formatted delegation prompt
        """
        # For now, use a simple delegation prompt format
        # In Phase 2, we would load agent-specific prompts from .claude/commands/
        agent_role_map = {
            AgentType.ARCHITECT: (
                "You are an expert software architect. Provide architectural guidance, "
                "design specifications, and technical recommendations. Focus on system design, "
                "patterns, and best practices."
            ),
            AgentType.PROJECT_MANAGER: (
                "You are a project manager. Provide strategic planning advice, project status, "
                "roadmap guidance, and milestone tracking. Focus on deliverables and progress."
            ),
            AgentType.CODE_DEVELOPER: (
                "You are a software developer. Provide implementation guidance, code examples, "
                "and technical solutions. Focus on writing, testing, and delivering code."
            ),
            AgentType.ASSISTANT: (
                "You are a helpful documentation expert and assistant. Provide clear explanations, "
                "documentation guidance, and helpful information. Focus on clarity and understanding."
            ),
            AgentType.CODE_SEARCHER: (
                "You are a code analysis expert. Help analyze the codebase, find patterns, "
                "trace dependencies, and identify improvements. Focus on deep code understanding."
            ),
            AgentType.UX_DESIGN_EXPERT: (
                "You are a UI/UX design expert. Provide design guidance, visual recommendations, "
                "and Tailwind CSS expertise. Focus on user experience and visual design."
            ),
        }

        role_prompt = agent_role_map.get(agent_type, "You are a helpful assistant providing expert guidance.")

        return f"""{role_prompt}

User request: {request}

Provide a helpful, focused response as this specialized agent would."""


# Convenience function for getting a router instance
def get_agent_router(ai_service: AIService) -> AgentDelegationRouter:
    """Get an agent router instance.

    Args:
        ai_service: AIService to use for classification

    Returns:
        AgentDelegationRouter instance
    """
    return AgentDelegationRouter(ai_service)
