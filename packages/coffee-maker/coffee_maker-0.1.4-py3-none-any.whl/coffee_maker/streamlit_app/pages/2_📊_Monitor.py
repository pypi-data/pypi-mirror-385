"""Monitor tab for real-time trace visualization."""

import streamlit as st
from datetime import datetime
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
    empty_state,
)

st.set_page_config(page_title="Monitor", page_icon="📊", layout="wide")

# Load custom CSS
load_css()

# Page header
page_header(
    "Monitor",
    "Real-time ACE execution monitoring and agent performance tracking",
    icon="📊",
)

# Initialize API
api = ACEAPI()

# Filters
st.subheader("Filters")
col1, col2, col3 = st.columns(3)

with col1:
    agent_filter = st.selectbox(
        "Agent",
        [
            "All",
            "user_interpret",
            "assistant",
            "code_searcher",
            "code_developer",
            "user_listener",
            "project_manager",
        ],
        key="agent_filter",
    )

with col2:
    hours_filter = st.selectbox(
        "Time Range",
        [
            ("Last Hour", 1),
            ("Last 6 Hours", 6),
            ("Last 24 Hours", 24),
            ("Last Week", 168),
        ],
        format_func=lambda x: x[0],
        key="hours_filter",
    )

with col3:
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=False, key="auto_refresh")

# Auto-refresh logic
if auto_refresh:
    st.info("Auto-refresh enabled - page will reload every 5 seconds")
    import time

    time.sleep(5)
    st.rerun()

# Fetch traces
try:
    with loading_spinner("Loading traces..."):
        agent_name = None if agent_filter == "All" else agent_filter
        traces = api.get_traces(agent=agent_name, hours=hours_filter[1], limit=100)
except Exception as e:
    error_message(f"Failed to load traces: {str(e)}")
    traces = []

# Display summary metrics
st.subheader("Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Traces", len(traces))

with col2:
    success_count = sum(1 for t in traces if all(e["result_status"] == "success" for e in t.get("executions", [])))
    st.metric(
        "Success",
        success_count,
        delta=f"{int(success_count / len(traces) * 100)}%" if traces else "0%",
    )

with col3:
    failure_count = len(traces) - success_count
    st.metric("Failures", failure_count)

with col4:
    if traces:
        avg_duration = sum(sum(e["duration_seconds"] for e in t.get("executions", [])) for t in traces) / len(traces)
        st.metric("Avg Duration", f"{avg_duration:.2f}s")
    else:
        st.metric("Avg Duration", "N/A")

st.divider()

# Live Trace Feed
st.subheader(f"Live Trace Feed ({len(traces)} traces)")

if not traces:
    empty_state(
        "No traces found",
        icon="📭",
        suggestion="Try adjusting the time range or agent filter, or run the daemon to generate traces.",
    )
else:
    for trace in traces[:50]:  # Limit to 50 for performance
        # Determine status
        executions = trace.get("executions", [])
        if not executions:
            status = "unknown"
            status_color = "gray"
        elif all(e["result_status"] == "success" for e in executions):
            status = "success"
            status_color = "green"
        else:
            status = "failure"
            status_color = "red"

        # Extract info
        trace_id = trace.get("trace_id", "N/A")
        timestamp = trace.get("timestamp", "N/A")
        agent_name = trace.get("agent_identity", {}).get("target_agent", "unknown")
        user_query = trace.get("user_query", "N/A")
        total_duration = sum(e["duration_seconds"] for e in executions)

        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestamp_str = timestamp

        # Display trace card
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"**{agent_name}**")
                st.caption(f"Query: {user_query[:80]}..." if len(user_query) > 80 else user_query)

            with col2:
                st.text(timestamp_str)
                st.caption(f"Duration: {total_duration:.2f}s")

            with col3:
                if status == "success":
                    st.success("✓ SUCCESS")
                elif status == "failure":
                    st.error("✗ FAILURE")
                else:
                    st.warning("? UNKNOWN")

            # Expandable details
            with st.expander("View Details"):
                st.json(trace)

        st.divider()

st.divider()

# Agent Performance Dashboard
st.subheader("Agent Performance")
st.markdown(f"Performance metrics for the last {hours_filter[0].lower()}")

# Get metrics
metrics = api.get_metrics(days=hours_filter[1] // 24 if hours_filter[1] >= 24 else 1)
agent_metrics = metrics.get("agent_metrics", {})

if not agent_metrics:
    st.info("No agent performance data available for this time range.")
else:
    # Sort agents by total traces (descending)
    sorted_agents = sorted(agent_metrics.items(), key=lambda x: x[1]["total_traces"], reverse=True)

    for agent_name, agent_data in sorted_agents:
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{agent_name}**")

                # Success rate progress bar
                success_rate = agent_data.get("success_rate", 0.0)
                if success_rate >= 90:
                    bar_color = "green"
                elif success_rate >= 70:
                    bar_color = "orange"
                else:
                    bar_color = "red"

                # Custom progress bar using markdown
                filled = int(success_rate / 2.5)  # Scale to 40 chars
                bar = "█" * filled + "░" * (40 - filled)
                st.markdown(f"`{bar}` {success_rate:.1f}%")

                st.caption(
                    f"{agent_data['total_traces']} traces | "
                    f"{agent_data['success_count']} success / {agent_data['failure_count']} failure | "
                    f"Avg: {agent_data['avg_duration_seconds']}s"
                )

            with col2:
                # Trend indicator
                if success_rate >= 90:
                    st.success("✓ Excellent")
                elif success_rate >= 70:
                    st.warning("⚠ Good")
                else:
                    st.error("✗ Needs Attention")

        st.divider()

st.divider()

# Reflection Status
st.subheader("Reflector Status")

reflection_status = api.get_reflection_status()

col1, col2, col3 = st.columns(3)

with col1:
    last_run = reflection_status.get("last_run")
    if last_run:
        try:
            dt = datetime.fromisoformat(last_run)
            time_ago = datetime.now() - dt
            minutes_ago = int(time_ago.total_seconds() / 60)
            if minutes_ago < 60:
                display_time = f"{minutes_ago} minutes ago"
            elif minutes_ago < 1440:
                display_time = f"{minutes_ago // 60} hours ago"
            else:
                display_time = f"{minutes_ago // 1440} days ago"
            st.metric("Last Run", display_time)
        except:
            st.metric("Last Run", "Unknown")
    else:
        st.metric("Last Run", "Never")

with col2:
    st.metric("Pending Traces", reflection_status.get("pending_traces", 0))

with col3:
    st.metric("Delta Items", reflection_status.get("delta_items_generated", 0))

st.info("Manual reflector trigger coming in Phase 3")

st.markdown(
    """
### About This Monitor

This monitor provides real-time visibility into the ACE framework's operation:

- **Live Trace Feed**: See agent executions as they happen
- **Performance Metrics**: Track success rates and execution times
- **Reflection Status**: Monitor the reflection pipeline

**Tips**:
- Enable auto-refresh for real-time monitoring
- Filter by agent to focus on specific components
- Expand traces to see full execution details
- Use different time ranges to analyze trends
"""
)
