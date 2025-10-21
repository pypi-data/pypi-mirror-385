"""AI Service - Claude AI integration for natural language understanding.

This module provides Claude AI integration for the project manager CLI,
enabling natural language understanding and intelligent roadmap management.

IMPORTANT: Communication Guidelines
    See docs/COLLABORATION_METHODOLOGY.md Section 4.6:
    - Use plain language, NOT technical shorthand (no "US-012")
    - Say "the email notification feature" not "US-012"
    - Always explain features descriptively to users

Example:
    >>> from coffee_maker.cli.ai_service import AIService
    >>>
    >>> service = AIService()
    >>> response = service.process_request(
    ...     user_input="Add a priority for user authentication",
    ...     context={'roadmap_summary': summary},
    ...     history=[]
    ... )
    >>> print(response.message)
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from anthropic import Anthropic

from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt
from coffee_maker.config import ConfigManager

# Import RequestClassifier for Phase 2 integration (US-021)
try:
    from coffee_maker.cli.request_classifier import RequestClassifier

    CLASSIFIER_AVAILABLE = True
except ImportError:
    CLASSIFIER_AVAILABLE = False

# Import DocumentUpdater for Phase 3 integration (US-021)
try:
    from coffee_maker.cli.document_updater import DocumentUpdater, DocumentUpdateError

    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Import Claude CLI interface (optional)
try:
    from coffee_maker.autonomous.claude_cli_interface import (
        ClaudeCLIInterface,
    )

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    logger.warning("ClaudeCLIInterface not available, API mode only")


@dataclass
class AIResponse:
    """AI response with optional action.

    Attributes:
        message: Response message from Claude
        action: Optional structured action to execute
        confidence: Confidence score (0.0-1.0)
        metadata: Optional metadata (e.g., classification info)
    """

    message: str
    action: Optional[Dict] = None
    confidence: float = 1.0
    metadata: Optional[Dict] = None


class AIService:
    """Claude AI service for natural language understanding.

    This service provides intelligent roadmap management through natural
    language processing using Claude AI.

    Attributes:
        model: Claude model to use
        max_tokens: Maximum tokens per response
        client: Anthropic API client

    Example:
        >>> service = AIService()
        >>> response = service.process_request(
        ...     "What should we work on next?",
        ...     context={'roadmap_summary': {...}},
        ...     history=[]
        ... )
    """

    def __init__(
        self,
        model: str = "claude-3-5-haiku-20241022",
        max_tokens: int = 4000,
        use_claude_cli: bool = False,
        claude_cli_path: str = "/opt/homebrew/bin/claude",
    ):
        """Initialize AI service.

        Args:
            model: Claude model to use (default: Haiku 4.5 for cost efficiency)
            max_tokens: Maximum tokens per response
            use_claude_cli: If True, use Claude CLI instead of API (default: False)
            claude_cli_path: Path to claude CLI executable (default: /opt/homebrew/bin/claude)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.use_claude_cli = use_claude_cli
        self.client = None
        self.cli_interface = None

        # Initialize RequestClassifier for Phase 2 (US-021)
        self.classifier = None
        if CLASSIFIER_AVAILABLE:
            self.classifier = RequestClassifier()
            logger.info("RequestClassifier initialized (US-021 Phase 1)")
        else:
            logger.debug("RequestClassifier not available (will be added in Phase 2)")

        # Initialize DocumentUpdater for Phase 3 (US-021)
        self.document_updater = None
        if UPDATER_AVAILABLE:
            self.document_updater = DocumentUpdater()
            logger.info("DocumentUpdater initialized (US-021 Phase 3)")
        else:
            logger.debug("DocumentUpdater not available (will be added in Phase 3)")

        if use_claude_cli:
            # Use Claude CLI (subscription-based, no API credits needed)
            if not CLI_AVAILABLE:
                raise ValueError(
                    "Claude CLI mode requested but ClaudeCLIInterface not available. "
                    "Please check the import or use API mode instead."
                )

            # For CLI mode, convert model name to CLI alias if needed
            cli_model = model
            if "sonnet" in model.lower():
                cli_model = "sonnet"
            elif "opus" in model.lower():
                cli_model = "opus"
            elif "haiku" in model.lower():
                cli_model = "haiku"

            self.cli_interface = ClaudeCLIInterface(
                claude_path=claude_cli_path,
                model=cli_model,
                max_tokens=max_tokens,
            )

            logger.info(f"AIService initialized with Claude CLI: {cli_model}")

        else:
            # Use Anthropic API (requires API credits)
            try:
                api_key = ConfigManager.get_anthropic_api_key()
            except Exception as e:
                raise ValueError(
                    f"ANTHROPIC_API_KEY environment variable not set. "
                    f"Please set it in your .env file or environment. Error: {e}"
                ) from e

            self.client = Anthropic(api_key=api_key)

            logger.info(f"AIService initialized with Anthropic API: {model}")

    def process_request(self, user_input: str, context: Dict, history: List[Dict], stream: bool = True) -> AIResponse:
        """Process user request with AI and automatic classification.

        This is the Phase 2 integration point for US-021. The flow:
        1. Classify the request (feature/methodology/hybrid/clarification)
        2. If clarification needed, return clarifying questions
        3. Otherwise, add classification context and process with AI
        4. Return response with classification metadata

        Args:
            user_input: User's natural language input
            context: Current roadmap context (summary, priorities, etc.)
            history: Conversation history
            stream: If True, returns a streaming response (default: True)

        Returns:
            AIResponse with message, action, and classification metadata

        Example:
            >>> # Feature request
            >>> response = service.process_request(
            ...     "I want to add email notifications",
            ...     context={'roadmap_summary': summary},
            ...     history=[],
            ...     stream=False
            ... )
            >>> response.metadata['classification']['request_type']
            'feature_request'
            >>> response.metadata['classification']['target_documents']
            ['docs/roadmap/ROADMAP.md']
        """
        try:
            # Phase 2: Classify the request FIRST (US-021)
            classification = None
            classification_context = {}

            if self.classifier:
                classification = self.classifier.classify(user_input)

                # Log classification
                logger.info(
                    f"Request classified as: {classification.request_type.value} "
                    f"(confidence: {classification.confidence:.2f})"
                )
                logger.debug(f"Target documents: {classification.target_documents}")

                # Build classification context for AI
                classification_context = {
                    "request_type": classification.request_type.value,
                    "confidence": classification.confidence,
                    "target_documents": classification.target_documents,
                    "feature_indicators": classification.feature_indicators,
                    "methodology_indicators": classification.methodology_indicators,
                    "needs_clarification": classification.request_type.value == "clarification_needed",
                }

                # If clarification needed, ask questions FIRST
                if classification.request_type.value == "clarification_needed":
                    clarification_prompt = self._build_clarification_prompt(classification)
                    return AIResponse(
                        message=clarification_prompt,
                        action=None,
                        confidence=classification.confidence,
                        metadata={
                            "needs_clarification": True,
                            "classification": classification_context,
                        },
                    )

            # Add classification to context
            enhanced_context = {**context, "classification": classification_context}

            # Build system prompt with classification context
            system_prompt = self._build_system_prompt_with_classification(enhanced_context)

            # Build conversation messages
            messages = self._build_messages(user_input, history)

            logger.debug(f"Processing request: {user_input[:100]}...")

            if self.use_claude_cli:
                # Use Claude CLI interface
                # Build full prompt: system + history + user input
                full_prompt = system_prompt + "\n\n"

                # Add conversation history
                for msg in messages[:-1]:  # All except last (current user input)
                    role = msg["role"]
                    content = msg["content"]
                    full_prompt += f"\n{role.upper()}: {content}\n"

                # Add current user input
                full_prompt += f"\nUSER: {user_input}\n\nASSISTANT:"

                # Execute via CLI
                result = self.cli_interface.execute_prompt(full_prompt)

                if not result.success:
                    raise Exception(result.error)

                content = result.content

            else:
                # Use Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt,
                    messages=messages,
                )

                # Extract content
                content = response.content[0].text

            logger.info(f"AI response generated ({len(content)} chars)")

            # Extract action if present
            action = self._extract_action(content)

            # Phase 3: Update documents if classification indicates it (US-021)
            update_results = None
            if (
                self.document_updater
                and classification
                and classification.request_type.value != "clarification_needed"
                and classification.target_documents
            ):
                try:
                    # Extract metadata from AI response or use defaults
                    metadata = self._extract_metadata_from_response(user_input, content, classification)

                    # Update documents
                    logger.info(f"Updating documents for {classification.request_type.value} request")
                    update_results = self.document_updater.update_documents(
                        request_type=classification.request_type,
                        content=user_input,
                        target_documents=classification.target_documents,
                        metadata=metadata,
                    )

                    # Log results
                    for doc_path, success in update_results.items():
                        if success:
                            logger.info(f"✅ Successfully updated {doc_path}")
                        else:
                            logger.warning(f"❌ Failed to update {doc_path}")

                except DocumentUpdateError as e:
                    logger.error(f"Document update failed: {e}")
                    # Return error response
                    return AIResponse(
                        message=f"I understood your request, but failed to update documents: {e}\n\nAI Response: {content}",
                        action=action,
                        confidence=0.5,
                        metadata={
                            "classification": classification_context,
                            "update_error": str(e),
                        },
                    )

            # Return with classification and update metadata
            response_metadata = {"classification": classification_context} if classification else {}
            if update_results:
                response_metadata["document_updates"] = update_results

            return AIResponse(
                message=content,
                action=action,
                confidence=1.0,
                metadata=response_metadata if response_metadata else None,
            )

        except Exception as e:
            logger.error(f"AI request failed: {e}")
            return AIResponse(
                message=f"Sorry, I encountered an error: {str(e)}",
                action=None,
                confidence=0.0,
                metadata=None,
            )

    def process_request_stream(self, user_input: str, context: Dict, history: List[Dict]):
        """Process user request with AI streaming.

        Args:
            user_input: User's natural language input
            context: Current roadmap context
            history: Conversation history

        Yields:
            Text chunks as they arrive from Claude API

        Example:
            >>> for chunk in service.process_request_stream("Hello", context, []):
            ...     print(chunk, end="")
            Hello! How can I help you today?
        """
        try:
            if self.use_claude_cli:
                # Claude CLI doesn't support streaming, so we get the full response
                # and yield it in chunks to simulate streaming
                response = self.process_request(user_input, context, history, stream=False)

                # Yield in smaller chunks with word-boundary awareness for smooth streaming
                # Similar to claude-cli's character-by-character appearance
                import time

                words = response.message.split()
                for word in words:
                    yield word + " "
                    # Small delay to simulate natural typing (adjustable)
                    time.sleep(0.01)  # 10ms per word feels natural

                logger.info("CLI response yielded word-by-word")
                return

            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Build conversation messages
            messages = self._build_messages(user_input, history)

            logger.debug(f"Processing streaming request: {user_input[:100]}...")

            # Stream from Claude API
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

            logger.info("Streaming response completed")

        except Exception as e:
            logger.error(f"Streaming request failed: {e}")
            yield f"\n\n❌ Sorry, I encountered an error: {str(e)}"

    def classify_intent(self, user_input: str) -> str:
        """Classify user intent based on input.

        Uses simple keyword matching for intent classification.
        Could be enhanced with a small classification model.

        Args:
            user_input: User input text

        Returns:
            Intent category (add_priority, update_priority, view_roadmap, etc.)

        Example:
            >>> intent = service.classify_intent("Add a new priority")
            >>> print(intent)
            'add_priority'
        """
        lower_input = user_input.lower()

        # Intent patterns
        intents = {
            "user_story": [
                "as a",
                "i want",
                "i need",
                "user story",
                "feature request",
                "so that",
            ],
            "add_priority": [
                "add",
                "create",
                "new priority",
                "insert priority",
            ],
            "update_priority": [
                "update",
                "change",
                "modify",
                "edit priority",
                "mark as",
            ],
            "view_roadmap": [
                "show",
                "view",
                "display",
                "see",
                "list",
                "what are",
            ],
            "analyze_roadmap": [
                "analyze",
                "health",
                "check",
                "status",
                "how is",
            ],
            "suggest_next": [
                "suggest",
                "recommend",
                "what next",
                "what should",
                "priority",
            ],
            "start_implementation": [
                "implement",
                "start",
                "begin",
                "work on",
                "build",
            ],
            "daemon_status": [
                "daemon",
                "running",
                "status",
                "progress",
            ],
        }

        # Check each intent pattern
        for intent, patterns in intents.items():
            if any(pattern in lower_input for pattern in patterns):
                logger.debug(f"Classified intent: {intent}")
                return intent

        # Default to general query
        logger.debug("Classified intent: general_query")
        return "general_query"

    def _build_clarification_prompt(self, classification: "ClassificationResult") -> str:
        """Build clarification prompt from classification result.

        Args:
            classification: Classification result with suggested questions

        Returns:
            Formatted clarification prompt

        Example:
            >>> # This is called when confidence is low or request is ambiguous
            >>> prompt = service._build_clarification_prompt(classification)
            >>> "clarification" in prompt.lower()
            True
        """
        prompt = "I need some clarification to help you effectively.\n\n"

        # Add confidence info if low
        if classification.confidence < 0.5:
            prompt += (
                f"I'm not confident about interpreting your request (confidence: {classification.confidence:.0%}).\n\n"
            )

        # Add suggested questions
        if classification.suggested_questions:
            prompt += "\n".join(classification.suggested_questions)

        # Add what we detected (for transparency)
        if classification.feature_indicators:
            indicators = ", ".join([ind.split(": ")[1] for ind in classification.feature_indicators[:3]])
            prompt += f"\n\nFeature indicators I detected: {indicators}"

        if classification.methodology_indicators:
            indicators = ", ".join([ind.split(": ")[1] for ind in classification.methodology_indicators[:3]])
            prompt += f"\n\nMethodology indicators I detected: {indicators}"

        return prompt

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with roadmap context.

        Enhanced: Now uses centralized prompt from .claude/commands/
        for easy migration to Gemini, OpenAI, or other LLMs.

        Args:
            context: Context dictionary with roadmap information

        Returns:
            System prompt string loaded from .claude/commands/agent-project-manager.md
        """
        roadmap_summary = context.get("roadmap_summary", {})

        total = roadmap_summary.get("total", 0)
        completed = roadmap_summary.get("completed", 0)
        in_progress = roadmap_summary.get("in_progress", 0)
        planned = roadmap_summary.get("planned", 0)

        # Build priority list if available
        priorities = roadmap_summary.get("priorities", [])
        priority_list = ""
        if priorities:
            for p in priorities[:10]:  # Limit to first 10
                priority_list += f"- {p['number']}: {p['title']} ({p['status']})\n"

        # Load centralized prompt and substitute variables
        prompt = load_prompt(
            PromptNames.AGENT_PROJECT_MANAGER,
            {
                "TOTAL_PRIORITIES": str(total),
                "COMPLETED_PRIORITIES": str(completed),
                "IN_PROGRESS_PRIORITIES": str(in_progress),
                "PLANNED_PRIORITIES": str(planned),
                "PRIORITY_LIST": priority_list or "No priorities currently listed.",
            },
        )

        return prompt

    def _build_system_prompt_with_classification(self, context: Dict) -> str:
        """Build system prompt with classification context (Phase 2 enhancement).

        This method enhances the base system prompt with classification guidance
        to help the AI understand what type of request it's handling and which
        documents should be updated.

        Args:
            context: Context dictionary with roadmap and classification info

        Returns:
            Enhanced system prompt with classification guidance
        """
        # Start with base system prompt
        system_prompt = self._build_system_prompt(context)

        # Add classification guidance if available
        classification = context.get("classification", {})
        if classification and classification.get("request_type"):
            classification_guidance = f"""

**Request Classification (US-021 Phase 2):**
- Type: {classification['request_type']}
- Confidence: {classification['confidence']:.0%}
- Target Documents: {', '.join(classification['target_documents'])}

**Your Instructions Based on Classification:**
1. Acknowledge the request type explicitly (e.g., "I see you're requesting a new feature...")
2. Explain which documents will be updated: {', '.join(classification['target_documents'])}
3. If hybrid request (both feature + methodology), explain you'll update both ROADMAP and TEAM_COLLABORATION
4. Provide your response addressing the specific request type
5. End with confirmation: "I'll update [documents] with this information."

Remember: Be transparent about what you'll do with the user's request!
"""
            system_prompt += classification_guidance

        return system_prompt

    def _build_messages(self, user_input: str, history: List[Dict]) -> List[Dict]:
        """Build conversation messages.

        Args:
            user_input: Current user input
            history: Conversation history

        Returns:
            List of message dictionaries for Claude API
        """
        messages = []

        # Add history (last 10 messages for context window)
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current input
        messages.append({"role": "user", "content": user_input})

        return messages

    def _extract_action(self, content: str) -> Optional[Dict]:
        """Extract structured action from AI response.

        Looks for XML-like action tags in the response:
        <action type="add_priority" priority="PRIORITY X" .../>

        Args:
            content: AI response content

        Returns:
            Action dictionary or None

        Example:
            >>> action = self._extract_action(
            ...     "Let's add it. <action type='add_priority' priority='10'/>"
            ... )
            >>> print(action['type'])
            'add_priority'
        """
        if "<action" not in content:
            return None

        try:
            # Parse action attributes
            match = re.search(r"<action\s+(.+?)/>", content, re.DOTALL)
            if not match:
                return None

            attrs_str = match.group(1)

            # Parse attributes: type="..." priority="..." etc.
            attrs = {}
            for attr_match in re.finditer(r'(\w+)=["\']([^"\']+)["\']', attrs_str):
                attrs[attr_match.group(1)] = attr_match.group(2)

            logger.debug(f"Extracted action: {attrs}")
            return attrs

        except Exception as e:
            logger.warning(f"Failed to extract action: {e}")
            return None

    def extract_user_story(self, user_input: str) -> Optional[Dict]:
        """Extract User Story components from natural language.

        Uses Claude AI to parse natural language into structured User Story format.

        Args:
            user_input: Natural language description

        Returns:
            Dictionary with User Story components:
            {
                'role': 'developer',
                'want': 'deploy on GCP',
                'so_that': 'runs 24/7',
                'title': 'Deploy code_developer on GCP'
            }
            or None if can't extract

        Example:
            >>> story = service.extract_user_story(
            ...     "I want to deploy on GCP so it runs 24/7"
            ... )
            >>> print(story['title'])
            'Deploy code_developer on GCP'
        """
        try:
            prompt = f"""Extract User Story from this input:

{user_input}

Respond ONLY in this exact XML format:
<user_story>
<role>system administrator</role>
<want>deploy code_developer on GCP</want>
<so_that>it runs 24/7 autonomously</so_that>
<title>Deploy code_developer on GCP</title>
</user_story>

If this is NOT a User Story (no clear feature request), respond with: NOT_A_USER_STORY

Remember:
- role: Who needs this (developer, user, admin, etc.)
- want: What they want (feature/capability)
- so_that: Why they want it (benefit/value)
- title: Short descriptive title (5-10 words)
"""

            logger.debug(f"Extracting User Story from: {user_input[:100]}...")

            if self.use_claude_cli:
                # Use Claude CLI
                result = self.cli_interface.execute_prompt(prompt)
                if not result.success:
                    raise Exception(result.error)
                content = result.content.strip()
            else:
                # Use Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text.strip()

            # Check if it's not a User Story
            if "NOT_A_USER_STORY" in content:
                logger.debug("Input is not a User Story")
                return None

            # Parse XML response
            role_match = re.search(r"<role>(.+?)</role>", content, re.DOTALL)
            want_match = re.search(r"<want>(.+?)</want>", content, re.DOTALL)
            so_that_match = re.search(r"<so_that>(.+?)</so_that>", content, re.DOTALL)
            title_match = re.search(r"<title>(.+?)</title>", content, re.DOTALL)

            if not all([role_match, want_match, so_that_match, title_match]):
                logger.warning("Failed to parse User Story XML")
                return None

            story = {
                "role": role_match.group(1).strip(),
                "want": want_match.group(1).strip(),
                "so_that": so_that_match.group(1).strip(),
                "title": title_match.group(1).strip(),
            }

            logger.info(f"Extracted User Story: {story['title']}")
            return story

        except Exception as e:
            logger.error(f"User Story extraction failed: {e}")
            return None

    def generate_prioritization_question(self, story1: Dict, story2: Dict) -> str:
        """Generate natural question asking user to prioritize between two stories.

        Args:
            story1: First User Story dict with keys: id, title, role, want, so_that, estimated_effort
            story2: Second User Story dict with same structure

        Returns:
            Natural language question for user to answer

        Example:
            >>> question = service.generate_prioritization_question(
            ...     {'id': 'US-001', 'title': 'Deploy on GCP', 'estimated_effort': '5-7 days'},
            ...     {'id': 'US-002', 'title': 'CSV Export', 'estimated_effort': '2-3 days'}
            ... )
            >>> print(question)
            Between these two User Stories, which is more urgent?
            ...
        """
        try:
            question = f"""
Between these two User Stories, which is more urgent for you?

**A) {story1.get('title', 'Story 1')}**
   As a: {story1.get('role', 'user')}
   I want: {story1.get('want', '...')}
   Estimated effort: {story1.get('estimated_effort', 'TBD')}

**B) {story2.get('title', 'Story 2')}**
   As a: {story2.get('role', 'user')}
   I want: {story2.get('want', '...')}
   Estimated effort: {story2.get('estimated_effort', 'TBD')}

Your business priorities will help me organize the roadmap effectively.
Type **A** or **B** to indicate which story is more important to complete first.
"""
            return question.strip()

        except Exception as e:
            logger.error(f"Failed to generate prioritization question: {e}")
            return "Which story is more important?"

    def analyze_user_story_impact(self, story: Dict, roadmap_summary: Dict, priorities: List[Dict]) -> str:
        """Analyze roadmap impact of adding a User Story.

        Uses Claude AI to analyze how adding a User Story would affect the roadmap.

        Args:
            story: User Story dict
            roadmap_summary: Current roadmap summary
            priorities: List of existing priorities

        Returns:
            Impact analysis as formatted markdown string

        Example:
            >>> analysis = service.analyze_user_story_impact(
            ...     story={'title': 'Deploy on GCP', 'want': 'deploy on GCP', ...},
            ...     roadmap_summary={'total': 9, 'completed': 3, ...},
            ...     priorities=[...]
            ... )
        """
        try:
            # Build context about current roadmap
            priorities_text = "\n".join([f"- {p['number']}: {p['title']} ({p['status']})" for p in priorities[:10]])

            prompt = f"""Analyze the roadmap impact of adding this User Story:

**New User Story:**
- Title: {story.get('title', 'Unknown')}
- As a: {story.get('role', 'user')}
- I want: {story.get('want', 'feature')}
- So that: {story.get('so_that', 'benefit')}
- Estimated effort: {story.get('estimated_effort', 'TBD')}

**Current Roadmap:**
Total priorities: {roadmap_summary.get('total', 0)}
Completed: {roadmap_summary.get('completed', 0)}
In Progress: {roadmap_summary.get('in_progress', 0)}
Planned: {roadmap_summary.get('planned', 0)}

**Existing Priorities:**
{priorities_text}

Analyze:
1. Which existing priority(ies) could this User Story fit into?
2. Would this require a new priority?
3. What priorities might be delayed if we add this?
4. What dependencies exist?
5. What are the risks?
6. What's your recommendation?

Provide a concise analysis in markdown format.
"""

            logger.debug(f"Analyzing roadmap impact for story: {story.get('title')}")

            if self.use_claude_cli:
                # Use Claude CLI
                result = self.cli_interface.execute_prompt(prompt)
                if not result.success:
                    raise Exception(result.error)
                analysis = result.content
            else:
                # Use Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                analysis = response.content[0].text

            logger.info("Roadmap impact analysis generated")
            return analysis

        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return f"Unable to analyze impact: {str(e)}"

    def check_available(self) -> bool:
        """Check if AI service is available.

        Returns:
            True if API key is configured and accessible

        Example:
            >>> if service.check_available():
            ...     print("AI service ready!")
        """
        try:
            if self.use_claude_cli:
                # Check if Claude CLI is available
                available = self.cli_interface.check_available()
                logger.info(f"Claude CLI service available: {available}")
                return available
            else:
                # Try a minimal API call
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}],
                )

                logger.info(f"AI service available: {response.model}")
                return True

        except Exception as e:
            logger.error(f"AI service not available: {e}")
            return False

    def classify_user_request(self, user_input: str) -> Optional[Dict]:
        """Classify user request into feature/methodology/hybrid/clarification.

        This is the integration point for US-021 Phase 2.
        Currently returns classification result if classifier is available.
        Phase 2 will integrate this into the main processing flow.

        Args:
            user_input: Raw user input text

        Returns:
            Dictionary with classification results:
            {
                'type': 'feature_request' | 'methodology_change' | 'hybrid' | 'clarification_needed',
                'confidence': 0.0-1.0,
                'target_documents': ['docs/roadmap/ROADMAP.md', ...],
                'suggested_questions': ['Question 1', 'Question 2', ...],
                'feature_indicators': ['indicator1', ...],
                'methodology_indicators': ['indicator1', ...]
            }
            or None if classifier not available

        Example:
            >>> service = AIService()
            >>> result = service.classify_user_request("I want to add email notifications")
            >>> print(result['type'])
            'feature_request'
            >>> print(result['target_documents'])
            ['docs/roadmap/ROADMAP.md']

        Phase 2 Integration Plan:
            1. Call this method at the start of process_request()
            2. If type == 'clarification_needed', ask clarification questions first
            3. Route to appropriate document update based on target_documents
            4. Add explicit confirmation: "I'll update ROADMAP.md with this feature..."
        """
        if not self.classifier:
            logger.warning("RequestClassifier not available, skipping classification")
            return None

        try:
            # Classify the request
            classification = self.classifier.classify(user_input)

            # Convert to dictionary for easier consumption
            result = {
                "type": classification.request_type.value,
                "confidence": classification.confidence,
                "target_documents": classification.target_documents,
                "suggested_questions": classification.suggested_questions,
                "feature_indicators": classification.feature_indicators,
                "methodology_indicators": classification.methodology_indicators,
            }

            logger.info(f"Request classified as: {result['type']} " f"(confidence: {result['confidence']:.2f})")

            # Log for debugging (Phase 2 will use this for routing)
            logger.debug(f"Target documents: {result['target_documents']}")
            if result["suggested_questions"]:
                logger.debug(f"Clarification needed: {len(result['suggested_questions'])} questions")

            return result

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None

    def _extract_metadata_from_response(
        self, user_input: str, ai_response: str, classification: "ClassificationResult"
    ) -> Dict:
        """Extract metadata for document update from AI response and user input.

        This method intelligently extracts metadata needed for document updates,
        including title, business_value, estimated_effort, acceptance_criteria, etc.

        Args:
            user_input: Original user input
            ai_response: AI's response to the request
            classification: Classification result with indicators

        Returns:
            Dictionary with metadata for document update

        Example:
            >>> metadata = self._extract_metadata_from_response(
            ...     "I want to add email notifications",
            ...     "Great idea! I'll add that to the roadmap...",
            ...     classification
            ... )
            >>> print(metadata['title'])
            'Add email notifications'
        """
        metadata = {}

        # Extract title from user input
        # Try to find the core request in the user input
        metadata["title"] = self._extract_title(user_input)

        # Set defaults based on request type
        if classification.request_type.value == "feature_request":
            metadata["business_value"] = "TBD - please specify business value"
            metadata["estimated_effort"] = "TBD - to be estimated during planning"
            metadata["acceptance_criteria"] = [
                "Feature implemented and tested",
                "Documentation updated",
                "User acceptance testing passed",
            ]
        elif classification.request_type.value == "methodology_change":
            metadata["rationale"] = "TBD - please specify rationale"
            metadata["applies_to"] = "All team members"
            metadata["section"] = "General Guidelines"
        elif classification.request_type.value == "hybrid":
            # Hybrid gets both feature and methodology metadata
            metadata["business_value"] = "TBD - please specify business value"
            metadata["estimated_effort"] = "TBD - to be estimated during planning"
            metadata["acceptance_criteria"] = [
                "Feature implemented and tested",
                "Methodology documented and communicated",
            ]
            metadata["rationale"] = "TBD - please specify rationale"
            metadata["applies_to"] = "All team members"

        return metadata

    def _extract_title(self, text: str) -> str:
        """Extract title from user input.

        Attempts to extract a concise title from the user's request.

        Args:
            text: User input text

        Returns:
            Extracted title (max 80 characters)

        Example:
            >>> title = self._extract_title("I want to add email notifications for completed tasks")
            >>> print(title)
            'Add email notifications for completed tasks'
        """
        # Remove common prefixes
        text = text.strip()
        prefixes_to_remove = [
            "i want to ",
            "i need to ",
            "we should ",
            "can we ",
            "please ",
            "could you ",
        ]

        lower_text = text.lower()
        for prefix in prefixes_to_remove:
            if lower_text.startswith(prefix):
                text = text[len(prefix) :]
                break

        # Capitalize first letter
        text = text[0].upper() + text[1:] if text else text

        # Take first sentence or truncate to 80 chars
        first_sentence = text.split(".")[0]
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."

        return first_sentence

    def warn_user(
        self,
        title: str,
        message: str,
        priority: str = "high",
        context: Optional[Dict] = None,
        play_sound: bool = True,
    ) -> int:
        """Create a warning notification for the user.

        This allows the project_manager agent to warn users about:
        - Blockers or issues requiring attention
        - High-priority items that need review
        - Critical project health concerns
        - Dependency problems
        - Resource constraints

        Args:
            title: Short warning title (e.g., "Blocker: US-021 waiting on spec review")
            message: Detailed warning message explaining the issue
            priority: Warning priority ("critical", "high", "normal", "low")
                     default: "high"
            context: Optional context data (e.g., {"priority": "US-021", "blocker_type": "spec_review"})
            play_sound: Whether to play notification sound (default: True)

        Returns:
            Notification ID

        Example:
            >>> service = AIService()
            >>> # Critical blocker warning
            >>> notif_id = service.warn_user(
            ...     title="🚨 BLOCKER: Technical spec review needed",
            ...     message="US-021 (Code Refactoring) is waiting on technical spec review. "
            ...             "code_developer cannot proceed until spec is approved. "
            ...             "Please review docs/US_021_TECHNICAL_SPEC.md and provide feedback.",
            ...     priority="critical",
            ...     context={"priority": "US-021", "blocker_type": "spec_review"}
            ... )

            >>> # High priority warning about dependencies
            >>> notif_id = service.warn_user(
            ...     title="⚠️ WARNING: Dependency conflict detected",
            ...     message="US-032 depends on US-031 which is not yet complete. "
            ...             "Recommend completing US-031 first to avoid rework.",
            ...     priority="high",
            ...     context={"priority": "US-032", "blocked_by": "US-031"}
            ... )

            >>> # Project health concern
            >>> notif_id = service.warn_user(
            ...     title="📊 Project Health: Velocity declining",
            ...     message="Completed priorities per week has dropped from 2.5 to 1.2. "
            ...             "Suggest reviewing scope or resources.",
            ...     priority="normal",
            ...     context={"metric": "velocity", "trend": "declining"}
            ... )
        """
        from coffee_maker.cli.notifications import NotificationDB

        try:
            db = NotificationDB()

            notif_id = db.create_notification(
                type="warning",
                title=title,
                message=message,
                priority=priority,
                context=context,
                play_sound=play_sound,
            )

            logger.info(f"User warning created: {title} (ID: {notif_id})")
            return notif_id

        except Exception as e:
            logger.error(f"Failed to create warning notification: {e}")
            # Log the warning even if notification fails
            logger.warning(f"USER WARNING: {title} - {message}")
            return -1

    def generate_technical_spec(
        self, user_story: str, feature_type: str = "general", complexity: str = "medium"
    ) -> Dict[str, any]:
        """Generate complete technical specification from user story.

        This method integrates SpecGenerator to automatically create
        detailed technical specifications with:
        - AI-assisted task breakdown
        - Intelligent time estimation
        - Phase grouping
        - Risk identification
        - Success criteria

        **US-016 Phase 3: AI-Assisted Task Breakdown**

        Args:
            user_story: User story description (natural language)
            feature_type: Type of feature (crud, integration, ui, infrastructure, analytics, security)
            complexity: Overall complexity (low, medium, high)

        Returns:
            Dictionary with:
            {
                'spec': TechnicalSpec object,
                'markdown': str (rendered markdown),
                'summary': {
                    'total_hours': float,
                    'total_days': float,
                    'phase_count': int,
                    'task_count': int,
                    'confidence': float
                }
            }

        Example:
            >>> service = AIService()
            >>> result = service.generate_technical_spec(
            ...     "As a user, I want email notifications when tasks complete",
            ...     feature_type="integration",
            ...     complexity="medium"
            ... )
            >>> print(result['summary']['total_hours'])
            16.5
            >>> print(result['markdown'][:100])
            # Technical Specification: Email Notifications
            >>> # Save to file
            >>> from pathlib import Path
            >>> Path("docs/EMAIL_NOTIFICATIONS_SPEC.md").write_text(result['markdown'])
        """
        from coffee_maker.autonomous.spec_generator import SpecGenerator

        try:
            logger.info(
                f"Generating technical spec for: '{user_story[:50]}...' "
                f"(type={feature_type}, complexity={complexity})"
            )

            # Initialize spec generator
            generator = SpecGenerator(self)

            # Generate spec
            spec = generator.generate_spec_from_user_story(
                user_story=user_story, feature_type=feature_type, complexity=complexity
            )

            # Render to markdown
            markdown = generator.render_spec_to_markdown(spec)

            # Count total tasks
            total_tasks = sum(len(phase.tasks) for phase in spec.phases)

            # Build summary
            summary = {
                "total_hours": spec.total_hours,
                "total_days": spec.total_days,
                "phase_count": len(spec.phases),
                "task_count": total_tasks,
                "confidence": spec.confidence,
            }

            logger.info(
                f"Spec generated: {summary['total_hours']}h "
                f"({summary['total_days']} days), "
                f"{summary['phase_count']} phases, "
                f"{summary['task_count']} tasks, "
                f"{summary['confidence']:.0%} confidence"
            )

            return {"spec": spec, "markdown": markdown, "summary": summary}

        except Exception as e:
            logger.error(f"Technical spec generation failed: {e}")
            raise Exception(f"Failed to generate technical spec: {str(e)}") from e
