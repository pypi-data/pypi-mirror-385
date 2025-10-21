"""Historical Metrics Integration for Improved Time Estimation.

This module integrates historical metrics from US-015 (TaskMetricsDB) with
the estimation system from US-016 to improve accuracy based on actual vs estimated trends.

**US-016 Phase 4: Integration with Estimation Metrics**

The MetricsIntegration class:
1. Queries historical task performance data
2. Calculates accuracy factors (actual/estimated ratios)
3. Adjusts new estimates based on historical patterns
4. Provides confidence levels based on sample size and variance

Example:
    >>> from coffee_maker.utils.metrics_integration import MetricsIntegration
    >>> from coffee_maker.utils.task_estimator import TaskComplexity, FeatureType
    >>>
    >>> integration = MetricsIntegration()
    >>>
    >>> # Get accuracy factor for CRUD features
    >>> factor = integration.calculate_accuracy_factor(
    ...     feature_type=FeatureType.CRUD,
    ...     complexity=TaskComplexity.MEDIUM
    ... )
    >>> print(factor)  # 1.15 (historically 15% over estimate)
    >>>
    >>> # Adjust estimate
    >>> adjusted = integration.adjust_estimate(
    ...     base_estimate=10.0,
    ...     feature_type=FeatureType.CRUD,
    ...     complexity=TaskComplexity.MEDIUM
    ... )
    >>> print(adjusted)  # 11.5h (10h × 1.15)
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from coffee_maker.autonomous.task_metrics import TaskMetricsDB
from coffee_maker.utils.task_estimator import FeatureType, TaskComplexity

logger = logging.getLogger(__name__)


@dataclass
class EstimateRecord:
    """Historical estimate vs actual record.

    Attributes:
        feature_type: Type of feature (CRUD, Integration, etc.)
        complexity: Task complexity (Low, Medium, High)
        estimated_hours: Original estimate in hours
        actual_hours: Actual time taken in hours
        accuracy_ratio: Actual/Estimated ratio
        date: When the task was completed
        subtask_name: Name of the subtask
    """

    feature_type: str
    complexity: str
    estimated_hours: float
    actual_hours: float
    accuracy_ratio: float
    date: datetime
    subtask_name: str


class MetricsIntegration:
    """Integration layer between historical metrics and estimation system.

    This class bridges US-015 (TaskMetricsDB) and US-016 (TaskEstimator) to:
    1. Query historical performance data
    2. Calculate accuracy adjustment factors
    3. Provide confidence levels based on data quality
    4. Adjust new estimates based on historical patterns

    The adjustment algorithm:
    - Groups historical data by feature_type and complexity
    - Calculates average accuracy_ratio (actual/estimated)
    - Applies weighted adjustment (recent data weighted higher)
    - Provides confidence based on sample size and variance

    Example:
        >>> integration = MetricsIntegration()
        >>>
        >>> # Check historical accuracy for CRUD/Medium tasks
        >>> records = integration.get_historical_estimates(
        ...     feature_type=FeatureType.CRUD,
        ...     complexity=TaskComplexity.MEDIUM,
        ...     limit=20
        ... )
        >>>
        >>> # Calculate adjustment factor
        >>> factor = integration.calculate_accuracy_factor(
        ...     feature_type=FeatureType.CRUD,
        ...     complexity=TaskComplexity.MEDIUM
        ... )
        >>>
        >>> # Adjust new estimate
        >>> adjusted = integration.adjust_estimate(
        ...     base_estimate=8.0,
        ...     feature_type=FeatureType.CRUD,
        ...     complexity=TaskComplexity.MEDIUM
        ... )
        >>> print(f"Adjusted: {adjusted}h (factor: {factor})")
    """

    # Default accuracy factors when no historical data exists
    DEFAULT_ACCURACY_FACTORS = {
        # Most teams underestimate by 10-30%
        (FeatureType.CRUD, TaskComplexity.LOW): 1.10,
        (FeatureType.CRUD, TaskComplexity.MEDIUM): 1.15,
        (FeatureType.CRUD, TaskComplexity.HIGH): 1.20,
        (FeatureType.INTEGRATION, TaskComplexity.LOW): 1.20,
        (FeatureType.INTEGRATION, TaskComplexity.MEDIUM): 1.25,
        (FeatureType.INTEGRATION, TaskComplexity.HIGH): 1.30,
        (FeatureType.UI, TaskComplexity.LOW): 1.15,
        (FeatureType.UI, TaskComplexity.MEDIUM): 1.20,
        (FeatureType.UI, TaskComplexity.HIGH): 1.25,
        (FeatureType.INFRASTRUCTURE, TaskComplexity.LOW): 1.25,
        (FeatureType.INFRASTRUCTURE, TaskComplexity.MEDIUM): 1.30,
        (FeatureType.INFRASTRUCTURE, TaskComplexity.HIGH): 1.40,
        (FeatureType.ANALYTICS, TaskComplexity.LOW): 1.15,
        (FeatureType.ANALYTICS, TaskComplexity.MEDIUM): 1.20,
        (FeatureType.ANALYTICS, TaskComplexity.HIGH): 1.30,
        (FeatureType.SECURITY, TaskComplexity.LOW): 1.20,
        (FeatureType.SECURITY, TaskComplexity.MEDIUM): 1.25,
        (FeatureType.SECURITY, TaskComplexity.HIGH): 1.35,
    }

    # Minimum samples required for high confidence
    MIN_SAMPLES_HIGH_CONFIDENCE = 20
    MIN_SAMPLES_MEDIUM_CONFIDENCE = 10
    MIN_SAMPLES_LOW_CONFIDENCE = 5

    # Recency weights (more recent = higher weight)
    RECENCY_WEIGHT_FACTOR = 0.95  # Exponential decay per week

    def __init__(self, metrics_db: Optional[TaskMetricsDB] = None):
        """Initialize metrics integration.

        Args:
            metrics_db: Optional TaskMetricsDB instance. If None, creates new instance.
        """
        self.metrics_db = metrics_db or TaskMetricsDB()
        logger.info("MetricsIntegration initialized")

    def get_historical_estimates(
        self,
        feature_type: Optional[FeatureType] = None,
        complexity: Optional[TaskComplexity] = None,
        limit: int = 100,
        days_back: int = 90,
    ) -> List[EstimateRecord]:
        """Query historical estimate vs actual data.

        Args:
            feature_type: Filter by feature type (None = all types)
            complexity: Filter by complexity (None = all complexities)
            limit: Maximum number of records to return
            days_back: Only include records from last N days

        Returns:
            List of EstimateRecord objects sorted by date (newest first)

        Example:
            >>> records = integration.get_historical_estimates(
            ...     feature_type=FeatureType.CRUD,
            ...     complexity=TaskComplexity.MEDIUM,
            ...     limit=50
            ... )
            >>> avg_accuracy = sum(r.accuracy_ratio for r in records) / len(records)
        """
        import sqlite3

        logger.debug(
            f"Querying historical estimates: feature_type={feature_type}, "
            f"complexity={complexity}, limit={limit}, days_back={days_back}"
        )

        # Build query
        query = """
            SELECT
                subtask_name,
                estimated_seconds,
                actual_seconds,
                timestamp
            FROM subtask_metrics
            WHERE status = 'completed'
                AND estimated_seconds > 0
                AND actual_seconds > 0
        """

        params = []

        # Add date filter
        cutoff_date = datetime.now() - timedelta(days=days_back)
        query += " AND timestamp >= ?"
        params.append(cutoff_date.isoformat())

        # Note: TaskMetricsDB doesn't store feature_type or complexity yet,
        # so we use heuristics based on subtask_name
        # TODO: Enhance TaskMetricsDB schema in future to include these fields

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        # Execute query
        conn = sqlite3.connect(str(self.metrics_db.db_path))
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to EstimateRecord objects
        records = []
        for row in rows:
            subtask_name = row[0]
            estimated_seconds = row[1]
            actual_seconds = row[2]
            timestamp = datetime.fromisoformat(row[3])

            # Infer feature_type and complexity from subtask_name (heuristic)
            inferred_feature_type, inferred_complexity = self._infer_task_metadata(subtask_name)

            # Apply filters
            if feature_type and inferred_feature_type != feature_type.value:
                continue
            if complexity and inferred_complexity != complexity.value:
                continue

            # Calculate accuracy ratio
            estimated_hours = estimated_seconds / 3600.0
            actual_hours = actual_seconds / 3600.0
            accuracy_ratio = actual_hours / estimated_hours if estimated_hours > 0 else 1.0

            record = EstimateRecord(
                feature_type=inferred_feature_type,
                complexity=inferred_complexity,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                accuracy_ratio=accuracy_ratio,
                date=timestamp,
                subtask_name=subtask_name,
            )
            records.append(record)

        logger.info(f"Retrieved {len(records)} historical estimate records")

        return records

    def calculate_accuracy_factor(
        self, feature_type: FeatureType, complexity: TaskComplexity, days_back: int = 90
    ) -> float:
        """Calculate accuracy adjustment factor based on historical data.

        The factor represents how much actual time differs from estimated time:
        - 1.0 = perfectly accurate (actual == estimated)
        - 1.2 = tasks take 20% longer than estimated
        - 0.8 = tasks take 20% less than estimated

        Uses weighted average with recency bias (recent data weighted higher).

        Args:
            feature_type: Type of feature
            complexity: Task complexity level
            days_back: Consider data from last N days (default: 90)

        Returns:
            Accuracy factor (typically 0.8 - 1.5)

        Example:
            >>> factor = integration.calculate_accuracy_factor(
            ...     FeatureType.CRUD,
            ...     TaskComplexity.MEDIUM
            ... )
            >>> print(factor)  # 1.18 (tasks take 18% longer than estimated)
        """
        logger.debug(f"Calculating accuracy factor: {feature_type.value}/{complexity.value}")

        # Get historical data
        records = self.get_historical_estimates(
            feature_type=feature_type, complexity=complexity, days_back=days_back, limit=100
        )

        # If no historical data, use defaults
        if not records:
            default_factor = self.DEFAULT_ACCURACY_FACTORS.get(
                (feature_type, complexity), 1.15  # Default 15% underestimate
            )
            logger.info(
                f"No historical data for {feature_type.value}/{complexity.value}, "
                f"using default factor: {default_factor}"
            )
            return default_factor

        # Calculate weighted average with recency bias
        weighted_sum = 0.0
        weight_total = 0.0

        now = datetime.now()

        for record in records:
            # Calculate recency weight (exponential decay)
            days_old = (now - record.date).days
            weeks_old = days_old / 7.0
            recency_weight = self.RECENCY_WEIGHT_FACTOR**weeks_old

            weighted_sum += record.accuracy_ratio * recency_weight
            weight_total += recency_weight

        if weight_total == 0:
            logger.warning("Weight total is zero, using default")
            return self.DEFAULT_ACCURACY_FACTORS.get((feature_type, complexity), 1.15)

        weighted_average = weighted_sum / weight_total

        # Clamp to reasonable range (0.7 - 2.0)
        clamped = max(0.7, min(2.0, weighted_average))

        logger.info(
            f"Accuracy factor for {feature_type.value}/{complexity.value}: "
            f"{clamped:.2f} (from {len(records)} samples)"
        )

        return round(clamped, 2)

    def get_confidence_level(
        self, feature_type: FeatureType, complexity: TaskComplexity, days_back: int = 90
    ) -> Tuple[float, str]:
        """Calculate confidence level for estimates based on data quality.

        Confidence is based on:
        1. Sample size (more samples = higher confidence)
        2. Variance (lower variance = higher confidence)
        3. Recency (recent data = higher confidence)

        Args:
            feature_type: Type of feature
            complexity: Task complexity level
            days_back: Consider data from last N days

        Returns:
            Tuple of (confidence_score, confidence_label)
            - confidence_score: 0.0 - 1.0
            - confidence_label: "Very High" | "High" | "Medium" | "Low" | "Very Low"

        Example:
            >>> confidence, label = integration.get_confidence_level(
            ...     FeatureType.CRUD,
            ...     TaskComplexity.MEDIUM
            ... )
            >>> print(f"{label}: {confidence:.0%}")  # "High: 85%"
        """
        logger.debug(f"Calculating confidence level: {feature_type.value}/{complexity.value}")

        # Get historical data
        records = self.get_historical_estimates(feature_type=feature_type, complexity=complexity, days_back=days_back)

        # Base confidence on sample size
        sample_size = len(records)

        if sample_size == 0:
            return 0.50, "Very Low"  # No data
        elif sample_size < self.MIN_SAMPLES_LOW_CONFIDENCE:
            base_confidence = 0.60  # Very limited data
        elif sample_size < self.MIN_SAMPLES_MEDIUM_CONFIDENCE:
            base_confidence = 0.70  # Limited data
        elif sample_size < self.MIN_SAMPLES_HIGH_CONFIDENCE:
            base_confidence = 0.80  # Good data
        else:
            base_confidence = 0.90  # Excellent data

        # Adjust for variance (lower variance = higher confidence)
        if records:
            accuracy_ratios = [r.accuracy_ratio for r in records]
            mean_ratio = sum(accuracy_ratios) / len(accuracy_ratios)
            variance = sum((r - mean_ratio) ** 2 for r in accuracy_ratios) / len(accuracy_ratios)
            std_dev = variance**0.5

            # High variance reduces confidence
            variance_factor = max(0.5, 1.0 - (std_dev * 0.5))
        else:
            variance_factor = 1.0

        # Adjust for recency (recent data increases confidence)
        if records:
            now = datetime.now()
            avg_age_days = sum((now - r.date).days for r in records) / len(records)
            recency_factor = max(0.7, 1.0 - (avg_age_days / days_back) * 0.3)
        else:
            recency_factor = 1.0

        # Calculate final confidence
        confidence = base_confidence * variance_factor * recency_factor

        # Clamp to 0.0 - 1.0
        confidence = max(0.0, min(1.0, confidence))

        # Determine label
        if confidence >= 0.90:
            label = "Very High"
        elif confidence >= 0.80:
            label = "High"
        elif confidence >= 0.70:
            label = "Medium"
        elif confidence >= 0.60:
            label = "Low"
        else:
            label = "Very Low"

        logger.info(
            f"Confidence for {feature_type.value}/{complexity.value}: "
            f"{label} ({confidence:.0%}, {sample_size} samples)"
        )

        return round(confidence, 2), label

    def adjust_estimate(
        self, base_estimate: float, feature_type: FeatureType, complexity: TaskComplexity
    ) -> Tuple[float, float, float]:
        """Adjust estimate based on historical accuracy factor.

        Args:
            base_estimate: Base estimate in hours (from TaskEstimator)
            feature_type: Type of feature
            complexity: Task complexity level

        Returns:
            Tuple of (adjusted_estimate, accuracy_factor, confidence)

        Example:
            >>> adjusted, factor, confidence = integration.adjust_estimate(
            ...     base_estimate=10.0,
            ...     feature_type=FeatureType.CRUD,
            ...     complexity=TaskComplexity.MEDIUM
            ... )
            >>> print(f"Adjusted: {adjusted}h (factor: {factor}, confidence: {confidence:.0%})")
            Adjusted: 11.5h (factor: 1.15, confidence: 85%)
        """
        logger.debug(f"Adjusting estimate: {base_estimate}h for {feature_type.value}/{complexity.value}")

        # Get accuracy factor
        accuracy_factor = self.calculate_accuracy_factor(feature_type, complexity)

        # Get confidence level
        confidence, _ = self.get_confidence_level(feature_type, complexity)

        # Apply adjustment
        adjusted_estimate = base_estimate * accuracy_factor

        # Round to nearest 0.5h
        adjusted_estimate = round(adjusted_estimate * 2) / 2

        logger.info(
            f"Estimate adjusted: {base_estimate}h → {adjusted_estimate}h "
            f"(factor: {accuracy_factor}, confidence: {confidence:.0%})"
        )

        return adjusted_estimate, accuracy_factor, confidence

    def get_adjustment_summary(self, feature_type: FeatureType, complexity: TaskComplexity) -> dict:
        """Get comprehensive adjustment summary for reporting.

        Args:
            feature_type: Type of feature
            complexity: Task complexity level

        Returns:
            Dictionary with:
            - accuracy_factor: Adjustment multiplier
            - confidence: Confidence score (0.0-1.0)
            - confidence_label: Human-readable confidence level
            - sample_size: Number of historical records
            - avg_actual_hours: Average actual time from historical data
            - avg_estimated_hours: Average estimated time from historical data

        Example:
            >>> summary = integration.get_adjustment_summary(
            ...     FeatureType.CRUD,
            ...     TaskComplexity.MEDIUM
            ... )
            >>> print(f"Factor: {summary['accuracy_factor']}")
            >>> print(f"Confidence: {summary['confidence_label']}")
        """
        # Get historical data
        records = self.get_historical_estimates(feature_type=feature_type, complexity=complexity)

        # Calculate accuracy factor and confidence
        accuracy_factor = self.calculate_accuracy_factor(feature_type, complexity)
        confidence, confidence_label = self.get_confidence_level(feature_type, complexity)

        # Calculate averages
        if records:
            avg_actual_hours = sum(r.actual_hours for r in records) / len(records)
            avg_estimated_hours = sum(r.estimated_hours for r in records) / len(records)
        else:
            avg_actual_hours = 0.0
            avg_estimated_hours = 0.0

        summary = {
            "accuracy_factor": accuracy_factor,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "sample_size": len(records),
            "avg_actual_hours": round(avg_actual_hours, 1),
            "avg_estimated_hours": round(avg_estimated_hours, 1),
        }

        logger.debug(f"Adjustment summary: {summary}")

        return summary

    def _infer_task_metadata(self, subtask_name: str) -> Tuple[str, str]:
        """Infer feature_type and complexity from subtask name (heuristic).

        This is a temporary solution until TaskMetricsDB schema is enhanced
        to include feature_type and complexity fields.

        Args:
            subtask_name: Name of the subtask

        Returns:
            Tuple of (feature_type_str, complexity_str)
        """
        name_lower = subtask_name.lower()

        # Infer feature type from keywords
        if any(kw in name_lower for kw in ["database", "model", "migration", "crud"]):
            feature_type = "crud"
        elif any(kw in name_lower for kw in ["api", "integration", "external", "webhook"]):
            feature_type = "integration"
        elif any(kw in name_lower for kw in ["ui", "component", "page", "form", "button"]):
            feature_type = "ui"
        elif any(kw in name_lower for kw in ["deploy", "infrastructure", "docker", "kubernetes"]):
            feature_type = "infrastructure"
        elif any(kw in name_lower for kw in ["analytics", "report", "dashboard", "metrics"]):
            feature_type = "analytics"
        elif any(kw in name_lower for kw in ["auth", "security", "permission", "encryption"]):
            feature_type = "security"
        else:
            feature_type = "crud"  # Default

        # Infer complexity from keywords
        if any(kw in name_lower for kw in ["simple", "basic", "create"]):
            complexity = "low"
        elif any(kw in name_lower for kw in ["complex", "advanced", "integration"]):
            complexity = "high"
        else:
            complexity = "medium"  # Default

        return feature_type, complexity
