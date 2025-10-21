"""Response formatter for AI service responses with classification context.

This module formats AI responses to include clear communication about:
- What type of request was detected
- Which documents will be updated
- Confirmation of actions taken

This is part of US-021 Phase 2: AI Service Integration for better user communication.
"""

from typing import List

from coffee_maker.cli.request_classifier import ClassificationResult, RequestType


class ResponseFormatter:
    """Formats AI responses with classification context for clear communication.

    The formatter adds:
    - Header: Explains what type of request was detected
    - Footer: Confirms which documents will be updated

    Example:
        >>> from coffee_maker.cli.request_classifier import RequestClassifier
        >>> classifier = RequestClassifier()
        >>> result = classifier.classify("I want to add email notifications")
        >>> formatter = ResponseFormatter()
        >>> header = formatter.format_classification_header(result)
        >>> print(header)
        📝 **Feature Request Detected**

        I'll add this to the ROADMAP (docs/roadmap/ROADMAP.md).
    """

    @staticmethod
    def format_classification_header(classification: ClassificationResult) -> str:
        """Format header explaining classification.

        Args:
            classification: Classification result from RequestClassifier

        Returns:
            Formatted header string with emoji and explanation

        Example:
            >>> result = ClassificationResult(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     confidence=0.85,
            ...     feature_indicators=["keyword: want"],
            ...     methodology_indicators=[],
            ...     suggested_questions=[],
            ...     target_documents=["docs/roadmap/ROADMAP.md"]
            ... )
            >>> header = ResponseFormatter.format_classification_header(result)
            >>> print(header)
            📝 **Feature Request Detected**
            <BLANKLINE>
            I'll add this to the ROADMAP (docs/roadmap/ROADMAP.md).
            <BLANKLINE>
        """
        if classification.request_type == RequestType.FEATURE_REQUEST:
            # Join document names for display
            doc_names = ", ".join(classification.target_documents)
            return "📝 **Feature Request Detected**\n\n" f"I'll add this to the ROADMAP ({doc_names}).\n"

        elif classification.request_type == RequestType.METHODOLOGY_CHANGE:
            # Join document names for display
            doc_names = ", ".join(classification.target_documents)
            return (
                "🔧 **Methodology Change Detected**\n\n" f"I'll update our collaboration methodology ({doc_names}).\n"
            )

        elif classification.request_type == RequestType.HYBRID:
            return (
                "🔀 **Hybrid Request Detected** (Feature + Methodology)\n\n"
                "I'll update both:\n"
                "- ROADMAP.md (for the feature)\n"
                "- TEAM_COLLABORATION.md (for methodology changes)\n"
            )

        else:  # CLARIFICATION_NEEDED
            return "❓ **Clarification Needed**\n\n"

    @staticmethod
    def format_confirmation_footer(target_documents: List[str]) -> str:
        """Format confirmation footer.

        Args:
            target_documents: List of document paths to update

        Returns:
            Formatted footer string confirming updates

        Example:
            >>> footer = ResponseFormatter.format_confirmation_footer(
            ...     ["docs/roadmap/ROADMAP.md"]
            ... )
            >>> print(footer)
            <BLANKLINE>
            <BLANKLINE>
            ✅ **Confirmed**: I'll update `docs/roadmap/ROADMAP.md`

            >>> footer = ResponseFormatter.format_confirmation_footer(
            ...     ["docs/roadmap/ROADMAP.md", "docs/roadmap/TEAM_COLLABORATION.md"]
            ... )
            >>> print(footer)
            <BLANKLINE>
            <BLANKLINE>
            ✅ **Confirmed**: I'll update:
            - `docs/roadmap/ROADMAP.md`
            - `docs/roadmap/TEAM_COLLABORATION.md`
        """
        if not target_documents:
            return ""

        if len(target_documents) == 1:
            return f"\n\n✅ **Confirmed**: I'll update `{target_documents[0]}`"
        else:
            docs_list = "\n".join(f"- `{doc}`" for doc in target_documents)
            return f"\n\n✅ **Confirmed**: I'll update:\n{docs_list}"

    @staticmethod
    def format_complete_response(classification: ClassificationResult, ai_message: str) -> str:
        """Format complete response with header, message, and footer.

        Args:
            classification: Classification result
            ai_message: AI-generated message body

        Returns:
            Complete formatted response

        Example:
            >>> result = ClassificationResult(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     confidence=0.85,
            ...     feature_indicators=["keyword: want"],
            ...     methodology_indicators=[],
            ...     suggested_questions=[],
            ...     target_documents=["docs/roadmap/ROADMAP.md"]
            ... )
            >>> response = ResponseFormatter.format_complete_response(
            ...     result,
            ...     "I'll add email notifications to the roadmap."
            ... )
            >>> "Feature Request Detected" in response
            True
            >>> "I'll add email notifications" in response
            True
            >>> "Confirmed" in response
            True
        """
        # Don't add formatting for clarification requests
        if classification.request_type == RequestType.CLARIFICATION_NEEDED:
            return ai_message

        header = ResponseFormatter.format_classification_header(classification)
        footer = ResponseFormatter.format_confirmation_footer(classification.target_documents)

        return f"{header}{ai_message}{footer}"
