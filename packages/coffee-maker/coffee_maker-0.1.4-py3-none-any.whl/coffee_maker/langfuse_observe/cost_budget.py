"""Cost budget enforcement for LLM usage.

This module provides budget management to prevent overspending on LLM API calls.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Time period for budget enforcement."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOTAL = "total"  # Lifetime budget


class BudgetExceededError(Exception):
    """Raised when cost budget is exceeded."""

    def __init__(self, budget: float, current: float, period: BudgetPeriod):
        """Initialize error with budget details."""
        self.budget = budget
        self.current = current
        self.period = period
        message = f"Budget exceeded: ${current:.4f} / ${budget:.4f} ({period.value})"
        super().__init__(message)


@dataclass
class BudgetConfig:
    """Configuration for cost budget."""

    amount: float
    period: BudgetPeriod
    hard_limit: bool = True  # If True, raise error when exceeded
    warning_threshold: float = 0.8  # Warn at 80% of budget


class CostBudgetEnforcer:
    """Enforces cost budgets for LLM usage."""

    def __init__(self, budgets: Optional[Dict[BudgetPeriod, BudgetConfig]] = None):
        """Initialize budget enforcer.

        Args:
            budgets: Dictionary mapping budget periods to configurations

        Example:
            >>> budgets = {
            ...     BudgetPeriod.DAILY: BudgetConfig(amount=10.0, period=BudgetPeriod.DAILY),
            ...     BudgetPeriod.MONTHLY: BudgetConfig(amount=200.0, period=BudgetPeriod.MONTHLY),
            ... }
            >>> enforcer = CostBudgetEnforcer(budgets)
        """
        self.budgets = budgets or {}
        self._spending: Dict[BudgetPeriod, Dict[str, float]] = {}
        self._reset_times: Dict[BudgetPeriod, float] = {}

        # Initialize spending tracking for each budget period
        for period in self.budgets:
            self._spending[period] = {"total": 0.0}
            self._reset_times[period] = time.time()

    def record_cost(self, cost: float, model: Optional[str] = None):
        """Record a cost and check against budgets.

        Args:
            cost: Cost in USD
            model: Optional model name for per-model tracking

        Raises:
            BudgetExceededError: If hard limit exceeded

        Example:
            >>> enforcer.record_cost(0.05, model="gpt-4")
        """
        # Reset budgets if period has elapsed
        self._check_and_reset_periods()

        # Track spending for each configured budget period
        for period, config in self.budgets.items():
            if period not in self._spending:
                self._spending[period] = {"total": 0.0}

            # Add to total
            self._spending[period]["total"] += cost

            # Add to model-specific if provided
            if model:
                if model not in self._spending[period]:
                    self._spending[period][model] = 0.0
                self._spending[period][model] += cost

            # Check budget
            current_total = self._spending[period]["total"]

            # Check warning threshold
            if current_total >= config.amount * config.warning_threshold:
                if current_total < config.amount:
                    logger.warning(
                        f"Budget warning: ${current_total:.4f} / ${config.amount:.4f} "
                        f"({period.value}) - {(current_total/config.amount)*100:.1f}% used"
                    )

            # Check hard limit
            if config.hard_limit and current_total > config.amount:
                raise BudgetExceededError(config.amount, current_total, period)

    def get_remaining(self, period: BudgetPeriod) -> float:
        """Get remaining budget for a period.

        Args:
            period: Budget period to check

        Returns:
            Remaining budget in USD
        """
        if period not in self.budgets:
            return float("inf")

        self._check_and_reset_periods()

        config = self.budgets[period]
        spent = self._spending.get(period, {}).get("total", 0.0)
        return max(0.0, config.amount - spent)

    def get_spent(self, period: BudgetPeriod, model: Optional[str] = None) -> float:
        """Get amount spent in a period.

        Args:
            period: Budget period to check
            model: Optional model name for per-model spending

        Returns:
            Amount spent in USD
        """
        self._check_and_reset_periods()

        if period not in self._spending:
            return 0.0

        if model:
            return self._spending[period].get(model, 0.0)
        return self._spending[period].get("total", 0.0)

    def get_budget_status(self) -> Dict[str, Dict[str, float]]:
        """Get status of all budgets.

        Returns:
            Dictionary with budget, spent, remaining for each period
        """
        self._check_and_reset_periods()

        status = {}
        for period, config in self.budgets.items():
            spent = self.get_spent(period)
            remaining = self.get_remaining(period)
            status[period.value] = {
                "budget": config.amount,
                "spent": spent,
                "remaining": remaining,
                "percentage": (spent / config.amount * 100) if config.amount > 0 else 0,
            }

        return status

    def can_afford(self, estimated_cost: float) -> bool:
        """Check if an estimated cost is affordable within budgets.

        Args:
            estimated_cost: Estimated cost of operation in USD

        Returns:
            True if all budgets can afford the cost
        """
        self._check_and_reset_periods()

        for period, config in self.budgets.items():
            spent = self.get_spent(period)
            if config.hard_limit and (spent + estimated_cost) > config.amount:
                return False

        return True

    def reset_budget(self, period: Optional[BudgetPeriod] = None):
        """Reset budget tracking for a period.

        Args:
            period: Period to reset, or None to reset all
        """
        if period is None:
            # Reset all
            for p in self.budgets:
                self._spending[p] = {"total": 0.0}
                self._reset_times[p] = time.time()
        else:
            # Reset specific period
            if period in self._spending:
                self._spending[period] = {"total": 0.0}
                self._reset_times[period] = time.time()

    def _check_and_reset_periods(self):
        """Check if any periods need to be reset based on elapsed time."""
        current_time = time.time()

        for period in self.budgets:
            if period not in self._reset_times:
                self._reset_times[period] = current_time
                continue

            last_reset = self._reset_times[period]
            elapsed = current_time - last_reset

            # Calculate reset interval in seconds
            should_reset = False
            if period == BudgetPeriod.HOURLY and elapsed >= 3600:
                should_reset = True
            elif period == BudgetPeriod.DAILY and elapsed >= 86400:
                should_reset = True
            elif period == BudgetPeriod.WEEKLY and elapsed >= 604800:
                should_reset = True
            elif period == BudgetPeriod.MONTHLY and elapsed >= 2592000:  # 30 days
                should_reset = True
            # TOTAL budget never resets automatically

            if should_reset:
                logger.info(f"Resetting {period.value} budget (elapsed: {elapsed:.0f}s)")
                self.reset_budget(period)


def create_budget_enforcer(
    daily_budget: Optional[float] = None,
    monthly_budget: Optional[float] = None,
    total_budget: Optional[float] = None,
    **kwargs,
) -> CostBudgetEnforcer:
    """Create a budget enforcer with common configurations.

    Args:
        daily_budget: Daily budget limit in USD
        monthly_budget: Monthly budget limit in USD
        total_budget: Total lifetime budget in USD
        **kwargs: Additional configuration options

    Returns:
        Configured CostBudgetEnforcer

    Example:
        >>> enforcer = create_budget_enforcer(daily_budget=5.0, monthly_budget=100.0)
    """
    budgets = {}

    if daily_budget is not None:
        budgets[BudgetPeriod.DAILY] = BudgetConfig(
            amount=daily_budget,
            period=BudgetPeriod.DAILY,
            hard_limit=kwargs.get("hard_limit", True),
            warning_threshold=kwargs.get("warning_threshold", 0.8),
        )

    if monthly_budget is not None:
        budgets[BudgetPeriod.MONTHLY] = BudgetConfig(
            amount=monthly_budget,
            period=BudgetPeriod.MONTHLY,
            hard_limit=kwargs.get("hard_limit", True),
            warning_threshold=kwargs.get("warning_threshold", 0.8),
        )

    if total_budget is not None:
        budgets[BudgetPeriod.TOTAL] = BudgetConfig(
            amount=total_budget,
            period=BudgetPeriod.TOTAL,
            hard_limit=kwargs.get("hard_limit", True),
            warning_threshold=kwargs.get("warning_threshold", 0.8),
        )

    return CostBudgetEnforcer(budgets)
