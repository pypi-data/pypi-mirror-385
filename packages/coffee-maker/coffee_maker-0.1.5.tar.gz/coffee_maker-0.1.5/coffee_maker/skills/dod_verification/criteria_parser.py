"""
Criteria Parser: Extract DoD criteria from priority descriptions.

Parses acceptance criteria from priority descriptions to create structured DoD checklists.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class DoDCriterion:
    """A single DoD criterion."""

    id: str  # e.g., "criterion_1"
    description: str  # e.g., "User can create new recipe"
    type: str  # "functionality", "testing", "quality", "documentation", "integration"
    priority: str  # "MUST", "SHOULD", "NICE_TO_HAVE"
    verification_method: str  # "automated_test", "manual_test", "code_review", "visual"
    status: str = "pending"  # "pending", "pass", "fail"


class CriteriaParser:
    """Parse DoD criteria from priority descriptions."""

    # Patterns for identifying criteria types
    MUST_KEYWORDS = ["must", "shall", "required", "mandatory", "critical"]
    SHOULD_KEYWORDS = ["should", "recommended", "important"]
    TEST_KEYWORDS = ["test", "coverage", "passing"]
    DOC_KEYWORDS = ["document", "readme", "comment", "docstring"]
    QUALITY_KEYWORDS = ["format", "lint", "type hint", "black", "quality"]

    def parse_criteria(self, description: str) -> List[DoDCriterion]:
        """
        Parse DoD criteria from priority description.

        Args:
            description: Full priority description

        Returns:
            List of DoDCriterion objects
        """
        criteria = []

        # Extract explicit acceptance criteria section
        acceptance_section = self._extract_acceptance_section(description)

        if acceptance_section:
            # Parse numbered/bulleted list
            criteria.extend(self._parse_list_items(acceptance_section))

        # Extract implicit criteria from description (only if no explicit criteria found)
        if not criteria:
            implicit = self._extract_implicit_criteria(description)
            criteria.extend(implicit)

        # If no criteria found, create basic default criteria
        if not criteria:
            criteria = self._get_default_criteria()

        # Assign IDs
        for i, criterion in enumerate(criteria, 1):
            criterion.id = f"criterion_{i}"

        return criteria

    def _extract_acceptance_section(self, description: str) -> str:
        """Extract acceptance criteria section from description."""
        # Look for "Acceptance Criteria:" or "Definition of Done:" sections
        # Stop at next section marker (double newline + **) or end
        patterns = [
            r"\*\*Acceptance Criteria\*\*:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"Acceptance Criteria:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"\*\*Definition of Done\*\*:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"Definition of Done:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"\*\*DoD\*\*:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"DoD:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"\*\*Criteria\*\*:(.+?)(?=\n\s*\n\s*\*\*|$)",
            r"Criteria:(.+?)(?=\n\s*\n\s*\*\*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, description, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _parse_list_items(self, text: str) -> List[DoDCriterion]:
        """Parse bulleted/numbered list items into criteria."""
        criteria = []
        seen_descriptions = set()  # Track unique criteria to avoid duplicates

        # Match patterns like "- [ ]", "1.", "- ", etc.
        # Try specific patterns first (checkbox), then fallback to general patterns
        patterns = [
            r"- \[ \] (.+)",  # Checkbox: - [ ] Item
            r"- \[x\] (.+)",  # Checked: - [x] Item
            r"\d+\. (.+)",  # Numbered: 1. Item
            r"- (.+)",  # Bullet: - Item
            r"\* (.+)",  # Asterisk: * Item
        ]

        # Try each pattern and use the first one that finds matches
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                for match in matches:
                    item_text = match.strip()
                    # Skip if too short or already seen
                    if item_text and len(item_text) > 5 and item_text.lower() not in seen_descriptions:
                        criterion = self._create_criterion_from_text(item_text)
                        criteria.append(criterion)
                        seen_descriptions.add(item_text.lower())
                # If we found matches with this pattern, don't try more general patterns
                # to avoid duplicates (e.g., "- [ ] Item" would also match "- (.+)")
                if criteria:
                    break

        return criteria

    def _extract_implicit_criteria(self, description: str) -> List[DoDCriterion]:
        """Extract implicit criteria based on keywords."""
        criteria = []

        # If description mentions tests, add test criterion
        if any(keyword in description.lower() for keyword in self.TEST_KEYWORDS):
            criteria.append(
                DoDCriterion(
                    id="",
                    description="All tests passing",
                    type="testing",
                    priority="MUST",
                    verification_method="automated_test",
                )
            )

        # If description mentions documentation
        if any(keyword in description.lower() for keyword in self.DOC_KEYWORDS):
            criteria.append(
                DoDCriterion(
                    id="",
                    description="Documentation updated",
                    type="documentation",
                    priority="MUST",
                    verification_method="code_review",
                )
            )

        # If description mentions code quality
        if any(keyword in description.lower() for keyword in self.QUALITY_KEYWORDS):
            criteria.append(
                DoDCriterion(
                    id="",
                    description="Code follows quality standards",
                    type="quality",
                    priority="MUST",
                    verification_method="automated_check",
                )
            )

        return criteria

    def _create_criterion_from_text(self, text: str) -> DoDCriterion:
        """Create DoD criterion from text description."""
        # Determine priority
        priority = "MUST"
        for keyword in self.MUST_KEYWORDS:
            if keyword in text.lower():
                priority = "MUST"
                break
        for keyword in self.SHOULD_KEYWORDS:
            if keyword in text.lower():
                priority = "SHOULD"
                break

        # Determine type and verification method
        criterion_type = "functionality"
        verification_method = "manual_test"

        if any(keyword in text.lower() for keyword in self.TEST_KEYWORDS):
            criterion_type = "testing"
            verification_method = "automated_test"
        elif any(keyword in text.lower() for keyword in self.DOC_KEYWORDS):
            criterion_type = "documentation"
            verification_method = "code_review"
        elif any(keyword in text.lower() for keyword in self.QUALITY_KEYWORDS):
            criterion_type = "quality"
            verification_method = "automated_check"
        elif "ui" in text.lower() or "interface" in text.lower() or "display" in text.lower():
            criterion_type = "functionality"
            verification_method = "visual"

        return DoDCriterion(
            id="",
            description=text,
            type=criterion_type,
            priority=priority,
            verification_method=verification_method,
        )

    def _get_default_criteria(self) -> List[DoDCriterion]:
        """Get default DoD criteria when none are explicitly specified."""
        return [
            DoDCriterion(
                id="",
                description="All tests passing",
                type="testing",
                priority="MUST",
                verification_method="automated_test",
            ),
            DoDCriterion(
                id="",
                description="Code formatted with Black",
                type="quality",
                priority="MUST",
                verification_method="automated_check",
            ),
            DoDCriterion(
                id="",
                description="Documentation updated",
                type="documentation",
                priority="SHOULD",
                verification_method="code_review",
            ),
            DoDCriterion(
                id="",
                description="No breaking changes",
                type="integration",
                priority="MUST",
                verification_method="automated_test",
            ),
        ]
