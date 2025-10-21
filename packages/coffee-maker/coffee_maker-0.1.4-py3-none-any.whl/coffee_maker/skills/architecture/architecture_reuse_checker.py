"""
Architecture Reuse Checker Skill

Detects when new specs duplicate existing patterns and suggests reuse opportunities.

Capabilities:
- analyze_spec(spec_content): Analyzes a spec draft to find reuse opportunities
- find_similar_patterns(pattern_type): Finds existing architectural patterns
- generate_comparison_report(spec1, spec2): Compares two specs for similarity

Used by: architect (before creating specs, during architectural design)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from difflib import SequenceMatcher


@dataclass
class ArchitecturalComponent:
    """Represents an existing architectural component."""

    name: str
    location: str  # File path
    type: str  # "mixin", "singleton", "utility", "service", etc.
    purpose: str  # What it does
    api: List[str] = field(default_factory=list)  # Key methods/functions
    dependencies: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)  # Design patterns used


@dataclass
class ReuseOpportunity:
    """Represents a detected reuse opportunity."""

    component: ArchitecturalComponent
    fitness_score: float  # 0-100%
    recommendation: str  # "REUSE", "EXTEND", "ADAPT", "NEW"
    rationale: str
    benefits: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)


@dataclass
class ReuseAnalysisResult:
    """Result of architecture reuse analysis."""

    problem_domain: str
    opportunities: List[ReuseOpportunity]
    recommended_approach: str
    execution_time_seconds: float = 0.0
    spec_comparison_report: Optional[str] = None


class ArchitectureReuseChecker:
    """
    Detects architectural pattern reuse opportunities.

    Analyzes spec drafts and existing codebase to find similar patterns
    and recommend reuse over duplication.
    """

    # Known component domains and their existing solutions
    COMPONENT_REGISTRY = {
        "inter-agent-communication": {
            "component": "Orchestrator Messaging",
            "location": "coffee_maker/autonomous/orchestrator.py",
            "type": "message-bus",
            "api": ["_send_message()", "_read_messages()"],
            "patterns": ["file-based-ipc", "async-polling"],
        },
        "singleton-enforcement": {
            "component": "AgentRegistry",
            "location": "coffee_maker/autonomous/agent_registry.py",
            "type": "singleton",
            "api": ["register()", "unregister()"],
            "patterns": ["singleton", "context-manager"],
        },
        "configuration": {
            "component": "ConfigManager",
            "location": "coffee_maker/config/manager.py",
            "type": "utility",
            "api": ["get_anthropic_api_key()", "get_config()"],
            "patterns": ["singleton", "fallback-chain"],
        },
        "file-io": {
            "component": "File I/O Utilities",
            "location": "coffee_maker/utils/file_io.py",
            "type": "utility",
            "api": ["read_json()", "write_json()"],
            "patterns": ["atomic-writes", "utf8-encoding"],
        },
        "observability": {
            "component": "Langfuse Decorators",
            "location": "coffee_maker/langfuse_observe/",
            "type": "decorator",
            "api": ["@observe()"],
            "patterns": ["decorator", "tracing"],
        },
        "prompt-management": {
            "component": "PromptLoader",
            "location": "coffee_maker/autonomous/prompt_loader.py",
            "type": "utility",
            "api": ["load_prompt()", "PromptNames"],
            "patterns": ["template-substitution", "multi-provider"],
        },
        "git-operations": {
            "component": "GitOperations Mixin",
            "location": "coffee_maker/autonomous/daemon_git_ops.py",
            "type": "mixin",
            "api": ["git.commit()", "git.push()"],
            "patterns": ["mixin", "composition"],
        },
        "notifications": {
            "component": "NotificationSystem",
            "location": "coffee_maker/cli/notifications.py",
            "type": "service",
            "api": ["create_notification()"],
            "patterns": ["observer", "event-driven"],
        },
    }

    def __init__(self, project_root: str = "."):
        """
        Initialize architecture reuse checker.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.specs_dir = self.project_root / "docs" / "architecture" / "specs"

    def analyze_spec(self, spec_content: str, spec_name: str = "unknown") -> ReuseAnalysisResult:
        """
        Analyze a spec draft to find reuse opportunities.

        Args:
            spec_content: Content of the spec (markdown text)
            spec_name: Name of the spec being analyzed

        Returns:
            ReuseAnalysisResult with detected opportunities

        Example:
            >>> checker = ArchitectureReuseChecker()
            >>> result = checker.analyze_spec(spec_text, "SPEC-070-example.md")
            >>> for opp in result.opportunities:
            >>>     print(f"{opp.component.name}: {opp.fitness_score}%")
        """
        import time

        start_time = time.time()

        # Step 1: Identify problem domain from spec content
        problem_domain = self._identify_problem_domain(spec_content)

        # Step 2: Find existing components in that domain
        opportunities = self._find_reuse_opportunities(problem_domain, spec_content)

        # Step 3: Rank opportunities by fitness score
        opportunities.sort(key=lambda x: x.fitness_score, reverse=True)

        # Step 4: Determine recommended approach
        recommended_approach = self._determine_recommendation(opportunities)

        # Step 5: Generate comparison report if similar specs exist
        spec_comparison = self._compare_with_existing_specs(spec_content)

        elapsed = time.time() - start_time

        return ReuseAnalysisResult(
            problem_domain=problem_domain,
            opportunities=opportunities,
            recommended_approach=recommended_approach,
            execution_time_seconds=elapsed,
            spec_comparison_report=spec_comparison,
        )

    def _identify_problem_domain(self, spec_content: str) -> str:
        """
        Identify the primary problem domain from spec content.

        Args:
            spec_content: Spec text

        Returns:
            Domain name (e.g., "inter-agent-communication")
        """
        spec_lower = spec_content.lower()

        # Domain keywords mapping
        domain_keywords = {
            "inter-agent-communication": [
                "agent.*notify",
                "agent.*message",
                "agent.*communication",
                "send.*agent",
                "inter-agent",
            ],
            "singleton-enforcement": ["singleton", "one instance", "prevent.*concurrent", "unique instance"],
            "configuration": ["config", "api key", "environment", "settings"],
            "file-io": ["file.*read", "file.*write", "json.*file", "atomic.*write"],
            "observability": ["observability", "langfuse", "track.*llm", "trace", "logging"],
            "prompt-management": ["prompt", "llm.*call", "template", "ai.*provider"],
            "git-operations": ["git.*commit", "git.*push", "git.*tag", "git operation"],
            "notifications": ["notification", "alert", "user.*notify"],
        }

        # Score each domain
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = 0
            for keyword_pattern in keywords:
                if re.search(keyword_pattern, spec_lower):
                    score += 1
            domain_scores[domain] = score

        # Return highest scoring domain (or "general" if no match)
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)

        return "general"

    def _find_reuse_opportunities(self, problem_domain: str, spec_content: str) -> List[ReuseOpportunity]:
        """
        Find reuse opportunities for the given domain.

        Args:
            problem_domain: Identified domain
            spec_content: Spec text for detailed analysis

        Returns:
            List of ReuseOpportunity objects
        """
        opportunities = []

        # Check registry for domain match
        if problem_domain in self.COMPONENT_REGISTRY:
            comp_data = self.COMPONENT_REGISTRY[problem_domain]

            component = ArchitecturalComponent(
                name=comp_data["component"],
                location=comp_data["location"],
                type=comp_data["type"],
                purpose=f"Existing solution for {problem_domain}",
                api=comp_data["api"],
                patterns=comp_data["patterns"],
            )

            # Calculate fitness score
            fitness_score = self._calculate_fitness_score(component, spec_content, problem_domain)

            # Determine recommendation based on fitness
            recommendation = self._fitness_to_recommendation(fitness_score)

            # Generate rationale
            rationale = self._generate_rationale(component, fitness_score, recommendation)

            # List benefits and tradeoffs
            benefits, tradeoffs = self._analyze_benefits_tradeoffs(component, recommendation)

            opportunities.append(
                ReuseOpportunity(
                    component=component,
                    fitness_score=fitness_score,
                    recommendation=recommendation,
                    rationale=rationale,
                    benefits=benefits,
                    tradeoffs=tradeoffs,
                )
            )

        # Also check for similar patterns in other domains (cross-domain reuse)
        for domain, comp_data in self.COMPONENT_REGISTRY.items():
            if domain != problem_domain:
                # Check for partial matches
                partial_fitness = self._calculate_cross_domain_fitness(comp_data, spec_content)

                if partial_fitness >= 30.0:  # At least 30% fit
                    component = ArchitecturalComponent(
                        name=comp_data["component"],
                        location=comp_data["location"],
                        type=comp_data["type"],
                        purpose=f"Alternative solution from {domain}",
                        api=comp_data["api"],
                        patterns=comp_data["patterns"],
                    )

                    recommendation = self._fitness_to_recommendation(partial_fitness)
                    rationale = f"Cross-domain match: {domain} patterns may be adaptable"

                    opportunities.append(
                        ReuseOpportunity(
                            component=component,
                            fitness_score=partial_fitness,
                            recommendation=recommendation,
                            rationale=rationale,
                        )
                    )

        return opportunities

    def _calculate_fitness_score(self, component: ArchitecturalComponent, spec_content: str, domain: str) -> float:
        """
        Calculate fitness score (0-100%) for a component.

        Considers:
        - Functional match (40%)
        - API compatibility (30%)
        - Performance (10%)
        - Consistency (10%)
        - Maintenance (10%)

        Args:
            component: Component to evaluate
            spec_content: Spec text
            domain: Problem domain

        Returns:
            Fitness score (0-100%)
        """
        # Functional match (40 points)
        functional_match = 40.0  # Assume perfect match for domain-matched components

        # API compatibility (30 points) - check if spec mentions similar APIs
        api_score = 0.0
        spec_lower = spec_content.lower()
        for api_method in component.api:
            api_name = api_method.split("(")[0]  # Extract method name
            if api_name.lower() in spec_lower:
                api_score += 10.0

        api_score = min(api_score, 30.0)  # Cap at 30

        # Performance (10 points) - assume acceptable for file-based systems
        performance_score = 10.0

        # Consistency (10 points) - existing components always consistent
        consistency_score = 10.0

        # Maintenance (10 points) - reusing reduces maintenance
        maintenance_score = 10.0

        total_score = functional_match + api_score + performance_score + consistency_score + maintenance_score

        return min(total_score, 100.0)

    def _calculate_cross_domain_fitness(self, comp_data: Dict[str, Any], spec_content: str) -> float:
        """Calculate fitness for cross-domain reuse (less strict)."""
        spec_lower = spec_content.lower()
        score = 0.0

        # Check for pattern mentions
        for pattern in comp_data.get("patterns", []):
            if pattern.lower() in spec_lower:
                score += 15.0

        # Check for API mentions
        for api in comp_data.get("api", []):
            if api.split("(")[0].lower() in spec_lower:
                score += 10.0

        return min(score, 70.0)  # Cross-domain max 70%

    def _fitness_to_recommendation(self, fitness_score: float) -> str:
        """Convert fitness score to recommendation."""
        if fitness_score >= 90.0:
            return "REUSE"
        elif fitness_score >= 70.0:
            return "EXTEND"
        elif fitness_score >= 50.0:
            return "ADAPT"
        else:
            return "NEW"

    def _generate_rationale(self, component: ArchitecturalComponent, fitness_score: float, recommendation: str) -> str:
        """Generate rationale for recommendation."""
        if recommendation == "REUSE":
            return f"Perfect fit ({fitness_score:.0f}%) - {component.name} provides exactly what's needed"
        elif recommendation == "EXTEND":
            return f"Good fit ({fitness_score:.0f}%) - {component.name} can be extended with new features"
        elif recommendation == "ADAPT":
            return f"Partial fit ({fitness_score:.0f}%) - {component.name} patterns can be adapted"
        else:
            return f"Poor fit ({fitness_score:.0f}%) - New component needed, but document why {component.name} insufficient"

    def _analyze_benefits_tradeoffs(
        self, component: ArchitecturalComponent, recommendation: str
    ) -> Tuple[List[str], List[str]]:
        """Analyze benefits and tradeoffs of reusing component."""
        benefits = []
        tradeoffs = []

        if recommendation in ["REUSE", "EXTEND"]:
            benefits = [
                f"No new infrastructure code (reuse {component.location})",
                f"Use existing API: {', '.join(component.api[:2])}",
                "Full observability and debugging support",
                "Consistent with project architecture",
                "Easier to test (established patterns)",
            ]

            if component.type == "message-bus":
                tradeoffs = [
                    "Slight latency (5-30s polling vs <1s direct call)",
                    "But: Consistency + observability >> slight latency",
                ]
            elif component.type == "singleton":
                tradeoffs = ["Thread-local context required", "But: Prevents race conditions"]
            else:
                tradeoffs = ["Minimal - follows established patterns"]

        return benefits, tradeoffs

    def _determine_recommendation(self, opportunities: List[ReuseOpportunity]) -> str:
        """
        Determine overall recommended approach.

        Args:
            opportunities: Sorted list of opportunities (highest fitness first)

        Returns:
            Recommended approach string
        """
        if not opportunities:
            return "CREATE NEW - No existing components found"

        best_opportunity = opportunities[0]

        if best_opportunity.recommendation == "REUSE":
            return f"✅ REUSE {best_opportunity.component.name} (fitness: {best_opportunity.fitness_score:.0f}%)"
        elif best_opportunity.recommendation == "EXTEND":
            return f"⚠️ EXTEND {best_opportunity.component.name} with new features (fitness: {best_opportunity.fitness_score:.0f}%)"
        elif best_opportunity.recommendation == "ADAPT":
            return f"⚠️ ADAPT patterns from {best_opportunity.component.name} (fitness: {best_opportunity.fitness_score:.0f}%)"
        else:
            return f"❌ CREATE NEW - {best_opportunity.component.name} insufficient (fitness: {best_opportunity.fitness_score:.0f}%)"

    def _compare_with_existing_specs(self, spec_content: str) -> Optional[str]:
        """
        Compare spec with existing specs to find duplicates.

        Args:
            spec_content: New spec content

        Returns:
            Comparison report or None if no similar specs found
        """
        if not self.specs_dir.exists():
            return None

        # Find all existing specs
        existing_specs = list(self.specs_dir.glob("SPEC-*.md"))

        if not existing_specs:
            return None

        # Compare with each spec
        similar_specs = []

        for spec_path in existing_specs:
            try:
                existing_content = spec_path.read_text()

                # Calculate similarity using SequenceMatcher
                similarity = SequenceMatcher(None, spec_content, existing_content).ratio()

                if similarity >= 0.3:  # At least 30% similar
                    similar_specs.append((spec_path.name, similarity))
            except Exception:
                # Skip specs that can't be read
                continue

        if not similar_specs:
            return None

        # Sort by similarity
        similar_specs.sort(key=lambda x: x[1], reverse=True)

        # Generate report
        report = "## Similar Existing Specs Detected\n\n"

        for spec_name, similarity in similar_specs[:3]:  # Top 3
            similarity_pct = similarity * 100
            report += f"- **{spec_name}**: {similarity_pct:.0f}% similar\n"

        report += "\n**Recommendation**: Review these specs for reusable patterns before creating new spec.\n"

        return report

    def generate_reuse_report(self, result: ReuseAnalysisResult) -> str:
        """
        Generate formatted reuse analysis report.

        Args:
            result: Analysis result

        Returns:
            Markdown-formatted report
        """
        report = "## 🔍 Architecture Reuse Check\n\n"

        # Problem domain
        report += f"### Problem Domain\n\n**{result.problem_domain}**\n\n"

        # Existing components evaluated
        report += "### Existing Components Evaluated\n\n"

        for i, opp in enumerate(result.opportunities, 1):
            report += f"#### Component {i}: {opp.component.name}\n\n"
            report += f"- **Location**: `{opp.component.location}`\n"
            report += f"- **Type**: {opp.component.type}\n"
            report += f"- **Fitness Score**: {opp.fitness_score:.0f}%\n"
            report += f"- **Decision**: {opp.recommendation}\n"
            report += f"- **Rationale**: {opp.rationale}\n\n"

            if opp.benefits:
                report += "**Benefits**:\n"
                for benefit in opp.benefits:
                    report += f"- ✅ {benefit}\n"
                report += "\n"

            if opp.tradeoffs:
                report += "**Trade-offs**:\n"
                for tradeoff in opp.tradeoffs:
                    report += f"- ⚠️ {tradeoff}\n"
                report += "\n"

        # Final decision
        report += "### Final Decision\n\n"
        report += f"**Recommended Approach**: {result.recommended_approach}\n\n"

        # Spec comparison
        if result.spec_comparison_report:
            report += result.spec_comparison_report
            report += "\n"

        # Execution time
        report += f"---\n\n*Analysis completed in {result.execution_time_seconds:.2f}s*\n"

        return report


# Convenience function for direct usage
def check_architecture_reuse(spec_content: str, spec_name: str = "unknown") -> str:
    """
    Convenience function to run architecture reuse check.

    Args:
        spec_content: Spec content to analyze
        spec_name: Name of the spec

    Returns:
        Markdown-formatted reuse analysis report

    Example:
        >>> report = check_architecture_reuse(spec_text, "SPEC-070-example.md")
        >>> print(report)
    """
    checker = ArchitectureReuseChecker()
    result = checker.analyze_spec(spec_content, spec_name)
    return checker.generate_reuse_report(result)
