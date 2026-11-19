"""Reusable Streamlit and Plotly UI components for TalentFlow Analytics."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

# Cloud-native enterprise SaaS color palette
COLORS = {
    "primary": "#0F172A",       # Dark Slate / Navy
    "secondary": "#0284C7",     # Enterprise Sky Blue
    "accent": "#6366F1",        # Indigo Accent
    "success": "#10B981",       # Emerald Green
    "warning": "#F59E0B",       # Amber
    "danger": "#F43F5E",        # Crimson Coral
    "slate": "#475569",         # Muted Slate
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text": "#0F172A",
}

def apply_custom_css():
    """Injects modern, responsive corporate SaaS styling."""
    st.markdown("""
    <style>
        /* Modern typography & layout */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
            max-width: 95%;
        }

        /* SaaS Metric Card */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            margin-bottom: 0.8rem;
            transition: all 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
            border-color: #CBD5E1;
        }
        .metric-title {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }
        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
            margin-bottom: 0.2rem;
        }
        .metric-subtitle {
            font-size: 0.78rem;
            color: #94A3B8;
        }

        /* Module Badge Header */
        .badge-header {
            display: inline-block;
            background: #E0F2FE;
            color: #0369A1;
            padding: 3px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.5rem;
        }

        /* Filter active badge */
        .filter-status-bar {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.82rem;
            color: #475569;
            margin-bottom: 1rem;
        }

        /* Table container styling */
        .stDataFrame {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, subtitle: str = ""):
    """Renders a styled SaaS metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_active_filter_bar(filters: Dict[str, Any]):
    """Displays an active filter status indicator across views."""
    active_labels = []
    if filters.get("departments"):
        active_labels.append(f"Departments ({len(filters['departments'])})")
    if filters.get("sources"):
        active_labels.append(f"Sources ({len(filters['sources'])})")
    if filters.get("job_levels"):
        active_labels.append(f"Levels ({len(filters['job_levels'])})")
    
    status_text = " • ".join(active_labels) if active_labels else "All Data (No Filters Applied)"
    st.markdown(f"""
    <div class="filter-status-bar">
        ⚡ <b>Filter Scope:</b> {status_text}
    </div>
    """, unsafe_allow_html=True)

def create_plotly_funnel(stages: List[Dict[str, Any]]) -> go.Figure:
    """Generates an interactive recruiting funnel chart."""
    df = pd.DataFrame(stages)
    colors = [COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["success"], COLORS["warning"], "#059669"]
    fig = go.Figure(go.Funnel(
        y=df["stage"],
        x=df["candidates"],
        textinfo="value+percent previous+percent initial",
        marker={"color": colors[:len(stages)]},
        connector={"line": {"color": "#CBD5E1", "width": 1.5}},
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=13),
    )
    return fig
