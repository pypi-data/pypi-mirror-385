# app.py
# co-author : Gemini 2.5 Pro Preview

# ==============================================================================
# --- Prerequisites ---
#
# 1. Start the Ollama server in a dedicated terminal:
#    ollama serve
#
# 2. Pull a capable model (8B parameters recommended for ReAct):
#    ollama pull llama3:8b
#
# 3. Start the dummy MCP tool server in a second dedicated terminal:
#    poetry run python dummy_mcp_server_tools.py
#
# 5. Finally, run this application in a third terminal:
#    poetry run python app.py
#
# ==============================================================================

import asyncio
import logging
import sys
import gradio as gr
from coffee_maker.utils.llama_index import get_agent_func_with_context
from coffee_maker.examples.llama_index.dummy_weather_mcp_server import PORT as weather_mcp_server_port

# --- Logging Configuration ---
# Set up a logger to provide detailed, timestamped output to the console.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)

# --- Configuration ---
MCP_SERVER_TOOL_URL = f"http://127.0.0.1:{weather_mcp_server_port}/sse"


async def main() -> None:
    """Initializes resources and launches the Gradio application."""
    agent_fn = await get_agent_func_with_context(MCP_SERVER_TOOL_URL)
    try:
        demo = gr.ChatInterface(
            fn=agent_fn,
            # Silences the Gradio UserWarning about message format
            chatbot=gr.Chatbot(
                label="Agent Chat", height=600, show_copy_button=True, render_markdown=True, type="messages"
            ),
            textbox=gr.Textbox(placeholder="Ask me something...", label="Your Message"),
            examples=["Quel temps fait il à Paris?"],
            title="Agent with MCP Tools",
            description="This agent uses an Ollama model and can use tools (dummy weather questions) via MCP.",
        )

        LOGGER.info("Launching Gradio interface...")
        demo.launch()

    except (OSError, ValueError) as e:
        LOGGER.critical(f"A critical error occurred in main: {e}", exc_info=True)
    finally:
        LOGGER.info("Application cleanup (no explicit MCP disconnect needed for BasicMCPClient).")


if __name__ == "__main__":
    from coffee_maker.examples.llama_index.dummy_weather_mcp_server import main as run_dummy_weather_server, PORT
    from coffee_maker.utils.run_daemon_process import run_daemon

    run_daemon(run_dummy_weather_server, PORT)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nApplication shutting down gracefully.")
