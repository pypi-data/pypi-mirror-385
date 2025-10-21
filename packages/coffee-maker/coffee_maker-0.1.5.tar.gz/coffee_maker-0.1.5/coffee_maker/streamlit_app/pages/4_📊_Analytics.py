"""Analytics Dashboard for comprehensive ACE metrics and insights."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from coffee_maker.autonomous.ace.api import ACEAPI
import sys
from pathlib import Path

# Add parent directory to path for components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.layout import (
    load_css,
    page_header,
    loading_spinner,
    error_message,
)

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# Load custom CSS
load_css()

# Page header
page_header(
    "Analytics Dashboard",
    "Comprehensive analytics and insights for the ACE framework",
    icon="📈",
)

# Initialize API
api = ACEAPI()

# Date range selector
st.sidebar.header("Analytics Settings")
days = st.sidebar.slider("Time Range (days)", 7, 90, 30)
st.sidebar.info(f"Analyzing data from the last {days} days")

# Agent filter (optional)
agent_filter = st.sidebar.selectbox(
    "Filter by Agent (optional)",
    [
        "All Agents",
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
    ],
)
selected_agent = None if agent_filter == "All Agents" else agent_filter

# Fetch analytics data
try:
    with loading_spinner("Loading analytics data (this may take a moment)..."):
        summary = api.get_executive_summary(days=days)
        cost_data = api.get_cost_analytics(agent=selected_agent, days=days)
        effectiveness_data = api.get_effectiveness_analytics(agent=selected_agent, days=days)
        performance_data = api.get_performance_analytics(agent=selected_agent, days=days)
except Exception as e:
    error_message(f"Failed to load analytics: {str(e)}")
    st.stop()

# ===== EXECUTIVE SUMMARY =====
st.header("📋 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Traces",
        f"{summary['total_traces']:,}",
        help="Number of execution traces in the selected time range",
    )

with col2:
    st.metric(
        "Total Cost",
        f"${summary['total_cost']:.2f}",
        help="Estimated total cost based on token usage",
    )

with col3:
    eff_value = summary["avg_effectiveness"]
    eff_display = f"{eff_value:.1%}" if eff_value > 0 else "N/A"
    eff_delta = "Good" if eff_value >= 0.8 else "Needs Improvement"
    st.metric(
        "Avg Effectiveness",
        eff_display,
        delta=eff_delta,
        help="Average success rate across all agents",
    )

with col4:
    st.metric(
        "Top Agent",
        summary["top_performing_agent"],
        help="Agent with highest effectiveness",
    )

st.divider()

# Key insights
if summary.get("key_insights"):
    st.subheader("💡 Key Insights")
    for i, insight in enumerate(summary["key_insights"][:5]):
        if i % 2 == 0:
            st.info(f"💡 {insight}")
        else:
            st.success(f"✨ {insight}")

st.divider()

# ===== COST ANALYTICS =====
st.header("💰 Cost Analytics")

if cost_data["total_cost"] > 0:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Cost",
            f"${cost_data['total_cost']:.2f}",
            delta=f"Trend: {cost_data['trend']}",
            help="Total estimated cost for the period",
        )

    with col2:
        st.metric(
            "Avg Cost/Trace",
            f"${cost_data['avg_cost_per_trace']:.4f}",
            help="Average cost per execution trace",
        )

    with col3:
        st.metric(
            "Most Expensive",
            cost_data["most_expensive_agent"],
            help="Agent with highest total cost",
        )

    # Cost visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Cost by agent (pie chart)
        if cost_data["cost_by_agent"]:
            fig = px.pie(
                values=list(cost_data["cost_by_agent"].values()),
                names=list(cost_data["cost_by_agent"].keys()),
                title="Cost Distribution by Agent",
                hole=0.4,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available for agents")

    with col2:
        # Cost trend over time (line chart)
        if cost_data["cost_by_day"]:
            df_cost = pd.DataFrame(cost_data["cost_by_day"])
            fig = px.line(
                df_cost,
                x="date",
                y="cost",
                title="Daily Cost Trend",
                markers=True,
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Cost ($)",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily cost trend data available")
else:
    st.info("No cost data available for the selected period")

st.divider()

# ===== EFFECTIVENESS ANALYTICS =====
st.header("✅ Effectiveness Analytics")

if effectiveness_data["avg_effectiveness"] > 0:
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Success Rate",
            f"{effectiveness_data['success_rate']:.1%}",
            help="Percentage of successful executions",
        )

    with col2:
        st.metric(
            "Error Rate",
            f"{effectiveness_data['error_rate']:.1%}",
            delta=("Lower is better" if effectiveness_data["error_rate"] > 0.1 else "Good"),
            help="Percentage of failed executions",
        )

    with col3:
        st.metric(
            "Avg Effectiveness",
            f"{effectiveness_data['avg_effectiveness']:.1%}",
            help="Average effectiveness across all agents",
        )

    with col4:
        problem_count = len(effectiveness_data.get("problem_areas", []))
        st.metric(
            "Problem Areas",
            problem_count,
            delta="Needs attention" if problem_count > 0 else "All good",
            help="Agents with effectiveness < 70%",
        )

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Success vs Error rate (gauge-like bar chart)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Success Rate"],
                y=[effectiveness_data["success_rate"]],
                name="Success",
                marker_color="#28a745",
                text=[f"{effectiveness_data['success_rate']:.1%}"],
                textposition="auto",
            )
        )
        fig.add_trace(
            go.Bar(
                x=["Error Rate"],
                y=[effectiveness_data["error_rate"]],
                name="Error",
                marker_color="#dc3545",
                text=[f"{effectiveness_data['error_rate']:.1%}"],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Success vs Error Rate",
            yaxis_title="Rate",
            yaxis=dict(range=[0, 1], tickformat=".0%"),
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Effectiveness by agent (horizontal bar chart)
        if effectiveness_data["effectiveness_by_agent"]:
            eff_df = pd.DataFrame(
                [
                    {"Agent": agent, "Effectiveness": eff}
                    for agent, eff in effectiveness_data["effectiveness_by_agent"].items()
                ]
            ).sort_values("Effectiveness", ascending=True)

            fig = px.bar(
                eff_df,
                x="Effectiveness",
                y="Agent",
                orientation="h",
                title="Effectiveness by Agent",
                color="Effectiveness",
                color_continuous_scale=["red", "yellow", "green"],
                range_color=[0, 1],
            )
            fig.update_layout(
                xaxis_title="Effectiveness",
                yaxis_title="Agent",
                xaxis=dict(tickformat=".0%"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No agent effectiveness data available")

    # Effectiveness trend over time
    if effectiveness_data.get("effectiveness_trend"):
        st.subheader("Effectiveness Trend Over Time")
        trend_df = pd.DataFrame(effectiveness_data["effectiveness_trend"])
        fig = px.line(
            trend_df,
            x="date",
            y="effectiveness",
            title="Daily Effectiveness Trend",
            markers=True,
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Effectiveness",
            yaxis=dict(tickformat=".0%"),
            hovermode="x unified",
        )
        # Add target line at 80%
        fig.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Target (80%)")
        st.plotly_chart(fig, use_container_width=True)

    # Problem areas
    if effectiveness_data.get("problem_areas"):
        st.warning("⚠️ Problem Areas Detected")
        for area in effectiveness_data["problem_areas"]:
            st.write(f"- {area}")
else:
    st.info("No effectiveness data available for the selected period")

st.divider()

# ===== PERFORMANCE ANALYTICS =====
st.header("⚡ Performance Analytics")

if performance_data["avg_duration"] > 0:
    # Metrics row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Avg Duration",
            f"{performance_data['avg_duration']:.2f}s",
            help="Average execution time per trace",
        )

    with col2:
        st.metric(
            "Avg Tokens",
            f"{performance_data['avg_tokens']:,}",
            help="Average token usage per trace",
        )

    with col3:
        opt_count = len(performance_data.get("optimization_opportunities", []))
        st.metric(
            "Optimization Opps",
            opt_count,
            help="Number of optimization opportunities identified",
        )

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Average duration by agent
        if performance_data["duration_by_agent"]:
            dur_df = pd.DataFrame(
                [{"Agent": agent, "Duration": dur} for agent, dur in performance_data["duration_by_agent"].items()]
            ).sort_values("Duration", ascending=False)

            fig = px.bar(
                dur_df,
                x="Agent",
                y="Duration",
                title="Avg Duration by Agent (seconds)",
                color="Duration",
                color_continuous_scale="Reds",
            )
            fig.update_layout(
                xaxis_title="Agent",
                yaxis_title="Duration (seconds)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No duration data available")

    with col2:
        # Token usage by agent
        if performance_data["tokens_by_agent"]:
            tok_df = pd.DataFrame(
                [{"Agent": agent, "Tokens": tok} for agent, tok in performance_data["tokens_by_agent"].items()]
            ).sort_values("Tokens", ascending=False)

            fig = px.bar(
                tok_df,
                x="Agent",
                y="Tokens",
                title="Avg Tokens by Agent",
                color="Tokens",
                color_continuous_scale="Blues",
            )
            fig.update_layout(
                xaxis_title="Agent",
                yaxis_title="Tokens",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No token usage data available")

    # Slowest operations table
    if performance_data.get("slowest_operations"):
        st.subheader("🐌 Slowest Operations")
        slowest_df = pd.DataFrame(performance_data["slowest_operations"])
        st.dataframe(
            slowest_df[["agent", "task", "duration"]],
            use_container_width=True,
            hide_index=True,
        )

    # Optimization opportunities
    if performance_data.get("optimization_opportunities"):
        st.subheader("✨ Optimization Opportunities")
        for opp in performance_data["optimization_opportunities"]:
            st.success(f"✨ {opp}")
else:
    st.info("No performance data available for the selected period")

st.divider()

# ===== RECOMMENDATIONS =====
st.header("📋 Recommendations")

if summary.get("recommendations"):
    st.markdown("Based on the analytics above, here are actionable recommendations:")

    for i, rec in enumerate(summary["recommendations"], 1):
        with st.container():
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown(f"**{i}.**")
            with col2:
                st.info(f"📋 {rec}")
else:
    st.success("✅ System is operating optimally. No recommendations at this time.")

st.divider()

# ===== ADVANCED ANALYTICS =====
with st.expander("🔬 Advanced Analytics"):
    st.subheader("Cost vs Effectiveness Scatter Plot")

    if cost_data["cost_by_agent"] and effectiveness_data["effectiveness_by_agent"]:
        # Prepare data for scatter plot
        scatter_data = []
        for agent in cost_data["cost_by_agent"].keys():
            if agent in effectiveness_data["effectiveness_by_agent"]:
                scatter_data.append(
                    {
                        "Agent": agent,
                        "Cost": cost_data["cost_by_agent"][agent],
                        "Effectiveness": effectiveness_data["effectiveness_by_agent"][agent],
                    }
                )

        if scatter_data:
            scatter_df = pd.DataFrame(scatter_data)
            fig = px.scatter(
                scatter_df,
                x="Cost",
                y="Effectiveness",
                text="Agent",
                title="Cost vs Effectiveness Analysis",
                size=[20] * len(scatter_df),  # Fixed size
                color="Effectiveness",
                color_continuous_scale="RdYlGn",
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(
                xaxis_title="Cost ($)",
                yaxis_title="Effectiveness",
                yaxis=dict(tickformat=".0%"),
            )
            # Add quadrant lines
            avg_cost = scatter_df["Cost"].mean()
            avg_eff = scatter_df["Effectiveness"].mean()
            fig.add_hline(y=avg_eff, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=avg_cost, line_dash="dash", line_color="gray", opacity=0.5)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                """
            **Quadrant Analysis**:
            - **Top Left**: High effectiveness, low cost (ideal)
            - **Top Right**: High effectiveness, high cost (review for optimization)
            - **Bottom Left**: Low effectiveness, low cost (needs improvement)
            - **Bottom Right**: Low effectiveness, high cost (high priority for optimization)
            """
            )
        else:
            st.info("Insufficient data for scatter plot")
    else:
        st.info("No data available for cost vs effectiveness analysis")

    st.divider()

    st.subheader("Agent Performance Heatmap")

    if (
        cost_data["cost_by_agent"]
        and effectiveness_data["effectiveness_by_agent"]
        and performance_data["duration_by_agent"]
    ):

        # Prepare heatmap data
        agents = sorted(set(cost_data["cost_by_agent"].keys()))
        metrics = ["Cost", "Effectiveness", "Duration"]

        # Normalize data for heatmap (0-1 scale)
        heatmap_data = []
        for agent in agents:
            row = []
            # Cost (higher is worse, so invert)
            max_cost = max(cost_data["cost_by_agent"].values())
            cost_norm = 1 - (cost_data["cost_by_agent"].get(agent, 0) / max_cost if max_cost > 0 else 0)
            row.append(cost_norm)

            # Effectiveness (higher is better)
            eff_norm = effectiveness_data["effectiveness_by_agent"].get(agent, 0)
            row.append(eff_norm)

            # Duration (higher is worse, so invert)
            max_dur = max(performance_data["duration_by_agent"].values())
            dur_norm = 1 - (performance_data["duration_by_agent"].get(agent, 0) / max_dur if max_dur > 0 else 0)
            row.append(dur_norm)

            heatmap_data.append(row)

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                x=metrics,
                y=agents,
                colorscale="RdYlGn",
                text=[[f"{val:.2f}" for val in row] for row in heatmap_data],
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate="Agent: %{y}<br>Metric: %{x}<br>Score: %{z:.2f}<extra></extra>",
            )
        )
        fig.update_layout(
            title="Agent Performance Heatmap (Normalized 0-1 scale, higher is better)",
            xaxis_title="Metric",
            yaxis_title="Agent",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info("All metrics are normalized to 0-1 scale where higher is better. Cost and Duration are inverted.")
    else:
        st.info("No data available for performance heatmap")

# Footer
st.divider()
st.markdown(
    """
### About This Dashboard

This analytics dashboard provides comprehensive insights into the ACE framework's performance:

- **Executive Summary**: High-level KPIs and insights
- **Cost Analytics**: Track spending trends and identify cost drivers
- **Effectiveness Analytics**: Monitor success rates and problem areas
- **Performance Analytics**: Analyze execution times and optimization opportunities
- **Recommendations**: Actionable suggestions based on data

**Tips**:
- Adjust the time range to see different trends
- Filter by agent to focus on specific components
- Review recommendations regularly to optimize system performance
- Use advanced analytics to identify correlations
"""
)
