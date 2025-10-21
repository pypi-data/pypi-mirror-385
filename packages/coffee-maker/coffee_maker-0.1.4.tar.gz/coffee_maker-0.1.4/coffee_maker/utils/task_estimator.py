"""Task Time Estimation Engine for Technical Specifications.

This module provides intelligent time estimation for tasks based on:
- Base complexity (Low, Medium, High)
- Feature type (CRUD, Integration, UI, Infrastructure)
- Multiplier adjustments for testing, documentation, security, integration

**US-016 Phase 3: AI-Assisted Task Breakdown**

Example:
    >>> from coffee_maker.utils.task_estimator import TaskEstimator, TaskComplexity, FeatureType
    >>>
    >>> estimator = TaskEstimator()
    >>> estimate = estimator.estimate_task(
    ...     task_description="Create user authentication endpoint",
    ...     complexity=TaskComplexity.MEDIUM,
    ...     feature_type=FeatureType.CRUD,
    ...     requires_testing=True,
    ...     requires_documentation=True,
    ...     requires_security=True
    ... )
    >>> print(estimate.total_hours)  # 4.5h
    >>> print(estimate.breakdown)   # {'implementation': 2.5h, 'testing': 0.75h, ...}
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels with base time estimates."""

    LOW = "low"  # 1-2h
    MEDIUM = "medium"  # 2-3h
    HIGH = "high"  # 3-4h


class FeatureType(Enum):
    """Feature types that affect time estimates."""

    CRUD = "crud"  # Basic create/read/update/delete operations
    INTEGRATION = "integration"  # Third-party service integration
    UI = "ui"  # User interface components
    INFRASTRUCTURE = "infrastructure"  # DevOps, deployment, monitoring
    ANALYTICS = "analytics"  # Data analysis, reporting
    SECURITY = "security"  # Authentication, authorization, encryption


@dataclass
class TimeEstimate:
    """Time estimate with breakdown by activity.

    Attributes:
        total_hours: Total estimated hours (rounded to 0.5h)
        base_hours: Base implementation time before multipliers
        breakdown: Time breakdown by activity (implementation, testing, docs, etc.)
        confidence: Confidence level (0.0-1.0)
        assumptions: List of assumptions made during estimation
        risks: Identified risks that could affect estimates
    """

    total_hours: float
    base_hours: float
    breakdown: Dict[str, float]
    confidence: float
    assumptions: List[str]
    risks: List[str]


class TaskEstimator:
    """Intelligent task time estimation engine.

    This class provides sophisticated time estimation based on:
    1. Base complexity levels (Low: 1-2h, Medium: 2-3h, High: 3-4h)
    2. Feature type adjustments
    3. Multipliers for testing, documentation, security, integration
    4. Historical patterns (future enhancement)

    All estimates are rounded to nearest 0.5h and capped at 4h per task.
    Tasks > 4h should be broken down into smaller subtasks.

    Example:
        >>> estimator = TaskEstimator()
        >>>
        >>> # Simple CRUD task
        >>> estimate = estimator.estimate_task(
        ...     "Create database model for User",
        ...     TaskComplexity.LOW,
        ...     FeatureType.CRUD,
        ...     requires_testing=True
        ... )
        >>> print(estimate.total_hours)  # 2.5h
        >>>
        >>> # Complex integration task
        >>> estimate = estimator.estimate_task(
        ...     "Integrate with external payment API",
        ...     TaskComplexity.HIGH,
        ...     FeatureType.INTEGRATION,
        ...     requires_testing=True,
        ...     requires_documentation=True,
        ...     requires_security=True,
        ...     is_integration_complex=True
        ... )
        >>> print(estimate.total_hours)  # 4.0h (capped at maximum)
    """

    # Base time estimates by complexity (midpoint of range)
    BASE_ESTIMATES = {
        TaskComplexity.LOW: 1.5,  # 1-2h → 1.5h average
        TaskComplexity.MEDIUM: 2.5,  # 2-3h → 2.5h average
        TaskComplexity.HIGH: 3.5,  # 3-4h → 3.5h average
    }

    # Multipliers for different factors
    TESTING_MULTIPLIER = 1.3  # +30% for testing
    DOCUMENTATION_MULTIPLIER = 1.15  # +15% for documentation
    INTEGRATION_COMPLEXITY_MULTIPLIER = 1.2  # +20% for complex integrations
    SECURITY_MULTIPLIER = 1.25  # +25% for security requirements

    # Maximum task size (hours) - tasks larger should be broken down
    MAX_TASK_HOURS = 4.0

    # Feature type adjustments (additive hours)
    FEATURE_TYPE_ADJUSTMENTS = {
        FeatureType.CRUD: 0.0,  # Baseline
        FeatureType.INTEGRATION: 0.5,  # +0.5h for integration complexity
        FeatureType.UI: 0.3,  # +0.3h for UI polishing
        FeatureType.INFRASTRUCTURE: 0.7,  # +0.7h for infrastructure complexity
        FeatureType.ANALYTICS: 0.4,  # +0.4h for data processing
        FeatureType.SECURITY: 0.6,  # +0.6h for security best practices
    }

    def __init__(self, use_historical_adjustment: bool = False):
        """Initialize the task estimator.

        Args:
            use_historical_adjustment: If True, use MetricsIntegration to adjust estimates
                                     based on historical accuracy data (default: False)
        """
        self.use_historical_adjustment = use_historical_adjustment
        self.metrics_integration = None

        if use_historical_adjustment:
            try:
                from coffee_maker.utils.metrics_integration import MetricsIntegration

                self.metrics_integration = MetricsIntegration()
                logger.info("TaskEstimator initialized with historical adjustment enabled")
            except ImportError:
                logger.warning("MetricsIntegration not available, falling back to base estimates")
                self.use_historical_adjustment = False
        else:
            logger.info("TaskEstimator initialized")

    def estimate_task(
        self,
        task_description: str,
        complexity: TaskComplexity,
        feature_type: FeatureType,
        requires_testing: bool = True,
        requires_documentation: bool = False,
        requires_security: bool = False,
        is_integration_complex: bool = False,
    ) -> TimeEstimate:
        """Estimate time for a single task with detailed breakdown.

        Args:
            task_description: Brief description of the task
            complexity: Task complexity level (LOW, MEDIUM, HIGH)
            feature_type: Type of feature (CRUD, Integration, UI, etc.)
            requires_testing: Whether task requires explicit testing (default: True)
            requires_documentation: Whether task requires documentation (default: False)
            requires_security: Whether task has security requirements (default: False)
            is_integration_complex: Whether integration is particularly complex (default: False)

        Returns:
            TimeEstimate with total hours, breakdown, confidence, assumptions, and risks

        Example:
            >>> estimator = TaskEstimator()
            >>> estimate = estimator.estimate_task(
            ...     "Create REST API endpoint for user login",
            ...     TaskComplexity.MEDIUM,
            ...     FeatureType.SECURITY,
            ...     requires_testing=True,
            ...     requires_documentation=True,
            ...     requires_security=True
            ... )
            >>> print(f"Total: {estimate.total_hours}h")
            Total: 4.0h
            >>> print(estimate.breakdown)
            {'implementation': 3.1, 'testing': 0.9, 'documentation': 0.5, 'security': 0.8}
        """
        logger.debug(
            f"Estimating task: '{task_description[:50]}...' "
            f"(complexity={complexity.value}, feature_type={feature_type.value})"
        )

        # Start with base estimate
        base_hours = self.BASE_ESTIMATES[complexity]

        # Add feature type adjustment
        feature_adjustment = self.FEATURE_TYPE_ADJUSTMENTS[feature_type]
        base_hours += feature_adjustment

        # Track assumptions and risks
        assumptions = [
            f"Base complexity: {complexity.value} ({self.BASE_ESTIMATES[complexity]}h)",
            f"Feature type: {feature_type.value} (+{feature_adjustment}h)",
        ]
        risks = []

        # Calculate breakdown
        breakdown = {"implementation": base_hours}

        # Apply multipliers and track breakdown
        total_hours = base_hours

        # Testing multiplier
        if requires_testing:
            testing_time = base_hours * (self.TESTING_MULTIPLIER - 1.0)
            breakdown["testing"] = testing_time
            total_hours += testing_time
            assumptions.append(f"Testing required (×{self.TESTING_MULTIPLIER})")

        # Documentation multiplier
        if requires_documentation:
            doc_time = base_hours * (self.DOCUMENTATION_MULTIPLIER - 1.0)
            breakdown["documentation"] = doc_time
            total_hours += doc_time
            assumptions.append(f"Documentation required (×{self.DOCUMENTATION_MULTIPLIER})")

        # Security multiplier
        if requires_security:
            security_time = base_hours * (self.SECURITY_MULTIPLIER - 1.0)
            breakdown["security"] = security_time
            total_hours += security_time
            assumptions.append(f"Security requirements (×{self.SECURITY_MULTIPLIER})")
            risks.append("Security review may identify additional work")

        # Integration complexity multiplier
        if is_integration_complex:
            integration_time = base_hours * (self.INTEGRATION_COMPLEXITY_MULTIPLIER - 1.0)
            breakdown["integration_complexity"] = integration_time
            total_hours += integration_time
            assumptions.append(f"Complex integration (×{self.INTEGRATION_COMPLEXITY_MULTIPLIER})")
            risks.append("Third-party API changes may require rework")

        # Round to nearest 0.5h
        total_hours = self._round_to_half_hour(total_hours)

        # Cap at maximum task size
        if total_hours > self.MAX_TASK_HOURS:
            risks.append(f"Task exceeds {self.MAX_TASK_HOURS}h - consider breaking into subtasks")
            total_hours = self.MAX_TASK_HOURS
            assumptions.append(f"Capped at maximum task size ({self.MAX_TASK_HOURS}h)")

        # Calculate base confidence
        base_confidence = self._calculate_confidence(complexity, requires_security, is_integration_complex)

        # Apply historical adjustment if enabled
        if self.use_historical_adjustment and self.metrics_integration:
            adjusted_total, accuracy_factor, historical_confidence = self.metrics_integration.adjust_estimate(
                base_estimate=total_hours, feature_type=feature_type, complexity=complexity
            )

            # Use historical confidence if available, otherwise use base
            final_confidence = historical_confidence if historical_confidence > 0.5 else base_confidence

            # Update assumptions with adjustment info
            assumptions.append(f"Historical adjustment: {total_hours}h → {adjusted_total}h (factor: {accuracy_factor})")
            assumptions.append(
                f"Adjusted confidence: {final_confidence:.0%} (based on {self.metrics_integration.get_adjustment_summary(feature_type, complexity)['sample_size']} samples)"
            )

            total_hours = adjusted_total
        else:
            final_confidence = base_confidence

        # Round all breakdown values
        breakdown = {k: self._round_to_half_hour(v) for k, v in breakdown.items()}

        estimate = TimeEstimate(
            total_hours=total_hours,
            base_hours=base_hours,
            breakdown=breakdown,
            confidence=final_confidence,
            assumptions=assumptions,
            risks=risks,
        )

        logger.info(
            f"Task estimated: {total_hours}h (base: {base_hours}h, confidence: {final_confidence:.0%}"
            + (f", adjusted: {self.use_historical_adjustment})" if self.use_historical_adjustment else ")")
        )

        return estimate

    def estimate_phase(self, tasks: List[TimeEstimate], phase_name: str = "Phase") -> Dict[str, any]:
        """Calculate total time for a phase from individual task estimates.

        Args:
            tasks: List of TimeEstimate objects for tasks in the phase
            phase_name: Name of the phase (for logging)

        Returns:
            Dictionary with phase totals:
            {
                'total_hours': float,
                'task_count': int,
                'breakdown': {'implementation': X, 'testing': Y, ...},
                'confidence': float (average),
                'risks': List[str] (aggregated)
            }

        Example:
            >>> estimator = TaskEstimator()
            >>> task1 = estimator.estimate_task("Task 1", TaskComplexity.LOW, FeatureType.CRUD)
            >>> task2 = estimator.estimate_task("Task 2", TaskComplexity.MEDIUM, FeatureType.UI)
            >>> phase_total = estimator.estimate_phase([task1, task2], "Phase 1")
            >>> print(phase_total['total_hours'])
            5.5
        """
        if not tasks:
            logger.warning(f"{phase_name}: No tasks provided")
            return {
                "total_hours": 0.0,
                "task_count": 0,
                "breakdown": {},
                "confidence": 0.0,
                "risks": [],
            }

        # Sum totals
        total_hours = sum(task.total_hours for task in tasks)

        # Aggregate breakdown across all tasks
        breakdown = {}
        for task in tasks:
            for activity, hours in task.breakdown.items():
                breakdown[activity] = breakdown.get(activity, 0.0) + hours

        # Round breakdown values
        breakdown = {k: self._round_to_half_hour(v) for k, v in breakdown.items()}

        # Average confidence
        avg_confidence = sum(task.confidence for task in tasks) / len(tasks)

        # Aggregate unique risks
        all_risks = []
        for task in tasks:
            all_risks.extend(task.risks)
        unique_risks = list(set(all_risks))

        phase_estimate = {
            "total_hours": self._round_to_half_hour(total_hours),
            "task_count": len(tasks),
            "breakdown": breakdown,
            "confidence": round(avg_confidence, 2),
            "risks": unique_risks,
        }

        logger.info(
            f"{phase_name}: {phase_estimate['total_hours']}h "
            f"({len(tasks)} tasks, {phase_estimate['confidence']:.0%} confidence)"
        )

        return phase_estimate

    def calculate_time_distribution(self, phases: List[Dict[str, any]]) -> Dict[str, any]:
        """Calculate overall time distribution across all phases.

        Args:
            phases: List of phase estimate dictionaries

        Returns:
            Dictionary with overall statistics:
            {
                'total_hours': float,
                'total_days': float (assuming 8h/day),
                'phase_count': int,
                'task_count': int,
                'distribution': {
                    'implementation': {'hours': X, 'percentage': Y%},
                    'testing': {'hours': X, 'percentage': Y%},
                    ...
                }
            }

        Example:
            >>> distribution = estimator.calculate_time_distribution(phases)
            >>> print(distribution['distribution']['implementation']['percentage'])
            45.5%
        """
        if not phases:
            return {
                "total_hours": 0.0,
                "total_days": 0.0,
                "phase_count": 0,
                "task_count": 0,
                "distribution": {},
            }

        # Sum totals
        total_hours = sum(phase["total_hours"] for phase in phases)
        total_tasks = sum(phase["task_count"] for phase in phases)

        # Aggregate all activity breakdowns
        activity_totals = {}
        for phase in phases:
            for activity, hours in phase["breakdown"].items():
                activity_totals[activity] = activity_totals.get(activity, 0.0) + hours

        # Calculate percentages
        distribution = {}
        for activity, hours in activity_totals.items():
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0
            distribution[activity] = {
                "hours": self._round_to_half_hour(hours),
                "percentage": round(percentage, 1),
            }

        result = {
            "total_hours": self._round_to_half_hour(total_hours),
            "total_days": round(total_hours / 8, 1),  # Assuming 8h/day
            "phase_count": len(phases),
            "task_count": total_tasks,
            "distribution": distribution,
        }

        logger.info(
            f"Total distribution: {result['total_hours']}h "
            f"({result['total_days']} days, {result['task_count']} tasks)"
        )

        return result

    def _round_to_half_hour(self, hours: float) -> float:
        """Round hours to nearest 0.5h.

        Args:
            hours: Hours to round

        Returns:
            Rounded hours

        Example:
            >>> estimator._round_to_half_hour(2.3)
            2.5
            >>> estimator._round_to_half_hour(2.7)
            3.0
        """
        return round(hours * 2) / 2

    def _calculate_confidence(
        self,
        complexity: TaskComplexity,
        requires_security: bool,
        is_integration_complex: bool,
    ) -> float:
        """Calculate confidence level for estimate.

        Higher complexity and more factors reduce confidence.

        Args:
            complexity: Task complexity level
            requires_security: Whether security is required
            is_integration_complex: Whether integration is complex

        Returns:
            Confidence score (0.0-1.0)

        Example:
            >>> estimator._calculate_confidence(TaskComplexity.LOW, False, False)
            0.9
            >>> estimator._calculate_confidence(TaskComplexity.HIGH, True, True)
            0.6
        """
        # Start with base confidence
        base_confidence = {
            TaskComplexity.LOW: 0.9,
            TaskComplexity.MEDIUM: 0.8,
            TaskComplexity.HIGH: 0.7,
        }

        confidence = base_confidence[complexity]

        # Reduce confidence for additional factors
        if requires_security:
            confidence -= 0.05
        if is_integration_complex:
            confidence -= 0.05

        # Ensure confidence stays in valid range
        confidence = max(0.5, min(1.0, confidence))

        return round(confidence, 2)
