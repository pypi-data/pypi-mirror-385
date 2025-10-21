"""Preview generation system for document updates.

This module generates human-readable previews of document changes before
they are applied, allowing users to review and confirm updates.

Key Features:
- Diff-style preview generation
- Color-coded additions/deletions (for terminal)
- Section highlighting
- Estimated line numbers
- Context extraction (before/after)
- Batch preview support

Integration with US-021 Phase 4:
- RequestClassifier identifies request type
- AIService processes with AI
- MetadataExtractor extracts metadata
- **PreviewGenerator shows preview** ← NEW in Phase 4
- User confirms changes
- DocumentUpdater applies changes

Example:
    >>> from coffee_maker.cli.preview_generator import PreviewGenerator
    >>> from coffee_maker.cli.request_classifier import RequestType
    >>>
    >>> generator = PreviewGenerator()
    >>> preview = generator.generate_preview(
    ...     request_type=RequestType.FEATURE_REQUEST,
    ...     content="I want to add email notifications",
    ...     target_documents=["docs/roadmap/ROADMAP.md"],
    ...     metadata={'title': 'Email Notifications'}
    ... )
    >>> print(preview)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from coffee_maker.cli.request_classifier import RequestType

logger = logging.getLogger(__name__)


@dataclass
class DocumentPreview:
    """Preview of document changes.

    Attributes:
        document_path: Path to document being modified
        preview_text: Human-readable preview of changes
        additions: List of lines being added
        estimated_location: Estimated location in document (section, line range)
        will_create_backup: Whether a backup will be created
        warnings: Any warnings about the changes
    """

    document_path: str
    preview_text: str
    additions: List[str]
    estimated_location: str
    will_create_backup: bool
    warnings: List[str]


@dataclass
class PreviewResult:
    """Result of preview generation.

    Attributes:
        previews: List of DocumentPreview objects (one per target document)
        summary: Summary of all changes
        requires_confirmation: Whether user confirmation is required
        total_additions: Total lines being added across all documents
    """

    previews: List[DocumentPreview]
    summary: str
    requires_confirmation: bool
    total_additions: int


class PreviewGenerator:
    """Generates human-readable previews of document updates.

    This class creates diff-style previews showing what will be added to
    documents, where it will be added, and any warnings or conflicts.

    Example:
        >>> generator = PreviewGenerator()
        >>>
        >>> # Feature request preview
        >>> result = generator.generate_preview(
        ...     request_type=RequestType.FEATURE_REQUEST,
        ...     content="Add Slack integration",
        ...     target_documents=["docs/roadmap/ROADMAP.md"],
        ...     metadata={'title': 'Slack Integration', 'estimated_effort': '2-3 days'}
        ... )
        >>>
        >>> for preview in result.previews:
        ...     print(preview.preview_text)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize preview generator.

        Args:
            project_root: Optional project root path (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        logger.info(f"PreviewGenerator initialized (project_root: {self.project_root})")

    def generate_preview(
        self,
        request_type: RequestType,
        content: str,
        target_documents: List[str],
        metadata: Optional[Dict] = None,
    ) -> PreviewResult:
        """Generate preview of document updates.

        This is the main entry point for preview generation. It creates
        previews for all target documents showing what will be added.

        Args:
            request_type: Type of request (FEATURE_REQUEST, METHODOLOGY_CHANGE, HYBRID)
            content: Content to add (user's original request)
            target_documents: List of document paths to update
            metadata: Additional metadata for the updates

        Returns:
            PreviewResult with previews for each document

        Example:
            >>> generator = PreviewGenerator()
            >>> result = generator.generate_preview(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     content="Add email notifications",
            ...     target_documents=["docs/roadmap/ROADMAP.md"],
            ...     metadata={'title': 'Email Notifications'}
            ... )
            >>> print(result.summary)
            >>> for preview in result.previews:
            ...     print(preview.preview_text)
        """
        metadata = metadata or {}
        previews = []
        total_additions = 0

        logger.info(f"Generating preview for {request_type.value} with {len(target_documents)} target(s)")

        for doc_path in target_documents:
            try:
                preview = self._generate_document_preview(
                    doc_path=doc_path,
                    request_type=request_type,
                    content=content,
                    metadata=metadata,
                )
                previews.append(preview)
                total_additions += len(preview.additions)

            except Exception as e:
                logger.error(f"Failed to generate preview for {doc_path}: {e}")
                # Create error preview
                previews.append(
                    DocumentPreview(
                        document_path=doc_path,
                        preview_text=f"❌ ERROR: Could not generate preview for {doc_path}\nError: {e}",
                        additions=[],
                        estimated_location="Unknown",
                        will_create_backup=False,
                        warnings=[f"Preview generation failed: {e}"],
                    )
                )

        # Generate summary
        summary = self._generate_summary(previews, request_type, total_additions)

        return PreviewResult(
            previews=previews,
            summary=summary,
            requires_confirmation=True,  # Phase 4: Always require confirmation
            total_additions=total_additions,
        )

    def _generate_document_preview(
        self,
        doc_path: str,
        request_type: RequestType,
        content: str,
        metadata: Dict,
    ) -> DocumentPreview:
        """Generate preview for a single document.

        Args:
            doc_path: Path to document (relative to project root)
            request_type: Type of request
            content: Content to add
            metadata: Metadata for the update

        Returns:
            DocumentPreview for this document
        """
        full_path = self.project_root / doc_path

        # Check if document exists
        if not full_path.exists():
            warnings = [f"Document does not exist: {doc_path} (will be created)"]
            will_create_backup = False
            estimated_location = "New file"
        else:
            warnings = []
            will_create_backup = True
            estimated_location = self._estimate_location(full_path, request_type)

        # Generate the content that will be added
        if "ROADMAP" in doc_path:
            additions, preview_text = self._preview_roadmap_update(content, metadata, estimated_location)
        elif "COLLABORATION" in doc_path:
            additions, preview_text = self._preview_collaboration_update(content, metadata, estimated_location)
        elif "CLAUDE.md" in doc_path:
            additions, preview_text = self._preview_claude_update(content, metadata, estimated_location)
        else:
            additions = [content]
            preview_text = self._format_generic_preview(doc_path, content, estimated_location)

        # Check for potential conflicts
        conflict_warnings = self._check_conflicts(full_path, additions, metadata)
        warnings.extend(conflict_warnings)

        return DocumentPreview(
            document_path=doc_path,
            preview_text=preview_text,
            additions=additions,
            estimated_location=estimated_location,
            will_create_backup=will_create_backup,
            warnings=warnings,
        )

    def _preview_roadmap_update(self, content: str, metadata: Dict, estimated_location: str) -> Tuple[List[str], str]:
        """Generate preview for ROADMAP.md update.

        Args:
            content: User story description
            metadata: User story details
            estimated_location: Where it will be inserted

        Returns:
            Tuple of (additions as list of lines, formatted preview text)
        """
        # Simulate what will be added
        us_number = metadata.get("us_number", "XXX")
        title = metadata.get("title", "New Feature")
        business_value = metadata.get("business_value", "TBD")
        estimated_effort = metadata.get("estimated_effort", "TBD")
        acceptance_criteria = metadata.get("acceptance_criteria", ["Feature implemented and tested"])

        timestamp = datetime.now().strftime("%Y-%m-%d")

        # Build preview
        preview_lines = [
            f"## US-{us_number}: {title}",
            "",
            "**Status**: 📝 **PLANNED**",
            f"**Created**: {timestamp}",
            "**Classification**: 🔵 FEATURE REQUEST (via AI classification)",
            "",
            "**Description**:",
            content,
            "",
            f"**Business Value**: {business_value}",
            f"**Estimated Effort**: {estimated_effort}",
            "",
            "**Acceptance Criteria**:",
        ]

        if isinstance(acceptance_criteria, list):
            for criterion in acceptance_criteria:
                preview_lines.append(f"- [ ] {criterion}")
        else:
            preview_lines.append(f"- [ ] {acceptance_criteria}")

        preview_lines.append("")
        preview_lines.append("---")

        # Format as preview text
        preview_text = self._format_preview_with_colors(
            document="docs/roadmap/ROADMAP.md",
            location=estimated_location,
            additions=preview_lines,
            will_add_lines=len(preview_lines),
        )

        return preview_lines, preview_text

    def _preview_collaboration_update(
        self, content: str, metadata: Dict, estimated_location: str
    ) -> Tuple[List[str], str]:
        """Generate preview for COLLABORATION_METHODOLOGY.md update.

        Args:
            content: Methodology change description
            metadata: Methodology details
            estimated_location: Where it will be inserted

        Returns:
            Tuple of (additions as list of lines, formatted preview text)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        title = metadata.get("title", "New Methodology")
        rationale = metadata.get("rationale", "TBD")
        applies_to = metadata.get("applies_to", "All team members")

        preview_lines = [
            f"### {title} (Added {timestamp})",
            "",
            content,
            "",
            f"**Rationale**: {rationale}",
            f"**Applies to**: {applies_to}",
            "",
        ]

        preview_text = self._format_preview_with_colors(
            document="docs/COLLABORATION_METHODOLOGY.md",
            location=estimated_location,
            additions=preview_lines,
            will_add_lines=len(preview_lines),
        )

        return preview_lines, preview_text

    def _preview_claude_update(self, content: str, metadata: Dict, estimated_location: str) -> Tuple[List[str], str]:
        """Generate preview for CLAUDE.md update.

        Args:
            content: Technical guideline description
            metadata: Guideline details
            estimated_location: Where it will be inserted

        Returns:
            Tuple of (additions as list of lines, formatted preview text)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        title = metadata.get("title", "New Guideline")

        preview_lines = [
            f"### {title} (Added {timestamp})",
            "",
            content,
            "",
        ]

        preview_text = self._format_preview_with_colors(
            document=".claude/CLAUDE.md",
            location=estimated_location,
            additions=preview_lines,
            will_add_lines=len(preview_lines),
        )

        return preview_lines, preview_text

    def _format_preview_with_colors(
        self, document: str, location: str, additions: List[str], will_add_lines: int
    ) -> str:
        """Format preview with diff-style colors.

        Args:
            document: Document path
            location: Estimated location
            additions: Lines being added
            will_add_lines: Number of lines to add

        Returns:
            Formatted preview text
        """
        preview = []

        # Header
        preview.append("=" * 80)
        preview.append(f"📄 PREVIEW: {document}")
        preview.append("=" * 80)
        preview.append("")
        preview.append(f"📍 Location: {location}")
        preview.append(f"➕ Will add: {will_add_lines} lines")
        preview.append("")
        preview.append("─" * 80)
        preview.append("ADDITIONS:")
        preview.append("─" * 80)

        # Show additions with + prefix (diff style)
        for line in additions:
            preview.append(f"+ {line}")

        preview.append("─" * 80)
        preview.append("")

        return "\n".join(preview)

    def _format_generic_preview(self, doc_path: str, content: str, location: str) -> str:
        """Format generic preview for unknown document types.

        Args:
            doc_path: Document path
            content: Content to add
            location: Estimated location

        Returns:
            Formatted preview text
        """
        preview = []
        preview.append("=" * 80)
        preview.append(f"📄 PREVIEW: {doc_path}")
        preview.append("=" * 80)
        preview.append("")
        preview.append(f"📍 Location: {location}")
        preview.append("")
        preview.append("─" * 80)
        preview.append("CONTENT:")
        preview.append("─" * 80)
        preview.append(content)
        preview.append("─" * 80)

        return "\n".join(preview)

    def _estimate_location(self, doc_path: Path, request_type: RequestType) -> str:
        """Estimate where content will be inserted in document.

        Args:
            doc_path: Path to document
            request_type: Type of request

        Returns:
            Human-readable location description
        """
        if not doc_path.exists():
            return "New file"

        try:
            with open(doc_path, "r") as f:
                lines = f.readlines()

            if "ROADMAP" in doc_path.name:
                # Find first user story
                for i, line in enumerate(lines):
                    if line.startswith("## US-"):
                        return f"Before line {i+1} (first user story)"
                return f"End of file (line {len(lines) + 1})"

            elif "COLLABORATION" in doc_path.name:
                section = "General Guidelines"  # Default
                for i, line in enumerate(lines):
                    if section.lower() in line.lower() and line.startswith("##"):
                        return f"Section '{section}', line {i+1}"
                return f"End of file (line {len(lines) + 1})"

            elif "CLAUDE.md" in doc_path.name:
                section = "Special Instructions for Claude"  # Default
                for i, line in enumerate(lines):
                    if section.lower() in line.lower() and line.startswith("##"):
                        return f"Section '{section}', line {i+1}"
                return f"End of file (line {len(lines) + 1})"

            else:
                return f"End of file (line {len(lines) + 1})"

        except Exception as e:
            logger.error(f"Failed to estimate location in {doc_path}: {e}")
            return "Unknown location"

    def _check_conflicts(self, doc_path: Path, additions: List[str], metadata: Dict) -> List[str]:
        """Check for potential conflicts in the update.

        Args:
            doc_path: Path to document
            additions: Lines being added
            metadata: Update metadata

        Returns:
            List of warning messages
        """
        warnings = []

        if not doc_path.exists():
            return warnings

        try:
            with open(doc_path, "r") as f:
                content = f.read()

            # Check for duplicate US numbers in ROADMAP
            if "ROADMAP" in doc_path.name:
                us_number = metadata.get("us_number")
                if us_number:
                    pattern = f"## US-{us_number:03d}:"
                    if pattern in content:
                        warnings.append(f"⚠️ WARNING: US-{us_number:03d} already exists in ROADMAP")

            # Check for duplicate titles
            title = metadata.get("title")
            if title:
                # Case-insensitive check
                if title.lower() in content.lower():
                    warnings.append(f"⚠️ WARNING: Similar title '{title}' may already exist in document")

            # Check for very long additions
            if len(additions) > 50:
                warnings.append(f"⚠️ INFO: Large update ({len(additions)} lines) - review carefully")

        except Exception as e:
            logger.error(f"Conflict check failed for {doc_path}: {e}")
            warnings.append(f"⚠️ WARNING: Could not check for conflicts: {e}")

        return warnings

    def _generate_summary(
        self,
        previews: List[DocumentPreview],
        request_type: RequestType,
        total_additions: int,
    ) -> str:
        """Generate summary of all previews.

        Args:
            previews: List of document previews
            request_type: Type of request
            total_additions: Total lines being added

        Returns:
            Summary text
        """
        summary = []

        summary.append("=" * 80)
        summary.append("📋 UPDATE SUMMARY")
        summary.append("=" * 80)
        summary.append("")
        summary.append(f"Request Type: {request_type.value}")
        summary.append(f"Documents to Update: {len(previews)}")
        summary.append(f"Total Lines to Add: {total_additions}")
        summary.append("")

        # List documents
        summary.append("Documents:")
        for preview in previews:
            summary.append(f"  • {preview.document_path} ({len(preview.additions)} lines)")

        summary.append("")

        # Warnings
        all_warnings = []
        for preview in previews:
            all_warnings.extend(preview.warnings)

        if all_warnings:
            summary.append("⚠️ Warnings:")
            for warning in all_warnings:
                summary.append(f"  {warning}")
            summary.append("")

        summary.append("=" * 80)

        return "\n".join(summary)

    def format_confirmation_prompt(self, preview_result: PreviewResult) -> str:
        """Format a confirmation prompt for the user.

        Args:
            preview_result: Preview result with all previews

        Returns:
            Formatted confirmation prompt

        Example:
            >>> prompt = generator.format_confirmation_prompt(result)
            >>> print(prompt)
            Would you like to apply these changes? [y/n]
        """
        prompt = []

        prompt.append(preview_result.summary)
        prompt.append("")

        for preview in preview_result.previews:
            prompt.append(preview.preview_text)
            prompt.append("")

        prompt.append("=" * 80)
        prompt.append("❓ CONFIRMATION REQUIRED")
        prompt.append("=" * 80)
        prompt.append("")
        prompt.append("Would you like to apply these changes to the documents?")
        prompt.append("")
        prompt.append("Type 'y' or 'yes' to apply changes")
        prompt.append("Type 'n' or 'no' to cancel")
        prompt.append("Type 'preview' to see the preview again")
        prompt.append("")
        prompt.append("Your choice: ")

        return "\n".join(prompt)
