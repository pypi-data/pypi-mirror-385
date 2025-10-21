"""Technical Specification Handler - Unified spec operations for architect and code_developer.

This module provides a single source of truth for all technical specification operations,
ensuring consistency across all agents.

Usage:
    from coffee_maker.utils.spec_handler import SpecHandler

    handler = SpecHandler()
    spec_path = handler.find_spec(priority)
    spec_content = handler.create_spec(us_number="104", title="Feature Name", ...)
"""

import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpecHandler:
    """Unified technical specification handler for all agents."""

    def __init__(self):
        """Initialize the spec handler."""
        self.specs_dir = Path("docs/architecture/specs")
        self.roadmap_dir = Path("docs/roadmap")

    # ==================== FINDING SPECIFICATIONS ====================

    def find_spec(self, priority: Dict[str, Any]) -> Optional[Path]:
        """Find spec file for a priority.

        Args:
            priority: Dict with keys:
                - "number": Priority number (e.g., "20")
                - "title": Title (e.g., "US-104 - Orchestrator...")
                - "name": Name (e.g., "US-104" or "PRIORITY 20")

        Returns:
            Path to spec file or None

        Examples:
            >>> priority = {"number": "20", "title": "US-104 - Feature"}
            >>> spec_path = handler.find_spec(priority)
            >>> # Returns: docs/architecture/specs/SPEC-104-feature.md
        """
        # 1. Extract US number from title
        us_match = re.search(r"US-(\d+)", priority.get("title", ""))
        us_number = us_match.group(1) if us_match else None

        # 2. Try specs directory with multiple patterns
        patterns = []

        # PRIMARY: Try US number (e.g., SPEC-104-*.md)
        if us_number:
            patterns.extend(
                [
                    f"SPEC-{us_number}-*.md",
                    f"SPEC-{us_number.zfill(3)}-*.md",  # Zero-padded
                ]
            )

        # FALLBACK: Try priority number (backward compatibility)
        priority_num = priority.get("number", "")
        if priority_num:
            patterns.extend(
                [
                    f"SPEC-{priority_num}-*.md",
                    f"SPEC-{priority_num.replace('.', '-')}-*.md",
                ]
            )

        # Search for first match
        for pattern in patterns:
            matches = list(self.specs_dir.glob(pattern))
            if matches:
                logger.debug(f"Found spec using pattern {pattern}: {matches[0]}")
                return matches[0]

        # Fallback: Old location (docs/roadmap/)
        old_path = self.roadmap_dir / f"PRIORITY_{priority_num}_TECHNICAL_SPEC.md"
        if old_path.exists():
            logger.debug(f"Found spec in old location: {old_path}")
            return old_path

        logger.debug(f"No spec found for priority {priority_num}")
        return None

    def find_spec_by_us_id(self, us_id: str) -> Optional[Path]:
        """Find spec by US-XXX identifier.

        Args:
            us_id: US identifier (e.g., "US-104" or "104")

        Returns:
            Path to spec file or None
        """
        # Extract number from US-XXX format
        us_match = re.search(r"(\d+)", us_id)
        if not us_match:
            return None

        us_number = us_match.group(1)

        # Try different patterns
        patterns = [
            f"SPEC-{us_number}-*.md",
            f"SPEC-{us_number.zfill(3)}-*.md",
        ]

        for pattern in patterns:
            matches = list(self.specs_dir.glob(pattern))
            if matches:
                return matches[0]

        return None

    def spec_exists(self, priority: Dict[str, Any]) -> bool:
        """Check if spec exists for priority.

        Args:
            priority: Priority dict

        Returns:
            bool: True if spec exists, False otherwise
        """
        return self.find_spec(priority) is not None

    # ==================== CREATING SPECIFICATIONS ====================

    def create_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str = "",
        user_story: str = "",
        architecture: str = "",
        implementation_plan: str = "",
        testing_strategy: str = "",
        estimated_effort: str = "TBD",
        template_type: str = "full",
    ) -> str:
        """Create technical specification content.

        Args:
            us_number: User story number (e.g., "104")
            title: Feature title (e.g., "Orchestrator Continuous Agent Work Loop")
            priority_number: Priority number (e.g., "20")
            problem_statement: What problem are we solving?
            user_story: As {role}, I want {feature} so that {benefit}
            architecture: Architecture description
            implementation_plan: Step-by-step implementation
            testing_strategy: Testing approach
            estimated_effort: Time estimate (e.g., "40-50 hours")
            template_type: "full", "minimal", or "poc"

        Returns:
            str: Spec file content
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        if template_type == "minimal":
            return self._create_minimal_spec(
                us_number, title, priority_number, problem_statement, estimated_effort, date_str
            )
        elif template_type == "poc":
            return self._create_poc_spec(us_number, title, priority_number, problem_statement, date_str)
        else:
            return self._create_full_spec(
                us_number,
                title,
                priority_number,
                problem_statement,
                user_story,
                architecture,
                implementation_plan,
                testing_strategy,
                estimated_effort,
                date_str,
            )

    def _create_full_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str,
        user_story: str,
        architecture: str,
        implementation_plan: str,
        testing_strategy: str,
        estimated_effort: str,
        date_str: str,
    ) -> str:
        """Create full technical specification."""
        # Default values for optional sections
        default_impl_plan = """### Phase 1: Foundation (X hours)
- [ ] Task 1
- [ ] Task 2

### Phase 2: Core Features (X hours)
- [ ] Task 3
- [ ] Task 4

### Phase 3: Polish (X hours)
- [ ] Task 5
- [ ] Task 6"""

        default_testing = """1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test full workflow

**Test Coverage Target**: >80%"""

        # Use provided values or defaults
        impl_plan_content = implementation_plan or default_impl_plan
        testing_content = testing_strategy or default_testing
        problem_content = problem_statement or "TODO: What problem are we solving? Why is this important?"
        user_story_content = (
            user_story or f"As a developer, I want {title.lower()} so that the system is more effective."
        )
        architecture_content = architecture or "TODO: Add architecture description"

        return f"""# SPEC-{us_number.zfill(3)}: {title}

**Status**: Draft
**Author**: architect agent
**Date**: {date_str}
**Version**: 1.0.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## Executive Summary

**TL;DR**: {problem_content}

**User Story**: {user_story_content}

**Success Criteria**:
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Code coverage >80%
- [ ] Documentation updated

---

## Problem Statement

{problem_content}

**Current Pain Points**:
1. TODO: Pain point 1
2. TODO: Pain point 2

**Desired Outcome**: TODO: What success looks like.

---

## Architecture

### High-Level Design

{architecture_content}

```
[Diagram or description of architecture]
```

### Components

1. **Component 1** (`path/to/component.py`):
   - Purpose: What it does
   - Interface: Key methods/classes
   - Dependencies: What it depends on

2. **Component 2** (`path/to/component2.py`):
   - Purpose: What it does
   - Interface: Key methods/classes
   - Dependencies: What it depends on

---

## Implementation Plan

{impl_plan_content}

**Total Estimate**: {estimated_effort}

---

## Testing Strategy

{testing_content}

---

## Acceptance Criteria (DoD)

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Code coverage >80%
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance benchmarks met

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TODO: Risk 1 | Medium | High | Mitigation strategy |
| TODO: Risk 2 | Low | Medium | Mitigation strategy |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {date_str} | architect | Initial specification |

---

## References

- [ROADMAP](../../roadmap/ROADMAP.md)
- Related specs: TODO
- Related ADRs: TODO
"""

    def _create_minimal_spec(
        self,
        us_number: str,
        title: str,
        priority_number: str,
        problem_statement: str,
        estimated_effort: str,
        date_str: str,
    ) -> str:
        """Create minimal technical specification."""
        return f"""# SPEC-{us_number.zfill(3)}: {title}

**Status**: Draft
**Author**: architect agent
**Date**: {date_str}
**Version**: 1.0.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## Summary

{problem_statement or "TODO: What are we building and why?"}

---

## Implementation

**Estimated Effort**: {estimated_effort}

**Tasks**:
- [ ] TODO: Task 1
- [ ] TODO: Task 2
- [ ] TODO: Task 3

---

## Acceptance Criteria

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | {date_str} | architect | Initial specification |
"""

    def _create_poc_spec(
        self, us_number: str, title: str, priority_number: str, problem_statement: str, date_str: str
    ) -> str:
        """Create POC technical specification."""
        return f"""# SPEC-{us_number.zfill(3)}: {title} (POC)

**Status**: POC
**Author**: architect agent
**Date**: {date_str}
**Version**: 0.1.0
**Related**: US-{us_number}, PRIORITY {priority_number}

---

## POC Goals

{problem_statement or "TODO: What concepts are we proving?"}

**Key Questions**:
1. TODO: Question 1
2. TODO: Question 2

---

## Scope

**In Scope**:
- TODO: What we're testing
- TODO: Minimal implementation

**Out of Scope**:
- Production code
- Error handling
- Performance optimization

---

## Success Criteria

- [ ] Concept 1 proven
- [ ] Concept 2 proven
- [ ] Concept 3 proven

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | {date_str} | architect | Initial POC specification |
"""

    def generate_spec_filename(self, us_number: str, title: str) -> str:
        """Generate spec filename from US number and title.

        Args:
            us_number: User story number (e.g., "104")
            title: Feature title

        Returns:
            str: Filename (e.g., "SPEC-104-orchestrator-continuous-agent-work-loop.md")
        """
        # Convert title to kebab-case
        kebab_title = title.lower()
        kebab_title = re.sub(r"[^a-z0-9\s-]", "", kebab_title)  # Remove special chars
        kebab_title = re.sub(r"\s+", "-", kebab_title)  # Replace spaces with hyphens
        kebab_title = re.sub(r"-+", "-", kebab_title)  # Collapse multiple hyphens

        return f"SPEC-{us_number.zfill(3)}-{kebab_title}.md"

    # ==================== UPDATING SPECIFICATIONS ====================

    def update_spec(self, spec_path: Path, changes: Dict[str, Any]) -> str:
        """Update existing specification.

        Args:
            spec_path: Path to existing spec
            changes: Dict with:
                - "version": New version (optional, will auto-bump if not provided)
                - "sections_to_update": Dict of section name -> new content
                - "changelog": Description of changes

        Returns:
            str: Updated spec content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        # Extract current version
        current_version = self.extract_version(content)

        # Determine new version
        new_version = changes.get("version")
        if not new_version:
            # Auto-bump minor version
            new_version = self.bump_version(current_version, "minor")

        # Update version in header
        content = re.sub(r"\*\*Version\*\*: .+", f"**Version**: {new_version}", content)

        # Update sections
        sections_to_update = changes.get("sections_to_update", {})
        for section_name, new_content in sections_to_update.items():
            content = self._update_section(content, section_name, new_content)

        # Add to version history
        changelog = changes.get("changelog", "Updated specification")
        date_str = datetime.now().strftime("%Y-%m-%d")
        content = self._add_version_history(content, new_version, date_str, changelog)

        return content

    def extract_version(self, content: str) -> str:
        """Extract version from spec content.

        Args:
            content: Spec file content

        Returns:
            str: Version (e.g., "1.2.3") or "1.0.0" if not found
        """
        match = re.search(r"\*\*Version\*\*: (\d+\.\d+\.\d+)", content)
        return match.group(1) if match else "1.0.0"

    def bump_version(self, version: str, bump_type: str = "minor") -> str:
        """Bump version number.

        Args:
            version: Current version (e.g., "1.2.3")
            bump_type: "major", "minor", or "patch"

        Returns:
            str: New version
        """
        parts = version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"

    def _update_section(self, content: str, section_name: str, new_content: str) -> str:
        """Update a section in the spec.

        Args:
            content: Full spec content
            section_name: Section header (e.g., "Architecture")
            new_content: New section content

        Returns:
            str: Updated content
        """
        # Find section header
        pattern = rf"(## {re.escape(section_name)}\s*\n)(.*?)(?=\n##|\Z)"

        def replace_section(match):
            header = match.group(1)
            return f"{header}\n{new_content}\n"

        updated = re.sub(pattern, replace_section, content, flags=re.DOTALL)
        return updated

    def _add_version_history(self, content: str, version: str, date: str, changelog: str) -> str:
        """Add entry to version history table.

        Args:
            content: Full spec content
            version: New version
            date: Date string
            changelog: Description of changes

        Returns:
            str: Updated content
        """
        # Find version history table
        pattern = r"(## Version History\s*\n.*?\n)(.*?)(\n---|\Z)"

        def add_entry(match):
            header = match.group(1)
            table = match.group(2)
            footer = match.group(3)

            # Add new entry after header row
            lines = table.split("\n")
            if len(lines) >= 2:
                # Insert after header separator
                new_entry = f"| {version} | {date} | architect | {changelog} |"
                lines.insert(2, new_entry)
                table = "\n".join(lines)

            return f"{header}{table}{footer}"

        updated = re.sub(pattern, add_entry, content, flags=re.DOTALL)
        return updated

    # ==================== CLEANING SPECIFICATIONS ====================

    def clean_spec(self, spec_path: Path, rules: Dict[str, Any]) -> str:
        """Clean specification by removing outdated content.

        Args:
            spec_path: Path to spec
            rules: Dict with:
                - "remove_completed_checklists": bool (default: True)
                - "archive_old_versions": bool (default: True)
                - "consolidate_redundant": bool (default: False)
                - "max_version_history": int (default: 5)

        Returns:
            str: Cleaned spec content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        # Remove completed checklists
        if rules.get("remove_completed_checklists", True):
            content = self._remove_completed_checklists(content)

        # Limit version history
        max_versions = rules.get("max_version_history", 5)
        content = self._limit_version_history(content, max_versions)

        return content

    def _remove_completed_checklists(self, content: str) -> str:
        """Remove completed checklist items.

        Args:
            content: Spec content

        Returns:
            str: Content with completed items removed
        """
        # Remove lines with [x] or [X]
        lines = content.split("\n")
        cleaned_lines = [line for line in lines if not re.match(r"^\s*-\s*\[[xX]\]", line)]
        return "\n".join(cleaned_lines)

    def _limit_version_history(self, content: str, max_entries: int) -> str:
        """Limit version history table to N entries.

        Args:
            content: Spec content
            max_entries: Maximum number of entries to keep

        Returns:
            str: Content with limited version history
        """
        pattern = r"(## Version History\s*\n.*?\n)(.*?)(\n---|\Z)"

        def limit_table(match):
            header = match.group(1)
            table = match.group(2)
            footer = match.group(3)

            lines = table.split("\n")
            if len(lines) > max_entries + 2:  # +2 for header and separator
                # Keep header, separator, and top N entries
                lines = lines[:2] + lines[2 : 2 + max_entries]
                table = "\n".join(lines)

            return f"{header}{table}{footer}"

        updated = re.sub(pattern, limit_table, content, flags=re.DOTALL)
        return updated

    # ==================== SUMMARIZING SPECIFICATIONS ====================

    def summarize_spec(self, spec_path: Path, summary_type: str = "executive", max_length: int = 500) -> str:
        """Summarize specification.

        Args:
            spec_path: Path to spec
            summary_type: "tldr", "executive", or "quick_reference"
            max_length: Maximum words (approximate)

        Returns:
            str: Summary content
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        content = spec_path.read_text(encoding="utf-8")

        if summary_type == "tldr":
            return self._extract_tldr(content)
        elif summary_type == "executive":
            return self._extract_executive_summary(content)
        else:  # quick_reference
            return self._generate_quick_reference(content)

    def _extract_tldr(self, content: str) -> str:
        """Extract TL;DR from spec."""
        # Try to find existing TL;DR
        match = re.search(r"\*\*TL;DR\*\*:?\s*(.+?)(?:\n|$)", content)
        if match:
            return match.group(1).strip()

        # Fallback: Extract from executive summary
        match = re.search(r"## Executive Summary\s*\n\s*(.+?)(?:\n\n|\n##)", content, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # Take first sentence
            first_sentence = summary.split(".")[0]
            return first_sentence + "."

        return "No summary available"

    def _extract_executive_summary(self, content: str) -> str:
        """Extract executive summary from spec."""
        match = re.search(r"## Executive Summary\s*\n(.*?)(?:\n##|\Z)", content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return "No executive summary available"

    def _generate_quick_reference(self, content: str) -> str:
        """Generate quick reference from spec."""
        ref = []

        # Extract key sections
        sections = {
            "Problem": r"## Problem Statement\s*\n(.*?)(?:\n##|\Z)",
            "Architecture": r"## Architecture\s*\n(.*?)(?:\n##|\Z)",
            "DoD": r"## Acceptance Criteria.*?\s*\n(.*?)(?:\n##|\Z)",
        }

        for name, pattern in sections.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_content = match.group(1).strip()
                # Take first 2-3 lines
                lines = section_content.split("\n")[:3]
                ref.append(f"**{name}**: {' '.join(lines)}")

        return "\n\n".join(ref) if ref else "No quick reference available"
