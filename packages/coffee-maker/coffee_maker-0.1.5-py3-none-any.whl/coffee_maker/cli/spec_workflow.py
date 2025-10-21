"""Spec Generation Workflow - Interactive spec generation and review.

This module implements US-016 Phase 5: Interactive workflow where PM triggers
spec generation when user approves a user story, then shows delivery estimate.

The workflow:
1. User requests spec generation: /spec <user-story>
2. PM generates technical spec (using SpecGenerator from Phase 3)
3. PM shows delivery estimate with spec reference
4. User reviews and approves/rejects spec
5. PM updates ROADMAP.md with estimate and spec link

Example:
    >>> from coffee_maker.cli.spec_workflow import SpecWorkflow
    >>> from coffee_maker.cli.ai_service import AIService
    >>>
    >>> ai_service = AIService()
    >>> workflow = SpecWorkflow(ai_service)
    >>>
    >>> # Generate and review spec
    >>> result = workflow.generate_and_review_spec(
    ...     user_story="As a user, I want email notifications",
    ...     feature_type="integration",
    ...     complexity="medium"
    ... )
    >>> print(result.delivery_date)
    '2025-10-20'
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from coffee_maker.autonomous.spec_generator import SpecGenerator, TechnicalSpec
from coffee_maker.cli.roadmap_editor import RoadmapEditor
from coffee_maker.config import ROADMAP_PATH

logger = logging.getLogger(__name__)


@dataclass
class SpecReviewResult:
    """Result of spec generation and review process.

    Attributes:
        spec: Generated TechnicalSpec object
        spec_path: Path where spec was saved
        markdown: Rendered markdown content
        summary: Summary stats (total_hours, total_days, etc.)
        delivery_estimate: Delivery estimate info
        approved: Whether spec was approved by user
        rejection_reason: Reason if rejected (None if approved)
    """

    spec: TechnicalSpec
    spec_path: Path
    markdown: str
    summary: Dict
    delivery_estimate: Dict
    approved: bool = False
    rejection_reason: Optional[str] = None


@dataclass
class DeliveryEstimate:
    """Delivery estimate with buffer calculations.

    Attributes:
        total_hours: Total estimated hours from spec
        total_days: Total estimated days (hours / 8)
        buffer_percentage: Buffer percentage (10-20%)
        buffered_hours: Hours with buffer
        buffered_days: Days with buffer
        delivery_date: Expected delivery date
        confidence: Confidence level (0.0-1.0)
    """

    total_hours: float
    total_days: float
    buffer_percentage: float
    buffered_hours: float
    buffered_days: float
    delivery_date: str
    confidence: float


class SpecWorkflow:
    """Interactive spec generation and review workflow.

    This class orchestrates the full workflow for US-016 Phase 5:
    1. Generate technical spec from user story
    2. Calculate delivery estimate with buffer
    3. Present to user for review
    4. Handle approval/rejection
    5. Update ROADMAP.md with spec reference

    Example:
        >>> workflow = SpecWorkflow(ai_service)
        >>> result = workflow.generate_and_review_spec(
        ...     "Email notifications for completed tasks",
        ...     "integration",
        ...     "medium"
        ... )
        >>> if result.approved:
        ...     print(f"Spec saved to: {result.spec_path}")
        ...     print(f"Delivery: {result.delivery_estimate['delivery_date']}")
    """

    def __init__(self, ai_service, velocity_hours_per_day: float = 6.0):
        """Initialize spec workflow.

        Args:
            ai_service: AIService instance for spec generation
            velocity_hours_per_day: Team velocity in working hours per day (default: 6.0)
                                   This accounts for meetings, interruptions, etc.
                                   8h/day * 0.75 = 6h productive time
        """
        self.ai_service = ai_service
        self.spec_generator = SpecGenerator(ai_service)
        self.roadmap_editor = RoadmapEditor(ROADMAP_PATH)
        self.velocity_hours_per_day = velocity_hours_per_day

        logger.info(f"SpecWorkflow initialized (velocity={velocity_hours_per_day}h/day)")

    def generate_and_review_spec(
        self,
        user_story: str,
        feature_type: str = "general",
        complexity: str = "medium",
        user_story_id: Optional[str] = None,
    ) -> SpecReviewResult:
        """Generate spec and handle user review workflow.

        This is the main entry point for the workflow. It:
        1. Generates technical spec using SpecGenerator
        2. Calculates delivery estimate with buffer
        3. Saves spec to docs/
        4. Returns result with summary for user review

        Args:
            user_story: User story description (natural language)
            feature_type: Type of feature (crud, integration, ui, infrastructure, analytics, security)
            complexity: Overall complexity (low, medium, high)
            user_story_id: Optional user story ID (e.g., "US-016") for filename

        Returns:
            SpecReviewResult with spec, path, summary, and delivery estimate

        Example:
            >>> result = workflow.generate_and_review_spec(
            ...     "As a user, I want email notifications when tasks complete",
            ...     "integration",
            ...     "medium",
            ...     "US-033"
            ... )
            >>> print(result.summary['total_hours'])
            24.5
            >>> print(result.delivery_estimate['delivery_date'])
            '2025-10-20'
        """
        try:
            logger.info(f"Starting spec generation workflow for: '{user_story[:50]}...'")

            # Step 1: Generate technical spec
            spec = self.spec_generator.generate_spec_from_user_story(
                user_story=user_story, feature_type=feature_type, complexity=complexity
            )

            # Step 2: Render to markdown
            markdown = self.spec_generator.render_spec_to_markdown(spec)

            # Step 3: Calculate delivery estimate with buffer
            delivery_estimate = self._calculate_delivery_estimate(spec.total_hours, spec.confidence)

            # Step 4: Generate spec filename
            if user_story_id:
                spec_filename = f"{user_story_id.upper()}_TECHNICAL_SPEC.md"
            else:
                # Extract title from spec and slugify
                title_slug = self._slugify(spec.feature_name)
                spec_filename = f"{title_slug.upper()}_TECHNICAL_SPEC.md"

            # Step 5: Save spec to docs/
            spec_path = Path("docs") / spec_filename
            spec_path.write_text(markdown)

            logger.info(f"Spec saved to: {spec_path}")

            # Step 6: Build summary
            total_tasks = sum(len(phase.tasks) for phase in spec.phases)
            summary = {
                "total_hours": spec.total_hours,
                "total_days": spec.total_days,
                "phase_count": len(spec.phases),
                "task_count": total_tasks,
                "confidence": spec.confidence,
            }

            # Step 7: Build delivery estimate dict
            delivery_estimate_dict = {
                "total_hours": delivery_estimate.total_hours,
                "total_days": delivery_estimate.total_days,
                "buffer_percentage": delivery_estimate.buffer_percentage,
                "buffered_hours": delivery_estimate.buffered_hours,
                "buffered_days": delivery_estimate.buffered_days,
                "delivery_date": delivery_estimate.delivery_date,
                "confidence": delivery_estimate.confidence,
            }

            # Step 8: Create result
            result = SpecReviewResult(
                spec=spec,
                spec_path=spec_path,
                markdown=markdown,
                summary=summary,
                delivery_estimate=delivery_estimate_dict,
                approved=False,  # User hasn't approved yet
                rejection_reason=None,
            )

            logger.info(
                f"Spec generation complete: {summary['total_hours']}h "
                f"({summary['total_days']} days), "
                f"{summary['phase_count']} phases, "
                f"{summary['task_count']} tasks"
            )

            return result

        except Exception as e:
            logger.error(f"Spec generation workflow failed: {e}")
            raise Exception(f"Failed to generate and review spec: {str(e)}") from e

    def approve_spec(self, result: SpecReviewResult, user_story_id: str) -> bool:
        """Approve spec and update ROADMAP.md with estimate and spec reference.

        This is called after user reviews and approves the spec. It:
        1. Updates ROADMAP.md with estimated time
        2. Adds reference to technical spec
        3. Updates status to READY TO IMPLEMENT

        Args:
            result: SpecReviewResult from generate_and_review_spec()
            user_story_id: User story ID to update in ROADMAP (e.g., "US-016")

        Returns:
            True if successful

        Example:
            >>> result = workflow.generate_and_review_spec(...)
            >>> # User reviews and approves
            >>> workflow.approve_spec(result, "US-016")
            True
        """
        try:
            logger.info(f"Approving spec for {user_story_id}")

            # Mark result as approved
            result.approved = True

            # Update ROADMAP.md with spec reference and estimate
            self._update_roadmap_with_spec(user_story_id, result)

            logger.info(f"Spec approved and ROADMAP updated for {user_story_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to approve spec: {e}")
            raise

    def reject_spec(self, result: SpecReviewResult, reason: str) -> bool:
        """Reject spec with reason.

        This is called if user rejects the spec. The spec file is kept for reference
        but ROADMAP is not updated.

        Args:
            result: SpecReviewResult from generate_and_review_spec()
            reason: Reason for rejection (for logging/feedback)

        Returns:
            True if successful

        Example:
            >>> result = workflow.generate_and_review_spec(...)
            >>> # User rejects
            >>> workflow.reject_spec(result, "Scope too large, need to split into phases")
            True
        """
        try:
            logger.info(f"Rejecting spec at {result.spec_path}: {reason}")

            # Mark result as rejected
            result.approved = False
            result.rejection_reason = reason

            # Spec file is kept for reference, but we could optionally move it to a "rejected" folder
            # For now, just log the rejection

            logger.info(f"Spec rejected: {reason}")

            return True

        except Exception as e:
            logger.error(f"Failed to reject spec: {e}")
            raise

    def _calculate_delivery_estimate(self, total_hours: float, confidence: float) -> DeliveryEstimate:
        """Calculate delivery date based on hours and velocity.

        Applies intelligent buffer based on confidence and complexity.

        Args:
            total_hours: Total estimated hours from spec
            confidence: Confidence level (0.0-1.0)

        Returns:
            DeliveryEstimate with buffer and delivery date

        Example:
            >>> estimate = workflow._calculate_delivery_estimate(24.0, 0.85)
            >>> print(estimate.buffer_percentage)
            15
            >>> print(estimate.buffered_days)
            3.5
        """
        # Calculate buffer based on confidence
        # High confidence (0.9+) → 10% buffer
        # Medium confidence (0.7-0.9) → 15% buffer
        # Low confidence (<0.7) → 20% buffer
        if confidence >= 0.9:
            buffer_percentage = 10
        elif confidence >= 0.7:
            buffer_percentage = 15
        else:
            buffer_percentage = 20

        # Calculate buffered hours and days
        buffer_multiplier = 1 + (buffer_percentage / 100)
        buffered_hours = total_hours * buffer_multiplier
        buffered_days = buffered_hours / self.velocity_hours_per_day

        # Calculate delivery date
        # Assuming work starts today
        start_date = datetime.now()
        delivery_date = start_date + timedelta(days=buffered_days)

        return DeliveryEstimate(
            total_hours=total_hours,
            total_days=round(total_hours / 8, 1),  # 8h/day for display
            buffer_percentage=buffer_percentage,
            buffered_hours=round(buffered_hours, 1),
            buffered_days=round(buffered_days, 1),
            delivery_date=delivery_date.strftime("%Y-%m-%d"),
            confidence=confidence,
        )

    def _update_roadmap_with_spec(self, user_story_id: str, result: SpecReviewResult) -> None:
        """Update ROADMAP.md with spec reference and estimate.

        Args:
            user_story_id: User story ID (e.g., "US-016")
            result: SpecReviewResult with spec info

        Raises:
            Exception if ROADMAP update fails
        """
        try:
            # Read current ROADMAP
            roadmap_content = ROADMAP_PATH.read_text()

            # Find user story section
            story_pattern = f"## {user_story_id.upper()}"
            if story_pattern not in roadmap_content:
                logger.warning(f"{user_story_id} not found in ROADMAP, skipping update")
                return

            # Build update text
            estimate = result.delivery_estimate
            spec_ref = f"docs/{result.spec_path.name}"

            update_text = f"""
**Status**: 📝 READY TO IMPLEMENT
**Estimated Time**: {estimate['buffered_hours']} hours ({estimate['buffered_days']} days)
**Spec**: {spec_ref}
**Confidence**: {estimate['confidence']:.0%}
**Expected Delivery**: {estimate['delivery_date']} (with {estimate['buffer_percentage']}% buffer)
"""

            # Find insertion point (after user story header)
            lines = roadmap_content.split("\n")
            insert_index = -1
            for i, line in enumerate(lines):
                if story_pattern in line:
                    # Insert after header
                    insert_index = i + 1
                    break

            if insert_index == -1:
                raise Exception(f"Could not find insertion point for {user_story_id}")

            # Insert update text
            lines.insert(insert_index, update_text)

            # Write back to ROADMAP
            new_content = "\n".join(lines)
            ROADMAP_PATH.write_text(new_content)

            logger.info(f"ROADMAP updated with spec reference for {user_story_id}")

        except Exception as e:
            logger.error(f"Failed to update ROADMAP: {e}")
            raise

    def _slugify(self, text: str) -> str:
        """Convert text to slug for filename.

        Args:
            text: Text to slugify

        Returns:
            Slugified text (lowercase, hyphens, no special chars)

        Example:
            >>> workflow._slugify("Email Notifications System")
            'email-notifications-system'
        """
        import re

        # Lowercase
        text = text.lower()

        # Replace spaces with hyphens
        text = re.sub(r"\s+", "-", text)

        # Remove special characters
        text = re.sub(r"[^a-z0-9-]", "", text)

        # Remove duplicate hyphens
        text = re.sub(r"-+", "-", text)

        # Strip leading/trailing hyphens
        text = text.strip("-")

        return text

    def format_spec_summary(self, result: SpecReviewResult) -> str:
        """Format spec summary for display to user.

        Creates a formatted summary showing:
        - Total time estimate
        - Phase breakdown
        - Task count
        - Confidence level
        - Delivery date

        Args:
            result: SpecReviewResult to format

        Returns:
            Formatted summary string

        Example:
            >>> summary = workflow.format_spec_summary(result)
            >>> print(summary)
            Specification complete! 📋

            Total Estimated Time: 24 hours (3 days)
            Phases: 4
            Tasks: 12
            Confidence: 85%

            Spec saved to: docs/US-XXX_TECHNICAL_SPEC.md

            Would you like to review the spec? [y/n]
        """
        summary = result.summary
        estimate = result.delivery_estimate

        formatted = f"""
Specification complete! 📋

Total Estimated Time: {summary['total_hours']} hours ({summary['total_days']} days)
Phases: {summary['phase_count']}
Tasks: {summary['task_count']}
Confidence: {summary['confidence']:.0%}

With {estimate['buffer_percentage']}% buffer for unknowns:
- Buffered Time: {estimate['buffered_hours']} hours ({estimate['buffered_days']} days)
- Expected Delivery: {estimate['delivery_date']}

Spec saved to: {result.spec_path}

Would you like to review the spec? [y/n]
"""

        return formatted.strip()

    def format_roadmap_update_example(self, result: SpecReviewResult, user_story_id: str) -> str:
        """Format example of how ROADMAP will be updated.

        Shows user what will be added to ROADMAP when they approve the spec.

        Args:
            result: SpecReviewResult
            user_story_id: User story ID

        Returns:
            Formatted example string

        Example:
            >>> example = workflow.format_roadmap_update_example(result, "US-016")
            >>> print(example)
            When approved, ROADMAP.md will be updated:

            ## US-016: Email Notification System

            **Status**: 📝 READY TO IMPLEMENT
            **Estimated Time**: 24 hours (3 days)
            **Spec**: docs/US-016_TECHNICAL_SPEC.md
            **Confidence**: 85%
        """
        estimate = result.delivery_estimate

        example = f"""
When approved, ROADMAP.md will be updated:

## {user_story_id.upper()}: {result.spec.feature_name}

**Status**: 📝 READY TO IMPLEMENT
**Estimated Time**: {estimate['buffered_hours']} hours ({estimate['buffered_days']} days)
**Spec**: docs/{result.spec_path.name}
**Confidence**: {estimate['confidence']:.0%}
**Expected Delivery**: {estimate['delivery_date']} (with {estimate['buffer_percentage']}% buffer)
"""

        return example.strip()
