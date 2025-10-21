"""Template-based Technical Specification Generator.

This module provides a fallback mechanism for creating technical specifications
when architect delegation is not available or fails. It generates basic specs
from SPEC-000-template.md by filling in priority details.

US-045: Phase 1 - Template Fallback for Immediate Daemon Unblock

This approach:
1. Loads SPEC-000-template.md as a template
2. Fills template placeholders with priority details
3. Adds a TODO marker for architect review
4. Writes the result to docs/architecture/specs/

This unblocks the daemon immediately while Phase 2 (Tool Use API) is developed.

Classes:
    SpecTemplateManager: Generate specs from templates

Usage:
    >>> manager = SpecTemplateManager()
    >>> priority = {
    ...     "name": "PRIORITY 9",
    ...     "title": "Enhanced Communication",
    ...     "content": "Implement enhanced inter-agent communication..."
    ... }
    >>> success = manager.create_spec_from_template(
    ...     priority=priority,
    ...     spec_filename="SPEC-009-enhanced-communication.md"
    ... )
    >>> print(f"Created: {success}")
    Created: True
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SpecTemplateManager:
    """Generate technical specifications from templates.

    This manager provides a fallback mechanism for creating basic technical
    specifications when architect delegation is not available. It:
    1. Loads a template from docs/architecture/specs/SPEC-000-template.md
    2. Fills in priority details
    3. Adds architect review markers
    4. Writes to docs/architecture/specs/

    Attributes:
        template_path: Path to template file
        specs_dir: Output directory for specs

    Example:
        >>> manager = SpecTemplateManager()
        >>> priority = {"name": "US-045", "title": "Fix Daemon Loop", "content": "..."}
        >>> manager.create_spec_from_template(priority, "SPEC-045-fix-daemon.md")
        True
    """

    def __init__(
        self,
        template_path: str = "docs/architecture/specs/SPEC-000-template.md",
        specs_dir: str = "docs/architecture/specs",
    ):
        """Initialize the spec template manager.

        Args:
            template_path: Path to template file relative to project root
            specs_dir: Output directory for generated specs relative to project root
        """
        self.template_path = Path(template_path)
        self.specs_dir = Path(specs_dir)

    def create_spec_from_template(
        self,
        priority: dict,
        spec_filename: str,
    ) -> bool:
        """Create a technical specification from template.

        Fills the template with priority details and writes to specs_dir.
        Marks the spec with a TODO for architect review.

        Args:
            priority: Priority dictionary with 'name', 'title', 'content'
            spec_filename: Output filename (e.g., "SPEC-009-priority-name.md")

        Returns:
            True if spec was created successfully, False otherwise

        Example:
            >>> manager = SpecTemplateManager()
            >>> priority = {
            ...     "name": "PRIORITY 9",
            ...     "title": "Enhanced Communication",
            ...     "content": "Add inter-agent communication..."
            ... }
            >>> manager.create_spec_from_template(priority, "SPEC-009-comm.md")
            True
        """
        try:
            # Validate inputs
            if not priority.get("name"):
                logger.error("Cannot create spec: priority missing 'name' field")
                return False

            if not spec_filename:
                logger.error("Cannot create spec: spec_filename is empty")
                return False

            # Load template
            if not self.template_path.exists():
                logger.error(f"Template not found: {self.template_path.resolve()}")
                return False

            template_content = self.template_path.read_text()
            logger.info(f"Loaded template from {self.template_path}")

            # Extract priority details
            priority_name = priority.get("name", "Unknown")
            priority_title = priority.get("title", "No title provided")
            priority_content = priority.get("content", "")

            # Extract problem statement from priority content
            problem_statement = self._extract_problem_statement(priority_name, priority_title, priority_content)

            # Generate basic architecture outline
            basic_architecture = self._generate_basic_architecture(priority)

            # Fill template placeholders
            spec_content = self._fill_template(
                template_content,
                priority_name=priority_name,
                priority_title=priority_title,
                problem_statement=problem_statement,
                basic_architecture=basic_architecture,
                spec_filename=spec_filename,
            )

            # Ensure specs directory exists
            self.specs_dir.mkdir(parents=True, exist_ok=True)

            # Write spec file
            output_path = self.specs_dir / spec_filename
            output_path.write_text(spec_content)

            logger.info(f"✅ Created technical spec from template: {output_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error creating spec from template: {e}", exc_info=True)
            return False

    def _extract_problem_statement(self, priority_name: str, priority_title: str, priority_content: str) -> str:
        """Extract problem statement from priority details.

        Args:
            priority_name: Priority identifier (e.g., "PRIORITY 9")
            priority_title: Priority title
            priority_content: Full priority content from ROADMAP

        Returns:
            Problem statement for the spec

        Example:
            >>> manager = SpecTemplateManager()
            >>> stmt = manager._extract_problem_statement(
            ...     "PRIORITY 9", "Enhanced Communication",
            ...     "Add inter-agent communication with metrics..."
            ... )
            >>> print(stmt[:50])
            Priority 9: Enhanced Communication
        """
        lines = []

        # Add priority identifier and title
        lines.append(f"**Priority**: {priority_name}")
        lines.append(f"**Title**: {priority_title}")
        lines.append("")

        # Use content if available, otherwise use title
        if priority_content and len(priority_content.strip()) > 0:
            # Take first 500 characters to avoid huge content blocks
            content_snippet = priority_content.strip()
            if len(content_snippet) > 500:
                content_snippet = content_snippet[:500] + "..."

            lines.append("**Details from ROADMAP**:")
            lines.append(content_snippet)
        else:
            lines.append("No additional details provided in ROADMAP. " "See ROADMAP.md for full context.")

        lines.append("")
        lines.append("**Note**: This spec was auto-generated from template.")
        lines.append("Architect review and enhancement recommended.")

        return "\n".join(lines)

    def _generate_basic_architecture(self, priority: dict) -> str:
        """Generate basic architecture outline from priority.

        Args:
            priority: Priority dictionary

        Returns:
            Basic architecture outline

        Example:
            >>> manager = SpecTemplateManager()
            >>> priority = {"name": "PRIORITY 9", "title": "Communication"}
            >>> arch = manager._generate_basic_architecture(priority)
            >>> print(arch[:30])
            This feature requires the fol
        """
        lines = []

        lines.append("This feature requires the following architectural components:")
        lines.append("")
        lines.append("1. **Core Component**: Main feature implementation")
        lines.append("2. **Integration Points**: How this interacts with existing code")
        lines.append("3. **Data Models**: Required data structures (if any)")
        lines.append("4. **Error Handling**: Graceful failure modes")
        lines.append("5. **Testing**: Unit, integration, and end-to-end tests")
        lines.append("")
        lines.append("**Note**: See ROADMAP and related strategic specs for context.")
        lines.append("Architect should expand this outline during review.")

        return "\n".join(lines)

    def _fill_template(
        self,
        template_content: str,
        priority_name: str,
        priority_title: str,
        problem_statement: str,
        basic_architecture: str,
        spec_filename: str,
    ) -> str:
        """Fill template placeholders with priority details.

        Args:
            template_content: Template file content
            priority_name: Priority identifier
            priority_title: Priority title
            problem_statement: Problem statement content
            basic_architecture: Architecture outline
            spec_filename: Output filename

        Returns:
            Filled template content ready to write

        Example:
            >>> template = "# SPEC-XXX: [Feature Name]\\n\\n**Status**: Draft"
            >>> filled = manager._fill_template(
            ...     template,
            ...     priority_name="PRIORITY 9",
            ...     priority_title="Communication",
            ...     problem_statement="Need better communication",
            ...     basic_architecture="Components: A, B, C",
            ...     spec_filename="SPEC-009-comm.md"
            ... )
            >>> print("PRIORITY 9" in filled)
            True
        """
        content = template_content

        # Extract spec number from filename (SPEC-009-comm.md -> 009-COMM)
        spec_filename.split("-", 1)[1].replace(".md", "")

        # Replace placeholders
        replacements = {
            "[Feature Name]": priority_title,
            "Draft | In Review | Approved | Implemented | Deprecated": "Draft (auto-generated from template)",
            "YYYY-MM-DD": datetime.now().strftime("%Y-%m-%d"),
            "[Link to project_manager's strategic spec": ("[Strategic spec link - to be added during architect review"),
            "[Link to relevant ADRs]": "[ADRs - to be added during architect review]",
            "[Agent responsible for implementation, typically code_developer]": ("code_developer"),
            "Brief 2-3 sentence summary of what this spec describes.": (
                f"This spec describes the technical implementation of {priority_title} "
                f"({priority_name}). Auto-generated from template - architect review needed."
            ),
            "Describe the current state and what problems exist.": (problem_statement),
            "Describe the solution at a high level.": basic_architecture,
        }

        for placeholder, replacement in replacements.items():
            content = content.replace(placeholder, replacement)

        # Add architect review marker at the top
        review_marker = (
            f"⚠️  **TODO: Review by architect**\n\n"
            f"This specification was auto-generated from SPEC-000-template.md by the daemon "
            f"(US-045 Phase 1 fallback). It should be reviewed and enhanced by the architect "
            f"to ensure quality and completeness. See the end of this document for "
            f"sections marked 'TODO'.\n\n"
        )

        # Insert review marker after the initial metadata
        lines = content.split("\n")
        # Find the line with "---" (end of metadata)
        separator_index = -1
        for i, line in enumerate(lines):
            if line.strip() == "---":
                separator_index = i
                break

        if separator_index > 0:
            # Insert after the first separator
            lines.insert(separator_index + 1, review_marker)
            content = "\n".join(lines)

        return content
