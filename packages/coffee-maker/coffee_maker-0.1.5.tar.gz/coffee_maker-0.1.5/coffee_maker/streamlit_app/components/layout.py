"""Layout components for consistent UI across the ACE Streamlit App."""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager


def load_css() -> None:
    """Load custom CSS styling for the app."""
    css_path = Path(__file__).parent.parent / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found. Using default styling.")


def page_header(title: str, subtitle: Optional[str] = None, icon: str = "📊") -> None:
    """
    Render a consistent page header with gradient background.

    Args:
        title: Main heading text
        subtitle: Optional subtitle text
        icon: Emoji icon to display before title
    """
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""

    st.markdown(
        f"""
    <div class="main-header">
        <h1>{icon} {title}</h1>
        {subtitle_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📈",
    card_class: str = "metric-card",
) -> None:
    """
    Render a styled metric card.

    Args:
        label: Metric label
        value: Metric value (formatted as string)
        delta: Optional change indicator
        icon: Emoji icon
        card_class: CSS class for styling (metric-card, info-card, etc.)
    """
    delta_html = f'<div style="color: #4CAF50; font-size: 0.8rem; margin-top: 0.25rem;">{delta}</div>' if delta else ""

    st.markdown(
        f"""
    <div class="{card_class}">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{icon} {label}</div>
        <div style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
        {delta_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


@contextmanager
def loading_spinner(message: str = "Loading..."):
    """
    Show a loading spinner with custom message.

    Usage:
        with loading_spinner("Loading data..."):
            # Your slow operation here
            pass
    """
    with st.spinner(message):
        yield


def success_message(message: str, icon: str = "✅") -> None:
    """Show a success notification."""
    st.success(f"{icon} {message}")


def error_message(message: str, icon: str = "❌") -> None:
    """Show an error notification."""
    st.error(f"{icon} {message}")


def warning_message(message: str, icon: str = "⚠️") -> None:
    """Show a warning notification."""
    st.warning(f"{icon} {message}")


def info_message(message: str, icon: str = "ℹ️") -> None:
    """Show an info notification."""
    st.info(f"{icon} {message}")


def render_metric_row(metrics: list[Dict[str, Any]], columns: Optional[int] = None) -> None:
    """
    Render a row of metrics using st.columns.

    Args:
        metrics: List of metric dicts with keys: label, value, delta, icon
        columns: Number of columns (defaults to len(metrics))

    Example:
        render_metric_row([
            {"label": "Total", "value": "100", "delta": "+10", "icon": "📊"},
            {"label": "Active", "value": "85", "delta": "+5", "icon": "🟢"},
        ])
    """
    n_cols = columns or len(metrics)
    cols = st.columns(n_cols)

    for col, metric in zip(cols, metrics):
        with col:
            st.metric(
                label=f"{metric.get('icon', '📊')} {metric['label']}",
                value=metric["value"],
                delta=metric.get("delta"),
            )


def render_card_section(
    title: str,
    content: str,
    card_type: str = "info",
    icon: str = "ℹ️",
) -> None:
    """
    Render a styled card section.

    Args:
        title: Card title
        content: Card content (markdown supported)
        card_type: Type of card (info, success, warning, danger)
        icon: Emoji icon
    """
    card_class = f"{card_type}-card"

    st.markdown(
        f"""
    <div class="{card_class}">
        <h3>{icon} {title}</h3>
        <div>{content}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def empty_state(
    message: str = "No data available",
    icon: str = "📭",
    suggestion: Optional[str] = None,
) -> None:
    """
    Display an empty state when no data is available.

    Args:
        message: Main message to display
        icon: Emoji icon
        suggestion: Optional suggestion text
    """
    suggestion_html = f"<p style='color: #666; margin-top: 0.5rem;'>{suggestion}</p>" if suggestion else ""

    st.markdown(
        f"""
    <div style="text-align: center; padding: 3rem 1rem; color: #999;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: #666;">{message}</h3>
        {suggestion_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


def page_footer() -> None:
    """Render a consistent page footer."""
    st.divider()
    st.markdown(
        """
    <div style="text-align: center; color: #999; font-size: 0.85rem; padding: 1rem 0;">
        ACE Framework Dashboard • Powered by Streamlit
    </div>
    """,
        unsafe_allow_html=True,
    )
