"""API layer for Streamlit app to interact with ACE framework.

This module provides a clean API interface for the Streamlit UI to interact
with the ACE framework components (Generator, Reflector, Curator).

Example:
    api = ACEApi()

    # Get traces
    traces = api.get_traces(agent="user_interpret", hours=24)

    # Get playbook
    playbook = api.get_playbook("user_interpret")

    # Get metrics
    metrics = api.get_metrics(days=7)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from coffee_maker.autonomous.ace.config import ACEConfig, get_default_config
from coffee_maker.autonomous.ace.models import ExecutionTrace
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.autonomous.ace.trace_manager import TraceManager
from coffee_maker.streamlit_app.utils.env_manager import EnvManager

logger = logging.getLogger(__name__)


class ACEApi:
    """API for Streamlit app to interact with ACE framework."""

    def __init__(self, config: Optional[ACEConfig] = None):
        """Initialize ACE API.

        Args:
            config: ACE configuration (optional, uses default if not provided)
        """
        self.config = config or get_default_config()
        self.trace_manager = TraceManager(self.config.trace_dir)
        self.env_manager = EnvManager()
        logger.info("ACEApi initialized")

    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get ACE status for all agents.

        Returns:
            Dictionary mapping agent names to status info

        Example:
            {
                "user_interpret": {
                    "ace_enabled": True,
                    "traces_today": 127,
                    "traces_total": 1453,
                    "playbook_size": 147
                },
                ...
            }
        """
        agent_statuses = {}

        # Known agents
        agents = [
            "user_interpret",
            "assistant",
            "code_searcher",
            "code_developer",
            "user_listener",
            "project_manager",
            "architect",
            "generator",
            "reflector",
            "curator",
        ]

        for agent_name in agents:
            try:
                # Check ACE status from .env
                ace_enabled = self.env_manager.get_agent_ace_status(agent_name)

                # Get trace counts
                today = datetime.now().strftime("%Y-%m-%d")
                traces_today = len(self.trace_manager.list_traces(date=today, agent=agent_name))
                traces_total = len(self.trace_manager.list_traces(agent=agent_name))

                # Get playbook size
                playbook_size = 0
                try:
                    loader = PlaybookLoader(agent_name, self.config)
                    playbook = loader.load()
                    playbook_size = playbook.total_bullets
                except Exception as e:
                    logger.debug(f"No playbook for {agent_name}: {e}")

                agent_statuses[agent_name] = {
                    "ace_enabled": ace_enabled,
                    "traces_today": traces_today,
                    "traces_total": traces_total,
                    "playbook_size": playbook_size,
                }
            except Exception as e:
                logger.warning(f"Failed to get status for {agent_name}: {e}")
                agent_statuses[agent_name] = {
                    "ace_enabled": False,
                    "traces_today": 0,
                    "traces_total": 0,
                    "playbook_size": 0,
                }

        return agent_statuses

    def enable_agent(self, agent_name: str) -> bool:
        """Enable ACE for specific agent.

        Args:
            agent_name: Agent to enable ACE for

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.env_manager.set_agent_ace_status(agent_name, True)
            if success:
                logger.info(f"Enabled ACE for {agent_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to enable ACE for {agent_name}: {e}")
            return False

    def disable_agent(self, agent_name: str) -> bool:
        """Disable ACE for specific agent.

        Args:
            agent_name: Agent to disable ACE for

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.env_manager.set_agent_ace_status(agent_name, False)
            if success:
                logger.info(f"Disabled ACE for {agent_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to disable ACE for {agent_name}: {e}")
            return False

    def get_traces(
        self,
        agent: Optional[str] = None,
        date: Optional[str] = None,
        hours: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get traces (optionally filtered).

        Args:
            agent: Filter by agent name
            date: Filter by date (YYYY-MM-DD)
            hours: Get traces from last N hours
            limit: Maximum number of traces to return

        Returns:
            List of trace dictionaries (serializable)

        Example:
            # Get last 24 hours of user_interpret traces
            traces = api.get_traces(agent="user_interpret", hours=24)
        """
        try:
            if hours:
                traces = self.trace_manager.get_traces_since(hours=hours, agent=agent)
            elif date:
                traces = self.trace_manager.list_traces(date=date, agent=agent)
            else:
                traces = self.trace_manager.list_traces(agent=agent)

            # Sort by timestamp descending (newest first)
            traces.sort(key=lambda t: t.timestamp, reverse=True)

            # Apply limit
            traces = traces[:limit]

            # Convert to dictionaries for JSON serialization
            return [trace.to_dict() for trace in traces]
        except Exception as e:
            logger.error(f"Failed to get traces: {e}")
            return []

    def get_trace_by_id(self, trace_id: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get specific trace by ID.

        Args:
            trace_id: Trace ID to retrieve
            date: Optional date hint (YYYY-MM-DD) to speed up search

        Returns:
            Trace dictionary or None if not found
        """
        try:
            trace = self.trace_manager.read_trace(trace_id, date=date)
            return trace.to_dict()
        except FileNotFoundError:
            logger.warning(f"Trace not found: {trace_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get trace {trace_id}: {e}")
            return None

    def get_playbook(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get playbook for agent.

        Args:
            agent_name: Agent name

        Returns:
            Playbook dictionary or None if not found

        Example:
            playbook = api.get_playbook("user_interpret")
            print(f"Total bullets: {playbook['total_bullets']}")
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            return playbook.to_dict()
        except Exception as e:
            logger.error(f"Failed to get playbook for {agent_name}: {e}")
            return None

    def get_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get ACE metrics for analytics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with aggregated metrics

        Example:
            metrics = api.get_metrics(days=7)
            print(f"Total traces: {metrics['total_traces']}")
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()

            # Filter by date range
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]

            # Calculate metrics
            total_traces = len(recent_traces)
            success_traces = len([t for t in recent_traces if self._is_success(t)])
            failure_traces = len([t for t in recent_traces if not self._is_success(t)])

            success_rate = (success_traces / total_traces * 100) if total_traces > 0 else 0.0

            # Per-agent metrics
            agent_metrics = {}
            agents = set(t.agent_identity.get("target_agent", "unknown") for t in recent_traces)

            for agent_name in agents:
                agent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent_name]
                agent_success = len([t for t in agent_traces if self._is_success(t)])
                agent_total = len(agent_traces)

                avg_duration = (
                    sum(sum(e.duration_seconds for e in t.executions) for t in agent_traces) / agent_total
                    if agent_total > 0
                    else 0.0
                )

                agent_metrics[agent_name] = {
                    "total_traces": agent_total,
                    "success_count": agent_success,
                    "failure_count": agent_total - agent_success,
                    "success_rate": ((agent_success / agent_total * 100) if agent_total > 0 else 0.0),
                    "avg_duration_seconds": round(avg_duration, 2),
                }

            # Trace stats by day
            traces_by_day = {}
            for trace in recent_traces:
                day = trace.timestamp.strftime("%Y-%m-%d")
                traces_by_day[day] = traces_by_day.get(day, 0) + 1

            return {
                "date_range_days": days,
                "total_traces": total_traces,
                "success_count": success_traces,
                "failure_count": failure_traces,
                "success_rate": round(success_rate, 2),
                "agent_metrics": agent_metrics,
                "traces_by_day": traces_by_day,
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "date_range_days": days,
                "total_traces": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "agent_metrics": {},
                "traces_by_day": {},
            }

    def get_reflection_status(self) -> Dict[str, Any]:
        """Get reflector status.

        Returns:
            Dictionary with reflector status info
        """
        try:
            # Check for latest delta files
            delta_dir = self.config.delta_dir
            if not delta_dir.exists():
                return {
                    "last_run": None,
                    "pending_traces": 0,
                    "delta_items_generated": 0,
                }

            # Find most recent delta file
            delta_files = sorted(delta_dir.glob("delta_*.json"), reverse=True)
            last_run = None
            delta_items_generated = 0

            if delta_files:
                latest_delta = delta_files[0]
                last_run = datetime.fromtimestamp(latest_delta.stat().st_mtime)

                # Count delta items in latest file
                try:
                    import json

                    with open(latest_delta, "r") as f:
                        deltas = json.load(f)
                        delta_items_generated = len(deltas.get("deltas", []))
                except Exception as e:
                    logger.warning(f"Failed to read delta file: {e}")

            # Count pending traces (traces without corresponding delta)
            all_traces = self.trace_manager.list_traces()
            pending_traces = len(all_traces)  # Simplified - could be more sophisticated

            return {
                "last_run": last_run.isoformat() if last_run else None,
                "pending_traces": pending_traces,
                "delta_items_generated": delta_items_generated,
            }
        except Exception as e:
            logger.error(f"Failed to get reflection status: {e}")
            return {
                "last_run": None,
                "pending_traces": 0,
                "delta_items_generated": 0,
            }

    def _is_success(self, trace: ExecutionTrace) -> bool:
        """Check if trace represents successful execution.

        Args:
            trace: ExecutionTrace to check

        Returns:
            True if all executions succeeded, False otherwise
        """
        if not trace.executions:
            return False
        return all(e.result_status == "success" for e in trace.executions)

    # Playbook curation methods

    def get_playbook_bullets(
        self,
        agent_name: str,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_effectiveness: Optional[float] = None,
        max_effectiveness: Optional[float] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get playbook bullets with optional filtering.

        Args:
            agent_name: Agent name
            category: Filter by category
            status: Filter by status (active, pending, archived)
            min_effectiveness: Minimum effectiveness score
            max_effectiveness: Maximum effectiveness score
            search_query: Text search in bullet content

        Returns:
            List of bullet dictionaries
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            bullets = playbook.bullets

            # Apply filters
            if category:
                bullets = [b for b in bullets if b.category == category]

            if status:
                bullets = [b for b in bullets if b.status == status]

            if min_effectiveness is not None:
                bullets = [b for b in bullets if b.effectiveness >= min_effectiveness]

            if max_effectiveness is not None:
                bullets = [b for b in bullets if b.effectiveness <= max_effectiveness]

            if search_query:
                query_lower = search_query.lower()
                bullets = [b for b in bullets if query_lower in b.content.lower()]

            return [b.to_dict() for b in bullets]
        except Exception as e:
            logger.error(f"Failed to get playbook bullets: {e}")
            return []

    def approve_bullet(self, agent_name: str, bullet_id: str) -> bool:
        """Approve a playbook bullet.

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID to approve

        Returns:
            True if successful, False otherwise
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()

            # Find and update bullet
            for bullet in playbook.bullets:
                if bullet.bullet_id == bullet_id:
                    bullet.status = "active"
                    bullet.metadata["approved_at"] = datetime.now().isoformat()
                    logger.info(f"Approved bullet {bullet_id} for {agent_name}")

                    # Save updated playbook
                    return loader.save(playbook)

            logger.warning(f"Bullet not found: {bullet_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to approve bullet: {e}")
            return False

    def reject_bullet(self, agent_name: str, bullet_id: str) -> bool:
        """Reject and archive a playbook bullet.

        Args:
            agent_name: Agent name
            bullet_id: Bullet ID to reject

        Returns:
            True if successful, False otherwise
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()

            # Find and update bullet
            for bullet in playbook.bullets:
                if bullet.bullet_id == bullet_id:
                    bullet.status = "archived"
                    bullet.metadata["rejected_at"] = datetime.now().isoformat()
                    logger.info(f"Rejected bullet {bullet_id} for {agent_name}")

                    # Update playbook stats
                    playbook.total_bullets = len([b for b in playbook.bullets if b.status == "active"])
                    active_bullets = [b for b in playbook.bullets if b.status == "active"]
                    if active_bullets:
                        playbook.avg_effectiveness = sum(b.effectiveness for b in active_bullets) / len(active_bullets)

                    # Save updated playbook
                    return loader.save(playbook)

            logger.warning(f"Bullet not found: {bullet_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to reject bullet: {e}")
            return False

    def bulk_approve_bullets(self, agent_name: str, bullet_ids: List[str]) -> Dict[str, int]:
        """Approve multiple bullets at once.

        Args:
            agent_name: Agent name
            bullet_ids: List of bullet IDs to approve

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for bullet_id in bullet_ids:
            if self.approve_bullet(agent_name, bullet_id):
                success_count += 1
            else:
                failure_count += 1

        return {"success": success_count, "failure": failure_count}

    def bulk_reject_bullets(self, agent_name: str, bullet_ids: List[str]) -> Dict[str, int]:
        """Reject multiple bullets at once.

        Args:
            agent_name: Agent name
            bullet_ids: List of bullet IDs to reject

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for bullet_id in bullet_ids:
            if self.reject_bullet(agent_name, bullet_id):
                success_count += 1
            else:
                failure_count += 1

        return {"success": success_count, "failure": failure_count}

    def get_curation_queue(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get pending bullets awaiting curation.

        Args:
            agent_name: Agent name

        Returns:
            List of pending bullet dictionaries
        """
        try:
            bullets = self.get_playbook_bullets(agent_name, status="pending")
            logger.info(f"Retrieved {len(bullets)} pending bullets for {agent_name}")
            return bullets
        except Exception as e:
            logger.error(f"Failed to get curation queue: {e}")
            return []

    def get_playbook_categories(self, agent_name: str) -> List[str]:
        """Get all unique categories in playbook.

        Args:
            agent_name: Agent name

        Returns:
            List of category names
        """
        try:
            loader = PlaybookLoader(agent_name, self.config)
            playbook = loader.load()
            categories = sorted(set(b.category for b in playbook.bullets))
            return categories
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []

    # Analytics methods

    def get_cost_analytics(self, agent: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get cost analytics for traces.

        Args:
            agent: Optional agent filter
            days: Number of days to analyze

        Returns:
            Dictionary with cost metrics including:
            - total_cost: Total cost across all traces
            - cost_by_agent: Cost breakdown by agent
            - cost_by_day: Daily cost trend
            - avg_cost_per_trace: Average cost per trace
            - most_expensive_agent: Agent with highest cost
            - trend: Cost trend (increasing/decreasing/stable)
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]

            if agent:
                recent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent]

            # Calculate costs (simulate based on executions and tokens)
            total_cost = 0.0
            cost_by_agent = {}
            cost_by_day = {}

            for trace in recent_traces:
                # Estimate cost: $0.001 per execution + token cost
                trace_cost = 0.0
                for execution in trace.executions:
                    # Base cost per execution
                    trace_cost += 0.001
                    # Token cost (estimate ~$0.003 per 1K tokens)
                    tokens = execution.metadata.get("tokens", len(execution.prompt.split()) * 1.5)
                    trace_cost += (tokens / 1000) * 0.003

                total_cost += trace_cost

                # Aggregate by agent
                agent_name = trace.agent_identity.get("target_agent", "unknown")
                cost_by_agent[agent_name] = cost_by_agent.get(agent_name, 0.0) + trace_cost

                # Aggregate by day
                day = trace.timestamp.strftime("%Y-%m-%d")
                cost_by_day[day] = cost_by_day.get(day, 0.0) + trace_cost

            # Calculate average cost per trace
            avg_cost_per_trace = total_cost / len(recent_traces) if recent_traces else 0.0

            # Find most expensive agent
            most_expensive_agent = max(cost_by_agent, key=cost_by_agent.get) if cost_by_agent else "N/A"

            # Calculate trend (compare first half vs second half)
            trend = "stable"
            if len(recent_traces) >= 10:
                mid_point = len(recent_traces) // 2
                first_half_cost = sum(
                    sum(0.001 + (e.metadata.get("tokens", 100) / 1000) * 0.003 for e in t.executions)
                    for t in recent_traces[:mid_point]
                )
                second_half_cost = sum(
                    sum(0.001 + (e.metadata.get("tokens", 100) / 1000) * 0.003 for e in t.executions)
                    for t in recent_traces[mid_point:]
                )
                if second_half_cost > first_half_cost * 1.2:
                    trend = "increasing"
                elif second_half_cost < first_half_cost * 0.8:
                    trend = "decreasing"

            # Convert cost_by_day to sorted list
            cost_by_day_list = [{"date": date, "cost": cost} for date, cost in sorted(cost_by_day.items())]

            return {
                "total_cost": round(total_cost, 2),
                "cost_by_agent": {k: round(v, 2) for k, v in cost_by_agent.items()},
                "cost_by_day": cost_by_day_list,
                "avg_cost_per_trace": round(avg_cost_per_trace, 4),
                "most_expensive_agent": most_expensive_agent,
                "trend": trend,
            }
        except Exception as e:
            logger.error(f"Failed to get cost analytics: {e}")
            return {
                "total_cost": 0.0,
                "cost_by_agent": {},
                "cost_by_day": [],
                "avg_cost_per_trace": 0.0,
                "most_expensive_agent": "N/A",
                "trend": "stable",
            }

    def get_effectiveness_analytics(self, agent: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get effectiveness analytics for traces.

        Args:
            agent: Optional agent filter
            days: Number of days to analyze

        Returns:
            Dictionary with effectiveness metrics including:
            - success_rate: Overall success rate (0.0-1.0)
            - error_rate: Overall error rate (0.0-1.0)
            - avg_effectiveness: Average effectiveness score
            - effectiveness_by_agent: Effectiveness breakdown by agent
            - effectiveness_trend: Time series of effectiveness
            - problem_areas: Agents/categories with low effectiveness
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]

            if agent:
                recent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent]

            if not recent_traces:
                return {
                    "success_rate": 0.0,
                    "error_rate": 0.0,
                    "avg_effectiveness": 0.0,
                    "effectiveness_by_agent": {},
                    "effectiveness_trend": [],
                    "problem_areas": [],
                }

            # Calculate success/error rates
            success_count = len([t for t in recent_traces if self._is_success(t)])
            error_count = len(recent_traces) - success_count
            success_rate = success_count / len(recent_traces)
            error_rate = error_count / len(recent_traces)

            # Calculate effectiveness by agent
            effectiveness_by_agent = {}
            agents = set(t.agent_identity.get("target_agent", "unknown") for t in recent_traces)

            for agent_name in agents:
                agent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent_name]
                agent_success = len([t for t in agent_traces if self._is_success(t)])
                effectiveness_by_agent[agent_name] = agent_success / len(agent_traces) if agent_traces else 0.0

            # Average effectiveness
            avg_effectiveness = (
                sum(effectiveness_by_agent.values()) / len(effectiveness_by_agent) if effectiveness_by_agent else 0.0
            )

            # Effectiveness trend over time (by day)
            effectiveness_by_day = {}
            for trace in recent_traces:
                day = trace.timestamp.strftime("%Y-%m-%d")
                if day not in effectiveness_by_day:
                    effectiveness_by_day[day] = {"success": 0, "total": 0}
                effectiveness_by_day[day]["total"] += 1
                if self._is_success(trace):
                    effectiveness_by_day[day]["success"] += 1

            effectiveness_trend = [
                {
                    "date": date,
                    "effectiveness": (data["success"] / data["total"] if data["total"] > 0 else 0.0),
                }
                for date, data in sorted(effectiveness_by_day.items())
            ]

            # Identify problem areas (effectiveness < 0.7)
            problem_areas = [
                f"{agent_name} ({eff:.2%})" for agent_name, eff in effectiveness_by_agent.items() if eff < 0.7
            ]

            return {
                "success_rate": round(success_rate, 3),
                "error_rate": round(error_rate, 3),
                "avg_effectiveness": round(avg_effectiveness, 3),
                "effectiveness_by_agent": {k: round(v, 3) for k, v in effectiveness_by_agent.items()},
                "effectiveness_trend": effectiveness_trend,
                "problem_areas": problem_areas,
            }
        except Exception as e:
            logger.error(f"Failed to get effectiveness analytics: {e}")
            return {
                "success_rate": 0.0,
                "error_rate": 0.0,
                "avg_effectiveness": 0.0,
                "effectiveness_by_agent": {},
                "effectiveness_trend": [],
                "problem_areas": [],
            }

    def get_performance_analytics(self, agent: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get performance analytics for traces.

        Args:
            agent: Optional agent filter
            days: Number of days to analyze

        Returns:
            Dictionary with performance metrics including:
            - avg_duration: Average duration in seconds
            - avg_tokens: Average token usage
            - duration_by_agent: Duration breakdown by agent
            - tokens_by_agent: Token usage breakdown by agent
            - slowest_operations: List of slowest operations
            - optimization_opportunities: List of optimization suggestions
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]

            if agent:
                recent_traces = [t for t in recent_traces if t.agent_identity.get("target_agent") == agent]

            if not recent_traces:
                return {
                    "avg_duration": 0.0,
                    "avg_tokens": 0,
                    "duration_by_agent": {},
                    "tokens_by_agent": {},
                    "slowest_operations": [],
                    "optimization_opportunities": [],
                }

            # Calculate durations and tokens
            total_duration = 0.0
            total_tokens = 0
            duration_by_agent = {}
            tokens_by_agent = {}
            agent_counts = {}
            slowest_ops = []

            for trace in recent_traces:
                agent_name = trace.agent_identity.get("target_agent", "unknown")
                trace_duration = sum(e.duration_seconds for e in trace.executions)
                trace_tokens = sum(e.metadata.get("tokens", len(e.prompt.split()) * 1.5) for e in trace.executions)

                total_duration += trace_duration
                total_tokens += trace_tokens

                # Aggregate by agent
                if agent_name not in duration_by_agent:
                    duration_by_agent[agent_name] = 0.0
                    tokens_by_agent[agent_name] = 0
                    agent_counts[agent_name] = 0

                duration_by_agent[agent_name] += trace_duration
                tokens_by_agent[agent_name] += trace_tokens
                agent_counts[agent_name] += 1

                # Track slowest operations
                slowest_ops.append(
                    {
                        "agent": agent_name,
                        "task": (trace.user_query[:50] + "..." if len(trace.user_query) > 50 else trace.user_query),
                        "duration": round(trace_duration, 2),
                        "trace_id": trace.trace_id,
                    }
                )

            # Calculate averages
            avg_duration = total_duration / len(recent_traces)
            avg_tokens = int(total_tokens / len(recent_traces))

            # Average by agent
            for agent_name in duration_by_agent:
                duration_by_agent[agent_name] = round(duration_by_agent[agent_name] / agent_counts[agent_name], 2)
                tokens_by_agent[agent_name] = int(tokens_by_agent[agent_name] / agent_counts[agent_name])

            # Get top 10 slowest operations
            slowest_operations = sorted(slowest_ops, key=lambda x: x["duration"], reverse=True)[:10]

            # Generate optimization opportunities
            optimization_opportunities = []
            for agent_name, avg_dur in duration_by_agent.items():
                if avg_dur > avg_duration * 1.5:
                    optimization_opportunities.append(
                        f"Optimize {agent_name}: {avg_dur:.2f}s avg (system avg: {avg_duration:.2f}s)"
                    )

            if avg_tokens > 5000:
                optimization_opportunities.append(
                    f"High token usage detected: {avg_tokens} tokens/trace. Consider prompt optimization."
                )

            return {
                "avg_duration": round(avg_duration, 2),
                "avg_tokens": avg_tokens,
                "duration_by_agent": duration_by_agent,
                "tokens_by_agent": tokens_by_agent,
                "slowest_operations": slowest_operations,
                "optimization_opportunities": optimization_opportunities,
            }
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {
                "avg_duration": 0.0,
                "avg_tokens": 0,
                "duration_by_agent": {},
                "tokens_by_agent": {},
                "slowest_operations": [],
                "optimization_opportunities": [],
            }

    def get_executive_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get high-level executive summary.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with executive-level metrics including:
            - total_traces: Total number of traces
            - total_cost: Total estimated cost
            - avg_effectiveness: Average effectiveness score
            - top_performing_agent: Best performing agent
            - biggest_cost_driver: Agent with highest cost
            - key_insights: List of key insights
            - recommendations: List of recommendations
        """
        try:
            from coffee_maker.autonomous.ace.insights import (
                generate_insights,
                generate_recommendations,
            )

            # Get component analytics
            cost_data = self.get_cost_analytics(days=days)
            effectiveness_data = self.get_effectiveness_analytics(days=days)
            performance_data = self.get_performance_analytics(days=days)

            # Count total traces
            cutoff = datetime.now() - timedelta(days=days)
            all_traces = self.trace_manager.list_traces()
            recent_traces = [t for t in all_traces if t.timestamp >= cutoff]
            total_traces = len(recent_traces)

            # Find top performing agent (highest effectiveness)
            top_performing_agent = (
                max(
                    effectiveness_data["effectiveness_by_agent"],
                    key=effectiveness_data["effectiveness_by_agent"].get,
                )
                if effectiveness_data["effectiveness_by_agent"]
                else "N/A"
            )

            # Generate insights and recommendations
            key_insights = generate_insights(cost_data, effectiveness_data, performance_data)
            recommendations = generate_recommendations(key_insights)

            return {
                "total_traces": total_traces,
                "total_cost": cost_data["total_cost"],
                "avg_effectiveness": effectiveness_data["avg_effectiveness"],
                "top_performing_agent": top_performing_agent,
                "biggest_cost_driver": cost_data["most_expensive_agent"],
                "key_insights": key_insights,
                "recommendations": recommendations,
            }
        except Exception as e:
            logger.error(f"Failed to get executive summary: {e}")
            return {
                "total_traces": 0,
                "total_cost": 0.0,
                "avg_effectiveness": 0.0,
                "top_performing_agent": "N/A",
                "biggest_cost_driver": "N/A",
                "key_insights": [],
                "recommendations": [],
            }
