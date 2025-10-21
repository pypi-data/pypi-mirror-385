"""Helpers for wiring LangChain chat models with Langfuse instrumentation.

Note: Quota exceeded errors (ResourceExhausted) are now handled in AutoPickerLLM
with automatic fallback to alternative models. See auto_picker_llm_refactored.py
and response_parser.py for implementation (Sprint 4, commit 026807d).
"""

import datetime
import logging
import os
from typing import Any, Optional

import langfuse
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

from coffee_maker.config.manager import ConfigManager
from coffee_maker.langfuse_observe.utils import get_callers_modules

load_dotenv()

logger = logging.getLogger(__name__)
SUPPORTED_PROVIDERS = dict()

# Default LLM provider (configurable via environment variable)
__DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")


try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    SUPPORTED_PROVIDERS.update(
        {"gemini": (ChatGoogleGenerativeAI, "GEMINI_API_KEY", "gemini-2.5-pro", {"max_tokens": 8192})}
    )
except ImportError:
    logger.warning("langchain_google_genai not installed. will not use google")
except Exception as e:
    logger.error(f"Unexpected error loading langchain_google_genai: {e}", exc_info=True)

try:
    from langchain_openai import ChatOpenAI

    #   Valid models for OpenAI class: gpt-3.5-turbo-instruct, davinci-002, babbage-002
    #
    #   Valid models for ChatOpenAI class: gpt-4, gpt-4-turbo, gpt-3.5-turbo, and their variants
    # Use gpt-4o-mini for better performance and larger context (128k tokens)
    SUPPORTED_PROVIDERS.update({"openai": (ChatOpenAI, "OPENAI_API_KEY", "gpt-4.1", {})})

    # from langchain_core.prompts import PromptTemplate
    #
    # prompt = PromptTemplate.from_template("How to say {input} in {output_language}:\n")
    #
    # chain = prompt | ChatOpenAI()
    # chain.invoke(
    #     {
    #         "output_language": "German",
    #         "input": "I love programming.",
    #     }
    # )
except ImportError:
    logger.warning("langchain_openai not installed. will not use openai")
except Exception as e:
    logger.error(f"Unexpected error loading langchain_openai: {e}", exc_info=True)
try:
    from langchain_anthropic import ChatAnthropic

    SUPPORTED_PROVIDERS.update(
        {"anthropic": (ChatAnthropic, "ANTHROPIC_API_KEY", "claude-opus-4-20250514", {"max_tokens": 8192})}
    )

    # from langchain_core.prompts import PromptTemplate
    #
    # prompt = PromptTemplate.from_template("How to say {input} in {output_language}:\n")
    # chat_anthropic = ChatAnthropic()
    #
    # chain = prompt | chat_anthropic
    # chain.invoke(
    #     {
    #         "output_language": "German",
    #         "input": "I love programming.",
    #     }
    # )

except ImportError:
    logger.warning("langchain_anthropic not installed. will not use anthropic")
except Exception as e:
    logger.error(f"Unexpected error loading langchain_anthropic: {e}", exc_info=True)


default_provider = (
    __DEFAULT_PROVIDER if __DEFAULT_PROVIDER in SUPPORTED_PROVIDERS.keys() else list(SUPPORTED_PROVIDERS.keys())[0]
)
logger.info(f"{default_provider=}")


def get_llm(
    langfuse_client: Optional[langfuse.Langfuse] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **llm_kwargs: Any,
) -> BaseChatModel:
    """Get a basic LLM instance without scheduling.

    Args:
        langfuse_client: Langfuse client for tracing
        provider: LLM provider (openai, gemini, anthropic)
        model: Model name
        **llm_kwargs: Additional LLM configuration

    Returns:
        Basic LLM instance (ChatOpenAI, ChatGoogleGenerativeAI, etc.)
    """
    if provider is None:
        provider = default_provider
        assert model is None, f"Please input a provider when you specify a specific model: {model}"
    if model is None:
        Llm, api_key, model, llm_kwargs_default = SUPPORTED_PROVIDERS[provider]
    else:
        Llm, api_key, _, llm_kwargs_default = SUPPORTED_PROVIDERS[provider]
    if langfuse_client is None:
        langfuse_client = langfuse.get_client()

    # Merge default kwargs with provided kwargs
    final_kwargs = llm_kwargs_default.copy()
    if llm_kwargs:
        final_kwargs.update(llm_kwargs)

    # Ensure model is in the kwargs
    final_kwargs["model"] = model

    if provider in SUPPORTED_PROVIDERS.keys():
        # Check if API key is configured using ConfigManager
        has_key = False
        if provider == "openai":
            has_key = ConfigManager.has_openai_api_key()
        elif provider == "gemini":
            has_key = ConfigManager.has_gemini_api_key()
        elif provider == "anthropic":
            has_key = ConfigManager.has_anthropic_api_key()

        if not has_key:
            logger.warning(
                f"ENVIRONMENT VARIABLE {api_key} not set, you asked {provider} with model {model} but it may not work"
            )
        logger.info(f"Instantiating LLM: {provider} {model} with kwargs: {final_kwargs}")
        llm = Llm(**final_kwargs)
        langfuse_client.update_current_trace(
            metadata={
                f"llm_config_{provider}_{model}_{datetime.datetime.now().isoformat()}": dict(
                    caller="/n".join(get_callers_modules()), provider=provider, **final_kwargs
                )
            }
        )
        return llm
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_scheduled_llm(
    langfuse_client: Optional[langfuse.Langfuse] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    tier: str = "tier1",
    max_wait_seconds: float = 300.0,
    **llm_kwargs,
):
    """Get an LLM instance with proactive rate limiting scheduling.

    This function wraps the base LLM with ScheduledLLM/ScheduledChatModel to add:
    - N-2 safety margin (never reaches N-1 of rate limits)
    - 60/RPM spacing between requests
    - Intelligent waiting based on actual usage

    Args:
        langfuse_client: Langfuse client for tracing
        provider: LLM provider (openai, gemini, anthropic)
        model: Model name
        tier: API tier for rate limiting (default: tier1)
        max_wait_seconds: Maximum wait time before raising error (default: 300s)
        **llm_kwargs: Additional LLM configuration

    Returns:
        ScheduledLLM or ScheduledChatModel instance with proactive rate limiting

    Example:
        >>> llm = get_scheduled_llm(provider="openai", model="gpt-4o-mini", tier="tier1")
        >>> response = llm.invoke("Hello")  # Automatically scheduled
    """
    from coffee_maker.langfuse_observe.global_rate_tracker import get_global_rate_tracker
    from coffee_maker.langfuse_observe.scheduled_llm import ScheduledLLM, ScheduledChatModel
    from coffee_maker.langfuse_observe.strategies.scheduling import ProactiveRateLimitScheduler
    from langchain_core.language_models import BaseChatModel

    # Get base LLM first
    llm = get_llm(langfuse_client=langfuse_client, provider=provider, model=model, **llm_kwargs)

    # Determine provider and model if not specified
    if provider is None:
        provider = default_provider
    if model is None:
        _, _, model, _ = SUPPORTED_PROVIDERS[provider]

    # Get global rate tracker for this tier
    rate_tracker = get_global_rate_tracker(tier)
    model_full_name = f"{provider}/{model}"

    # Check if model is in rate tracker
    if model_full_name not in rate_tracker.model_limits:
        logger.warning(
            f"Model {model_full_name} not in rate tracker for tier {tier}. " f"Returning base LLM without scheduling."
        )
        return llm

    # Create scheduling strategy
    scheduler = ProactiveRateLimitScheduler(
        rate_tracker=rate_tracker,
        safety_margin=2,  # Stay at N-2 of limits
    )

    # Wrap with appropriate scheduled wrapper
    if isinstance(llm, BaseChatModel):
        logger.info(f"Wrapping {model_full_name} with ScheduledChatModel (proactive rate limiting)")
        scheduled_llm = ScheduledChatModel(
            llm=llm,
            model_name=model_full_name,
            scheduling_strategy=scheduler,
            max_wait_seconds=max_wait_seconds,
        )
    else:
        logger.info(f"Wrapping {model_full_name} with ScheduledLLM (proactive rate limiting)")
        scheduled_llm = ScheduledLLM(
            llm=llm,
            model_name=model_full_name,
            scheduling_strategy=scheduler,
            max_wait_seconds=max_wait_seconds,
        )

    return scheduled_llm
