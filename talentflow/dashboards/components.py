"""Reusable Streamlit and Plotly UI components for TalentFlow."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Enterprise color palette (Elastic / modern enterprise teal, slate, amber, coral)
COLORS = {
    "primary": "#005571",     # Deep Elastic Teal
    "secondary": "#00A9E0",   # Bright Cyan/Sky
    "accent": "#F04E98",      # Pink Accent
    "success": "#00BFB3",     # Mint Green
    "warning": "#FEC514",     # Golden Yellow
    "danger": "#BD271E",      # Crimson Coral
    "slate": "#343741",       # Charcoal Slate
    "card_bg": "#FFFFFF",
    "text": "#1A1C21",
}

def apply_custom_css():
    """Injects modern, responsive corporate enterprise styling."""
    st.markdown("""
    <style>
        /* General layout and typography */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 95%;
        }
        
        /* Metric Card styling */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E1E4EA;
            border-radius: 10px;
            padding: 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .metric-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: #69707D;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }
        .metric-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #1A1C21;
            margin-bottom: 0.2rem;
        }
        .metric-subtitle {
            font-size: 0.8rem;
            color: #8C94A0;
        }
        
        /* Section Header badge */
        .badge-header {
            display: inline-block;
            background: #EBF8FF;
            color: #007799;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, subtitle: str = ""):
    """Renders a styled corporate metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def create_plotly_funnel(stages: list[dict]) -> go.Figure:
    """Generates an interactive recruiting funnel chart."""
    df = pd.DataFrame(stages)
    fig = go.Figure(go.Funnel(
        y=df["stage"],
        x=df["candidates"],
        textinfo="value+percent previous+percent initial",
        marker={"color": [COLORS["primary"], COLORS["secondary"], "#17A2B8", COLORS["success"], COLORS["warning"], "#28A745"]},
        connector={"line": {"color": "#C4C9D4", "width": 1.5}},
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=13),
    )
    return fig
