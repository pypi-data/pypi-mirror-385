"""Cost calculation and tracking for LLM API usage."""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

from langfuse import observe

from coffee_maker.utils.time import get_timestamp_threshold

logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """Record of a single cost calculation."""

    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"


class CostCalculator:
    """Calculate and track LLM API costs with pricing and history."""

    def __init__(self, pricing_info: Dict[str, Dict]):
        """Initialize with pricing info dict: model -> {input_per_1m, output_per_1m}."""
        self.pricing_info = pricing_info
        self._cost_history: List[CostRecord] = []
        self._cumulative_cost_by_model: Dict[str, float] = defaultdict(float)
        self._cumulative_cost_total: float = 0.0

    @observe(capture_input=False, capture_output=False)
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calculate cost for a request.

        Args:
            model: Full model name (e.g., "openai/gpt-4o")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Dictionary with cost breakdown:
            {
                "input_cost": float,
                "output_cost": float,
                "total_cost": float,
                "currency": "USD",
                "input_tokens": int,
                "output_tokens": int,
                "total_tokens": int
            }
        """
        # Get pricing for model
        pricing = self.pricing_info.get(model)

        if pricing is None:
            logger.warning(f"No pricing info for model {model}, cost will be $0.00")
            return {
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
                "currency": "USD",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

        # Handle free tier models
        if pricing.get("free") or pricing.get("free_tier"):
            logger.debug(f"Model {model} is free tier")
            cost_info = {
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
                "currency": "USD",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }
        else:
            # Calculate costs based on per-1M-token pricing
            input_cost = (input_tokens / 1_000_000) * pricing.get("input_per_1m", 0.0)
            output_cost = (output_tokens / 1_000_000) * pricing.get("output_per_1m", 0.0)

            cost_info = {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": input_cost + output_cost,
                "currency": "USD",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

        # Record cost
        record = CostRecord(
            timestamp=time.time(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=cost_info["input_cost"],
            output_cost=cost_info["output_cost"],
            total_cost=cost_info["total_cost"],
        )

        self._cost_history.append(record)
        self._cumulative_cost_by_model[model] += cost_info["total_cost"]
        self._cumulative_cost_total += cost_info["total_cost"]

        logger.debug(
            f"Cost calculated for {model}: "
            f"${cost_info['total_cost']:.4f} "
            f"({input_tokens} in + {output_tokens} out tokens)"
        )

        return cost_info

    @observe(capture_input=False, capture_output=False)
    def get_cumulative_cost(self, model: Optional[str] = None, timeframe: str = "all") -> float:
        """Get total spending (optionally filtered by model/timeframe).

        Args:
            model: Optional model name to filter by
            timeframe: Time period to calculate cost for:
                - "all": All time (default)
                - "day": Last 24 hours
                - "hour": Last hour
                - "minute": Last minute

        Returns:
            Total cost in USD
        """
        # Calculate time threshold using centralized utility
        threshold = get_timestamp_threshold(timeframe)

        # Filter records
        filtered_records = [
            r for r in self._cost_history if r.timestamp >= threshold and (model is None or r.model == model)
        ]

        return sum(r.total_cost for r in filtered_records)

    @observe(capture_input=False, capture_output=False)
    def get_cost_by_model(self, timeframe: str = "all") -> Dict[str, float]:
        """Get cost breakdown by model.

        Args:
            timeframe: Time period (same as get_cumulative_cost)

        Returns:
            Dictionary mapping model names to total cost
        """
        # Calculate time threshold using centralized utility
        threshold = get_timestamp_threshold(timeframe)

        # Filter records
        filtered_records = [r for r in self._cost_history if r.timestamp >= threshold]

        # Aggregate by model
        costs_by_model = defaultdict(float)
        for record in filtered_records:
            costs_by_model[record.model] += record.total_cost

        return dict(costs_by_model)

    @observe(capture_input=False, capture_output=False)
    def get_cost_stats(self, timeframe: str = "all") -> Dict:
        """Get comprehensive cost statistics.

        Args:
            timeframe: Time period to analyze

        Returns:
            Dictionary with cost statistics
        """
        total_cost = self.get_cumulative_cost(timeframe=timeframe)
        cost_by_model = self.get_cost_by_model(timeframe=timeframe)

        # Calculate time threshold using centralized utility
        threshold = get_timestamp_threshold(timeframe)

        filtered_records = [r for r in self._cost_history if r.timestamp >= threshold]

        total_requests = len(filtered_records)
        total_input_tokens = sum(r.input_tokens for r in filtered_records)
        total_output_tokens = sum(r.output_tokens for r in filtered_records)

        return {
            "total_cost_usd": total_cost,
            "cost_by_model": cost_by_model,
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "timeframe": timeframe,
        }

    def reset_history(self):
        """Reset cost history (useful for testing)."""
        self._cost_history.clear()
        self._cumulative_cost_by_model.clear()
        self._cumulative_cost_total = 0.0
        logger.info("Cost history reset")

    def get_recent_costs(self, limit: int = 10) -> List[CostRecord]:
        """Get most recent cost records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent CostRecord objects
        """
        return self._cost_history[-limit:]
