"""Token estimation utilities."""

import logging
from typing import Any

import tiktoken

logger = logging.getLogger(__name__)


def estimate_tokens(input_data: Any, model_name: str = "gpt-4") -> int:
    """Estimate token count for input data.

    Args:
        input_data: Input to estimate (dict, str, or list)
        model_name: Model name for tokenizer selection

    Returns:
        Estimated token count
    """
    try:
        # Try to get encoding for the specific model
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to cl100k_base (used by gpt-4, gpt-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")

    # Convert input_data to string
    if isinstance(input_data, dict):
        # For dict inputs (common in LangChain)
        text = str(input_data.get("input", "") or input_data.get("prompt", "") or str(input_data))
    elif isinstance(input_data, list):
        # For list of messages
        text = " ".join(str(msg) for msg in input_data)
    else:
        text = str(input_data)

    # Estimate tokens
    try:
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token estimation failed: {e}, using fallback")
        # Fallback: ~4 characters per token
        return len(text) // 4
