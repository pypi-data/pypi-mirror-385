"""Request classification system for interpreting user input types.

This module provides intelligent classification of user requests into:
- Feature requests (new functionality)
- Methodology changes (how we work)
- Hybrid requests (both feature + methodology)
- Clarification needed (ambiguous input)

The classifier uses keyword matching, pattern detection, and confidence scoring
to route user input to the appropriate documentation (ROADMAP vs TEAM_COLLABORATION).
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
import re


class RequestType(Enum):
    """Types of user requests."""

    FEATURE_REQUEST = "feature_request"  # User wants new functionality
    METHODOLOGY_CHANGE = "methodology_change"  # User wants to change how we work
    HYBRID = "hybrid"  # Both feature + methodology
    CLARIFICATION_NEEDED = "clarification_needed"  # Ambiguous, need to ask


@dataclass
class ClassificationResult:
    """Result of classifying a user request.

    Attributes:
        request_type: The classified type of request
        confidence: Confidence score from 0.0 to 1.0
        feature_indicators: List of feature indicators found in the text
        methodology_indicators: List of methodology indicators found in the text
        suggested_questions: Questions to ask for clarification (if needed)
        target_documents: Which documents should be updated based on classification
    """

    request_type: RequestType
    confidence: float  # 0.0-1.0
    feature_indicators: List[str]
    methodology_indicators: List[str]
    suggested_questions: List[str]  # Questions to ask for clarification
    target_documents: List[str]  # Which documents to update


class RequestClassifier:
    """Classifies user requests into feature requests, methodology changes, or both.

    The classifier uses multiple heuristics:
    1. Keyword matching (feature vs methodology keywords)
    2. Pattern detection (regex patterns for common phrasings)
    3. Confidence scoring (normalized based on indicator count)
    4. Threshold-based decision making

    Example:
        >>> classifier = RequestClassifier()
        >>> result = classifier.classify("I want to add email notifications")
        >>> print(result.request_type)
        RequestType.FEATURE_REQUEST
        >>> print(result.target_documents)
        ['docs/roadmap/ROADMAP.md']
    """

    # Feature request indicators
    FEATURE_KEYWORDS = {
        "want",
        "need",
        "add",
        "implement",
        "create",
        "build",
        "feature",
        "functionality",
        "capability",
        "able to",
        "should be able",
        "notification",
        "dashboard",
        "report",
        "integration",
        "api",
        "interface",
        "command",
        "tool",
        "button",
        "page",
        "view",
        "screen",
    }

    FEATURE_PATTERNS = [
        r"\b(I|we) (want|need|would like) to\b",
        r"\bas a .+, I (want|need) to\b",  # User story format
        r"\bshould (be able to|allow|enable|support)\b",
        r"\b(add|implement|create|build) (a|an|the)\b",
        r"\bnew (feature|functionality|capability)\b",
        r"\b(user|developer|system) (can|could|should be able to)\b",
    ]

    # Methodology change indicators
    METHODOLOGY_KEYWORDS = {
        "process",
        "workflow",
        "methodology",
        "approach",
        "way",
        "should work",
        "collaborate",
        "communication",
        "review",
        "approval",
        "git",
        "branching",
        "testing strategy",
        "ci/cd",
        "deployment",
        "always",
        "never",
        "policy",
        "guideline",
        "standard",
        "convention",
        "practice",
        "procedure",
        "strategy",
        "must have",
        "requires",
        "required",
        "tests",  # "Every PR must have tests" - methodology
    }

    METHODOLOGY_PATTERNS = [
        r"\bhow (we|you|the team) (should|must|need to) (work|collaborate|communicate)\b",
        r"\b(change|update|modify) (the|our) (process|workflow|methodology|approach)\b",
        r"\bfrom now on\b",
        r"\b(always|never) (do|use|follow|apply|implement)\b",
        r"\b(PM|project manager|developer|team) should (always|never|consistently)\b",
        r"\b(our|the) (policy|guideline|standard|convention|practice) (is|should be)\b",
        r"\b(every|each|all) (time|commit|PR|pull request|feature)\b",
    ]

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.67  # 2+ indicators
    MEDIUM_CONFIDENCE = 0.33  # 1+ indicator

    def classify(self, user_input: str) -> ClassificationResult:
        """Classify user input into request type.

        Args:
            user_input: Raw user input text to classify

        Returns:
            ClassificationResult with type, confidence, and suggestions

        The classification algorithm:
        1. Searches for feature and methodology indicators
        2. Calculates normalized scores (0.0-1.0)
        3. Determines request type based on scores and thresholds
        4. Generates appropriate clarifying questions if needed
        5. Identifies target documents for updates
        """
        # Handle edge cases
        if not user_input or not user_input.strip():
            return ClassificationResult(
                request_type=RequestType.CLARIFICATION_NEEDED,
                confidence=0.0,
                feature_indicators=[],
                methodology_indicators=[],
                suggested_questions=[
                    "Could you please provide more details about your request?",
                    "Are you suggesting a new feature or a process change?",
                ],
                target_documents=[],
            )

        lower_input = user_input.lower()

        # Find indicators
        feature_indicators = self._find_feature_indicators(lower_input)
        methodology_indicators = self._find_methodology_indicators(lower_input)

        # Calculate scores (normalize to 0.0-1.0 range)
        # Use a scaling factor that's more forgiving
        # With 3+ indicators, we're confident (3/3 = 1.0)
        # With 2 indicators, medium confidence (2/3 = 0.67)
        # With 1 indicator, low confidence (1/3 = 0.33)
        feature_score = min(len(feature_indicators) / 3.0, 1.0)
        methodology_score = min(len(methodology_indicators) / 3.0, 1.0)

        # Determine type based on scores
        if feature_score > self.MEDIUM_CONFIDENCE and methodology_score > self.MEDIUM_CONFIDENCE:
            # Both types present - hybrid request
            request_type = RequestType.HYBRID
            confidence = min(feature_score, methodology_score)
            target_docs = ["docs/roadmap/ROADMAP.md", "docs/COLLABORATION_METHODOLOGY.md"]
            questions = [
                "I see you're requesting both a feature and a methodology change. Should I:",
                "A) Focus on the feature first, then update methodology?",
                "B) Update methodology first, then implement feature?",
                "C) Handle them separately?",
            ]

        elif feature_score > methodology_score:
            # Feature request dominant
            if feature_score >= self.MEDIUM_CONFIDENCE:
                # Has at least 1 indicator - classify as feature
                request_type = RequestType.FEATURE_REQUEST
                confidence = feature_score
                target_docs = ["docs/roadmap/ROADMAP.md"]
                questions = []
            else:
                # No clear indicators
                request_type = RequestType.CLARIFICATION_NEEDED
                confidence = feature_score
                target_docs = []
                questions = [
                    "This looks like a feature request. Can you clarify:",
                    "- What specific functionality do you need?",
                    "- What problem does this solve?",
                    "- Are there any methodology/process changes needed?",
                ]

        elif methodology_score > feature_score:
            # Methodology change dominant
            if methodology_score >= self.MEDIUM_CONFIDENCE:
                # Has at least 1 indicator - classify as methodology
                request_type = RequestType.METHODOLOGY_CHANGE
                confidence = methodology_score
                target_docs = ["docs/COLLABORATION_METHODOLOGY.md", ".claude/CLAUDE.md"]
                questions = []
            else:
                # No clear indicators
                request_type = RequestType.CLARIFICATION_NEEDED
                confidence = methodology_score
                target_docs = []
                questions = [
                    "This looks like a methodology change. Can you clarify:",
                    "- What process/workflow should change?",
                    "- Why is this change needed?",
                    "- Should this apply to all future work?",
                ]

        else:
            # Ambiguous - no clear indicators
            request_type = RequestType.CLARIFICATION_NEEDED
            confidence = max(feature_score, methodology_score)
            target_docs = []
            questions = [
                "I'm not sure if this is a feature request or a methodology change.",
                "Can you help me understand:",
                "- Are you requesting new functionality (feature)?",
                "- Are you suggesting how we should work differently (methodology)?",
                "- Or both?",
            ]

        return ClassificationResult(
            request_type=request_type,
            confidence=confidence,
            feature_indicators=feature_indicators,
            methodology_indicators=methodology_indicators,
            suggested_questions=questions,
            target_documents=target_docs,
        )

    def _find_feature_indicators(self, text: str) -> List[str]:
        """Find feature request indicators in text.

        Args:
            text: Lowercased text to search

        Returns:
            List of indicators found (e.g., "keyword: want", "pattern: ...")
        """
        indicators = []

        # Check keywords
        for keyword in self.FEATURE_KEYWORDS:
            if keyword in text:
                indicators.append(f"keyword: {keyword}")

        # Check patterns
        for pattern in self.FEATURE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                indicators.append(f"pattern: {pattern}")

        return indicators

    def _find_methodology_indicators(self, text: str) -> List[str]:
        """Find methodology change indicators in text.

        Args:
            text: Lowercased text to search

        Returns:
            List of indicators found (e.g., "keyword: process", "pattern: ...")
        """
        indicators = []

        # Check keywords
        for keyword in self.METHODOLOGY_KEYWORDS:
            if keyword in text:
                indicators.append(f"keyword: {keyword}")

        # Check patterns
        for pattern in self.METHODOLOGY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                indicators.append(f"pattern: {pattern}")

        return indicators
