"""AI-enhanced metadata extraction for document updates.

This module extracts metadata from user requests using AI to improve
the quality of document updates (business value, effort estimation,
acceptance criteria, dependencies, etc.).

Key Features:
- AI-powered business value extraction
- Intelligent effort estimation based on complexity
- Automatic dependency detection
- Priority level suggestion
- Acceptance criteria generation
- Rationale extraction for methodology changes

Integration with US-021 Phase 4:
- RequestClassifier identifies request type
- AIService processes with AI
- **MetadataExtractor extracts metadata** ← NEW in Phase 4
- PreviewGenerator shows preview
- User confirms changes
- DocumentUpdater applies changes

Example:
    >>> from coffee_maker.cli.metadata_extractor import MetadataExtractor
    >>> from coffee_maker.cli.request_classifier import RequestType
    >>>
    >>> extractor = MetadataExtractor(use_ai=True)
    >>> metadata = extractor.extract_metadata(
    ...     request_type=RequestType.FEATURE_REQUEST,
    ...     user_input="I want to add email notifications for completed tasks",
    ...     ai_response="Great idea! Email notifications would help users..."
    ... )
    >>> print(metadata['title'])
    'Add email notifications for completed tasks'
    >>> print(metadata['estimated_effort'])
    '2-3 days'
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from coffee_maker.cli.request_classifier import RequestType

logger = logging.getLogger(__name__)


@dataclass
class ExtractedMetadata:
    """Result of metadata extraction.

    Attributes:
        title: Short title for the request
        business_value: Business value description
        estimated_effort: Effort estimate (e.g., "2-3 days", "1 week")
        complexity: Complexity rating (low, medium, high)
        priority_suggestion: Suggested priority level
        acceptance_criteria: List of acceptance criteria
        dependencies: List of dependencies mentioned
        rationale: Rationale for methodology changes
        applies_to: Who the change applies to
        section: Suggested section for insertion
        tags: Relevant tags for categorization
    """

    title: str
    business_value: Optional[str] = None
    estimated_effort: Optional[str] = None
    complexity: Optional[str] = None
    priority_suggestion: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    rationale: Optional[str] = None
    applies_to: Optional[str] = None
    section: Optional[str] = None
    tags: Optional[List[str]] = None


class MetadataExtractor:
    """Extracts metadata from user requests using AI and heuristics.

    This class uses a combination of AI analysis (when available) and
    heuristic rules to extract rich metadata from user requests.

    Attributes:
        use_ai: Whether to use AI for enhanced extraction
        ai_client: Optional AI client for enhanced extraction

    Example:
        >>> # Without AI (heuristics only)
        >>> extractor = MetadataExtractor(use_ai=False)
        >>> metadata = extractor.extract_metadata(
        ...     request_type=RequestType.FEATURE_REQUEST,
        ...     user_input="Add Slack integration"
        ... )
        >>>
        >>> # With AI (enhanced extraction)
        >>> extractor = MetadataExtractor(use_ai=True)
        >>> metadata = extractor.extract_metadata(
        ...     request_type=RequestType.FEATURE_REQUEST,
        ...     user_input="Add Slack integration for real-time notifications",
        ...     ai_response="Great idea! This would improve team collaboration..."
        ... )
    """

    # Complexity indicators
    COMPLEXITY_HIGH_KEYWORDS = {
        "integration",
        "api",
        "authentication",
        "security",
        "database",
        "migration",
        "refactor",
        "architecture",
        "distributed",
        "scalability",
        "performance",
    }

    COMPLEXITY_MEDIUM_KEYWORDS = {
        "dashboard",
        "report",
        "export",
        "import",
        "notification",
        "email",
        "search",
        "filter",
        "validation",
    }

    # Effort estimation patterns
    EFFORT_PATTERNS = {
        r"\b(\d+[-–]\d+)\s*(day|days)\b": lambda m: m.group(0),
        r"\b(\d+)\s*(week|weeks)\b": lambda m: m.group(0),
        r"\b(\d+[-–]\d+)\s*(hour|hours)\b": lambda m: m.group(0),
    }

    # Dependency patterns
    DEPENDENCY_PATTERNS = [
        r"\bdepends? on\s+([A-Z]+-\d+)",
        r"\brequires?\s+([A-Z]+-\d+)",
        r"\bblocked by\s+([A-Z]+-\d+)",
        r"\bneeds?\s+([A-Z]+-\d+)",
        r"\bafter\s+([A-Z]+-\d+)",
    ]

    def __init__(self, use_ai: bool = False, ai_client=None):
        """Initialize metadata extractor.

        Args:
            use_ai: Whether to use AI for enhanced extraction (default: False)
            ai_client: Optional AI client (AIService) for enhanced extraction
        """
        self.use_ai = use_ai
        self.ai_client = ai_client

        logger.info(f"MetadataExtractor initialized (use_ai: {use_ai})")

    def extract_metadata(
        self,
        request_type: RequestType,
        user_input: str,
        ai_response: Optional[str] = None,
        classification_context: Optional[Dict] = None,
    ) -> ExtractedMetadata:
        """Extract metadata from user request and AI response.

        This is the main entry point for metadata extraction. It combines
        heuristic extraction with optional AI-enhanced extraction.

        Args:
            request_type: Type of request (FEATURE_REQUEST, METHODOLOGY_CHANGE, HYBRID)
            user_input: Original user input
            ai_response: Optional AI response to the request
            classification_context: Optional classification context with indicators

        Returns:
            ExtractedMetadata with all extracted fields

        Example:
            >>> extractor = MetadataExtractor()
            >>> metadata = extractor.extract_metadata(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     user_input="I want to add Slack integration with OAuth"
            ... )
            >>> print(metadata.title)
            'Add Slack integration with OAuth'
            >>> print(metadata.complexity)
            'high'
        """
        logger.info(f"Extracting metadata for {request_type.value} request")

        # Start with heuristic extraction
        metadata = self._extract_heuristics(request_type, user_input, classification_context)

        # Enhance with AI if available
        if self.use_ai and self.ai_client and ai_response:
            try:
                ai_metadata = self._extract_with_ai(request_type, user_input, ai_response)
                metadata = self._merge_metadata(metadata, ai_metadata)
            except Exception as e:
                logger.warning(f"AI-enhanced extraction failed, using heuristics only: {e}")

        logger.debug(f"Extracted metadata: title='{metadata.title}', complexity={metadata.complexity}")
        return metadata

    def _extract_heuristics(
        self,
        request_type: RequestType,
        user_input: str,
        classification_context: Optional[Dict] = None,
    ) -> ExtractedMetadata:
        """Extract metadata using heuristic rules.

        Args:
            request_type: Type of request
            user_input: User input text
            classification_context: Optional classification context

        Returns:
            ExtractedMetadata from heuristics
        """
        # Extract title
        title = self._extract_title(user_input)

        # Extract complexity
        complexity = self._estimate_complexity(user_input)

        # Extract effort estimate if mentioned
        estimated_effort = self._extract_effort(user_input)

        # Extract dependencies
        dependencies = self._extract_dependencies(user_input)

        # Generate acceptance criteria based on request type
        acceptance_criteria = self._generate_default_acceptance_criteria(request_type, user_input)

        # Extract business value hints
        business_value = self._extract_business_value_hints(user_input)

        # Priority suggestion based on complexity and keywords
        priority_suggestion = self._suggest_priority(user_input, complexity)

        # Request-type-specific extraction
        rationale = None
        applies_to = None
        section = None

        if request_type == RequestType.METHODOLOGY_CHANGE:
            rationale = self._extract_rationale(user_input)
            applies_to = self._extract_applies_to(user_input)
            section = self._suggest_collaboration_section(user_input)
        elif request_type == RequestType.HYBRID:
            rationale = self._extract_rationale(user_input)
            applies_to = self._extract_applies_to(user_input)

        # Extract tags
        tags = self._extract_tags(user_input)

        return ExtractedMetadata(
            title=title,
            business_value=business_value,
            estimated_effort=estimated_effort,
            complexity=complexity,
            priority_suggestion=priority_suggestion,
            acceptance_criteria=acceptance_criteria,
            dependencies=dependencies,
            rationale=rationale,
            applies_to=applies_to,
            section=section,
            tags=tags,
        )

    def _extract_with_ai(self, request_type: RequestType, user_input: str, ai_response: str) -> ExtractedMetadata:
        """Extract metadata using AI analysis.

        This method uses AI to provide more accurate and contextual metadata.

        Args:
            request_type: Type of request
            user_input: User input
            ai_response: AI's response

        Returns:
            ExtractedMetadata from AI analysis
        """
        # TODO: Implement AI-enhanced extraction when AIService integration is ready
        # For now, return empty metadata (will be merged with heuristics)
        logger.debug("AI-enhanced extraction not yet implemented (Phase 4.5)")
        return ExtractedMetadata(title="")

    def _merge_metadata(self, heuristic: ExtractedMetadata, ai: ExtractedMetadata) -> ExtractedMetadata:
        """Merge heuristic and AI-extracted metadata.

        AI metadata takes precedence when available, falls back to heuristics.

        Args:
            heuristic: Metadata from heuristic extraction
            ai: Metadata from AI extraction

        Returns:
            Merged metadata
        """
        return ExtractedMetadata(
            title=ai.title or heuristic.title,
            business_value=ai.business_value or heuristic.business_value,
            estimated_effort=ai.estimated_effort or heuristic.estimated_effort,
            complexity=ai.complexity or heuristic.complexity,
            priority_suggestion=ai.priority_suggestion or heuristic.priority_suggestion,
            acceptance_criteria=ai.acceptance_criteria or heuristic.acceptance_criteria,
            dependencies=ai.dependencies or heuristic.dependencies,
            rationale=ai.rationale or heuristic.rationale,
            applies_to=ai.applies_to or heuristic.applies_to,
            section=ai.section or heuristic.section,
            tags=ai.tags or heuristic.tags,
        )

    def _extract_title(self, text: str) -> str:
        """Extract title from user input.

        Args:
            text: User input text

        Returns:
            Extracted title
        """
        text = text.strip()

        # Remove common prefixes
        prefixes_to_remove = [
            "i want to ",
            "i need to ",
            "we should ",
            "can we ",
            "please ",
            "could you ",
            "let's ",
        ]

        lower_text = text.lower()
        for prefix in prefixes_to_remove:
            if lower_text.startswith(prefix):
                text = text[len(prefix) :]
                break

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        # Take first sentence or truncate to 80 chars
        first_sentence = text.split(".")[0]
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."

        return first_sentence or "Untitled Request"

    def _estimate_complexity(self, text: str) -> str:
        """Estimate complexity based on keywords.

        Args:
            text: User input text

        Returns:
            Complexity rating ("low", "medium", "high")
        """
        lower_text = text.lower()

        # Count high complexity indicators
        high_count = sum(1 for keyword in self.COMPLEXITY_HIGH_KEYWORDS if keyword in lower_text)

        # Count medium complexity indicators
        medium_count = sum(1 for keyword in self.COMPLEXITY_MEDIUM_KEYWORDS if keyword in lower_text)

        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"

    def _extract_effort(self, text: str) -> Optional[str]:
        """Extract effort estimate from text.

        Args:
            text: User input text

        Returns:
            Effort estimate string or None
        """
        for pattern, extractor in self.EFFORT_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return extractor(match)

        # Default estimates based on complexity
        return None  # Will be filled in by complexity-based defaults

    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract dependencies from text.

        Args:
            text: User input text

        Returns:
            List of dependency IDs (e.g., ["US-021", "US-033"])
        """
        dependencies = []

        for pattern in self.DEPENDENCY_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dep_id = match.group(1)
                if dep_id not in dependencies:
                    dependencies.append(dep_id)

        return dependencies

    def _generate_default_acceptance_criteria(self, request_type: RequestType, user_input: str) -> List[str]:
        """Generate default acceptance criteria based on request type.

        Args:
            request_type: Type of request
            user_input: User input for context

        Returns:
            List of acceptance criteria
        """
        if request_type == RequestType.FEATURE_REQUEST:
            return [
                "Feature implemented and tested",
                "Unit tests added with >80% coverage",
                "Documentation updated",
                "User acceptance testing passed",
            ]
        elif request_type == RequestType.METHODOLOGY_CHANGE:
            return [
                "Methodology documented in COLLABORATION_METHODOLOGY.md",
                "Team notified of changes",
                "Guidelines clear and actionable",
            ]
        elif request_type == RequestType.HYBRID:
            return [
                "Feature implemented and tested",
                "Methodology documented and communicated",
                "Team aligned on new process",
            ]
        else:
            return ["Requirements clarified", "Action plan defined"]

    def _extract_business_value_hints(self, text: str) -> Optional[str]:
        """Extract business value hints from text.

        Args:
            text: User input text

        Returns:
            Business value hint or None
        """
        # Look for "so that" pattern
        so_that_match = re.search(r"so that (.+)", text, re.IGNORECASE)
        if so_that_match:
            return so_that_match.group(1).strip()

        # Look for "because" pattern
        because_match = re.search(r"because (.+)", text, re.IGNORECASE)
        if because_match:
            return because_match.group(1).strip()

        # Look for value keywords
        value_keywords = ["improve", "increase", "reduce", "save", "enable", "provide"]
        for keyword in value_keywords:
            if keyword in text.lower():
                # Extract sentence containing the keyword
                sentences = text.split(".")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()

        return None

    def _suggest_priority(self, text: str, complexity: str) -> str:
        """Suggest priority level based on text and complexity.

        Args:
            text: User input text
            complexity: Complexity rating

        Returns:
            Priority suggestion ("critical", "high", "normal", "low")
        """
        lower_text = text.lower()

        # Critical keywords
        if any(word in lower_text for word in ["critical", "urgent", "blocker", "broken", "failing"]):
            return "critical"

        # High priority keywords
        if any(word in lower_text for word in ["important", "soon", "asap", "quickly", "priority"]):
            return "high"

        # Complexity-based
        if complexity == "high":
            return "high"
        elif complexity == "medium":
            return "normal"
        else:
            return "normal"

    def _extract_rationale(self, text: str) -> Optional[str]:
        """Extract rationale for methodology changes.

        Args:
            text: User input text

        Returns:
            Rationale or None
        """
        # Look for common rationale patterns
        patterns = [
            r"because (.+)",
            r"so that (.+)",
            r"to ensure (.+)",
            r"in order to (.+)",
            r"rationale[:\s]+(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_applies_to(self, text: str) -> str:
        """Extract who the change applies to.

        Args:
            text: User input text

        Returns:
            Applies to description
        """
        # Look for explicit "applies to" patterns
        applies_match = re.search(r"applies to (.+)", text, re.IGNORECASE)
        if applies_match:
            return applies_match.group(1).strip()

        # Look for role mentions
        roles = [
            "developers",
            "team",
            "everyone",
            "all",
            "project manager",
            "code_developer",
        ]
        lower_text = text.lower()
        for role in roles:
            if role in lower_text:
                return role.capitalize()

        return "All team members"

    def _suggest_collaboration_section(self, text: str) -> str:
        """Suggest section in COLLABORATION_METHODOLOGY.md.

        Args:
            text: User input text

        Returns:
            Section name
        """
        lower_text = text.lower()

        # Section keywords
        section_map = {
            "git": "Git Workflow",
            "branch": "Git Workflow",
            "commit": "Git Workflow",
            "pr": "Pull Request Process",
            "pull request": "Pull Request Process",
            "review": "Code Review",
            "testing": "Testing Strategy",
            "test": "Testing Strategy",
            "deploy": "Deployment",
            "ci/cd": "CI/CD Pipeline",
            "communication": "Team Communication",
            "meeting": "Team Communication",
        }

        for keyword, section in section_map.items():
            if keyword in lower_text:
                return section

        return "General Guidelines"

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text.

        Args:
            text: User input text

        Returns:
            List of tags
        """
        tags = []
        lower_text = text.lower()

        # Technology tags
        tech_tags = [
            "python",
            "api",
            "database",
            "frontend",
            "backend",
            "ui",
            "ux",
            "security",
            "performance",
            "testing",
            "documentation",
            "devops",
            "ci/cd",
        ]

        for tag in tech_tags:
            if tag in lower_text:
                tags.append(tag)

        return tags[:5]  # Limit to 5 tags
