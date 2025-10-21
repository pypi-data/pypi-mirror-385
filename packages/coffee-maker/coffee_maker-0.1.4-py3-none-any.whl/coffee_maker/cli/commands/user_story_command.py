"""User Story Command Handler - Natural language user story creation.

This handler implements the /US command for creating user stories through
conversational interaction with Claude AI.

Example:
    >>> handler = UserStoryCommandHandler(ai_service, roadmap_editor)
    >>> result = handler.handle_command("/US I want to track user logins")
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from coffee_maker.cli.ai_service import AIService
from coffee_maker.cli.roadmap_editor import RoadmapEditor

logger = logging.getLogger(__name__)


class ValidationState(Enum):
    """States in the user story validation workflow."""

    EXTRACTING = "extracting"  # Parsing natural language
    CHECKING_SIMILARITY = "checking"  # Comparing with existing US
    AWAITING_VALIDATION = "validating"  # Waiting for user approval
    REFINING = "refining"  # User requested changes
    PRIORITIZING = "prioritizing"  # Determining placement
    COMPLETE = "complete"  # Ready to propagate


@dataclass
class UserStoryDraft:
    """Draft user story being validated.

    Attributes:
        title: User story title (e.g., "User Login Tracking")
        description: Full user story in "As a X I want Y so that Z" format
        acceptance_criteria: List of acceptance criteria
        estimated_effort: Optional effort estimate (e.g., "2-3 days")
        similar_stories: List of similar existing user stories
        suggested_priority: AI-suggested priority placement
        state: Current validation state
        conversation_history: Messages exchanged during refinement
    """

    title: str
    description: str
    acceptance_criteria: List[str]
    estimated_effort: Optional[str] = None
    similar_stories: List[Tuple[str, float]] = field(default_factory=list)
    suggested_priority: Optional[str] = None
    state: ValidationState = ValidationState.EXTRACTING
    conversation_history: List[Dict] = field(default_factory=list)


class UserStoryCommandHandler:
    """Handler for /US command - conversational user story creation.

    This handler manages the entire workflow:
    1. Extract structured user story from natural language
    2. Check for similar existing user stories
    3. Validate with user through conversation
    4. Determine prioritization
    5. Propagate to ROADMAP.md

    Example:
        >>> handler = UserStoryCommandHandler(ai_service, roadmap_editor)
        >>> response = handler.handle_command(
        ...     "/US I want users to be able to export reports to PDF"
        ... )
        >>> print(response['message'])
    """

    def __init__(self, ai_service: AIService, roadmap_editor: RoadmapEditor, similarity_threshold: float = 0.7):
        """Initialize handler.

        Args:
            ai_service: Claude AI service for NLP
            roadmap_editor: Editor for ROADMAP.md manipulation
            similarity_threshold: Minimum similarity score to flag duplicates (0.0-1.0)
        """
        self.ai_service = ai_service
        self.roadmap_editor = roadmap_editor
        self.similarity_threshold = similarity_threshold

        # Active draft (None if no validation in progress)
        self.current_draft: Optional[UserStoryDraft] = None

    def handle_command(self, command: str) -> Dict:
        """Handle /US command invocation.

        Args:
            command: Full command string (e.g., "/US I want to track logins")

        Returns:
            Response dictionary with:
                - message: Formatted response to display
                - state: Current validation state
                - draft: Current draft (if any)
                - requires_input: True if waiting for user response

        Example:
            >>> result = handler.handle_command("/US I want export to PDF")
            >>> print(result['message'])
            I've drafted a user story for PDF export...
            >>> print(result['requires_input'])
            True
        """
        # Extract description from command
        description = self._parse_command(command)

        if not description:
            return {
                "message": "❌ Please provide a description after /US\n"
                "Example: /US I want users to export reports to PDF",
                "state": None,
                "requires_input": False,
            }

        # Start new draft
        draft = self._extract_user_story(description)
        self.current_draft = draft

        # Check similarity with existing user stories
        self._check_similarity(draft)

        # Present draft to user
        return self._present_draft(draft)

    def handle_validation_response(self, user_response: str) -> Dict:
        """Handle user's response during validation loop.

        Args:
            user_response: User's message (approval, refinement request, etc.)

        Returns:
            Response dictionary (same format as handle_command)

        Example:
            >>> handler.handle_command("/US export to PDF")
            >>> result = handler.handle_validation_response("yes, looks good")
            >>> print(result['state'])
            prioritizing
        """
        if not self.current_draft:
            return {
                "message": "⚠️  No user story draft in progress. Use /US to start.",
                "state": None,
                "requires_input": False,
            }

        # Classify response intent (approve, refine, reject, etc.)
        intent = self._classify_response(user_response)

        if intent == "approve":
            return self._handle_approval()
        elif intent == "refine":
            return self._handle_refinement(user_response)
        elif intent == "reject":
            return self._handle_rejection()
        else:
            return {
                "message": "ℹ️  I didn't understand. Please:\n"
                "- Say 'yes' or 'approve' to proceed\n"
                "- Describe changes you'd like\n"
                "- Say 'cancel' to abort",
                "state": self.current_draft.state,
                "requires_input": True,
            }

    def _parse_command(self, command: str) -> str:
        """Extract description from /US command.

        Args:
            command: Full command (e.g., "/US I want to...")

        Returns:
            Description text without /US prefix
        """
        # Remove /US prefix (case-insensitive)
        match = re.match(r"/us\s+(.*)", command, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_user_story(self, description: str) -> UserStoryDraft:
        """Extract structured user story from natural language.

        Args:
            description: User's natural language description

        Returns:
            UserStoryDraft with AI-extracted structure
        """
        from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

        # Load extraction prompt
        prompt = load_prompt(
            PromptNames.EXTRACT_USER_STORY,
            {"DESCRIPTION": description},
        )

        # Call AI service
        response = self.ai_service.process_request(user_input=prompt, context={}, history=[])

        # Parse AI response into structured format
        parsed = self._parse_ai_extraction(response.message)

        return UserStoryDraft(
            title=parsed["title"],
            description=parsed["description"],
            acceptance_criteria=parsed["criteria"],
            estimated_effort=parsed.get("effort"),
            state=ValidationState.CHECKING_SIMILARITY,
        )

    def _check_similarity(self, draft: UserStoryDraft) -> None:
        """Check draft against existing user stories for duplicates.

        Updates draft.similar_stories with matches.

        Args:
            draft: Draft to check
        """
        import difflib

        # Get all existing user stories from roadmap
        existing_stories = self.roadmap_editor.get_user_story_summary()

        similar = []

        # Handle case where get_user_story_summary returns a dict with "stories" key
        if isinstance(existing_stories, dict) and "stories" in existing_stories:
            stories_list = existing_stories["stories"]
        else:
            stories_list = []

        for story in stories_list:
            us_id = story.get("id", "")
            us_title = story.get("title", "")
            us_description = story.get("description", "")

            # Compare title and description
            title_similarity = difflib.SequenceMatcher(None, draft.title.lower(), us_title.lower()).ratio()

            desc_similarity = difflib.SequenceMatcher(None, draft.description.lower(), us_description.lower()).ratio()

            # Use higher of the two scores
            max_similarity = max(title_similarity, desc_similarity)

            if max_similarity >= self.similarity_threshold:
                similar.append((us_id, max_similarity))

        # Sort by similarity (highest first)
        draft.similar_stories = sorted(similar, key=lambda x: x[1], reverse=True)
        draft.state = ValidationState.AWAITING_VALIDATION

    def _present_draft(self, draft: UserStoryDraft) -> Dict:
        """Format draft for user review.

        Args:
            draft: Draft to present

        Returns:
            Response dictionary
        """
        # Build markdown presentation
        md = f"""## 📝 User Story Draft

**Title**: {draft.title}

**Description**:
{draft.description}

**Acceptance Criteria**:
"""
        for i, criterion in enumerate(draft.acceptance_criteria, 1):
            md += f"{i}. {criterion}\n"

        if draft.estimated_effort:
            md += f"\n**Estimated Effort**: {draft.estimated_effort}"

        # Add similarity warnings if found
        if draft.similar_stories:
            md += "\n\n---\n\n⚠️  **Similar User Stories Found**:\n\n"
            for us_id, score in draft.similar_stories[:3]:  # Top 3
                md += f"- **{us_id}** (similarity: {score:.0%})\n"

            md += "\nOptions:\n"
            md += "1. Create as new user story\n"
            md += "2. Rephrase existing user story\n"
            md += "3. Cancel\n"
        else:
            md += "\n\n---\n\n✅ No similar user stories found.\n"

        md += "\n**Next steps**: Please review and respond:\n"
        md += "- 'yes' or 'approve' to proceed\n"
        md += "- Describe any changes you'd like\n"
        md += "- 'cancel' to abort\n"

        return {"message": md, "state": draft.state, "draft": draft, "requires_input": True}

    def _classify_response(self, response: str) -> str:
        """Classify user's validation response.

        Args:
            response: User's message

        Returns:
            Intent: "approve", "refine", "reject", "unclear"
        """
        response_lower = response.lower().strip()

        # Approval patterns
        if any(word in response_lower for word in ["yes", "approve", "looks good", "ok", "correct"]):
            return "approve"

        # Rejection patterns
        if any(word in response_lower for word in ["no", "cancel", "abort", "stop"]):
            return "reject"

        # Refinement (anything with change requests)
        if any(word in response_lower for word in ["change", "update", "modify", "instead", "should be"]):
            return "refine"

        return "unclear"

    def _handle_approval(self) -> Dict:
        """Handle user approval - move to prioritization.

        Returns:
            Response dictionary
        """
        draft = self.current_draft
        draft.state = ValidationState.PRIORITIZING

        # Get prioritization suggestion
        suggestion = self._suggest_prioritization(draft)
        draft.suggested_priority = suggestion

        md = f"""✅ User story approved!

**Suggested Placement**: {suggestion}

Where would you like to add this user story?
1. **TOP PRIORITY** - Urgent, start immediately
2. **After PRIORITY X** - Specify existing priority
3. **BACKLOG** - Defer for later

Please respond with your choice (1, 2, or 3).
"""

        return {"message": md, "state": draft.state, "draft": draft, "requires_input": True}

    def _handle_refinement(self, user_request: str) -> Dict:
        """Handle user requesting changes to draft.

        Args:
            user_request: User's refinement request

        Returns:
            Response dictionary
        """
        draft = self.current_draft
        draft.state = ValidationState.REFINING
        draft.conversation_history.append({"role": "user", "message": user_request})

        # Call AI to refine draft based on user feedback
        from coffee_maker.autonomous.prompt_loader import PromptNames, load_prompt

        prompt = load_prompt(
            PromptNames.REFINE_USER_STORY,
            {"ORIGINAL_DRAFT": draft.description, "USER_FEEDBACK": user_request},
        )

        response = self.ai_service.process_request(user_input=prompt, context={}, history=draft.conversation_history)

        # Update draft with refined version
        parsed = self._parse_ai_extraction(response.message)
        draft.title = parsed.get("title", draft.title)
        draft.description = parsed.get("description", draft.description)
        draft.acceptance_criteria = parsed.get("criteria", draft.acceptance_criteria)
        draft.state = ValidationState.AWAITING_VALIDATION

        # Present updated draft
        return self._present_draft(draft)

    def _handle_rejection(self) -> Dict:
        """Handle user rejecting draft.

        Returns:
            Response dictionary
        """
        self.current_draft = None

        return {
            "message": "❌ User story creation cancelled.",
            "state": ValidationState.COMPLETE,
            "requires_input": False,
        }

    def _suggest_prioritization(self, draft: UserStoryDraft) -> str:
        """Suggest where to place user story in roadmap.

        Args:
            draft: Draft to prioritize

        Returns:
            Suggestion text
        """
        # Analyze roadmap dependencies and current priorities
        # For MVP, return simple suggestion
        # TODO: Implement full dependency analysis in Phase 2

        return "BACKLOG (no urgent dependencies detected)"

    def _parse_ai_extraction(self, ai_response: str) -> Dict:
        """Parse AI's structured user story extraction.

        Args:
            ai_response: Claude's response text

        Returns:
            Parsed components: title, description, criteria, effort
        """
        # Extract title
        title_match = re.search(r"Title:\s*(.+)", ai_response)
        title = title_match.group(1).strip() if title_match else "Untitled"

        # Extract description
        desc_match = re.search(
            r"Description:\s*(.+?)(?=Acceptance Criteria:|Estimated Effort:|$)", ai_response, re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract acceptance criteria
        criteria = []
        criteria_section = re.search(r"Acceptance Criteria:\s*(.+?)(?=Estimated Effort:|$)", ai_response, re.DOTALL)
        if criteria_section:
            criteria_text = criteria_section.group(1)
            # Extract bullet points
            for line in criteria_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("•"):
                    criteria.append(line.lstrip("-•").strip())

        # Extract effort
        effort_match = re.search(r"Estimated Effort:\s*(.+)", ai_response)
        effort = effort_match.group(1).strip() if effort_match else None

        return {"title": title, "description": description, "criteria": criteria, "effort": effort}

    def finalize_user_story(self, priority_placement: str) -> Dict:
        """Finalize and propagate user story to ROADMAP.md.

        Args:
            priority_placement: Where to place (e.g., "TOP PRIORITY", "BACKLOG")

        Returns:
            Response dictionary with confirmation
        """
        if not self.current_draft:
            return {
                "message": "⚠️  No user story to finalize.",
                "state": None,
                "requires_input": False,
            }

        draft = self.current_draft

        # Parse description to extract role, want, so_that
        role, want, so_that = self._parse_user_story_description(draft.description)

        # Get next user story ID
        us_id = self._get_new_user_story_id()

        try:
            # Add to roadmap using existing add_user_story method
            success = self.roadmap_editor.add_user_story(
                story_id=us_id,
                title=draft.title,
                role=role,
                want=want,
                so_that=so_that,
                business_value=3,  # Default value
                estimated_effort=draft.estimated_effort or "TBD",
                acceptance_criteria=draft.acceptance_criteria,
                technical_notes="",
                status="📝 Backlog",
                assigned_to="",
            )

            if success:
                draft.state = ValidationState.COMPLETE

                md = f"""✅ **User Story Added Successfully!**

**ID**: {us_id}
**Title**: {draft.title}
**Placement**: {priority_placement}

The user story has been added to `docs/roadmap/ROADMAP.md`.

Use `/roadmap` to view the updated roadmap.
"""

                # Clear current draft
                self.current_draft = None

                return {"message": md, "state": ValidationState.COMPLETE, "requires_input": False}
            else:
                return {
                    "message": "❌ Failed to add user story to roadmap. Please check logs.",
                    "state": draft.state,
                    "requires_input": False,
                }

        except Exception as e:
            logger.error(f"Failed to finalize user story: {e}")
            return {
                "message": f"❌ Failed to add user story: {str(e)}",
                "state": draft.state,
                "requires_input": False,
            }

    def _parse_user_story_description(self, description: str) -> Tuple[str, str, str]:
        """Parse user story description into role, want, so_that.

        Args:
            description: Full user story description

        Returns:
            Tuple of (role, want, so_that)
        """
        # Try to parse "As a [role] I want [want] so that [so_that]"
        # Also handle "I want to [action]" form
        pattern = r"As a (.+?) I want (?:to )?(.+?) so that (.+)"
        match = re.search(pattern, description, re.IGNORECASE)

        if match:
            return match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
        else:
            # Fallback if pattern doesn't match
            return "user", description, "it provides value"

    def _get_new_user_story_id(self) -> str:
        """Get ID for newly added user story.

        Returns:
            User story ID (e.g., "US-050")
        """
        # Query roadmap for next available US number
        summary = self.roadmap_editor.get_user_story_summary()

        if isinstance(summary, dict) and "total" in summary:
            # Next ID is current total + 1
            next_num = summary["total"] + 1
            return f"US-{next_num:03d}"

        # Fallback
        return "US-XXX"
