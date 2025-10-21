"""Helpers for wiring LangChain chat models with Langfuse instrumentation."""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Optional, Tuple

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langfuse import observe
from pydantic import ConfigDict

from coffee_maker.config import ConfigManager
from coffee_maker.langfuse_observe.llm import get_llm

logger = logging.getLogger(__name__)


def instrument_llm(llm_instance: Any, *, methods: Iterable[str] = ("invoke", "ainvoke")) -> Any:
    """Instrument LLM instance methods with Langfuse observability.

    Wraps specified LLM methods with Langfuse's observe decorator for tracing.
    Avoids double-instrumentation by tracking which methods have been wrapped.

    Args:
        llm_instance: LLM instance to instrument (e.g., ChatAnthropic, ChatOpenAI)
        methods: Method names to instrument (default: invoke and ainvoke)

    Returns:
        The same LLM instance with instrumented methods

    Example:
        >>> from langchain_anthropic import ChatAnthropic
        >>> llm = ChatAnthropic(model="claude-3-sonnet")
        >>> instrumented = instrument_llm(llm)
        >>> # Now llm.invoke() calls will be traced in Langfuse
    """
    if getattr(llm_instance, "_langfuse_instrumented", False):
        return llm_instance

    cls = llm_instance.__class__
    already_instrumented = set(getattr(cls, "_langfuse_instrumented_methods", set()))

    for method_name in methods:
        if method_name in already_instrumented:
            continue

        func = getattr(cls, method_name, None)
        if func is None or not callable(func):
            continue

        wrapped = observe(as_type="generation")(func)
        setattr(cls, method_name, wrapped)
        already_instrumented.add(method_name)

    setattr(cls, "_langfuse_instrumented_methods", already_instrumented)
    setattr(llm_instance, "_langfuse_instrumented", True)
    return llm_instance


def resolve_gemini_api_key() -> str:
    """Resolve Gemini API key from multiple possible environment variables.

    Uses ConfigManager to check for API key in multiple environment variable names
    and ensures GEMINI_API_KEY is set for consistent access. Supports three variable names:
    - GEMINI_API_KEY (primary)
    - GOOGLE_API_KEY (alternative)
    - COFFEE_MAKER_GEMINI_API_KEY (project-specific)

    Returns:
        The resolved API key string

    Raises:
        APIKeyMissingError: If no API key found in any of the checked environment variables

    Example:
        >>> import os
        >>> os.environ["GOOGLE_API_KEY"] = "my-key"
        >>> key = resolve_gemini_api_key()
        >>> # ConfigManager normalizes to GEMINI_API_KEY
    """
    return ConfigManager.get_gemini_api_key()


def _build_stub_llm(provider: str, model: Optional[str], error: Exception) -> Any:
    message = f"Stubbed response: failed to initialise provider '{provider}' with model '{model}'. " f"Details: {error}"

    class _StubChatModel(BaseChatModel):
        """Stub chat model for testing when real LLM is unavailable."""

        description: str
        model_name: str = model or "stub"

        model_config = ConfigDict(arbitrary_types_allowed=True)

        def _generate(
            self,
            messages: list[BaseMessage],
            stop: Optional[list[str]] = None,
            run_manager: Optional[Any] = None,
            **kwargs: Any,
        ) -> ChatResult:
            """Generate stub response."""
            msg = AIMessage(content=self.description)
            generation = ChatGeneration(message=msg)
            return ChatResult(generations=[generation])

        @property
        def _llm_type(self) -> str:
            """Return type of chat model."""
            return "stub"

    return _StubChatModel(description=message)


def _build_llm(provider: Optional[str] = None, model=None, **kwargs: Any):
    """Build LLM instance from provider and model specification.

    Args:
        provider: LLM provider name (e.g., 'anthropic', 'openai', 'gemini')
        model: Model name, or None to use default for provider
        **kwargs: Additional arguments to pass to LLM constructor

    Returns:
        Configured LLM instance
    """
    return get_llm(provider=provider, model=model, **kwargs)


def configure_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    *,
    strict: bool = True,
    default_models: Optional[Mapping[str, Optional[str]]] = None,
    methods: Iterable[str] = ("invoke", "ainvoke"),
    **kwargs: Any,
) -> Tuple[Any, str, Optional[str]]:
    """Configure and instrument an LLM instance with Langfuse observability.

    Creates an LLM instance for the specified provider and model, then instruments
    it with Langfuse tracing. Falls back to a stub LLM if initialization fails
    and strict=False.

    Args:
        provider: LLM provider name (e.g., 'anthropic', 'openai', 'gemini')
        model: Model name, or None to use provider default
        strict: If True, raise exceptions on initialization errors. If False, return stub LLM.
        default_models: Mapping of provider names to default model names (unused in current implementation)
        methods: LLM methods to instrument with Langfuse (default: invoke and ainvoke)
        **kwargs: Additional arguments passed to LLM constructor

    Returns:
        Tuple of (instrumented_llm, provider_name, model_name)

    Raises:
        Exception: If LLM initialization fails and strict=True

    Example:
        >>> llm, provider, model = configure_llm(provider="anthropic", model="claude-3-sonnet")
        >>> # llm is now ready to use with Langfuse tracing enabled
        >>> response = llm.invoke("Hello!")
    """

    try:
        candidate_llm = _build_llm(provider, model, **kwargs)
    except Exception as exc:
        if strict:
            raise
        logger.warning(
            "Falling back to stubbed LLM for provider '%s' and model '%s': %s",
            provider,
            model,
            exc,
        )
        candidate_llm = _build_stub_llm(provider, model, exc)

    instrumented = instrument_llm(candidate_llm, methods=methods)
    return instrumented, provider, model
