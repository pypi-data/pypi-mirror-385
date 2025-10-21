"""LLM Tools for ReAct Agent.

This module provides LLM instances wrapped as tools that can be used by ReAct agents
to invoke specific models based on purpose (e.g., long-context, fast, accurate).
"""

import logging
from typing import Any, Dict, List

from langchain_core.tools import Tool

from coffee_maker.langfuse_observe.auto_picker_llm_refactored import (
    AutoPickerLLMRefactored,
    create_auto_picker_llm_refactored,
)
from coffee_maker.langfuse_observe.rate_limiter import RateLimitTracker

logger = logging.getLogger(__name__)

# Model configurations: purpose -> provider -> (provider, primary, fallback, description)
MODEL_PURPOSES = {
    "long_context": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "Very long context (128K tokens)"),
        "gemini": ("gemini", "gemini-2.5-pro", "gemini-2.5-flash", "Very long context (2M tokens)"),
    },
    "reasoning": {
        "openai": ("openai", "o1", "o1-mini", "Advanced reasoning with chain-of-thought"),
        "gemini": ("gemini", "gemini-2.0-flash-thinking-exp", "gemini-2.5-flash", "Extended thinking"),
    },
    "best_model": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "Best overall quality and performance"),
        "gemini": ("gemini", "gemini-2.5-pro", "gemini-2.5-flash", "Best overall quality and performance"),
    },
    "second_best_model": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Good quality, better cost"),
        "gemini": ("gemini", "gemini-2.5-flash", "gemini-2.5-flash-lite", "Good quality, better cost"),
    },
    "fast": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Fastest for quick tasks"),
        "gemini": ("gemini", "gemini-2.5-flash-lite", "gemini-2.5-flash", "Fastest for quick tasks"),
    },
    "accurate": {
        "openai": ("openai", "gpt-4o", "gpt-4o-mini", "Most accurate"),
        "gemini": ("gemini", "gemini-2.5-pro", "gemini-2.5-flash", "Most accurate"),
    },
    "budget": {
        "openai": ("openai", "gpt-4o-mini", "gpt-3.5-turbo", "Most cost-effective"),
        "gemini": ("gemini", "gemini-2.5-flash-lite", "gemini-2.5-flash", "Most cost-effective"),
    },
}


def create_llm_tool_wrapper(
    purpose: str,
    provider: str,
    rate_tracker: RateLimitTracker,
    tier: str = "tier1",
    auto_wait: bool = True,
    max_wait_seconds: float = 10.0,
) -> AutoPickerLLMRefactored:
    """Create an AutoPickerLLMRefactored configured for a specific purpose and provider.

    Args:
        purpose: Purpose of the LLM (e.g., 'long_context', 'fast', 'accurate')
        provider: Provider to use ('openai' or 'gemini')
        rate_tracker: Shared rate limit tracker instance (kept for backward compatibility)
        tier: API tier for rate limiting
        auto_wait: Whether to auto-wait when rate limited (kept for backward compatibility)
        max_wait_seconds: Max seconds to wait before fallback

    Returns:
        Configured AutoPickerLLMRefactored instance

    Raises:
        ValueError: If purpose or provider is invalid
    """
    if purpose not in MODEL_PURPOSES:
        raise ValueError(f"Invalid purpose '{purpose}'. Valid purposes: {list(MODEL_PURPOSES.keys())}")

    if provider not in MODEL_PURPOSES[purpose]:
        available = list(MODEL_PURPOSES[purpose].keys())
        raise ValueError(f"Invalid provider '{provider}' for purpose '{purpose}'. Available: {available}")

    provider_name, primary_model, fallback_model, description = MODEL_PURPOSES[purpose][provider]

    logger.info(f"Creating LLM tool: {purpose} ({provider}) - {description}")
    logger.info(f"  Primary: {primary_model}, Fallback: {fallback_model}")

    # Use the new refactored version
    auto_picker = create_auto_picker_llm_refactored(
        primary_provider=provider_name,
        primary_model=primary_model,
        fallback_configs=[(provider_name, fallback_model)],
        tier=tier,
        max_wait_seconds=max_wait_seconds,
    )

    return auto_picker


def invoke_llm_tool(
    provider: str,
    purpose: str,
    task_description: str,
    rate_tracker: RateLimitTracker,
    tier: str = "tier1",
) -> str:
    """Invoke an LLM tool with specific provider and purpose.

    This is the function that gets wrapped as a LangChain tool.

    Args:
        provider: Provider to use ('openai' or 'gemini')
        purpose: Purpose/use case ('long_context', 'fast', 'accurate', 'budget', 'second_best_model')
        task_description: The task/prompt to send to the LLM
        rate_tracker: Rate limit tracker instance
        tier: API tier

    Returns:
        LLM response as string
    """
    logger.info(f"Invoking LLM tool: provider={provider}, purpose={purpose}")

    try:
        llm = create_llm_tool_wrapper(
            purpose=purpose,
            provider=provider,
            rate_tracker=rate_tracker,
            tier=tier,
        )

        response = llm.invoke({"input": task_description})

        # Extract content from response
        if hasattr(response, "content"):
            return response.content
        return str(response)

    except Exception as e:
        logger.error(f"LLM tool invocation failed: {e}", exc_info=True)
        return f"Error invoking LLM: {str(e)}"


def get_model_characteristics(
    provider_name: str, primary_model: str, fallback_model: str, rate_tracker: RateLimitTracker
) -> str:
    """Get detailed characteristics of a model including rate limits, context, and cost.

    Args:
        provider_name: Provider name (e.g., "openai", "gemini")
        primary_model: Primary model name
        fallback_model: Fallback model name
        rate_tracker: Rate tracker instance

    Returns:
        Formatted string with model characteristics
    """
    from coffee_maker.langfuse_observe.llm_config import MODEL_CONFIGS, get_model_context_length_from_name

    primary_full_name = f"{provider_name}/{primary_model}"
    fallback_full_name = f"{provider_name}/{fallback_model}"

    # Get context lengths
    primary_context = get_model_context_length_from_name(primary_full_name)
    fallback_context = get_model_context_length_from_name(fallback_full_name)

    # Get rate limits
    primary_limits = rate_tracker.model_limits.get(primary_full_name)
    fallback_limits = rate_tracker.model_limits.get(fallback_full_name)

    # Get current usage
    primary_stats = rate_tracker.get_usage_stats(primary_full_name) if primary_limits else {}
    fallback_stats = rate_tracker.get_usage_stats(fallback_full_name) if fallback_limits else {}

    # Get pricing info
    primary_pricing = MODEL_CONFIGS.get(provider_name, {}).get(primary_model, {}).get("pricing", {})
    fallback_pricing = MODEL_CONFIGS.get(provider_name, {}).get(fallback_model, {}).get("pricing", {})

    # Format characteristics
    chars = []

    # Primary model info
    chars.append(f"\nPRIMARY MODEL: {primary_model}")
    chars.append(f"  Context Window: {primary_context:,} tokens")

    if primary_pricing:
        input_cost = primary_pricing.get("input_per_1m", 0)
        output_cost = primary_pricing.get("output_per_1m", 0)
        if input_cost > 0 or output_cost > 0:
            chars.append(f"  Cost: ${input_cost:.2f}/1M input tokens, ${output_cost:.2f}/1M output tokens")
        else:
            chars.append(f"  Cost: FREE")

    if primary_limits:
        chars.append(f"  Rate Limits:")
        chars.append(f"    - {primary_limits.requests_per_minute} requests/minute")
        chars.append(f"    - {primary_limits.tokens_per_minute:,} tokens/minute")
        if primary_limits.requests_per_day:
            chars.append(f"    - {primary_limits.requests_per_day:,} requests/day")

    if primary_stats:
        rpm_usage = primary_stats.get("requests_per_minute", {}).get("usage_percent", 0)
        tpm_usage = primary_stats.get("tokens_per_minute", {}).get("usage_percent", 0)
        chars.append(f"  Current Usage:")
        chars.append(f"    - Requests: {rpm_usage:.1f}% of limit")
        chars.append(f"    - Tokens: {tpm_usage:.1f}% of limit")

        # Availability status
        if rpm_usage >= 100 or tpm_usage >= 100:
            chars.append(f"  ⚠️  STATUS: RATE LIMITED (will auto-wait or fallback)")
        elif rpm_usage >= 80 or tpm_usage >= 80:
            chars.append(f"  ⚠️  STATUS: NEAR LIMIT ({max(rpm_usage, tpm_usage):.0f}% used)")
        else:
            chars.append(f"  ✓ STATUS: AVAILABLE")

    # Fallback model info
    chars.append(f"\nFALLBACK MODEL: {fallback_model}")
    chars.append(f"  Context Window: {fallback_context:,} tokens")

    if fallback_pricing:
        input_cost = fallback_pricing.get("input_per_1m", 0)
        output_cost = fallback_pricing.get("output_per_1m", 0)
        if input_cost > 0 or output_cost > 0:
            chars.append(f"  Cost: ${input_cost:.2f}/1M input tokens, ${output_cost:.2f}/1M output tokens")
        else:
            chars.append(f"  Cost: FREE")

    if fallback_limits:
        chars.append(f"  Rate Limits:")
        chars.append(f"    - {fallback_limits.requests_per_minute} requests/minute")
        chars.append(f"    - {fallback_limits.tokens_per_minute:,} tokens/minute")

    if fallback_stats:
        rpm_usage = fallback_stats.get("requests_per_minute", {}).get("usage_percent", 0)
        tpm_usage = fallback_stats.get("tokens_per_minute", {}).get("usage_percent", 0)
        chars.append(f"  Current Usage:")
        chars.append(f"    - Requests: {rpm_usage:.1f}% of limit")
        chars.append(f"    - Tokens: {tpm_usage:.1f}% of limit")

    return "\n".join(chars)


def create_llm_tools(tier: str = "tier1") -> List[Tool]:
    """Create all LLM tools for the ReAct agent.

    Args:
        tier: API tier for rate limiting

    Returns:
        List of LangChain Tool instances
    """
    # Use global rate tracker to ensure rate limits are shared across all LLM instances
    from coffee_maker.langfuse_observe.global_rate_tracker import get_global_rate_tracker

    rate_tracker = get_global_rate_tracker(tier)

    tools = []

    # Create a tool for each purpose
    for purpose, providers_config in MODEL_PURPOSES.items():
        for provider in providers_config.keys():
            provider_name, primary_model, fallback_model, description = providers_config[provider]

            # Get detailed model characteristics
            characteristics = get_model_characteristics(provider_name, primary_model, fallback_model, rate_tracker)

            tool_name = f"invoke_llm_{provider}_{purpose}"
            tool_description = f"""Invoke {provider} LLM for {purpose} tasks. {description}

{characteristics}

BEHAVIOR:
- System will automatically wait (with exponential backoff) if rate limited
- Minimum 90 seconds must pass since last call before fallback to alternative model
- Falls back only if wait exceeds 5 minutes OR unexpected errors occur
- All costs and usage are tracked in Langfuse

Input format (JSON):
{{
    "task_description": "The task or prompt to send to the LLM"
}}

Use this tool when you need to:
- {purpose.replace('_', ' ').title()}: {description}
- Provider preference: {provider}

Example:
{{"task_description": "Analyze this code and suggest improvements: <code here>"}}
"""

            def make_tool_func(p=provider, pur=purpose):
                def tool_func(task_description: str) -> str:
                    """Invoke LLM with specific provider and purpose."""
                    return invoke_llm_tool(
                        provider=p,
                        purpose=pur,
                        task_description=task_description,
                        rate_tracker=rate_tracker,
                        tier=tier,
                    )

                return tool_func

            tool = Tool(
                name=tool_name,
                func=make_tool_func(),
                description=tool_description,
            )

            tools.append(tool)
            logger.info(f"Created LLM tool: {tool_name}")

    # Add the availability checker tool
    availability_tool = Tool(
        name="check_llm_availability",
        func=lambda: check_llm_availability(tier),
        description="""Check current availability, rate limits, and characteristics of all LLM models.

This tool provides real-time information about:
- Current rate limit usage (requests/minute, tokens/minute)
- Model availability status (AVAILABLE, NEAR LIMIT, RATE LIMITED)
- Context window sizes for each model
- Cost per token for each model
- Time since last LLM call (affects 90s fallback rule)

Use this tool to:
- Decide which LLM tool to use based on current availability
- Avoid triggering rate limit waits by choosing available models
- Select appropriate model based on input size vs context window
- Optimize costs by choosing cheaper models when appropriate

Returns comprehensive status report for all available LLM models.
""",
    )
    tools.append(availability_tool)
    logger.info("Created check_llm_availability tool")

    logger.info(f"Created {len(tools)} LLM tools total")
    return tools


def check_llm_availability(tier: str = "tier1") -> str:
    """Check availability and current status of all LLM models.

    This tool allows agents to query the current rate limit status,
    availability, and characteristics of all LLM models before deciding
    which one to use.

    Args:
        tier: API tier

    Returns:
        Formatted string with availability information for all models
    """
    from coffee_maker.langfuse_observe.global_rate_tracker import get_global_rate_tracker
    from coffee_maker.langfuse_observe.llm_config import MODEL_CONFIGS, get_model_context_length_from_name

    rate_tracker = get_global_rate_tracker(tier)

    result = ["=" * 80]
    result.append("LLM MODEL AVAILABILITY AND STATUS")
    result.append("=" * 80)

    # Get last global call time
    last_call = rate_tracker.get_last_call_time()
    if last_call:
        import time

        seconds_since = time.time() - last_call
        result.append(f"\n⏱️  Last LLM call: {seconds_since:.1f} seconds ago")
        if seconds_since < 90:
            remaining = 90 - seconds_since
            result.append(f"⚠️  Must wait {remaining:.1f}s more before fallback allowed (90s minimum)")
        else:
            result.append("✓ Sufficient time passed for fallback if needed")
    else:
        result.append("\n⏱️  No LLM calls made yet in this session")

    result.append("")

    # Group models by purpose
    for purpose, providers_config in MODEL_PURPOSES.items():
        result.append(f"\n{'=' * 80}")
        result.append(f"PURPOSE: {purpose.upper().replace('_', ' ')}")
        result.append(f"{'=' * 80}")

        for provider, (prov_name, primary, fallback, desc) in providers_config.items():
            result.append(f"\n[{provider.upper()}] {desc}")

            primary_full = f"{prov_name}/{primary}"
            fallback_full = f"{prov_name}/{fallback}"

            # Primary model
            result.append(f"\n  PRIMARY: {primary}")
            primary_context = get_model_context_length_from_name(primary_full)
            result.append(f"    Context: {primary_context:,} tokens")

            primary_pricing = MODEL_CONFIGS.get(prov_name, {}).get(primary, {}).get("pricing", {})
            if primary_pricing:
                in_cost = primary_pricing.get("input_per_1m", 0)
                out_cost = primary_pricing.get("output_per_1m", 0)
                if in_cost > 0 or out_cost > 0:
                    result.append(f"    Cost: ${in_cost:.2f}/${out_cost:.2f} per 1M tokens (in/out)")
                else:
                    result.append(f"    Cost: FREE")

            primary_stats = rate_tracker.get_usage_stats(primary_full)
            if primary_stats:
                rpm = primary_stats.get("requests_per_minute", {})
                tpm = primary_stats.get("tokens_per_minute", {})
                rpm_pct = rpm.get("usage_percent", 0)
                tpm_pct = tpm.get("usage_percent", 0)

                result.append(
                    f"    Usage: {rpm['current']}/{rpm['limit']} req/min ({rpm_pct:.0f}%), "
                    f"{tpm['current']:,}/{tpm['limit']:,} tok/min ({tpm_pct:.0f}%)"
                )

                if rpm_pct >= 100 or tpm_pct >= 100:
                    result.append("    ⚠️  RATE LIMITED - will wait or use fallback")
                elif rpm_pct >= 80 or tpm_pct >= 80:
                    result.append(f"    ⚠️  NEAR LIMIT - {max(rpm_pct, tpm_pct):.0f}% used")
                else:
                    result.append("    ✓ AVAILABLE")

            # Fallback model
            result.append(f"\n  FALLBACK: {fallback}")
            fallback_context = get_model_context_length_from_name(fallback_full)
            result.append(f"    Context: {fallback_context:,} tokens")

            fallback_pricing = MODEL_CONFIGS.get(prov_name, {}).get(fallback, {}).get("pricing", {})
            if fallback_pricing:
                in_cost = fallback_pricing.get("input_per_1m", 0)
                out_cost = fallback_pricing.get("output_per_1m", 0)
                if in_cost > 0 or out_cost > 0:
                    result.append(f"    Cost: ${in_cost:.2f}/${out_cost:.2f} per 1M tokens (in/out)")
                else:
                    result.append(f"    Cost: FREE")

            fallback_stats = rate_tracker.get_usage_stats(fallback_full)
            if fallback_stats:
                rpm = fallback_stats.get("requests_per_minute", {})
                tpm = fallback_stats.get("tokens_per_minute", {})
                rpm_pct = rpm.get("usage_percent", 0)
                tpm_pct = tpm.get("usage_percent", 0)

                result.append(
                    f"    Usage: {rpm['current']}/{rpm['limit']} req/min ({rpm_pct:.0f}%), "
                    f"{tpm['current']:,}/{tpm['limit']:,} tok/min ({tpm_pct:.0f}%)"
                )

                if rpm_pct >= 100 or tpm_pct >= 100:
                    result.append("    ⚠️  RATE LIMITED")
                elif rpm_pct >= 80 or tpm_pct >= 80:
                    result.append(f"    ⚠️  NEAR LIMIT - {max(rpm_pct, tpm_pct):.0f}% used")
                else:
                    result.append("    ✓ AVAILABLE")

    result.append(f"\n{'=' * 80}")
    result.append("RECOMMENDATION:")
    result.append("- Use models with ✓ AVAILABLE status for immediate execution")
    result.append("- Models at ⚠️ NEAR LIMIT may trigger waits")
    result.append("- Models ⚠️ RATE LIMITED will wait (exponential backoff) or fallback")
    result.append("- Choose larger context models for inputs > 128K tokens")
    result.append(f"{'=' * 80}")

    return "\n".join(result)


def get_llm_tool_names() -> List[str]:
    """Get list of all LLM tool names.

    Returns:
        List of tool names
    """
    names = ["check_llm_availability"]  # Add the availability checker tool
    for purpose in MODEL_PURPOSES.keys():
        for provider in MODEL_PURPOSES[purpose].keys():
            names.append(f"invoke_llm_{provider}_{purpose}")
    return names


def get_llm_tools_summary() -> Dict[str, Any]:
    """Get summary of available LLM tools.

    Returns:
        Dictionary with tools organized by purpose and provider
    """
    summary: Dict[str, Any] = {}
    for purpose, providers_config in MODEL_PURPOSES.items():
        summary[purpose] = {}
        for provider, (prov_name, primary, fallback, desc) in providers_config.items():
            summary[purpose][provider] = {
                "primary_model": f"{prov_name}/{primary}",
                "fallback_model": f"{prov_name}/{fallback}",
                "description": desc,
                "tool_name": f"invoke_llm_{provider}_{purpose}",
            }
    return summary
