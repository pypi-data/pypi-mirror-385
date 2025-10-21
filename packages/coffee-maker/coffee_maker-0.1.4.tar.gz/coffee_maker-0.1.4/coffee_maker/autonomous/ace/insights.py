"""Insights generation engine for ACE analytics.

This module provides intelligent insights and recommendations based on
analytics data from the ACE framework.

Example:
    from coffee_maker.autonomous.ace.insights import generate_insights, generate_recommendations

    insights = generate_insights(cost_data, effectiveness_data, performance_data)
    recommendations = generate_recommendations(insights)
"""

from typing import Any, Dict, List


def generate_insights(
    cost_data: Dict[str, Any],
    effectiveness_data: Dict[str, Any],
    performance_data: Dict[str, Any],
) -> List[str]:
    """Generate actionable insights from analytics data.

    Args:
        cost_data: Cost analytics dictionary
        effectiveness_data: Effectiveness analytics dictionary
        performance_data: Performance analytics dictionary

    Returns:
        List of insight strings

    Example:
        insights = generate_insights(cost_data, effectiveness_data, performance_data)
        # Returns: ["Cost is increasing. Consider optimizing code_developer", ...]
    """
    insights = []

    # Cost insights
    if cost_data.get("trend") == "increasing":
        most_expensive = cost_data.get("most_expensive_agent", "unknown")
        total_cost = cost_data.get("total_cost", 0)
        insights.append(
            f"Cost trend is increasing (${total_cost:.2f} total). " f"Consider optimizing {most_expensive}."
        )
    elif cost_data.get("trend") == "decreasing":
        insights.append("Cost trend is decreasing. Recent optimizations are effective.")

    # High cost per trace
    avg_cost = cost_data.get("avg_cost_per_trace", 0)
    if avg_cost > 0.01:
        insights.append(
            f"Average cost per trace is ${avg_cost:.4f}. " f"Consider prompt optimization to reduce token usage."
        )

    # Cost concentration
    cost_by_agent = cost_data.get("cost_by_agent", {})
    if cost_by_agent and len(cost_by_agent) > 1:
        max_agent_cost = max(cost_by_agent.values())
        total_cost = sum(cost_by_agent.values())
        concentration = max_agent_cost / total_cost
        if concentration > 0.4:  # Changed from 0.5 to 0.4 to be more sensitive
            top_agent = max(cost_by_agent, key=cost_by_agent.get)
            insights.append(
                f"{top_agent} accounts for {concentration*100:.1f}% of total costs. "
                f"This agent may benefit from optimization."
            )

    # Effectiveness insights
    success_rate = effectiveness_data.get("success_rate", 0)
    if success_rate < 0.8:
        insights.append(
            f"Success rate is {success_rate:.1%}, below target. " f"Focus on improving error handling and validation."
        )
    elif success_rate >= 0.95:
        insights.append(f"Excellent success rate of {success_rate:.1%}. System is performing well.")

    # Problem areas
    problem_areas = effectiveness_data.get("problem_areas", [])
    if problem_areas:
        insights.append(f"Problem areas detected: {', '.join(problem_areas)}. " f"These agents need attention.")

    # Error rate insights
    error_rate = effectiveness_data.get("error_rate", 0)
    if error_rate > 0.2:
        insights.append(
            f"Error rate is {error_rate:.1%}, higher than acceptable. "
            f"Review failure patterns and add defensive programming."
        )

    # Effectiveness variance
    eff_by_agent = effectiveness_data.get("effectiveness_by_agent", {})
    if eff_by_agent and len(eff_by_agent) > 1:
        values = list(eff_by_agent.values())
        max_eff = max(values)
        min_eff = min(values)
        if max_eff - min_eff > 0.3:
            best_agent = max(eff_by_agent, key=eff_by_agent.get)
            worst_agent = min(eff_by_agent, key=eff_by_agent.get)
            insights.append(
                f"Large effectiveness variance: {best_agent} ({max_eff:.1%}) vs "
                f"{worst_agent} ({min_eff:.1%}). Learn from top performers."
            )

    # Performance insights
    avg_duration = performance_data.get("avg_duration", 0)
    if avg_duration > 30:
        insights.append(f"Average execution time is {avg_duration:.1f}s. " f"Performance optimization recommended.")
    elif avg_duration < 5:
        insights.append(f"Fast execution times ({avg_duration:.1f}s average). Good performance.")

    # Slow agents
    duration_by_agent = performance_data.get("duration_by_agent", {})
    if duration_by_agent and avg_duration > 0:
        slow_agents = [
            agent
            for agent, dur in duration_by_agent.items()
            if dur > avg_duration * 1.5  # Changed from 2x to 1.5x to be more sensitive
        ]
        if slow_agents:
            insights.append(
                f"Agents {', '.join(slow_agents)} are significantly slower than average. " f"Investigate bottlenecks."
            )

    # Token usage insights
    avg_tokens = performance_data.get("avg_tokens", 0)
    if avg_tokens > 10000:
        insights.append(f"High token usage detected ({avg_tokens} tokens/trace). " f"Optimize prompts to reduce costs.")

    # Optimization opportunities
    opt_opportunities = performance_data.get("optimization_opportunities", [])
    if opt_opportunities:
        insights.append(
            f"{len(opt_opportunities)} optimization opportunities identified. " f"Review slowest operations."
        )

    # If no significant insights, provide positive feedback
    if not insights:
        insights.append("System is operating within normal parameters. " "Continue monitoring for trends.")

    return insights


def generate_recommendations(insights: List[str]) -> List[str]:
    """Generate actionable recommendations based on insights.

    Args:
        insights: List of insight strings

    Returns:
        List of recommendation strings

    Example:
        recommendations = generate_recommendations(insights)
        # Returns: ["Implement retry logic and better error handling", ...]
    """
    recommendations = []

    # Analyze insights and generate recommendations
    insights_text = " ".join(insights).lower()

    # Cost-related recommendations
    if "cost" in insights_text and "increasing" in insights_text:
        recommendations.append("Review expensive operations and implement caching where appropriate")
        recommendations.append("Analyze token usage patterns and optimize prompts to reduce length")
        recommendations.append("Consider batching similar operations to reduce API calls")

    if "optimization" in insights_text:
        recommendations.append("Profile slow agents to identify specific bottlenecks")
        recommendations.append("Review execution traces for the slowest operations")

    # Effectiveness recommendations
    if "success rate" in insights_text or "error rate" in insights_text:
        recommendations.append("Implement comprehensive error handling and retry logic")
        recommendations.append("Add input validation to catch errors early")
        recommendations.append("Review failed traces to identify common failure patterns")

    if "problem areas" in insights_text:
        recommendations.append("Focus development effort on underperforming agents")
        recommendations.append("Review and update playbooks for problematic categories")

    if "variance" in insights_text and "learn from" in insights_text:
        recommendations.append("Analyze top-performing agents and share best practices")
        recommendations.append("Update playbooks based on successful agent patterns")

    # Performance recommendations
    if "slower than average" in insights_text or "execution time" in insights_text:
        recommendations.append("Optimize database queries and reduce I/O operations")
        recommendations.append("Consider async operations for long-running tasks")
        recommendations.append("Review and optimize slow agents identified in analytics")

    if "token usage" in insights_text:
        recommendations.append("Compress prompts by removing redundant context")
        recommendations.append("Use prompt templates to standardize and optimize prompts")
        recommendations.append("Consider using smaller models for simple tasks")

    # Monitoring recommendations (always include)
    if not recommendations:
        recommendations.append("Continue monitoring analytics trends for early detection of issues")
        recommendations.append("Set up alerts for key metrics (cost, success rate, performance)")

    # General best practices (add if we have space)
    if len(recommendations) < 5:
        recommendations.append("Regularly review and curate playbooks to maintain quality")
        recommendations.append("Document successful patterns in agent playbooks")

    # Return top 8 most relevant recommendations
    return recommendations[:8]


def categorize_insights(insights: List[str]) -> Dict[str, List[str]]:
    """Categorize insights by type for better organization.

    Args:
        insights: List of insight strings

    Returns:
        Dictionary mapping categories to lists of insights

    Example:
        categorized = categorize_insights(insights)
        # Returns: {"cost": [...], "effectiveness": [...], "performance": [...]}
    """
    categories = {
        "cost": [],
        "effectiveness": [],
        "performance": [],
        "other": [],
    }

    for insight in insights:
        insight_lower = insight.lower()
        if any(keyword in insight_lower for keyword in ["cost", "expensive", "$"]):
            categories["cost"].append(insight)
        elif any(keyword in insight_lower for keyword in ["success", "error", "failure", "effective"]):
            categories["effectiveness"].append(insight)
        elif any(keyword in insight_lower for keyword in ["duration", "slow", "performance", "token", "time"]):
            categories["performance"].append(insight)
        else:
            categories["other"].append(insight)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def prioritize_recommendations(recommendations: List[str]) -> List[Dict[str, Any]]:
    """Prioritize recommendations by impact and urgency.

    Args:
        recommendations: List of recommendation strings

    Returns:
        List of dictionaries with recommendations and priority scores

    Example:
        prioritized = prioritize_recommendations(recommendations)
        # Returns: [{"text": "...", "priority": "high", "score": 9}, ...]
    """
    prioritized = []

    # Keywords indicating high priority
    high_priority_keywords = ["error", "failure", "critical", "significant"]
    medium_priority_keywords = ["optimize", "improve", "consider", "review"]
    low_priority_keywords = ["continue", "monitor", "document"]

    for rec in recommendations:
        rec_lower = rec.lower()

        # Calculate priority score
        score = 5  # Default medium priority
        priority = "medium"

        if any(keyword in rec_lower for keyword in high_priority_keywords):
            score = 9
            priority = "high"
        elif any(keyword in rec_lower for keyword in medium_priority_keywords):
            score = 6
            priority = "medium"
        elif any(keyword in rec_lower for keyword in low_priority_keywords):
            score = 3
            priority = "low"

        prioritized.append(
            {
                "text": rec,
                "priority": priority,
                "score": score,
            }
        )

    # Sort by score descending
    prioritized.sort(key=lambda x: x["score"], reverse=True)

    return prioritized
