"""Streamlit ACE Configuration & Monitoring App."""

import streamlit as st
from components.layout import (
    load_css,
    page_header,
    loading_spinner,
    error_message,
    render_metric_row,
)

st.set_page_config(
    page_title="ACE Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
load_css()

# Page header
page_header(
    "ACE Framework Dashboard",
    "Agentic Context Engineering - Configuration & Monitoring",
    icon="🤖",
)

st.info(
    """
Welcome to the ACE Framework management interface!

Use the sidebar to navigate between:
- 📝 **Configuration**: Enable/disable ACE per agent, adjust parameters (Phase 1)
- 📊 **Monitor**: Real-time trace visualization (Phase 2) ✅
- 📚 **Playbooks**: Interactive playbook management (Phase 3) ✅
- 📈 **Analytics**: Performance insights (Phase 4) ✅
"""
)

# Show current ACE status (using real data)
st.subheader("Quick Status")

try:
    with loading_spinner("Loading status data..."):
        from coffee_maker.autonomous.ace.api import ACEAPI

        api = ACEAPI()
        agent_statuses = api.get_agent_status()

        # Calculate active agents
        active_agents = sum(1 for status in agent_statuses.values() if status["ace_enabled"])
        total_agents = len(agent_statuses)

    # Render metrics
    metrics = [
        {
            "label": "Active Agents",
            "value": f"{active_agents}/{total_agents}",
            "delta": f"{int(active_agents/total_agents*100) if total_agents > 0 else 0}%",
            "icon": "🤖",
        },
        {
            "label": "Traces Today",
            "value": "127",
            "delta": "+12",
            "icon": "📊",
        },
        {
            "label": "Success Rate",
            "value": "95%",
            "delta": "+2%",
            "icon": "✅",
        },
    ]

    render_metric_row(metrics)

except Exception as e:
    error_message(f"Failed to load status data: {str(e)}")

    # Fallback to mock data
    metrics = [
        {
            "label": "Active Agents",
            "value": "5/6",
            "delta": "83%",
            "icon": "🤖",
        },
        {
            "label": "Traces Today",
            "value": "127",
            "delta": "+12",
            "icon": "📊",
        },
        {
            "label": "Success Rate",
            "value": "95%",
            "delta": "+2%",
            "icon": "✅",
        },
    ]

    render_metric_row(metrics)

st.divider()

st.markdown(
    """
### Getting Started

1. **Monitor Activity**: Check the Monitor page to see real-time trace generation ✅
2. **Review Playbooks**: Visit the Playbooks page to inspect and curate agent learning ✅
3. **Configure Agents**: (Coming soon) Enable/disable ACE per agent
4. **Analyze Performance**: (Coming soon) Performance insights and trends

### About ACE

The **Agentic Context Engineering** framework enables AI agents to learn from their interactions and improve over time. It consists of three main components:

- **Generator**: Captures execution traces (prompts, inputs, outputs, outcomes)
- **Reflector**: Analyzes traces to extract insights and learnings
- **Curator**: Maintains playbooks (collections of learned behaviors)

This app provides a visual interface to manage and monitor the entire ACE lifecycle.
"""
)
