"""LLM Provider configurations."""

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS: Dict[str, Tuple[Any, str, str, Dict[str, int]]] = {}

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    SUPPORTED_PROVIDERS.update(
        {"gemini": (ChatGoogleGenerativeAI, "GEMINI_API_KEY", "gemini-2.5-pro", {"max_tokens": 8192})}
    )
except ImportError:
    logger.warning("langchain_google_genai not installed. will not use google")

# class ClassicLlm
