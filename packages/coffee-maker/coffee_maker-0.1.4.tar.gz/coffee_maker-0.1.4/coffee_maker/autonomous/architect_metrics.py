"""Metrics tracker for architect continuous improvement loop.

This module tracks simplification metrics, reuse opportunities, and effort saved
through architect's continuous review process.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ArchitectMetrics:
    """Track architect review metrics.

    Metrics tracked:
    - Simplification rate (% reduction in implementation complexity)
    - Reuse rate (% of specs using shared components)
    - Effort saved (hours saved by simplifications)
    - Spec count (total specs reviewed)
    """

    def __init__(self, metrics_file: Path = Path("data/architect_metrics.json")):
        """Initialize metrics tracker.

        Args:
            metrics_file: Path to metrics JSON file
        """
        self.metrics_file = metrics_file
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def record_simplification(
        self,
        spec_id: str,
        original_hours: float,
        simplified_hours: float,
        description: str,
    ) -> None:
        """Record a spec simplification.

        Args:
            spec_id: Spec identifier (e.g., "SPEC-009")
            original_hours: Original estimated hours
            simplified_hours: Simplified estimated hours
            description: Brief description of simplification
        """
        metrics = self._load_metrics()

        if "simplifications" not in metrics:
            metrics["simplifications"] = []

        simplification = {
            "spec_id": spec_id,
            "original_hours": original_hours,
            "simplified_hours": simplified_hours,
            "effort_saved": original_hours - simplified_hours,
            "reduction_percent": ((original_hours - simplified_hours) / original_hours) * 100,
            "description": description,
            "date": datetime.now().isoformat(),
        }

        metrics["simplifications"].append(simplification)
        self._save_metrics(metrics)

    def record_reuse(self, spec_id: str, reused_components: List[str], description: str) -> None:
        """Record component reuse in a spec.

        Args:
            spec_id: Spec identifier
            reused_components: List of reused component names
            description: Brief description
        """
        metrics = self._load_metrics()

        if "reuse" not in metrics:
            metrics["reuse"] = []

        reuse = {
            "spec_id": spec_id,
            "components": reused_components,
            "count": len(reused_components),
            "description": description,
            "date": datetime.now().isoformat(),
        }

        metrics["reuse"].append(reuse)
        self._save_metrics(metrics)

    def get_summary(self) -> Dict:
        """Get summary metrics.

        Returns:
            Dict with summary metrics:
            - total_simplifications: int
            - total_effort_saved: float (hours)
            - avg_reduction_percent: float
            - total_reuse_opportunities: int
            - specs_reviewed: int
        """
        metrics = self._load_metrics()

        simplifications = metrics.get("simplifications", [])
        reuse = metrics.get("reuse", [])

        total_effort_saved = sum(s["effort_saved"] for s in simplifications)
        avg_reduction = (
            sum(s["reduction_percent"] for s in simplifications) / len(simplifications) if simplifications else 0
        )

        # Get unique spec IDs from both simplifications and reuse
        all_spec_ids = set(s["spec_id"] for s in simplifications)
        all_spec_ids.update(r["spec_id"] for r in reuse)

        return {
            "total_simplifications": len(simplifications),
            "total_effort_saved": total_effort_saved,
            "avg_reduction_percent": avg_reduction,
            "total_reuse_opportunities": len(reuse),
            "specs_reviewed": len(all_spec_ids),
        }

    def _load_metrics(self) -> dict:
        """Load metrics from JSON file.

        Returns:
            Dict with metrics data
        """
        if not self.metrics_file.exists():
            return {}

        with open(self.metrics_file) as f:
            return json.load(f)

    def _save_metrics(self, metrics: dict) -> None:
        """Save metrics to JSON file.

        Args:
            metrics: Dict with metrics data
        """
        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
