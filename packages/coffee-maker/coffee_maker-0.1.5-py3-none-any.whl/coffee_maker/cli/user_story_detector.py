"""User Story Detection - Automatically detect user stories in natural language.

This module provides intelligent user story detection using pattern matching
and AI-powered confidence scoring. It can detect both formal ("As a X I want Y
so that Z") and informal ("I want to...") user story patterns.

Example:
    >>> from coffee_maker.cli.user_story_detector import UserStoryDetector
    >>> from coffee_maker.cli.ai_service import AIService
    >>>
    >>> detector = UserStoryDetector(ai_service=AIService())
    >>> detection = detector.detect("As a developer I want to deploy on GCP so it runs 24/7")
    >>> print(detection.confidence)
    0.95
    >>> print(detection.as_a)
    'developer'
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class UserStoryDetection:
    """Result of user story detection.

    Attributes:
        raw_input: Original user input
        as_a: Detected role/actor (e.g., "developer", "user")
        i_want: Detected feature/capability
        so_that: Detected benefit/value
        confidence: Confidence score 0.0-1.0
        suggested_title: AI-generated title for the user story
        suggested_category: Suggested category (feature, integration, etc.)
        is_user_story: True if detected as user story (confidence > threshold)
        detection_method: How it was detected ("formal_pattern", "informal_ai", "ai_enhanced")
    """

    raw_input: str
    as_a: str = ""
    i_want: str = ""
    so_that: str = ""
    confidence: float = 0.0
    suggested_title: str = ""
    suggested_category: str = "feature"
    is_user_story: bool = False
    detection_method: str = "none"

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "raw_input": self.raw_input,
            "as_a": self.as_a,
            "i_want": self.i_want,
            "so_that": self.so_that,
            "confidence": self.confidence,
            "suggested_title": self.suggested_title,
            "suggested_category": self.suggested_category,
            "is_user_story": self.is_user_story,
            "detection_method": self.detection_method,
        }


class UserStoryDetector:
    """Detects user stories in natural language input.

    Uses a combination of:
    1. Regex pattern matching for formal user stories
    2. AI-powered analysis for informal user stories
    3. Confidence scoring to determine if input is a user story

    The detector triggers on confidence > 0.70 (70%).

    Attributes:
        ai_service: AIService instance for AI-powered detection
        confidence_threshold: Minimum confidence to classify as user story (default: 0.70)

    Example:
        >>> detector = UserStoryDetector(ai_service=AIService())
        >>> # Formal format detection
        >>> detection = detector.detect("As a developer I want CI/CD so builds are automated")
        >>> detection.is_user_story
        True
        >>> detection.confidence
        1.0
        >>> # Informal format detection
        >>> detection = detector.detect("I need email notifications when tasks complete")
        >>> detection.is_user_story
        True
        >>> detection.confidence >= 0.75
        True
    """

    # Formal user story patterns (high confidence)
    FORMAL_PATTERNS = [
        # Standard format: "As a X, I want Y so that Z"
        r"as\s+a(?:n)?\s+(?P<role>.+?),?\s+I\s+(?:want|need)\s+(?P<want>.+?)(?:\s+so\s+that\s+(?P<so_that>.+?))?$",
        # Variation: "As a X, I want to Y so that Z"
        r"as\s+a(?:n)?\s+(?P<role>.+?),?\s+I\s+(?:want|need)\s+to\s+(?P<want>.+?)(?:\s+so\s+that\s+(?P<so_that>.+?))?$",
        # Variation with benefit first: "So that X, as a Y, I want Z"
        r"so\s+that\s+(?P<so_that>.+?),\s+as\s+a(?:n)?\s+(?P<role>.+?),?\s+I\s+(?:want|need)\s+(?:to\s+)?(?P<want>.+?)$",
    ]

    # Informal patterns (require AI validation)
    INFORMAL_PATTERNS = [
        r"(?i)^I\s+(?:want|need)\s+(?:to\s+)?(.+)",
        r"(?i)^We\s+(?:should|need\s+to|want\s+to)\s+(.+)",
        r"(?i)^Can\s+(?:we|you)\s+(?:add|implement|create|build)\s+(.+)",
        r"(?i)^(?:Add|Implement|Create|Build)\s+(.+)",
        r"(?i)^(?:Would\s+be\s+nice|It\s+would\s+be\s+good)\s+(?:to\s+have|if\s+we\s+had)\s+(.+)",
    ]

    def __init__(self, ai_service: Optional["AIService"] = None, confidence_threshold: float = 0.70):
        """Initialize user story detector.

        Args:
            ai_service: AIService instance for AI-powered detection (optional)
            confidence_threshold: Minimum confidence to classify as user story (default: 0.70)
        """
        self.ai_service = ai_service
        self.confidence_threshold = confidence_threshold
        logger.info(f"UserStoryDetector initialized (threshold: {confidence_threshold:.0%})")

    def detect(self, user_input: str) -> UserStoryDetection:
        """Detect user story components in user input.

        Process:
        1. Try formal pattern matching (regex)
        2. If no match, try informal pattern matching
        3. Use AI to enhance/validate detection
        4. Calculate confidence score
        5. Return detection result

        Args:
            user_input: Raw user input text

        Returns:
            UserStoryDetection with extracted components and confidence score

        Example:
            >>> detector = UserStoryDetector()
            >>> # Formal format
            >>> result = detector.detect("As a user I want email alerts so I stay informed")
            >>> result.confidence >= 0.9
            True
            >>> result.as_a
            'user'
            >>> # Informal format (requires AI)
            >>> result = detector.detect("I need a dashboard to visualize metrics")
            >>> result.is_user_story
            True  # If AI service available
        """
        if not user_input or not user_input.strip():
            return UserStoryDetection(
                raw_input="",
                confidence=0.0,
                is_user_story=False,
                detection_method="empty_input",
            )

        # Step 1: Try formal pattern matching
        formal_detection = self._detect_formal_pattern(user_input)
        if formal_detection and formal_detection.confidence >= 0.90:
            logger.info(
                f"Formal user story detected (confidence: {formal_detection.confidence:.0%}): "
                f"{formal_detection.suggested_title}"
            )
            return formal_detection

        # Step 2: Try informal pattern matching
        informal_match = self._detect_informal_pattern(user_input)

        # Step 3: Use AI to enhance/validate
        if self.ai_service:
            if formal_detection:
                # Enhance formal detection with AI
                ai_detection = self._ai_enhance_detection(formal_detection)
                logger.info(f"AI-enhanced detection (confidence: {ai_detection.confidence:.0%})")
                return ai_detection
            elif informal_match:
                # Validate informal with AI
                ai_detection = self._ai_validate_informal(user_input, informal_match)
                logger.info(
                    f"AI-validated informal user story (confidence: {ai_detection.confidence:.0%}): "
                    f"{ai_detection.suggested_title}"
                )
                return ai_detection
            else:
                # Try pure AI detection
                ai_detection = self._ai_detect_user_story(user_input)
                if ai_detection.confidence >= self.confidence_threshold:
                    logger.info(f"AI-detected user story (confidence: {ai_detection.confidence:.0%})")
                    return ai_detection

        # Step 4: Return best effort (might not be user story)
        if formal_detection:
            return formal_detection
        elif informal_match:
            # Informal without AI validation - low confidence
            return UserStoryDetection(
                raw_input=user_input,
                i_want=informal_match,
                confidence=0.50,  # Medium-low confidence without AI
                is_user_story=False,  # Don't trigger without AI validation
                detection_method="informal_pattern",
            )
        else:
            # Not detected as user story
            return UserStoryDetection(
                raw_input=user_input,
                confidence=0.0,
                is_user_story=False,
                detection_method="no_match",
            )

    def _detect_formal_pattern(self, text: str) -> Optional[UserStoryDetection]:
        """Detect formal user story pattern with regex.

        Args:
            text: User input text

        Returns:
            UserStoryDetection if formal pattern found, else None

        Example:
            >>> detector = UserStoryDetector()
            >>> result = detector._detect_formal_pattern(
            ...     "As a developer, I want CI/CD so that builds are automated"
            ... )
            >>> result.as_a
            'developer'
            >>> result.i_want
            'CI/CD'
            >>> result.so_that
            'builds are automated'
        """
        for pattern in self.FORMAL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                groups = match.groupdict()

                role = groups.get("role", "") or ""
                want = groups.get("want", "") or ""
                so_that = groups.get("so_that", "") or ""

                # Handle None values from regex
                role = role.strip() if role else ""
                want = want.strip() if want else ""
                so_that = so_that.strip() if so_that else ""

                # Clean up extracted text
                role = self._clean_text(role) if role else ""
                want = self._clean_text(want) if want else ""
                so_that = self._clean_text(so_that) if so_that else ""

                # Skip if we didn't extract meaningful role and want
                if not role or not want:
                    continue

                # Generate title
                title = self._generate_title(role, want, so_that)

                # Calculate confidence (formal patterns are high confidence)
                confidence = 1.0 if so_that else 0.95  # Slightly lower if no "so that"

                return UserStoryDetection(
                    raw_input=text,
                    as_a=role,
                    i_want=want,
                    so_that=so_that,
                    confidence=confidence,
                    suggested_title=title,
                    is_user_story=True,
                    detection_method="formal_pattern",
                )

        return None

    def _detect_informal_pattern(self, text: str) -> Optional[str]:
        """Detect informal user story pattern.

        Returns the main feature request if found.

        Args:
            text: User input text

        Returns:
            Extracted feature request string, or None

        Example:
            >>> detector = UserStoryDetector()
            >>> result = detector._detect_informal_pattern("I want to add email notifications")
            >>> "email notifications" in result
            True
        """
        for pattern in self.INFORMAL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                feature = match.group(1).strip()
                return self._clean_text(feature)

        return None

    def _ai_enhance_detection(self, detection: UserStoryDetection) -> UserStoryDetection:
        """Use AI to enhance formal detection with better title and category.

        Args:
            detection: Initial detection from formal pattern

        Returns:
            Enhanced detection with AI-generated title and category
        """
        if not self.ai_service:
            return detection

        try:
            prompt = f"""Enhance this user story detection:

Role: {detection.as_a}
Want: {detection.i_want}
So that: {detection.so_that}

Provide:
1. A concise title (5-10 words)
2. A category (feature, integration, ui, infrastructure, analytics, security)

Respond in this exact format:
TITLE: [your title]
CATEGORY: [category]

Example:
TITLE: Deploy application on GCP
CATEGORY: infrastructure
"""

            if self.ai_service.use_claude_cli:
                result = self.ai_service.cli_interface.execute_prompt(prompt)
                if not result.success:
                    logger.warning(f"AI enhancement failed: {result.error}")
                    return detection
                response = result.content
            else:
                api_response = self.ai_service.client.messages.create(
                    model=self.ai_service.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                )
                response = api_response.content[0].text

            # Parse response
            title_match = re.search(r"TITLE:\s*(.+)", response, re.IGNORECASE)
            category_match = re.search(r"CATEGORY:\s*(\w+)", response, re.IGNORECASE)

            if title_match:
                detection.suggested_title = title_match.group(1).strip()
            if category_match:
                detection.suggested_category = category_match.group(1).strip().lower()

            detection.detection_method = "ai_enhanced"
            return detection

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return detection

    def _ai_validate_informal(self, user_input: str, feature: str) -> UserStoryDetection:
        """Use AI to validate and extract user story from informal input.

        Args:
            user_input: Original user input
            feature: Extracted feature from informal pattern

        Returns:
            UserStoryDetection with AI-extracted components
        """
        if not self.ai_service:
            return UserStoryDetection(
                raw_input=user_input,
                i_want=feature,
                confidence=0.50,
                is_user_story=False,
                detection_method="informal_no_ai",
            )

        try:
            prompt = f"""Analyze if this is a user story request:

Input: "{user_input}"

If this is a feature request / user story, extract:
1. Role (who needs this - user, developer, admin, etc.)
2. Want (what they want - the feature/capability)
3. So that (why they want it - the benefit/value)
4. Title (concise 5-10 word title)
5. Category (feature, integration, ui, infrastructure, analytics, security)
6. Confidence (0.0-1.0, how confident you are this is a user story)

If NOT a user story (just a question, conversation, etc.), respond with:
NOT_A_USER_STORY

Otherwise, respond in this exact format:
ROLE: [role]
WANT: [what]
SO_THAT: [benefit]
TITLE: [title]
CATEGORY: [category]
CONFIDENCE: [0.0-1.0]

Example for "I want email notifications when builds fail":
ROLE: developer
WANT: email notifications when builds fail
SO_THAT: I can respond quickly to failures
TITLE: Email Notifications for Build Failures
CATEGORY: integration
CONFIDENCE: 0.85
"""

            if self.ai_service.use_claude_cli:
                result = self.ai_service.cli_interface.execute_prompt(prompt)
                if not result.success:
                    logger.warning(f"AI validation failed: {result.error}")
                    return UserStoryDetection(
                        raw_input=user_input,
                        i_want=feature,
                        confidence=0.50,
                        is_user_story=False,
                        detection_method="ai_failed",
                    )
                response = result.content
            else:
                api_response = self.ai_service.client.messages.create(
                    model=self.ai_service.model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}],
                )
                response = api_response.content[0].text

            # Check if not a user story
            if "NOT_A_USER_STORY" in response:
                return UserStoryDetection(
                    raw_input=user_input,
                    confidence=0.0,
                    is_user_story=False,
                    detection_method="ai_rejected",
                )

            # Parse response
            role_match = re.search(r"ROLE:\s*(.+)", response, re.IGNORECASE)
            want_match = re.search(r"WANT:\s*(.+)", response, re.IGNORECASE)
            so_that_match = re.search(r"SO_THAT:\s*(.+)", response, re.IGNORECASE)
            title_match = re.search(r"TITLE:\s*(.+)", response, re.IGNORECASE)
            category_match = re.search(r"CATEGORY:\s*(\w+)", response, re.IGNORECASE)
            confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", response, re.IGNORECASE)

            role = role_match.group(1).strip() if role_match else "user"
            want = want_match.group(1).strip() if want_match else feature
            so_that = so_that_match.group(1).strip() if so_that_match else ""
            title = title_match.group(1).strip() if title_match else self._generate_title(role, want, so_that)
            category = category_match.group(1).strip().lower() if category_match else "feature"
            confidence = float(confidence_match.group(1)) if confidence_match else 0.75

            return UserStoryDetection(
                raw_input=user_input,
                as_a=role,
                i_want=want,
                so_that=so_that,
                confidence=confidence,
                suggested_title=title,
                suggested_category=category,
                is_user_story=confidence >= self.confidence_threshold,
                detection_method="informal_ai",
            )

        except Exception as e:
            logger.error(f"AI validation failed: {e}")
            return UserStoryDetection(
                raw_input=user_input,
                i_want=feature,
                confidence=0.50,
                is_user_story=False,
                detection_method="ai_error",
            )

    def _ai_detect_user_story(self, user_input: str) -> UserStoryDetection:
        """Use pure AI detection when no patterns match.

        Args:
            user_input: Raw user input

        Returns:
            UserStoryDetection from AI analysis
        """
        # Reuse the same AI validation method
        return self._ai_validate_informal(user_input, user_input)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove trailing punctuation from role/want/so_that
        text = text.rstrip(".,!?;:")

        return text

    def _generate_title(self, role: str, want: str, so_that: str) -> str:
        """Generate title from components.

        Args:
            role: User role
            want: Feature/capability
            so_that: Benefit

        Returns:
            Generated title (capitalized, max 80 chars)
        """
        # Use want as base
        if want:
            title = want.strip()
        else:
            title = "Feature Request"

        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]

        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + "..."

        return title
