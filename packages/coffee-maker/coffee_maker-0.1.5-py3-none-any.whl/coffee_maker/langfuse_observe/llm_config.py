"""Centralized configuration for LLM models and their rate limits.

This module consolidates rate limit information from provider files
and provides a single source of truth for model configurations.
"""

from typing import Any, Dict, List, Optional, Tuple

from coffee_maker.langfuse_observe.rate_limiter import RateLimitConfig
from coffee_maker.langfuse_observe.llm_providers import gemini, openai as openai_provider


def _transform_provider_info_to_config(provider_name: str, models_info: Dict[str, Any]) -> Dict[str, Any]:
    """Transform provider MODELS_INFO format to MODEL_CONFIGS format.

    Args:
        provider_name: Name of the provider ('openai' or 'gemini')
        models_info: The provider's MODELS_INFO dictionary

    Returns:
        Dictionary of model configurations in MODEL_CONFIGS format
    """
    configs = {}

    # Get the provider-specific info
    provider_info = models_info.get(provider_name, {})
    tiers = provider_info.get("values", {})

    # Collect all unique model names across all tiers
    all_models = set()
    for tier_name, tier_models in tiers.items():
        all_models.update(tier_models.keys())

    # Build config for each model
    for model_name in all_models:
        model_config = {
            "rate_limits": {},
            "pricing": {},
            "use_cases": _infer_use_cases(model_name),
        }

        # Collect rate limits and pricing from all tiers
        for tier_name, tier_models in tiers.items():
            if model_name in tier_models:
                model_info = tier_models[model_name]

                # Add context length and max output tokens (should be same across tiers)
                if "context_length" in model_info:
                    model_config["context_length"] = model_info["context_length"]
                if "max_output_tokens" in model_info:
                    model_config["max_output_tokens"] = model_info["max_output_tokens"]

                # Add rate limits for this tier
                rpm = model_info.get("requests per minute", -1)
                tpm = model_info.get("tokens per minute", -1)
                rpd = model_info.get("requests per day", -1)

                model_config["rate_limits"][tier_name] = RateLimitConfig(
                    requests_per_minute=rpm, tokens_per_minute=tpm, requests_per_day=rpd
                )

                # Add pricing info
                price_info = model_info.get("price", {})
                if price_info:
                    # Handle simple pricing (OpenAI style)
                    if "per 1M tokens input" in price_info and "per 1M tokens output" in price_info:
                        if tier_name in ["tier1", "tier2", "paid"]:  # Use paid tier pricing
                            model_config["pricing"]["input_per_1m"] = price_info["per 1M tokens input"]
                            model_config["pricing"]["output_per_1m"] = price_info["per 1M tokens output"]
                        elif tier_name == "free":
                            # Mark as free if it's zero
                            if price_info["per 1M tokens input"] == 0:
                                model_config["pricing"]["free"] = True
                            model_config["pricing"]["input_per_1m"] = price_info["per 1M tokens input"]
                            model_config["pricing"]["output_per_1m"] = price_info["per 1M tokens output"]

                    # Handle tiered pricing (Gemini 2.5 Pro style)
                    if "per 1M tokens input (<=200k)" in price_info:
                        model_config["pricing"]["input_per_1m_low"] = price_info["per 1M tokens input (<=200k)"]
                        model_config["pricing"]["output_per_1m_low"] = price_info["per 1M tokens output (<=200k)"]
                    if "per 1M tokens input (>200k)" in price_info:
                        model_config["pricing"]["input_per_1m_high"] = price_info["per 1M tokens input (>200k)"]
                        model_config["pricing"]["output_per_1m_high"] = price_info["per 1M tokens output (>200k)"]

        configs[model_name] = model_config

    return configs


def _infer_use_cases(model_name: str) -> List[str]:
    """Infer use cases based on model name.

    Args:
        model_name: Name of the model

    Returns:
        List of use case strings
    """
    use_cases = []
    model_lower = model_name.lower()

    # Large context models
    if "2.5-pro" in model_lower or "1.5-pro" in model_lower or "4.1" in model_lower:
        use_cases.append("large_context")

    # Primary/best models
    if "2.5-pro" in model_lower or "4o" == model_lower.split("-")[-1]:
        use_cases.append("primary")

    # Reasoning models
    if "o1" in model_lower or "thinking" in model_lower:
        use_cases.append("reasoning")
        use_cases.append("planning")
        if "mini" in model_lower:
            use_cases.append("budget_reasoning")
        else:
            use_cases.append("complex_problem_solving")

    # General purpose models
    if "flash" in model_lower or "mini" in model_lower or "3.5" in model_lower:
        use_cases.append("general")

    # Budget/fallback models
    if "lite" in model_lower or "mini" in model_lower or "3.5" in model_lower or "flash" in model_lower:
        use_cases.append("fallback")
        use_cases.append("budget")

    # Code review
    if "4o" in model_lower or "pro" in model_lower:
        use_cases.append("code_review")

    # If no use cases matched, add simple
    if not use_cases:
        use_cases.append("simple")

    return use_cases


# Build MODEL_CONFIGS from provider files
MODEL_CONFIGS = {
    "openai": _transform_provider_info_to_config("openai", openai_provider.MODELS_INFO),
    "gemini": _transform_provider_info_to_config("gemini", gemini.MODELS_ÌNFO),
}


def get_rate_limits_for_tier(tier: str = "tier1") -> Dict[str, RateLimitConfig]:
    """Get rate limit configurations for all models at a specific tier.

    Args:
        tier: API tier (e.g., 'free', 'tier1', 'tier2', 'paid')

    Returns:
        Dictionary mapping model names to RateLimitConfig objects
    """
    rate_limits = {}

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            if tier in config["rate_limits"]:
                full_model_name = f"{provider}/{model_name}"
                rate_limits[full_model_name] = config["rate_limits"][tier]

    return rate_limits


def get_model_context_length(provider: str, model: str) -> int:
    """Get the context length for a specific model.

    Args:
        provider: Provider name (e.g., 'openai', 'gemini')
        model: Model name

    Returns:
        Context length in tokens
    """
    if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
        return MODEL_CONFIGS[provider][model]["context_length"]
    return 4096  # Default fallback


def get_fallback_models(use_case: Optional[str] = None) -> List[Tuple[str, str]]:
    """Get a list of models suitable for fallback, ordered by preference.

    Args:
        use_case: Optional use case to filter by (e.g., 'large_context', 'budget')

    Returns:
        List of (provider, model_name) tuples ordered by preference
    """
    fallback_models = []

    # Priority order for fallbacks
    priority_order = [
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-2.5-flash"),
        ("gemini", "gemini-2.5-flash-lite"),
        ("gemini", "gemini-1.5-flash"),
        ("openai", "gpt-3.5-turbo"),
    ]

    for provider, model_name in priority_order:
        if provider in MODEL_CONFIGS and model_name in MODEL_CONFIGS[provider]:
            config = MODEL_CONFIGS[provider][model_name]
            if use_case is None or use_case in config["use_cases"]:
                fallback_models.append((provider, model_name))

    return fallback_models


def get_large_context_model() -> Tuple[str, str]:
    """Get the model with the largest context window.

    Returns:
        (provider, model_name) tuple
    """
    max_context = 0
    best_model = None

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            if config.get("context_length", 0) > max_context:
                max_context = config["context_length"]
                best_model = (provider, model_name)

    return best_model if best_model else ("openai", "gpt-4o-mini")


def get_large_context_models() -> List[Tuple[str, str, int]]:
    """Get all models sorted by context length (largest first).

    Returns:
        List of (provider, model_name, context_length) tuples sorted by context descending
    """
    models_with_context = []

    for provider, models in MODEL_CONFIGS.items():
        for model_name, config in models.items():
            context = config.get("context_length", 0)
            models_with_context.append((provider, model_name, context))

    # Sort by context length descending
    sorted_models = sorted(models_with_context, key=lambda x: x[2], reverse=True)

    return sorted_models


def get_model_context_length_from_name(full_model_name: str) -> int:
    """Get context length from full model name.

    Args:
        full_model_name: Format "provider/model" (e.g., "openai/gpt-4o")

    Returns:
        Context length in tokens

    Raises:
        ValueError: If model not found
    """
    if "/" not in full_model_name:
        raise ValueError(f"Invalid model name format: {full_model_name}. Expected 'provider/model'")

    provider, model = full_model_name.split("/", 1)

    if provider not in MODEL_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}")

    if model not in MODEL_CONFIGS[provider]:
        raise ValueError(f"Unknown model: {model} for provider {provider}")

    return MODEL_CONFIGS[provider][model]["context_length"]


def get_all_model_context_limits() -> Dict[str, int]:
    """Get all model context limits as a flat dictionary.

    Returns:
        Dict mapping "provider/model" to context length

    Example:
        >>> limits = get_all_model_context_limits()
        >>> limits["openai/gpt-4o-mini"]
        128000
    """
    limits = {}
    for provider, models in MODEL_CONFIGS.items():
        for model, config in models.items():
            full_name = f"{provider}/{model}"
            limits[full_name] = config["context_length"]
    return limits
