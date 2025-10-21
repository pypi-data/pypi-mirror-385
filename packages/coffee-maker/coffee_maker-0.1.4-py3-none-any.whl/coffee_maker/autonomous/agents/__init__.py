"""Autonomous agents package - Multi-agent orchestration.

This package contains all autonomous agent implementations that work together
as a coordinated team to implement features, manage projects, and provide
intelligent assistance.

Agents:
    - architect: Proactive technical specification creation (CFR-011)
    - code_developer: Feature implementation execution
    - project_manager: GitHub monitoring and DoD verification
    - assistant: Demo creation and bug reporting
    - code_searcher: Weekly code analysis and insights
    - ux_design_expert: UI/UX design reviews and guidance

Base Classes:
    - BaseAgent: Abstract base class with common infrastructure
      (CFR-013 enforcement, CFR-012 interruption, status, messaging)

Architecture:
    - All agents inherit from BaseAgent
    - All agents use file-based messaging (data/agent_messages/)
    - All agents write status files (data/agent_status/)
    - All agents work on roadmap branch only (CFR-013)
    - Only one instance per agent type can run (US-035)

Related:
    - ../../autonomous/orchestrator.py: Multi-process orchestrator
    - SPEC-057: Technical specification for multi-agent orchestrator
    - US-057: Strategic requirement document
"""

__all__ = [
    "BaseAgent",
]
