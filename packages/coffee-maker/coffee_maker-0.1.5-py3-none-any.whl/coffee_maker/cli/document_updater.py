"""Document updater system for intelligent document routing and updates.

This module handles automatic updates to project documentation based on
classified user requests (feature requests, methodology changes, hybrid).

Key Features:
- Atomic updates with automatic backups
- Graceful error handling with auto-restore
- Smart insertion logic for different document types
- Verification of applied updates

Integration with US-021:
- RequestClassifier identifies request type
- AIService processes request with AI
- DocumentUpdater routes to appropriate documents
- Backup/restore ensures no data loss

Example:
    >>> from coffee_maker.cli.document_updater import DocumentUpdater
    >>> from coffee_maker.cli.request_classifier import RequestType
    >>>
    >>> updater = DocumentUpdater()
    >>> result = updater.update_documents(
    ...     request_type=RequestType.FEATURE_REQUEST,
    ...     content="I want to add email notifications",
    ...     target_documents=["docs/roadmap/ROADMAP.md"],
    ...     metadata={'title': 'Email Notifications', 'business_value': 'High'}
    ... )
    >>> print(result)
    {'docs/roadmap/ROADMAP.md': True}
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.cli.request_classifier import RequestType

# Phase 4 imports
try:
    from coffee_maker.cli.preview_generator import PreviewGenerator, PreviewResult

    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentUpdateError(Exception):
    """Raised when document update fails."""


class ValidationError(Exception):
    """Raised when validation fails."""


class DocumentUpdater:
    """Handles updates to project documentation files.

    This class provides intelligent document routing and updates based on
    request classification. It ensures atomic updates with automatic backups
    and graceful error recovery.

    Attributes:
        ROADMAP_PATH: Path to main roadmap file
        COLLABORATION_PATH: Path to collaboration methodology file
        CLAUDE_PATH: Path to Claude instructions file
        backup_dir: Directory for document backups

    Example:
        >>> updater = DocumentUpdater()
        >>> # Feature request -> ROADMAP.md
        >>> updater.update_documents(
        ...     request_type=RequestType.FEATURE_REQUEST,
        ...     content="Add Slack integration",
        ...     target_documents=["docs/roadmap/ROADMAP.md"],
        ...     metadata={'title': 'Slack Integration'}
        ... )
        >>>
        >>> # Methodology change -> COLLABORATION_METHODOLOGY.md + CLAUDE.md
        >>> updater.update_documents(
        ...     request_type=RequestType.METHODOLOGY_CHANGE,
        ...     content="Always require 2 PR approvals",
        ...     target_documents=["docs/COLLABORATION_METHODOLOGY.md", ".claude/CLAUDE.md"],
        ...     metadata={'title': 'PR Approval Policy'}
        ... )
    """

    # Document paths (relative to project root)
    ROADMAP_PATH = Path("docs/roadmap/ROADMAP.md")
    COLLABORATION_PATH = Path("docs/COLLABORATION_METHODOLOGY.md")
    CLAUDE_PATH = Path(".claude/CLAUDE.md")

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize document updater.

        Args:
            project_root: Optional project root path (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.backup_dir = self.project_root / ".backups" / "document_updates"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize PreviewGenerator for Phase 4
        self.preview_generator = None
        if PREVIEW_AVAILABLE:
            self.preview_generator = PreviewGenerator(project_root=self.project_root)
            logger.info("PreviewGenerator initialized (US-021 Phase 4)")

        logger.info(f"DocumentUpdater initialized (backup_dir: {self.backup_dir})")

    def preview_updates(
        self,
        request_type: RequestType,
        content: str,
        target_documents: List[str],
        metadata: Optional[Dict] = None,
    ) -> Optional[PreviewResult]:
        """Generate preview of document updates without applying changes.

        Phase 4 feature: Shows user what will be added before committing changes.

        Args:
            request_type: Type of request
            content: Content to add
            target_documents: List of document paths to update
            metadata: Additional metadata

        Returns:
            PreviewResult with previews, or None if preview not available

        Example:
            >>> updater = DocumentUpdater()
            >>> preview = updater.preview_updates(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     content="Add email notifications",
            ...     target_documents=["docs/roadmap/ROADMAP.md"],
            ...     metadata={'title': 'Email Notifications'}
            ... )
            >>> print(preview.summary)
        """
        if not self.preview_generator:
            logger.warning("PreviewGenerator not available, skipping preview")
            return None

        try:
            # Add US number to metadata if not present
            metadata = metadata or {}
            if "us_number" not in metadata and "ROADMAP" in str(target_documents):
                # Get next US number
                roadmap_path = self.project_root / "docs/roadmap/ROADMAP.md"
                if roadmap_path.exists():
                    with open(roadmap_path, "r") as f:
                        lines = f.readlines()
                    metadata["us_number"] = self._get_next_us_number(lines)

            preview = self.preview_generator.generate_preview(
                request_type=request_type,
                content=content,
                target_documents=target_documents,
                metadata=metadata,
            )

            logger.info(f"Preview generated: {len(preview.previews)} document(s), {preview.total_additions} lines")
            return preview

        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return None

    def validate_update(
        self,
        request_type: RequestType,
        content: str,
        target_documents: List[str],
        metadata: Optional[Dict] = None,
    ) -> Dict[str, List[str]]:
        """Validate document update before applying changes.

        Phase 4 feature: Checks for conflicts, duplicates, and consistency issues.

        Args:
            request_type: Type of request
            content: Content to add
            target_documents: List of document paths
            metadata: Additional metadata

        Returns:
            Dictionary with validation results:
            {
                'errors': ['error1', ...],    # Must fix before applying
                'warnings': ['warning1', ...], # Should review, but can proceed
                'info': ['info1', ...]        # Informational messages
            }

        Example:
            >>> updater = DocumentUpdater()
            >>> validation = updater.validate_update(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     content="Add email notifications",
            ...     target_documents=["docs/roadmap/ROADMAP.md"],
            ...     metadata={'title': 'Email Notifications'}
            ... )
            >>> if validation['errors']:
            ...     print("Cannot proceed:", validation['errors'])
        """
        errors = []
        warnings = []
        info = []

        metadata = metadata or {}

        try:
            # Validate target documents exist or can be created
            for doc_path in target_documents:
                full_path = self.project_root / doc_path

                if not full_path.exists():
                    parent_dir = full_path.parent
                    if not parent_dir.exists():
                        errors.append(f"Parent directory does not exist: {parent_dir}")
                    else:
                        info.append(f"Document will be created: {doc_path}")

            # Validate ROADMAP updates
            if any("ROADMAP" in doc for doc in target_documents):
                roadmap_path = self.project_root / "docs/roadmap/ROADMAP.md"
                if roadmap_path.exists():
                    with open(roadmap_path, "r") as f:
                        roadmap_content = f.read()

                    # Check for duplicate US numbers
                    us_number = metadata.get("us_number")
                    if us_number:
                        pattern = f"## US-{us_number:03d}:"
                        if pattern in roadmap_content:
                            errors.append(f"US-{us_number:03d} already exists in ROADMAP")

                    # Check for similar titles
                    title = metadata.get("title")
                    if title and title.lower() in roadmap_content.lower():
                        warnings.append(f"Similar title '{title}' may already exist in ROADMAP")

                    # Check metadata completeness
                    if not metadata.get("title"):
                        warnings.append("Title not provided, will use default")
                    if not metadata.get("business_value"):
                        info.append("Business value not provided, will be marked as TBD")
                    if not metadata.get("estimated_effort"):
                        info.append("Estimated effort not provided, will be marked as TBD")

            # Validate COLLABORATION_METHODOLOGY updates
            if any("COLLABORATION" in doc for doc in target_documents):
                # Check metadata completeness
                if not metadata.get("rationale"):
                    warnings.append("Rationale not provided for methodology change")
                if not metadata.get("applies_to"):
                    info.append("'Applies to' not specified, defaulting to 'All team members'")

            # Validate content not empty
            if not content or not content.strip():
                errors.append("Content is empty, cannot create update")

            # Check for very long content
            if len(content) > 10000:
                warnings.append(f"Content is very long ({len(content)} chars), may be too detailed")

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            errors.append(f"Validation error: {e}")

        logger.info(f"Validation completed: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info")

        return {"errors": errors, "warnings": warnings, "info": info}

    def update_documents(
        self,
        request_type: RequestType,
        content: str,
        target_documents: List[str],
        metadata: Optional[Dict] = None,
    ) -> Dict[str, bool]:
        """Update documents based on classification.

        This method performs atomic updates with automatic backup/restore:
        1. Creates backup of each target document
        2. Updates documents sequentially
        3. Verifies updates applied correctly
        4. Restores from backup on error

        Args:
            request_type: Type of request (FEATURE_REQUEST, METHODOLOGY_CHANGE, HYBRID)
            content: Content to add/update (user's original request)
            target_documents: List of document paths to update
            metadata: Additional metadata (title, business_value, section, etc.)

        Returns:
            Dict mapping document paths to success status
            Example: {'docs/roadmap/ROADMAP.md': True, '.claude/CLAUDE.md': False}

        Raises:
            DocumentUpdateError: If update fails (after restoring backups)

        Example:
            >>> updater = DocumentUpdater()
            >>> result = updater.update_documents(
            ...     request_type=RequestType.FEATURE_REQUEST,
            ...     content="Add GraphQL API support",
            ...     target_documents=["docs/roadmap/ROADMAP.md"],
            ...     metadata={
            ...         'title': 'GraphQL API',
            ...         'business_value': 'Enable modern API access patterns',
            ...         'estimated_effort': '3-5 days'
            ...     }
            ... )
        """
        metadata = metadata or {}
        results = {}

        logger.info(f"Updating {len(target_documents)} document(s) for {request_type.value} request")

        for doc_path in target_documents:
            try:
                # Resolve full path
                full_path = self.project_root / doc_path

                # Create backup first
                logger.debug(f"Creating backup of {doc_path}")
                self._create_backup(full_path)

                # Update the document
                if "ROADMAP" in doc_path:
                    success = self._update_roadmap(full_path, content, metadata)
                elif "COLLABORATION" in doc_path:
                    success = self._update_collaboration(full_path, content, metadata)
                elif "CLAUDE.md" in doc_path:
                    success = self._update_claude(full_path, content, metadata)
                else:
                    logger.warning(f"Unknown document type: {doc_path}")
                    success = False

                results[doc_path] = success

                if success:
                    logger.info(f"✅ Successfully updated {doc_path}")
                else:
                    logger.warning(f"❌ Failed to update {doc_path}")

            except Exception as e:
                # Restore from backup on error
                logger.error(f"Error updating {doc_path}: {e}")
                logger.info(f"Restoring {doc_path} from backup...")
                self._restore_backup(full_path)
                raise DocumentUpdateError(f"Failed to update {doc_path}: {e}") from e

        return results

    def _create_backup(self, doc_path: Path):
        """Create backup of document before modification.

        Args:
            doc_path: Path to document to backup
        """
        if not doc_path.exists():
            logger.warning(f"Document {doc_path} does not exist, skipping backup")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{doc_path.stem}_{timestamp}{doc_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(doc_path, backup_path)
        logger.debug(f"Backup created: {backup_path}")

    def _restore_backup(self, doc_path: Path):
        """Restore document from most recent backup.

        Args:
            doc_path: Path to document to restore
        """
        # Find most recent backup
        backups = sorted(
            self.backup_dir.glob(f"{doc_path.stem}_*{doc_path.suffix}"),
            reverse=True,
        )

        if not backups:
            logger.warning(f"No backup found for {doc_path}")
            return

        most_recent = backups[0]
        shutil.copy2(most_recent, doc_path)
        logger.info(f"Restored {doc_path} from backup: {most_recent.name}")

    def _update_roadmap(self, roadmap_path: Path, content: str, metadata: Dict) -> bool:
        """Add user story to ROADMAP.md.

        Args:
            roadmap_path: Path to ROADMAP.md file
            content: User story description (original user request)
            metadata: User story details (title, priority, business_value, etc.)

        Returns:
            True if successful

        Example Entry Format:
            ## US-034: Email Notifications

            **Status**: 📝 **PLANNED**
            **Created**: 2025-10-15
            **Classification**: 🔵 FEATURE REQUEST

            **Description**:
            I want to add email notifications for completed tasks

            **Business Value**: Keep users informed without checking app
            **Estimated Effort**: 2-3 days

            **Acceptance Criteria**:
            - [ ] Users can configure email preferences
            - [ ] Emails sent on task completion
            - [ ] Email templates are customizable

            ---
        """
        if not roadmap_path.exists():
            logger.error(f"ROADMAP not found at {roadmap_path}")
            return False

        try:
            # Read current ROADMAP
            with open(roadmap_path, "r") as f:
                lines = f.readlines()

            # Find insertion point (after TOP PRIORITY section)
            insert_index = self._find_roadmap_insertion_point(lines)

            # Get next US number
            us_number = self._get_next_us_number(lines)
            timestamp = datetime.now().strftime("%Y-%m-%d")

            # Format new user story
            title = metadata.get("title", "New Feature")
            business_value = metadata.get("business_value", "TBD")
            estimated_effort = metadata.get("estimated_effort", "TBD")
            acceptance_criteria = metadata.get("acceptance_criteria", ["Feature implemented and tested"])

            # Build acceptance criteria list
            if isinstance(acceptance_criteria, str):
                acceptance_criteria = [acceptance_criteria]

            criteria_lines = "\n".join([f"- [ ] {criterion}" for criterion in acceptance_criteria])

            new_entry = f"""
## US-{us_number:03d}: {title}

**Status**: 📝 **PLANNED**
**Created**: {timestamp}
**Classification**: 🔵 FEATURE REQUEST (via AI classification)

**Description**:
{content}

**Business Value**: {business_value}
**Estimated Effort**: {estimated_effort}

**Acceptance Criteria**:
{criteria_lines}

---

"""

            # Insert new entry
            lines.insert(insert_index, new_entry)

            # Write back
            with open(roadmap_path, "w") as f:
                f.writelines(lines)

            logger.info(f"Added US-{us_number:03d} to ROADMAP: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to update ROADMAP: {e}")
            return False

    def _update_collaboration(self, collab_path: Path, content: str, metadata: Dict) -> bool:
        """Update COLLABORATION_METHODOLOGY.md with methodology change.

        Args:
            collab_path: Path to COLLABORATION_METHODOLOGY.md file
            content: Methodology change description
            metadata: Change details (title, rationale, applies_to, section, etc.)

        Returns:
            True if successful

        Example Entry Format:
            ### PR Approval Policy (Added 2025-10-15)

            All pull requests must have 2 approvals before merging to ensure
            code quality and knowledge sharing.

            **Rationale**: Reduces bugs, improves code quality, spreads knowledge
            **Applies to**: All team members
        """
        if not collab_path.exists():
            logger.error(f"COLLABORATION_METHODOLOGY not found at {collab_path}")
            return False

        try:
            # Read current document
            with open(collab_path, "r") as f:
                lines = f.readlines()

            # Find appropriate section
            section_name = metadata.get("section", "General Guidelines")
            insert_index = self._find_collaboration_section(lines, section_name)

            # Format new methodology entry
            timestamp = datetime.now().strftime("%Y-%m-%d")
            title = metadata.get("title", "New Methodology")
            rationale = metadata.get("rationale", "TBD")
            applies_to = metadata.get("applies_to", "All team members")

            new_entry = f"""
### {title} (Added {timestamp})

{content}

**Rationale**: {rationale}
**Applies to**: {applies_to}

"""

            # Insert
            lines.insert(insert_index, new_entry)

            # Write back
            with open(collab_path, "w") as f:
                f.writelines(lines)

            logger.info(f"Added methodology to COLLABORATION_METHODOLOGY: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to update COLLABORATION_METHODOLOGY: {e}")
            return False

    def _update_claude(self, claude_path: Path, content: str, metadata: Dict) -> bool:
        """Update .claude/CLAUDE.md with technical guidelines.

        Args:
            claude_path: Path to CLAUDE.md file
            content: Technical guideline description
            metadata: Guideline details (title, section, etc.)

        Returns:
            True if successful

        Example Entry Format:
            ### Git Branch Naming Convention (Added 2025-10-15)

            All feature branches must follow the pattern: feature/us-XXX-descriptive-name

            This ensures branch names are consistent and traceable to user stories.
        """
        if not claude_path.exists():
            logger.error(f"CLAUDE.md not found at {claude_path}")
            return False

        try:
            # Read current document
            with open(claude_path, "r") as f:
                lines = f.readlines()

            # Find appropriate section
            section_name = metadata.get("section", "Special Instructions for Claude")
            insert_index = self._find_claude_section(lines, section_name)

            # Format new entry
            timestamp = datetime.now().strftime("%Y-%m-%d")
            title = metadata.get("title", "New Guideline")

            new_entry = f"""
### {title} (Added {timestamp})

{content}

"""

            # Insert
            lines.insert(insert_index, new_entry)

            # Write back
            with open(claude_path, "w") as f:
                f.writelines(lines)

            logger.info(f"Added guideline to CLAUDE.md: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to update CLAUDE.md: {e}")
            return False

    def _find_roadmap_insertion_point(self, lines: List[str]) -> int:
        """Find where to insert new user story in ROADMAP.

        Strategy:
        1. Look for "## US-" pattern (user story heading)
        2. Insert before the first user story found
        3. If no user stories, append to end

        Args:
            lines: List of lines from ROADMAP.md

        Returns:
            Line index where new user story should be inserted
        """
        for i, line in enumerate(lines):
            if line.startswith("## US-"):
                # Found first user story, insert before it
                return i

        # No user stories found, append to end
        return len(lines)

    def _find_collaboration_section(self, lines: List[str], section: str) -> int:
        """Find section in COLLABORATION_METHODOLOGY.md.

        Args:
            lines: List of lines from document
            section: Section name to find (e.g., "Workflows", "General Guidelines")

        Returns:
            Line index where new content should be inserted
        """
        for i, line in enumerate(lines):
            if section.lower() in line.lower() and line.startswith("##"):
                # Insert after section heading
                return i + 1

        # Section not found, create new section at end
        logger.warning(f"Section '{section}' not found, appending to end")
        return len(lines)

    def _find_claude_section(self, lines: List[str], section: str) -> int:
        """Find section in CLAUDE.md.

        Args:
            lines: List of lines from document
            section: Section name to find

        Returns:
            Line index where new content should be inserted
        """
        for i, line in enumerate(lines):
            if section.lower() in line.lower() and line.startswith("##"):
                # Insert after section heading
                return i + 1

        # Section not found, append to end
        logger.warning(f"Section '{section}' not found, appending to end")
        return len(lines)

    def _get_next_us_number(self, lines: List[str]) -> int:
        """Get next available US number from ROADMAP.

        Scans all lines looking for "## US-XXX:" pattern and returns max + 1.

        Args:
            lines: List of lines from ROADMAP.md

        Returns:
            Next available US number (e.g., if US-033 exists, returns 34)
        """
        max_num = 0

        for line in lines:
            if line.startswith("## US-"):
                try:
                    # Extract number from "## US-XXX:" pattern
                    num = int(line.split("US-")[1].split(":")[0])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    # Skip malformed lines
                    pass

        return max_num + 1

    def verify_update(self, doc_path: str, expected_content: str) -> bool:
        """Verify that document was updated correctly.

        Args:
            doc_path: Path to document (relative to project root)
            expected_content: Content that should be present

        Returns:
            True if content found in document

        Example:
            >>> updater = DocumentUpdater()
            >>> updater.verify_update("docs/roadmap/ROADMAP.md", "Email Notifications")
            True
        """
        full_path = self.project_root / doc_path

        if not full_path.exists():
            logger.warning(f"Document {doc_path} does not exist")
            return False

        try:
            with open(full_path, "r") as f:
                content = f.read()

            found = expected_content in content

            if found:
                logger.debug(f"✅ Verified: '{expected_content}' found in {doc_path}")
            else:
                logger.warning(f"❌ Verification failed: '{expected_content}' not found in {doc_path}")

            return found

        except Exception as e:
            logger.error(f"Verification failed for {doc_path}: {e}")
            return False
