"""Playbook Management page for ACE framework."""

import streamlit as st
from datetime import datetime
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
    empty_state,
)

st.set_page_config(page_title="Playbooks", page_icon="📚", layout="wide")

# Load custom CSS
load_css()

# Page header
page_header(
    "Playbook Management",
    "Interactive playbook curation and bullet management",
    icon="📚",
)

# Initialize API
api = ACEAPI()

# Agent selection
st.subheader("Select Agent")
agent_names = [
    "user_interpret",
    "assistant",
    "code_searcher",
    "code_developer",
    "user_listener",
    "project_manager",
]
selected_agent = st.selectbox("Agent", agent_names, key="agent_selector")

# Load playbook
try:
    with loading_spinner(f"Loading playbook for {selected_agent}..."):
        playbook = api.get_playbook(selected_agent)
        if not playbook:
            error_message(f"Failed to load playbook for {selected_agent}")
            st.stop()

        bullets = playbook.get("bullets", [])
        total_bullets = playbook.get("total_bullets", 0)
        avg_effectiveness = playbook.get("avg_effectiveness", 0.0)
        last_updated = playbook.get("last_updated")

except Exception as e:
    error_message(f"Error loading playbook: {e}")
    st.stop()

# Display quick stats
st.subheader("Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Bullets", total_bullets)

with col2:
    st.metric("Avg Effectiveness", f"{avg_effectiveness:.2f}")

with col3:
    active_count = len([b for b in bullets if b.get("status") == "active"])
    st.metric("Active", active_count)

with col4:
    pending_count = len([b for b in bullets if b.get("status") == "pending"])
    st.metric("Pending Review", pending_count, delta=f"{pending_count} items")

st.divider()

# Filters section
st.subheader("Filters & Search")

col1, col2, col3 = st.columns(3)

with col1:
    # Category filter
    categories = api.get_playbook_categories(selected_agent)
    category_filter = st.selectbox("Category", ["All"] + categories, key="category_filter")

with col2:
    # Status filter
    status_filter = st.selectbox("Status", ["All", "active", "pending", "archived"], key="status_filter")

with col3:
    # Effectiveness slider
    effectiveness_range = st.slider(
        "Effectiveness Range", min_value=0.0, max_value=1.0, value=(0.0, 1.0), step=0.05, key="effectiveness_slider"
    )

# Search box
search_query = st.text_input("Search bullets", placeholder="Type to search bullet content...", key="search_input")

# Sort options
sort_by = st.selectbox(
    "Sort by",
    ["Effectiveness (High to Low)", "Effectiveness (Low to High)", "Date Added (Newest)", "Date Added (Oldest)"],
    key="sort_selector",
)

st.divider()

# Apply filters
filtered_bullets = api.get_playbook_bullets(
    agent_name=selected_agent,
    category=category_filter if category_filter != "All" else None,
    status=status_filter if status_filter != "All" else None,
    min_effectiveness=effectiveness_range[0],
    max_effectiveness=effectiveness_range[1],
    search_query=search_query if search_query else None,
)

# Apply sorting
if sort_by == "Effectiveness (High to Low)":
    filtered_bullets.sort(key=lambda b: b.get("effectiveness", 0), reverse=True)
elif sort_by == "Effectiveness (Low to High)":
    filtered_bullets.sort(key=lambda b: b.get("effectiveness", 0))
elif sort_by == "Date Added (Newest)":
    filtered_bullets.sort(
        key=lambda b: b.get("added_date", "1970-01-01"),
        reverse=True,
    )
else:  # Date Added (Oldest)
    filtered_bullets.sort(key=lambda b: b.get("added_date", "1970-01-01"))

# Display filtered count
st.subheader(f"Bullets ({len(filtered_bullets)} matching filters)")

if not filtered_bullets:
    empty_state(
        "No bullets match filters",
        icon="🔍",
        suggestion="Try adjusting your search criteria or filters.",
    )
else:
    # Pagination
    items_per_page = 20
    total_pages = (len(filtered_bullets) + items_per_page - 1) // items_per_page

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("◀ Previous", key="prev_page") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()

    with col2:
        st.markdown(f"<center>Page {st.session_state.current_page} of {total_pages}</center>", unsafe_allow_html=True)

    with col3:
        if st.button("Next ▶", key="next_page") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()

    # Calculate slice for current page
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_bullets = filtered_bullets[start_idx:end_idx]

    # Bulk selection
    if st.checkbox("Enable bulk actions", key="bulk_mode"):
        st.info("Check bullets below to select for bulk approve/reject")

        # Bulk action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Bulk Approve Selected", key="bulk_approve"):
                selected_ids = [
                    b["bullet_id"] for b in page_bullets if st.session_state.get(f"select_{b['bullet_id']}", False)
                ]
                if selected_ids:
                    result = api.bulk_approve_bullets(selected_agent, selected_ids)
                    st.success(f"Approved {result['success']} bullets, {result['failure']} failed")
                    st.rerun()
                else:
                    st.warning("No bullets selected")

        with col2:
            if st.button("❌ Bulk Reject Selected", key="bulk_reject"):
                selected_ids = [
                    b["bullet_id"] for b in page_bullets if st.session_state.get(f"select_{b['bullet_id']}", False)
                ]
                if selected_ids:
                    result = api.bulk_reject_bullets(selected_agent, selected_ids)
                    st.success(f"Rejected {result['success']} bullets, {result['failure']} failed")
                    st.rerun()
                else:
                    st.warning("No bullets selected")

        st.divider()

    # Display bullets
    for bullet in page_bullets:
        bullet_id = bullet.get("bullet_id", "unknown")
        content = bullet.get("content", "")
        category = bullet.get("category", "uncategorized")
        effectiveness = bullet.get("effectiveness", 0.0)
        usage_count = bullet.get("usage_count", 0)
        status = bullet.get("status", "active")
        added_date = bullet.get("added_date")

        # Parse added date
        try:
            if added_date:
                dt = datetime.fromisoformat(added_date)
                date_str = dt.strftime("%Y-%m-%d")
            else:
                date_str = "Unknown"
        except:
            date_str = "Unknown"

        # Effectiveness color coding
        if effectiveness >= 0.7:
            effectiveness_color = "🟢"
        elif effectiveness >= 0.3:
            effectiveness_color = "🟡"
        else:
            effectiveness_color = "🔴"

        # Status badge
        status_badge = {"active": "✅", "pending": "⏳", "archived": "🗄️"}.get(status, "❓")

        # Bulk selection checkbox (if enabled)
        if st.session_state.get("bulk_mode", False):
            st.checkbox(f"Select", key=f"select_{bullet_id}", label_visibility="collapsed")

        # Bullet card
        with st.expander(f"{effectiveness_color} {status_badge} {content[:80]}..." if len(content) > 80 else content):
            st.markdown(f"**Full Content**: {content}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Category**: {category}")
                st.markdown(f"**Effectiveness**: {effectiveness:.2f} {effectiveness_color}")

            with col2:
                st.markdown(f"**Usage Count**: {usage_count}")
                st.markdown(f"**Added**: {date_str}")
                st.markdown(f"**Status**: {status} {status_badge}")

            # Metadata
            metadata = bullet.get("metadata", {})
            if metadata:
                st.caption(f"Metadata: {metadata}")

            st.divider()

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if status != "active":
                    if st.button(f"✅ Approve", key=f"approve_{bullet_id}"):
                        if api.approve_bullet(selected_agent, bullet_id):
                            st.success("Bullet approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve bullet")

            with col2:
                if status != "archived":
                    if st.button(f"❌ Reject", key=f"reject_{bullet_id}"):
                        if api.reject_bullet(selected_agent, bullet_id):
                            st.success("Bullet rejected!")
                            st.rerun()
                        else:
                            st.error("Failed to reject bullet")

            with col3:
                st.caption(f"ID: {bullet_id}")

st.divider()

# Visualizations section
st.subheader("📊 Playbook Analytics")

# Use tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Category Distribution", "Effectiveness Distribution", "Status Breakdown"])

with tab1:
    # Category distribution pie chart
    category_counts = {}
    for bullet in bullets:
        cat = bullet.get("category", "uncategorized")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    if category_counts:
        fig = px.pie(
            names=list(category_counts.keys()),
            values=list(category_counts.values()),
            title=f"Bullets by Category ({sum(category_counts.values())} total)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")

with tab2:
    # Effectiveness histogram
    effectiveness_values = [b.get("effectiveness", 0) for b in bullets]

    if effectiveness_values:
        fig = px.histogram(
            x=effectiveness_values,
            nbins=20,
            title="Effectiveness Distribution",
            labels={"x": "Effectiveness", "y": "Count"},
        )
        fig.add_vline(x=0.7, line_dash="dash", line_color="green", annotation_text="High (0.7+)")
        fig.add_vline(x=0.3, line_dash="dash", line_color="orange", annotation_text="Low (0.3-)")
        st.plotly_chart(fig, use_container_width=True)

        # Effectiveness stats
        col1, col2, col3 = st.columns(3)

        with col1:
            high_eff = len([e for e in effectiveness_values if e >= 0.7])
            st.metric("High Effectiveness (≥0.7)", high_eff, f"{int(high_eff/len(effectiveness_values)*100)}%")

        with col2:
            med_eff = len([e for e in effectiveness_values if 0.3 <= e < 0.7])
            st.metric("Medium (0.3-0.7)", med_eff, f"{int(med_eff/len(effectiveness_values)*100)}%")

        with col3:
            low_eff = len([e for e in effectiveness_values if e < 0.3])
            st.metric("Low Effectiveness (<0.3)", low_eff, f"{int(low_eff/len(effectiveness_values)*100)}%")
    else:
        st.info("No effectiveness data available")

with tab3:
    # Status breakdown
    status_counts = {"active": 0, "pending": 0, "archived": 0}
    for bullet in bullets:
        status = bullet.get("status", "active")
        status_counts[status] = status_counts.get(status, 0) + 1

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                marker_color=["green", "orange", "gray"],
            )
        ]
    )
    fig.update_layout(title="Bullets by Status", xaxis_title="Status", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Curation Queue section
st.subheader("⏳ Curation Queue")

curation_queue = api.get_curation_queue(selected_agent)

if not curation_queue:
    st.success("No bullets pending curation! 🎉")
else:
    st.warning(f"{len(curation_queue)} bullets awaiting review")

    for bullet in curation_queue[:10]:  # Show first 10
        bullet_id = bullet.get("bullet_id", "unknown")
        content = bullet.get("content", "")
        effectiveness = bullet.get("effectiveness", 0.0)

        with st.container():
            st.markdown(f"**{content[:100]}**..." if len(content) > 100 else f"**{content}**")
            st.caption(f"Effectiveness: {effectiveness:.2f}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"✅ Quick Approve", key=f"queue_approve_{bullet_id}"):
                    if api.approve_bullet(selected_agent, bullet_id):
                        st.success("Approved!")
                        st.rerun()

            with col2:
                if st.button(f"❌ Quick Reject", key=f"queue_reject_{bullet_id}"):
                    if api.reject_bullet(selected_agent, bullet_id):
                        st.success("Rejected!")
                        st.rerun()

            st.divider()

    if len(curation_queue) > 10:
        st.info(f"Showing 10 of {len(curation_queue)} pending bullets. Use filters above to see more.")

st.divider()

# Help section
with st.expander("ℹ️ About Playbook Management"):
    st.markdown(
        """
### Playbook Management

This page allows you to:

1. **Browse Bullets**: View all playbook bullets with rich metadata
2. **Search & Filter**: Find specific bullets by content, category, effectiveness, or status
3. **Curate Content**: Approve or reject bullets individually or in bulk
4. **Visualize Data**: Understand playbook health through interactive charts
5. **Manage Queue**: Quickly process pending bullets awaiting review

### Bullet Status

- **Active** (✅): Bullet is actively used by the agent
- **Pending** (⏳): Bullet awaits curation/approval
- **Archived** (🗄️): Bullet has been rejected or deprecated

### Effectiveness Scores

- **🟢 High (≥0.7)**: Highly effective, proven behaviors
- **🟡 Medium (0.3-0.7)**: Moderately effective, needs monitoring
- **🔴 Low (<0.3)**: Low effectiveness, consider rejecting

### Tips

- Use bulk actions for efficient curation of multiple bullets
- Sort by effectiveness to identify low-performing bullets
- Filter by "pending" status to focus on curation queue
- Search for specific topics to review related bullets together
- Check category distribution to identify knowledge gaps
"""
    )
