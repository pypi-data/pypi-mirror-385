"""
Langfuse tracking for Claude Skills (Phase 2).

Provides observability for skill executions across all agents.

Author: code_developer (implementing architect's spec)
Date: 2025-10-19
Related: SPEC-056, US-056
"""

from typing import Any, Dict, List, Optional

try:
    from langfuse.decorators import observe

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

    # Fallback decorator when langfuse not available
    def observe(name: Optional[str] = None, **kwargs):
        """Fallback decorator when Langfuse is not available."""

        def decorator(func):
            return func

        return decorator


@observe(name="skill_execution")
def track_skill_execution(
    agent_type: str,
    skill_name: str,
    duration: float,
    success: bool,
    errors: Optional[List[str]] = None,
    context_size: int = 0,
    output_size: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Track skill execution in Langfuse.

    Args:
        agent_type: Agent that executed the skill (e.g., "project_manager")
        skill_name: Name of the skill (e.g., "roadmap-health")
        duration: Execution time in seconds
        success: Whether skill execution succeeded
        errors: List of error messages (if any)
        context_size: Size of input context in bytes
        output_size: Size of output in bytes
        metadata: Additional metadata dictionary

    Returns:
        Dict with tracking information

    Example:
        >>> track_skill_execution(
        ...     agent_type="project_manager",
        ...     skill_name="roadmap-health",
        ...     duration=5.23,
        ...     success=True,
        ...     context_size=1024,
        ...     output_size=2048
        ... )
        {'tracked': True, 'agent': 'project_manager', 'skill': 'roadmap-health'}
    """
    errors = errors or []
    metadata = metadata or {}

    if not LANGFUSE_AVAILABLE:
        # Langfuse not available - log to console
        status = "SUCCESS" if success else "FAILED"
        print(f"[Skill Tracking] {agent_type}.{skill_name}: {status} " f"({duration:.2f}s, {len(errors)} errors)")
        return {
            "tracked": False,
            "agent": agent_type,
            "skill": skill_name,
            "reason": "langfuse_not_available",
        }

    try:
        # Import Langfuse client
        from langfuse import Langfuse

        langfuse = Langfuse()

        # Track skill execution event
        langfuse.track(
            name="skill_execution",
            properties={
                "agent_type": agent_type,
                "skill_name": skill_name,
                "duration_seconds": duration,
                "success": success,
                "error_count": len(errors),
                "errors": errors,
                "context_size_bytes": context_size,
                "output_size_bytes": output_size,
                **metadata,  # Include additional metadata
            },
        )

        # Flush to ensure data is sent
        langfuse.flush()

        return {
            "tracked": True,
            "agent": agent_type,
            "skill": skill_name,
            "duration": duration,
            "success": success,
        }

    except Exception as e:
        # Langfuse tracking failed - don't fail the skill
        print(f"[Skill Tracking] Warning: Failed to track {skill_name}: {e}")
        return {
            "tracked": False,
            "agent": agent_type,
            "skill": skill_name,
            "error": str(e),
        }


@observe(name="skill_batch_execution")
def track_batch_execution(
    agent_type: str, skills: List[Dict[str, Any]], total_duration: float, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Track batch execution of multiple skills.

    Args:
        agent_type: Agent that executed the skills
        skills: List of skill execution results
        total_duration: Total execution time in seconds
        metadata: Additional metadata dictionary

    Returns:
        Dict with batch tracking information

    Example:
        >>> track_batch_execution(
        ...     agent_type="architect",
        ...     skills=[
        ...         {"name": "architecture-analysis", "duration": 15.2, "success": True},
        ...         {"name": "dependency-impact", "duration": 5.1, "success": True}
        ...     ],
        ...     total_duration=20.3
        ... )
        {'tracked': True, 'agent': 'architect', 'skill_count': 2}
    """
    metadata = metadata or {}

    if not LANGFUSE_AVAILABLE:
        print(f"[Skill Tracking] Batch: {agent_type} executed {len(skills)} skills ({total_duration:.2f}s)")
        return {"tracked": False, "agent": agent_type, "skill_count": len(skills), "reason": "langfuse_not_available"}

    try:
        from langfuse import Langfuse

        langfuse = Langfuse()

        # Track batch execution
        langfuse.track(
            name="skill_batch_execution",
            properties={
                "agent_type": agent_type,
                "skill_count": len(skills),
                "total_duration_seconds": total_duration,
                "skills": skills,
                "success_rate": sum(1 for s in skills if s.get("success", False)) / len(skills) if skills else 0.0,
                **metadata,
            },
        )

        langfuse.flush()

        return {"tracked": True, "agent": agent_type, "skill_count": len(skills), "total_duration": total_duration}

    except Exception as e:
        print(f"[Skill Tracking] Warning: Failed to track batch execution: {e}")
        return {"tracked": False, "agent": agent_type, "skill_count": len(skills), "error": str(e)}
