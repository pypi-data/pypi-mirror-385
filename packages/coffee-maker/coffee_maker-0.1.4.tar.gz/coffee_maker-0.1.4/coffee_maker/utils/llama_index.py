from llama_index.core import Settings
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
import logging
import sys
from functools import partial
from typing import AsyncGenerator, Callable

# This prompt is focused ONLY on getting the model to call the tool correctly.
# The final summarization step will be handled by a separate, simpler prompt.
SYSTEM_PROMPT = """
You are an expert assistant that uses tools to answer questions.
To use a tool, you MUST respond in this format, and nothing else:
Thought: The user is asking a question that requires a tool. I will use the correct tool.
Action: get_weather
Action Input: {"location": "the user's requested city"}
"""

OLLAMA_MODEL = "llama3:8b"
REQUEST_TIMEOUT = 600

# --- Logging Configuration ---
# Set up a logger to provide detailed, timestamped output to the console.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)


async def get_agent_and_llm(
    tools_spec: McpToolSpec, ollama_model: str = OLLAMA_MODEL, request_timeout: int = REQUEST_TIMEOUT
) -> tuple[ReActAgent, Ollama]:
    """Creates and configures the ReActAgent and the LLM instance.

    Args:
        tools_spec (McpToolSpec): The MCP tool specification to provide to the agent.

    Returns:
        ReActAgent: A tuple containing the configured agent and LLM instance.
    """
    LOGGER.info("---")
    LOGGER.info("--- Step: Initializing Agent and LLM ---")

    # LlamaDebugHandler will print all LLM inputs/outputs and other events.
    llama_debug_handler = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug_handler])
    Settings.callback_manager = callback_manager

    LOGGER.info("Fetching tools from MCP server...")
    tool_list = await tools_spec.to_tool_list_async()
    LOGGER.info(f"Tools fetched: {[tool.metadata.name for tool in tool_list]}")

    LOGGER.info("Initializing LLM...")
    llm = Ollama(model=ollama_model, request_timeout=request_timeout)
    Settings.llm = llm

    LOGGER.info(
        f"Creating ReActAgent with the following system prompt:\n---PROMPT START---\n{SYSTEM_PROMPT}\n---PROMPT END---"
    )
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    agent = ReActAgent(tools=tool_list, llm=llm, memory=memory, system_prompt=SYSTEM_PROMPT, verbose=True)
    LOGGER.info("ReActAgent created successfully.")
    return agent, llm


async def run_agent_chat(message: str, history: list, agent: ReActAgent) -> str:
    """Runs the agent for a given message and returns the full answer.

    Args:
        message (str): The user's input message.
        _history (list): The chat history from the Gradio interface (currently unused).
        agent (ReActAgent): The agent instance to run the query.
    Yields:
        str: The agent's response as a string.
    """
    LOGGER.info(f"--- Running Agent for user message: '{message}' ---")
    response = await agent.run(message)
    LOGGER.info(f"Agent response: {response}")
    return str(response)


async def run_agent_chat_stream(message: str, history: list, agent: ReActAgent) -> AsyncGenerator[str, None]:
    """Runs the agent for a given message and streams the response token by token.

    Args:
        message (str): The user's input message.
        history (list): The chat history from the Gradio interface (currently unused).
        agent (ReActAgent): The agent instance to run the query.

    Yields:
        str: The agent's response, one token at a time.
    """
    LOGGER.info(f"--- Running Agent for user message: '{message}' ---")
    # Use astream_chat for true streaming instead of the blocking agent.run()
    response = await agent.astream_chat(message)

    # Stream the response tokens back to the caller
    async for token in response.async_stream_response():
        yield token


async def get_agent_func_with_context(
    mcp_server_tool_url: str, ollama_model: str = OLLAMA_MODEL, request_timeout: int = REQUEST_TIMEOUT
) -> Callable:
    """Creates a partially configured agent chat function.

    This function initializes an MCP client and tools, creates a ReActAgent,
    and then returns a `run_agent_chat_stream` function with the agent
    instance pre-filled.

    Args:
        mcp_server_tool_url (str): The URL for the MCP server providing tools.
        ollama_model (str): The name of the Ollama model to use.
        request_timeout (int): The timeout in seconds for requests to the LLM.

    Returns:
        callable: A function that can be called with a message and history
            to start a chat stream with the agent.
    """
    mcp_client = BasicMCPClient(mcp_server_tool_url)
    mcp_tools_spec = McpToolSpec(mcp_client)
    agent, llm = await get_agent_and_llm(mcp_tools_spec, ollama_model=ollama_model, request_timeout=request_timeout)

    return partial(run_agent_chat_stream, agent=agent)
