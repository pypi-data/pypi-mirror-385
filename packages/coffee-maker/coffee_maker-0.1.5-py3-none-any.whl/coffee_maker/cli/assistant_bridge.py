"""LangChain-powered Assistant Bridge for project-manager.

This module provides a transparent assistant that can help project-manager
answer complex questions using LangChain agents with tools.

PRIORITY 2.9.5: Transparent Assistant Integration

The assistant:
- Uses LangChain agents (can use any LLM provider)
- Has access to tools (file reading, code search, git, etc.)
- Streams actions to user in real-time
- Allows user to provide guidance during execution
- Is completely transparent to the user
"""

import logging
from typing import Callable, Dict, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from coffee_maker.cli.assistant_tools import get_assistant_tools
from coffee_maker.config import ConfigManager

logger = logging.getLogger(__name__)


class AssistantBridge:
    """Bridge to invoke LangChain-powered assistant transparently.

    The assistant uses LangChain agents with tools to help answer
    complex questions. Actions are streamed to the user in real-time.

    Attributes:
        agent: LangChain agent executor
        action_callback: Callback to display actions to user
    """

    def __init__(self, action_callback: Optional[Callable[[str], None]] = None):
        """Initialize assistant bridge.

        Args:
            action_callback: Callback function to display action steps
                            Called with action string like "🔍 Analyzing logs..."
        """
        self.action_callback = action_callback or self._default_action_callback
        self.agent = None
        self._initialize_agent()

    def _default_action_callback(self, action: str):
        """Default action callback that just logs."""
        logger.info(f"Assistant action: {action}")

    def _initialize_agent(self):
        """Initialize LangChain agent with tools."""
        try:
            # Get tools
            tools = get_assistant_tools()

            # Initialize LLM (try multiple providers)
            llm = self._get_llm()

            if not llm:
                logger.warning("No LLM available - assistant disabled")
                return

            # Create prompt template
            template = """Answer the following question using the tools available to you.
Think step by step and use tools when needed.

You have access to these tools:
{tools}

Tool names: {tool_names}

Use this format:
Question: the input question
Thought: think about what to do
Action: tool name
Action Input: input to the tool
Observation: result from tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question

Question: {input}

{agent_scratchpad}
"""

            prompt = PromptTemplate.from_template(template)

            # Create agent
            agent = create_react_agent(llm, tools, prompt)

            # Create executor
            self.agent = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                max_iterations=10,
                handle_parsing_errors=True,
                return_intermediate_steps=True,  # Important for action streaming
            )

            logger.debug("LangChain assistant initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize assistant: {e}", exc_info=True)
            self.agent = None

    def _get_llm(self):
        """Get LLM for agent (tries multiple providers).

        Uses Haiku 4.5 for cost efficiency on assistant tasks.

        Returns:
            LLM instance or None if no provider available
        """
        # Try Anthropic first (using Haiku 4.5 for cost efficiency)
        if ConfigManager.has_anthropic_api_key():
            try:
                return ChatAnthropic(model="claude-3-5-haiku-20241022", temperature=0)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic LLM: {e}")

        # Try OpenAI
        if ConfigManager.has_openai_api_key():
            try:
                return ChatOpenAI(model="gpt-4", temperature=0)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI LLM: {e}")

        # No provider available
        return None

    def is_available(self) -> bool:
        """Check if assistant is available.

        Returns:
            True if assistant can be used
        """
        return self.agent is not None

    def invoke(self, question: str, context: Optional[Dict] = None) -> Dict:
        """Invoke assistant to answer a question.

        Args:
            question: Question or task for assistant
            context: Optional context (not currently used)

        Returns:
            Dict with:
            - success: bool
            - answer: str (if successful)
            - actions: List[str] (actions taken)
            - error: str (if failed)
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Assistant not available (no LLM configured)",
            }

        try:
            logger.info(f"Invoking assistant for: {question[:100]}...")

            # Track actions
            actions = []

            # Invoke agent
            result = self.agent.invoke({"input": question})

            # Extract intermediate steps (actions)
            if "intermediate_steps" in result:
                for action, observation in result["intermediate_steps"]:
                    action_str = f"🔧 {action.tool}: {action.tool_input}"
                    actions.append(action_str)
                    self.action_callback(action_str)

            # Get final answer
            answer = result.get("output", "No answer provided")

            return {"success": True, "answer": answer, "actions": actions}

        except Exception as e:
            logger.error(f"Assistant invocation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def should_invoke_for_question(self, question: str) -> bool:
        """Determine if assistant should be invoked for a question.

        Args:
            question: User's question

        Returns:
            True if question is complex enough to warrant assistant help
        """
        # Keywords that suggest need for assistant
        complex_keywords = [
            "why",
            "how",
            "analyze",
            "debug",
            "investigate",
            "find",
            "search",
            "check",
            "review",
            "what's wrong",
            "what caused",
            "explain",
            "trace",
            "root cause",
        ]

        question_lower = question.lower()
        return any(keyword in question_lower for keyword in complex_keywords)
