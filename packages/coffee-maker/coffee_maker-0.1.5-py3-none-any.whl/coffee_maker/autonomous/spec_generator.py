"""AI-Assisted Technical Specification Generator.

This module provides automatic generation of technical specifications from user stories,
including intelligent task breakdown and time estimation.

**US-016 Phase 3: AI-Assisted Task Breakdown**

The SpecGenerator uses AI (Claude/Gemini) to:
1. Analyze user stories and identify major components
2. Break components into atomic tasks (1-4h each)
3. Suggest realistic time estimates
4. Group tasks into logical phases
5. Identify dependencies and risks

Example:
    >>> from coffee_maker.autonomous.spec_generator import SpecGenerator
    >>> from coffee_maker.cli.ai_service import AIService
    >>>
    >>> ai_service = AIService()
    >>> generator = SpecGenerator(ai_service)
    >>>
    >>> spec = generator.generate_spec_from_user_story(
    ...     user_story="As a developer, I want to deploy on GCP so it runs 24/7",
    ...     feature_type="infrastructure",
    ...     complexity="high"
    ... )
    >>>
    >>> print(spec.total_hours)  # 24.5
    >>> print(spec.phases[0].name)  # "Environment Setup"
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.utils.task_estimator import (
    FeatureType,
    TaskComplexity,
    TaskEstimator,
    TimeEstimate,
)

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """A single task in the implementation plan.

    Attributes:
        title: Short task title (e.g., "Create database model")
        description: Detailed description
        deliverable: What will be delivered
        dependencies: List of task titles this depends on
        testing: Testing requirements
        time_estimate: TimeEstimate object with breakdown
    """

    title: str
    description: str
    deliverable: str
    dependencies: List[str] = field(default_factory=list)
    testing: str = ""
    time_estimate: Optional[TimeEstimate] = None


@dataclass
class Phase:
    """A logical grouping of tasks.

    Attributes:
        name: Phase name (e.g., "Database Layer")
        goal: What this phase achieves
        tasks: List of Task objects
        risks: Identified risks for this phase
        success_criteria: What defines success
        total_hours: Total phase time (calculated)
    """

    name: str
    goal: str
    tasks: List[Task] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    total_hours: float = 0.0


@dataclass
class TechnicalSpec:
    """Complete technical specification.

    Attributes:
        feature_name: Name of the feature
        feature_type: Type of feature (CRUD, Integration, etc.)
        complexity: Overall complexity (Low, Medium, High)
        summary: Executive summary
        business_value: Business value description
        phases: List of Phase objects
        total_hours: Total estimated hours (calculated)
        total_days: Total estimated days (calculated)
        confidence: Overall confidence (0.0-1.0)
        metadata: Additional metadata
    """

    feature_name: str
    feature_type: str
    complexity: str
    summary: str
    business_value: str
    phases: List[Phase] = field(default_factory=list)
    total_hours: float = 0.0
    total_days: float = 0.0
    confidence: float = 0.0
    metadata: Dict = field(default_factory=dict)


class SpecGenerator:
    """AI-assisted technical specification generator.

    This class orchestrates the generation of complete technical specifications
    by combining AI analysis with intelligent time estimation.

    The generation process:
    1. Analyze user story with AI to identify components
    2. Break components into atomic tasks
    3. Estimate task times using TaskEstimator
    4. Group tasks into logical phases
    5. Calculate totals and generate formatted spec

    Example:
        >>> from coffee_maker.cli.ai_service import AIService
        >>> ai_service = AIService()
        >>> generator = SpecGenerator(ai_service)
        >>>
        >>> # Generate from user story
        >>> spec = generator.generate_spec_from_user_story(
        ...     "As a user, I want email notifications for completed tasks",
        ...     feature_type="integration",
        ...     complexity="medium"
        ... )
        >>>
        >>> # Render to markdown file
        >>> markdown = generator.render_spec_to_markdown(spec)
        >>> Path("docs/MY_SPEC.md").write_text(markdown)
    """

    def __init__(self, ai_service, use_historical_adjustment: bool = False):
        """Initialize the spec generator.

        Args:
            ai_service: AIService instance for LLM calls
            use_historical_adjustment: If True, use historical metrics to adjust estimates (default: False)
        """
        self.ai_service = ai_service
        self.estimator = TaskEstimator(use_historical_adjustment=use_historical_adjustment)
        self.use_historical_adjustment = use_historical_adjustment
        logger.info(f"SpecGenerator initialized (historical_adjustment={use_historical_adjustment})")

    def generate_spec_from_user_story(
        self,
        user_story: str,
        feature_type: str = "general",
        complexity: str = "medium",
    ) -> TechnicalSpec:
        """Generate complete technical spec from user story.

        This is the main entry point for spec generation. It:
        1. Analyzes the user story with AI
        2. Identifies major components (database, API, UI, etc.)
        3. Breaks each component into tasks
        4. Estimates time for each task
        5. Groups tasks into phases
        6. Calculates totals and confidence

        Args:
            user_story: User story description (can be natural language)
            feature_type: Type of feature (crud, integration, ui, infrastructure, analytics, security)
            complexity: Overall complexity (low, medium, high)

        Returns:
            TechnicalSpec object ready to be rendered to markdown

        Example:
            >>> spec = generator.generate_spec_from_user_story(
            ...     "I want to add CSV export for analytics data",
            ...     feature_type="analytics",
            ...     complexity="low"
            ... )
            >>> spec.total_hours
            12.5
            >>> len(spec.phases)
            3
        """
        logger.info(
            f"Generating spec from user story: '{user_story[:50]}...' "
            f"(type={feature_type}, complexity={complexity})"
        )

        # Parse complexity and feature type
        task_complexity = self._parse_complexity(complexity)
        task_feature_type = self._parse_feature_type(feature_type)

        # Step 1: Extract feature name and business value from user story
        feature_name, business_value = self._extract_feature_info(user_story)

        # Step 2: Analyze user story with AI to get components and tasks
        analysis = self._analyze_user_story_with_ai(user_story, feature_type, complexity)

        # Step 3: Convert AI analysis to phases and tasks
        phases = self._create_phases_from_analysis(analysis, task_complexity, task_feature_type)

        # Step 4: Calculate totals
        total_hours = sum(phase.total_hours for phase in phases)
        total_days = round(total_hours / 8, 1)  # 8h/day

        # Step 5: Calculate overall confidence
        all_task_confidences = []
        for phase in phases:
            for task in phase.tasks:
                if task.time_estimate:
                    all_task_confidences.append(task.time_estimate.confidence)
        avg_confidence = sum(all_task_confidences) / len(all_task_confidences) if all_task_confidences else 0.8

        # Create spec
        spec = TechnicalSpec(
            feature_name=feature_name,
            feature_type=feature_type,
            complexity=complexity,
            summary=analysis.get("summary", ""),
            business_value=business_value,
            phases=phases,
            total_hours=total_hours,
            total_days=total_days,
            confidence=round(avg_confidence, 2),
            metadata={
                "created_at": datetime.now().isoformat(),
                "user_story": user_story,
                "ai_analysis": analysis,
            },
        )

        logger.info(
            f"Spec generated: {total_hours}h ({total_days} days), "
            f"{len(phases)} phases, confidence={avg_confidence:.0%}"
        )

        return spec

    def render_spec_to_markdown(self, spec: TechnicalSpec, template_path: Optional[Path] = None) -> str:
        """Render TechnicalSpec to markdown format.

        Uses the TECHNICAL_SPEC_TEMPLATE.md and fills in all variables.

        Args:
            spec: TechnicalSpec object to render
            template_path: Path to template file (default: docs/templates/TECHNICAL_SPEC_TEMPLATE.md)

        Returns:
            Rendered markdown string ready to save to file

        Example:
            >>> markdown = generator.render_spec_to_markdown(spec)
            >>> Path("docs/US_016_PHASE_3_SPEC.md").write_text(markdown)
        """
        # Load template
        if template_path is None:
            template_path = Path("docs/templates/TECHNICAL_SPEC_TEMPLATE.md")

        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            # Return basic markdown if template missing
            return self._render_basic_markdown(spec)

        template = template_path.read_text()

        # Calculate time distribution
        phase_dicts = []
        for phase in spec.phases:
            task_estimates = [task.time_estimate for task in phase.tasks if task.time_estimate]
            phase_dict = self.estimator.estimate_phase(task_estimates, phase.name)
            phase_dicts.append(phase_dict)

        distribution = self.estimator.calculate_time_distribution(phase_dicts)

        # Build variable replacements
        replacements = self._build_template_replacements(spec, distribution)

        # Replace variables
        rendered = template
        for var, value in replacements.items():
            rendered = rendered.replace(f"{{{{{var}}}}}", str(value))

        logger.info(f"Spec rendered to markdown ({len(rendered)} chars)")

        return rendered

    def _analyze_user_story_with_ai(self, user_story: str, feature_type: str, complexity: str) -> Dict:
        """Analyze user story with AI to identify components and tasks.

        This uses the AI service to:
        1. Identify major components (database, API, UI, infrastructure, etc.)
        2. Break each component into atomic tasks
        3. Suggest dependencies between tasks
        4. Identify risks per phase

        Args:
            user_story: User story text
            feature_type: Feature type
            complexity: Complexity level

        Returns:
            Dictionary with structure:
            {
                'summary': str,
                'components': [
                    {
                        'name': 'Database Layer',
                        'tasks': [
                            {
                                'title': 'Create User model',
                                'description': '...',
                                'deliverable': '...',
                                'dependencies': [],
                                'testing': '...',
                                'complexity': 'low'
                            },
                            ...
                        ],
                        'risks': ['Risk 1', 'Risk 2'],
                        'success_criteria': ['Criterion 1', ...]
                    },
                    ...
                ]
            }
        """
        logger.debug(f"Analyzing user story with AI: '{user_story[:50]}...'")

        prompt = f"""Analyze this user story and generate a detailed task breakdown for a technical specification.

**User Story:**
{user_story}

**Feature Type:** {feature_type}
**Complexity:** {complexity}

**Your Task:**
Generate a comprehensive technical breakdown with:

1. **Summary**: 2-3 sentence executive summary of what will be built
2. **Components**: Major logical components (e.g., Database Layer, API Layer, UI Layer, Infrastructure)
3. **Tasks per Component**: Break each component into atomic tasks (1-4h each)

For each task, provide:
- **Title**: Short descriptive title (e.g., "Create User database model")
- **Description**: What needs to be done
- **Deliverable**: Concrete output (e.g., "User model in models.py with fields: id, email, created_at")
- **Dependencies**: Other task titles this depends on (empty list if none)
- **Testing**: What testing is required
- **Complexity**: low | medium | high

For each component, also provide:
- **Risks**: 2-3 potential risks
- **Success Criteria**: 2-3 criteria for phase completion

**IMPORTANT GUIDELINES:**
- Break large tasks into smaller ones (no task > 4h)
- Tasks should be atomic and testable
- Identify dependencies between tasks
- Use realistic complexity levels based on task scope
- Testing is REQUIRED for all implementation tasks

**Output Format (JSON):**
{{
  "summary": "We will build...",
  "components": [
    {{
      "name": "Database Layer",
      "tasks": [
        {{
          "title": "Create User database model",
          "description": "Implement User model with SQLAlchemy ORM",
          "deliverable": "User model in models.py with id, email, password_hash, created_at",
          "dependencies": [],
          "testing": "Unit tests for model validation and relationships",
          "complexity": "low"
        }},
        {{
          "title": "Create database migration script",
          "description": "Generate Alembic migration for User table",
          "deliverable": "Migration script in alembic/versions/",
          "dependencies": ["Create User database model"],
          "testing": "Test migration up/down in test database",
          "complexity": "low"
        }}
      ],
      "risks": [
        "Database schema changes may require data migration",
        "Performance issues with large datasets"
      ],
      "success_criteria": [
        "All models created with proper relationships",
        "Migrations tested and verified",
        "Unit tests passing at 90%+ coverage"
      ]
    }},
    {{
      "name": "API Layer",
      "tasks": [...]
    }}
  ]
}}

Generate the complete JSON analysis now:"""

        try:
            # Use AI service to get response
            if self.ai_service.use_claude_cli:
                result = self.ai_service.cli_interface.execute_prompt(prompt)
                if not result.success:
                    raise Exception(result.error)
                response_text = result.content
            else:
                response = self.ai_service.client.messages.create(
                    model=self.ai_service.model,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.content[0].text

            # Extract JSON from response
            analysis = self._extract_json_from_response(response_text)

            logger.info(f"AI analysis complete: {len(analysis.get('components', []))} components identified")

            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return fallback analysis
            return self._fallback_analysis(user_story, feature_type, complexity)

    def _create_phases_from_analysis(
        self, analysis: Dict, task_complexity: TaskComplexity, task_feature_type: FeatureType
    ) -> List[Phase]:
        """Convert AI analysis to Phase objects with time estimates.

        Args:
            analysis: AI analysis dictionary
            task_complexity: Default task complexity
            task_feature_type: Feature type for estimation

        Returns:
            List of Phase objects with tasks and estimates
        """
        phases = []

        components = analysis.get("components", [])
        if not components:
            logger.warning("No components in analysis, returning empty phases")
            return phases

        for component in components:
            phase = Phase(
                name=component.get("name", "Unnamed Phase"),
                goal=component.get("goal", "Complete component implementation"),
                risks=component.get("risks", []),
                success_criteria=component.get("success_criteria", []),
            )

            # Create tasks
            for task_data in component.get("tasks", []):
                # Parse task complexity (default to provided complexity)
                task_complexity_str = task_data.get("complexity", "medium")
                task_complexity_enum = self._parse_complexity(task_complexity_str)

                # Determine if task requires special handling
                requires_testing = "test" in task_data.get("testing", "").lower()
                requires_documentation = "doc" in task_data.get("description", "").lower()
                requires_security = (
                    "security" in task_data.get("title", "").lower() or "auth" in task_data.get("title", "").lower()
                )
                is_integration_complex = task_feature_type == FeatureType.INTEGRATION

                # Estimate task time
                time_estimate = self.estimator.estimate_task(
                    task_description=task_data.get("title", "Task"),
                    complexity=task_complexity_enum,
                    feature_type=task_feature_type,
                    requires_testing=requires_testing,
                    requires_documentation=requires_documentation,
                    requires_security=requires_security,
                    is_integration_complex=is_integration_complex,
                )

                # Create task
                task = Task(
                    title=task_data.get("title", "Unnamed Task"),
                    description=task_data.get("description", ""),
                    deliverable=task_data.get("deliverable", ""),
                    dependencies=task_data.get("dependencies", []),
                    testing=task_data.get("testing", ""),
                    time_estimate=time_estimate,
                )

                phase.tasks.append(task)

            # Calculate phase total
            phase.total_hours = sum(task.time_estimate.total_hours for task in phase.tasks if task.time_estimate)

            phases.append(phase)

        logger.info(f"Created {len(phases)} phases with tasks")

        return phases

    def _extract_feature_info(self, user_story: str) -> tuple[str, str]:
        """Extract feature name and business value from user story.

        Args:
            user_story: User story text

        Returns:
            Tuple of (feature_name, business_value)
        """
        # Simple extraction - could be enhanced with AI
        lines = user_story.strip().split("\n")
        first_line = lines[0] if lines else user_story

        # Try to extract from "As a X, I want Y, so that Z" format
        if "i want" in first_line.lower():
            parts = first_line.lower().split("i want")
            if len(parts) > 1:
                feature_name = parts[1].strip()
                # Clean up
                feature_name = feature_name.split("so that")[0].strip()
                feature_name = feature_name.capitalize()
            else:
                feature_name = first_line
        else:
            feature_name = first_line

        # Extract business value (after "so that")
        business_value = "Improve system functionality and user experience"
        if "so that" in user_story.lower():
            parts = user_story.lower().split("so that")
            if len(parts) > 1:
                business_value = parts[1].strip().capitalize()

        return feature_name, business_value

    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON object from AI response.

        Args:
            response_text: Raw AI response

        Returns:
            Parsed JSON dictionary
        """
        import json

        # Try to find JSON in response
        try:
            # Look for JSON block
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            return {}

    def _fallback_analysis(self, user_story: str, feature_type: str, complexity: str) -> Dict:
        """Generate fallback analysis if AI fails.

        Args:
            user_story: User story text
            feature_type: Feature type
            complexity: Complexity level

        Returns:
            Basic analysis dictionary
        """
        logger.warning("Using fallback analysis (AI failed)")

        return {
            "summary": f"Implement {user_story[:100]}",
            "components": [
                {
                    "name": "Implementation",
                    "tasks": [
                        {
                            "title": "Implement core feature",
                            "description": user_story,
                            "deliverable": "Feature implemented and tested",
                            "dependencies": [],
                            "testing": "Unit and integration tests",
                            "complexity": complexity,
                        }
                    ],
                    "risks": ["Implementation complexity may be underestimated"],
                    "success_criteria": ["Feature implemented", "Tests passing"],
                }
            ],
        }

    def _parse_complexity(self, complexity: str) -> TaskComplexity:
        """Parse complexity string to TaskComplexity enum.

        Args:
            complexity: Complexity string (low, medium, high)

        Returns:
            TaskComplexity enum value
        """
        complexity_lower = complexity.lower()
        if complexity_lower in ["low", "simple", "easy"]:
            return TaskComplexity.LOW
        elif complexity_lower in ["high", "complex", "hard"]:
            return TaskComplexity.HIGH
        else:
            return TaskComplexity.MEDIUM

    def _parse_feature_type(self, feature_type: str) -> FeatureType:
        """Parse feature type string to FeatureType enum.

        Args:
            feature_type: Feature type string

        Returns:
            FeatureType enum value
        """
        feature_type_lower = feature_type.lower()

        type_mapping = {
            "crud": FeatureType.CRUD,
            "integration": FeatureType.INTEGRATION,
            "ui": FeatureType.UI,
            "infrastructure": FeatureType.INFRASTRUCTURE,
            "analytics": FeatureType.ANALYTICS,
            "security": FeatureType.SECURITY,
        }

        return type_mapping.get(feature_type_lower, FeatureType.CRUD)

    def _build_template_replacements(self, spec: TechnicalSpec, distribution: Dict) -> Dict[str, str]:
        """Build template variable replacements.

        Args:
            spec: TechnicalSpec object
            distribution: Time distribution dictionary

        Returns:
            Dictionary of template variables to values
        """
        # Basic info
        replacements = {
            "FEATURE_NAME": spec.feature_name,
            "FEATURE_TYPE": spec.feature_type.upper(),
            "COMPLEXITY": spec.complexity.capitalize(),
            "TOTAL_TIME_HOURS": str(spec.total_hours),
            "TOTAL_TIME_DAYS": str(spec.total_days),
            "AUTHOR": "AI-Generated (SpecGenerator)",
            "DATE": datetime.now().strftime("%Y-%m-%d"),
            "FEATURE_SUMMARY": spec.summary,
            "BUSINESS_VALUE": spec.business_value,
            "USER_IMPACT": "TBD - To be specified",
            "TECHNICAL_IMPACT": "TBD - To be specified",
            "BACKGROUND_CONTEXT": spec.metadata.get("user_story", ""),
            "PROBLEM_STATEMENT": "TBD - To be specified",
            "SOLUTION_OVERVIEW": spec.summary,
            "TOTAL_PHASES": str(len(spec.phases)),
        }

        # Add phase-specific variables
        for i, phase in enumerate(spec.phases, 1):
            phase_prefix = f"PHASE_{i}_"
            replacements[f"{phase_prefix}NAME"] = phase.name
            replacements[f"{phase_prefix}DURATION"] = str(phase.total_hours)
            replacements[f"{phase_prefix}GOAL"] = phase.goal
            replacements[f"{phase_prefix}TASK_COUNT"] = str(len(phase.tasks))

            # Add tasks for this phase
            for j, task in enumerate(phase.tasks[:5], 1):  # Limit to 5 tasks
                task_prefix = f"TASK_{i}_{j}_"
                replacements[f"{task_prefix}TITLE"] = task.title
                replacements[f"{task_prefix}DESCRIPTION"] = task.description
                replacements[f"{task_prefix}DELIVERABLE"] = task.deliverable
                replacements[f"{task_prefix}DEPENDENCIES"] = (
                    ", ".join(task.dependencies) if task.dependencies else "None"
                )
                replacements[f"{task_prefix}TESTING"] = task.testing
                replacements[f"{task_prefix}HOURS"] = str(task.time_estimate.total_hours) if task.time_estimate else "0"

            # Add risks
            risks_text = "\n".join([f"- {risk}" for risk in phase.risks[:3]])  # Limit to 3
            replacements[f"{phase_prefix}RISK_1"] = phase.risks[0] if len(phase.risks) > 0 else "TBD"
            replacements[f"{phase_prefix}MITIGATION_1"] = "TBD - To be determined"
            replacements[f"{phase_prefix}RISK_2"] = phase.risks[1] if len(phase.risks) > 1 else "TBD"
            replacements[f"{phase_prefix}MITIGATION_2"] = "TBD - To be determined"

            # Add success criteria
            success_text = "\n".join([f"- {sc}" for sc in phase.success_criteria[:3]])
            replacements[f"{phase_prefix}SUCCESS_1"] = (
                phase.success_criteria[0] if len(phase.success_criteria) > 0 else "TBD"
            )
            replacements[f"{phase_prefix}SUCCESS_2"] = (
                phase.success_criteria[1] if len(phase.success_criteria) > 1 else "TBD"
            )

        # Time distribution
        impl_dist = distribution["distribution"].get("implementation", {})
        test_dist = distribution["distribution"].get("testing", {})
        doc_dist = distribution["distribution"].get("documentation", {})

        replacements["IMPLEMENTATION_HOURS"] = str(impl_dist.get("hours", 0))
        replacements["IMPLEMENTATION_PERCENTAGE"] = str(impl_dist.get("percentage", 0))
        replacements["UNIT_TESTING_HOURS"] = str(test_dist.get("hours", 0))
        replacements["UNIT_TESTING_PERCENTAGE"] = str(test_dist.get("percentage", 0))
        replacements["DOCUMENTATION_HOURS"] = str(doc_dist.get("hours", 0))
        replacements["DOCUMENTATION_PERCENTAGE"] = str(doc_dist.get("percentage", 0))

        return replacements

    def _render_basic_markdown(self, spec: TechnicalSpec) -> str:
        """Render basic markdown if template is missing.

        Args:
            spec: TechnicalSpec object

        Returns:
            Basic markdown string
        """
        md = f"""# Technical Specification: {spec.feature_name}

**Feature Type**: {spec.feature_type.upper()}
**Complexity**: {spec.complexity.capitalize()}
**Estimated Total Time**: {spec.total_hours} hours ({spec.total_days} days)
**Confidence**: {spec.confidence:.0%}

**Created**: {datetime.now().strftime('%Y-%m-%d')}

---

## Executive Summary

{spec.summary}

**Business Value**: {spec.business_value}

---

## Phase Breakdown

"""

        for i, phase in enumerate(spec.phases, 1):
            md += f"""### Phase {i}: {phase.name} ({phase.total_hours}h)

**Goal**: {phase.goal}

**Tasks**:

"""
            for j, task in enumerate(phase.tasks, 1):
                hours = task.time_estimate.total_hours if task.time_estimate else 0
                md += f"""{j}. **{task.title}** ({hours}h)
   - Description: {task.description}
   - Deliverable: {task.deliverable}
   - Testing: {task.testing}
   - Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}

"""

            md += f"""**Risks**:
"""
            for risk in phase.risks:
                md += f"- {risk}\n"

            md += f"""
**Success Criteria**:
"""
            for criterion in phase.success_criteria:
                md += f"- {criterion}\n"

            md += "\n---\n\n"

        md += f"""## Summary

**Total Time**: {spec.total_hours} hours ({spec.total_days} days)
**Phases**: {len(spec.phases)}
**Confidence**: {spec.confidence:.0%}

---

*Generated by SpecGenerator (US-016 Phase 3)*
"""

        return md
