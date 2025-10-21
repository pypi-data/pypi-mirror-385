"""Spec Diff Analyzer for CFR-010: Continuous Spec Improvement.

Compares technical specifications to actual implementations and highlights
differences to help architect learn and improve future specs.

This module provides:
- Spec vs implementation comparison
- Discrepancy analysis
- Recommendations for spec improvements
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.utils.file_io import read_text_file


class SpecDiffAnalyzer:
    """Compare spec to implementation, highlight differences."""

    def __init__(self):
        """Initialize the analyzer."""
        self.project_root = Path("/Users/bobain/PycharmProjects/MonolithicCoffeeMakerAgent")
        self.specs_dir = self.project_root / "docs" / "architecture" / "specs"

    def _get_spec_path(self, priority_name: str) -> Optional[Path]:
        """Find spec file for a priority.

        Args:
            priority_name: Priority name like "PRIORITY 9" or "SPEC-049"

        Returns:
            Path to spec file or None if not found
        """
        # Normalize priority name
        if priority_name.startswith("PRIORITY"):
            # Extract priority number
            match = re.search(r"PRIORITY\s+(\d+\.?\d*)", priority_name)
            if match:
                priority_num = match.group(1)
        else:
            # Assume it's already a spec ID like SPEC-049
            priority_num = priority_name

        # Search for spec files
        if self.specs_dir.exists():
            for spec_file in sorted(self.specs_dir.glob("SPEC-*.md")):
                if priority_num in spec_file.name or priority_name in spec_file.name:
                    return spec_file

        return None

    def _extract_key_points_from_spec(self, spec_content: str) -> List[str]:
        """Extract key implementation points from a spec.

        Args:
            spec_content: Full spec markdown content

        Returns:
            List of key points (sections, requirements, etc.)
        """
        points = []

        # Extract component names
        component_matches = re.findall(r"^##+ (.+)$", spec_content, re.MULTILINE)
        for match in component_matches:
            if match not in ["Testing", "Risks", "Approval", "Implementation Checklist"]:
                points.append(f"Section: {match}")

        # Extract "must" requirements
        must_matches = re.findall(r"- \[.?\] ([^-].*?[Mm]ust.*)", spec_content)
        for match in must_matches:
            points.append(f"Requirement: {match.strip()}")

        # Extract key classes/functions mentioned
        class_matches = re.findall(r"`([A-Z][a-zA-Z]+)(\([^)]*\))?`", spec_content)
        for class_name, params in class_matches:
            if len(class_name) > 3:  # Skip short names
                points.append(f"Component: {class_name}")

        # Extract acceptance criteria
        if "Acceptance Criteria" in spec_content:
            start = spec_content.find("Acceptance Criteria")
            end = spec_content.find("\n## ", start + 1)
            if end == -1:
                end = len(spec_content)
            criteria_section = spec_content[start:end]
            criteria = re.findall(r"- \[.?\] (.+)", criteria_section)
            for criterion in criteria:
                points.append(f"Acceptance: {criterion.strip()}")

        return points

    def _analyze_implementation(self, priority_name: str) -> Dict[str, str]:
        """Analyze what was actually implemented.

        Args:
            priority_name: Priority being implemented

        Returns:
            Dictionary with implementation details
        """
        analysis = {
            "files_changed": "Unknown (requires git analysis)",
            "modules": "Unknown",
            "estimated_loc": "Unknown",
            "key_components": [],
        }

        # This is a basic analysis; full implementation would use git diff
        # For now, return placeholder that guides architect investigation
        return analysis

    def analyze_priority(self, priority_name: str) -> str:
        """Analyze how implementation differs from spec.

        Args:
            priority_name: Priority to analyze (e.g., "PRIORITY 9")

        Returns:
            Markdown report of differences and analysis
        """
        spec_path = self._get_spec_path(priority_name)

        report = "# Spec vs Implementation Analysis\n\n"
        report += f"Priority: {priority_name}\n\n"

        if not spec_path:
            report += "❌ No spec found for this priority\n\n"
            report += "**Recommendation**: Create a spec for this priority using `project-manager spec`\n"
            return report

        # Read spec
        try:
            spec_content = read_text_file(spec_path)
        except Exception as e:
            report += f"❌ Could not read spec: {e}\n"
            return report

        # Extract key points from spec
        spec_points = self._extract_key_points_from_spec(spec_content)

        report += "## Spec Overview\n\n"
        report += f"Spec File: {spec_path.name}\n\n"

        # Extract estimated effort
        effort_match = re.search(
            r"[Ee]stimated[^\n]*?(\d+[-–]\d+\s*(?:hours|days|hours?)|[^\n]*?(?:hours|days))", spec_content
        )
        if effort_match:
            report += f"Estimated Effort: {effort_match.group(1)}\n"
        else:
            report += "Estimated Effort: Not specified in spec\n"

        report += "\n"

        # Key requirements from spec
        if spec_points:
            report += "## What Spec Says Should Be Built\n\n"
            for i, point in enumerate(spec_points[:10], 1):  # Show first 10
                report += f"{i}. {point}\n"
            report += "\n"

        # Implementation analysis
        report += "## What Was Actually Built\n\n"
        self._analyze_implementation(priority_name)

        report += "**Note**: Full implementation analysis requires git integration\n"
        report += "Currently showing what architect should check:\n\n"
        report += "- [ ] Review git commits for this priority\n"
        report += "- [ ] Check what files were modified\n"
        report += "- [ ] Count lines of code added\n"
        report += "- [ ] Verify all spec requirements are in code\n"
        report += "\n"

        # Comparison and recommendations
        report += "## Discrepancy Analysis\n\n"
        report += "To identify discrepancies:\n\n"
        report += "1. **Read the implementation** (code_developer's PR)\n"
        report += "2. **Ask discovery questions**:\n"
        report += "   - Was the spec unclear about how to build this?\n"
        report += "   - Did the implementation take a simpler/better approach?\n"
        report += "   - Were there unexpected technical challenges?\n"
        report += "   - Did the estimate match reality?\n"
        report += "3. **Update the spec** with learnings\n"
        report += "\n"

        # Template for updating spec
        report += "## Update Spec Template\n\n"
        report += "After reviewing implementation, add this to the spec:\n\n"
        report += "```markdown\n"
        report += "## Actual Implementation Notes\n\n"
        report += "**Date**: [Completion date]\n\n"
        report += "### What Was Built\n"
        report += "[Summary of what was actually built]\n\n"
        report += "### Divergences from Spec\n"
        report += "[What was different and why]\n\n"
        report += "### Lessons Learned\n"
        report += "[What architect learned for future specs]\n\n"
        report += "### Metrics\n"
        report += "- Estimated effort: [X days]\n"
        report += "- Actual effort: [Y days]\n"
        report += "- Accuracy: [Z%]\n"
        report += "```\n\n"

        return report

    def suggest_spec_improvements(self, spec_name: str) -> str:
        """Generate suggestions for improving a spec based on patterns.

        Args:
            spec_name: Spec file name or priority

        Returns:
            Markdown report with improvement suggestions
        """
        spec_path = self._get_spec_path(spec_name)

        report = "# Spec Improvement Suggestions\n\n"
        report += f"Spec: {spec_name}\n\n"

        if not spec_path:
            report += "❌ Spec not found\n"
            return report

        try:
            spec_content = read_text_file(spec_path)
        except Exception as e:
            report += f"❌ Could not read spec: {e}\n"
            return report

        suggestions = []

        # Check for common issues
        if len(spec_content) < 500:
            suggestions.append("📝 Spec is very brief - consider adding more detail to implementation section")

        if len(spec_content) > 5000:
            suggestions.append("📚 Spec is quite long - consider breaking into multiple smaller specs")

        if "```python" not in spec_content and "```" not in spec_content:
            suggestions.append("📋 No code examples - consider adding Python code snippets to clarify design")

        if "Acceptance Criteria" not in spec_content:
            suggestions.append('✅ Add explicit "Acceptance Criteria" section to make testing clear')

        if re.search(r"[Ee]stimated.*?(\d+)\s*(?:hours|days)", spec_content) is None:
            suggestions.append('⏱️  Add explicit time estimate (e.g., "Estimated: 2-3 days")')

        if "Component" not in spec_content and "class" not in spec_content.lower():
            suggestions.append("🔧 Describe key components/classes that will be created")

        if "API" not in spec_content and "interface" not in spec_content.lower():
            suggestions.append("⚙️  Describe interfaces/APIs that will be exposed")

        # Check for overly complex language
        complex_words = ["unfortunately", "basically", "clearly", "obviously", "simply"]
        for word in complex_words:
            if word in spec_content.lower():
                suggestions.append(f"🎯 Remove informal language like '{word}' for clarity")
                break

        if suggestions:
            report += "## Suggestions\n\n"
            for suggestion in suggestions:
                report += f"- {suggestion}\n"
        else:
            report += "✅ Spec looks well-structured! No major improvements suggested.\n"

        report += "\n"

        # Statistics
        lines = len(spec_content.split("\n"))
        words = len(spec_content.split())
        sections = len(re.findall(r"^##+ ", spec_content, re.MULTILINE))

        report += "## Spec Statistics\n\n"
        report += f"- Lines: {lines}\n"
        report += f"- Words: {words}\n"
        report += f"- Sections: {sections}\n"

        return report
