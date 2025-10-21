"""Google Gemini LLM provider configuration and utilities.

This module provides configuration data for Google's Gemini models including:
- Available models (chat, embeddings, code, reasoning)
- Rate limits for free and paid tiers
- Model pricing and context lengths
- API limit handling with fallback support

The module supports automatic rate limit handling with fallback to alternative
models when quotas are exceeded.

Example:
    >>> from coffee_maker.langfuse_observe.llm_providers.gemini import MODELS_LIST
    >>> best_chat_model = MODELS_LIST["chat"]["best_models"][0]
    >>> print(best_chat_model)  # gemini-2.5-pro
"""

import google
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)
import langchain_google_genai as lg

MODELS_LIST: Dict[str, Any] = {
    "chat": dict(
        best_models=[
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
        ],
        create_instance=[lg.ChatGoogleGenerativeAI],
    ),
    "embeddings": [dict(best_models=["gemini-embedding-001"], create_instance=[lg.GoogleGenerativeAIEmbeddings])],
    "code": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"],
    "reasoning": ["gemini-2.0-flash-thinking-exp"],
    "cheapest general purpose": ["gemini-2.5-flash-lite"],
}

MODELS_ÌNFO: Dict[str, Dict[str, Any]] = dict(
    gemini=dict(
        reference="https://ai.google.dev/gemini-api/docs/rate-limits",
        values=dict(
            free=dict(
                **{
                    "gemini-2.5-pro": {
                        "requests per minute": 5,
                        "tokens per minute": 250000,
                        "requests per day": 100,
                        "context_length": 2097152,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                    "gemini-2.5-flash": {
                        "requests per minute": 15,
                        "tokens per minute": 1000000,
                        "requests per day": 1500,
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                    "gemini-2.5-flash-lite": {
                        "requests per minute": 15,
                        "tokens per minute": 250000,
                        "requests per day": 1000,
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                    "gemini-1.5-pro": {
                        "requests per minute": 2,
                        "tokens per minute": 32768,
                        "requests per day": 50,
                        "context_length": 2097152,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                    "gemini-1.5-flash": {
                        "requests per minute": 15,
                        "tokens per minute": 1000000,
                        "requests per day": 1500,
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                    "gemini-2.0-flash-thinking-exp": {
                        "requests per minute": 10,
                        "tokens per minute": 32000,
                        "requests per day": 500,
                        "context_length": 32768,
                        "max_output_tokens": 8192,
                        "price": {"per 1M tokens input": 0, "per 1M tokens output": 0},
                    },
                }
            ),
            paid=dict(
                **{
                    "gemini-2.5-pro": {
                        "requests per minute": 1000,
                        "tokens per minute": -1,  # Unlimited
                        "requests per day": -1,  # Unlimited
                        "context_length": 2097152,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input (<=200k)": 1.25,
                            "per 1M tokens output (<=200k)": 10.00,
                            "per 1M tokens input (>200k)": 2.50,
                            "per 1M tokens output (>200k)": 15.00,
                        },
                    },
                    "gemini-2.5-flash": {
                        "requests per minute": 2000,
                        "tokens per minute": -1,  # Unlimited
                        "requests per day": -1,  # Unlimited
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input": 0.20,
                            "per 1M tokens output": 0.70,
                        },
                    },
                    "gemini-2.5-flash-lite": {
                        "requests per minute": 2000,
                        "tokens per minute": -1,  # Unlimited
                        "requests per day": -1,  # Unlimited
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input": 0.10,
                            "per 1M tokens output": 0.40,
                        },
                    },
                    "gemini-1.5-pro": {
                        "requests per minute": 1000,
                        "tokens per minute": 8192000,
                        "requests per day": -1,  # Unlimited
                        "context_length": 2097152,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input (<128k)": 3.50,
                            "per 1M tokens output (<128k)": 10.50,
                        },
                    },
                    "gemini-1.5-flash": {
                        "requests per minute": 2000,
                        "tokens per minute": 8192000,
                        "requests per day": -1,  # Unlimited
                        "context_length": 1048576,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input": 0.35,
                            "per 1M tokens output": 1.05,
                        },
                    },
                }
            ),
            tier1=dict(
                **{
                    "gemini-2.0-flash-thinking-exp": {
                        "requests per minute": 50,
                        "tokens per minute": 100000,
                        "requests per day": 2000,
                        "context_length": 32768,
                        "max_output_tokens": 8192,
                        "price": {
                            "per 1M tokens input": 0.00,
                            "per 1M tokens output": 0.00,
                        },
                    },
                }
            ),
        ),
    )
)


def set_api_limits(providers_fallback: Callable, model: Any, **kwargs: Any) -> None:

    def _run_with_api_limits(self: Any, **kwargs: Any) -> Any:
        try:
            return self.invoke(**kwargs)
        except google.api_core.exceptions.ResourceExhausted as e:

            return providers_fallback("gemini", model, kwargs)

    setattr(model, "invoke", _run_with_api_limits)


if __name__ == "__main__":

    def update_rate_limits(model_kwargs: Optional[Dict[str, Any]] = None) -> None:
        from dotenv import load_dotenv

        load_dotenv()
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name=MODELS_LIST["chat"]["best_models"][0])

        response = model.generate_content(
            contents=f"""Please update the information I use about gemini's list of models and add some newer models or missing models in my lists

        {MODELS_LIST=}

        {MODELS_INFO=}""",
        )

        print(response)

    update_rate_limits()
