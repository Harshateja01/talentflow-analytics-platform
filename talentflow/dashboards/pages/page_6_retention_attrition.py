"""Module 6: Retention & Attrition Intelligence."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_department_metrics,
    get_cached_attrition_analysis,
)
from talentflow.dashboards.components import render_metric_card, render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    sources = filters.get("sources")
    job_levels = filters.get("job_levels")

    st.markdown('<span class="badge-header">Retention Diagnostics & Turnover Risk</span>', unsafe_allow_html=True)
    st.title("Retention & Attrition Intelligence")
    st.markdown("Examine turnover patterns, departure timing horizons, exit engagement indicators, and cohort longevity.")

    render_active_filter_bar(filters)

    # Scientific Methodology Notice on Correlation vs. Causation
    st.info("""
    **Analytical Methodology Notice: Correlation vs. Causation**  
    Observed associations between recruitment origin, department turnover, and tenure represent statistical correlations within historic cohorts.
    *Example:* While internal referrals correlate with higher 1-year retention, sourcing channel alone does not cause employee longevity; factors such as onboarding quality, team leadership, role expectation alignment, and market compensation contribute significantly to retention.
    """)

    queries = get_shared_analytics_queries()
    dept_df = get_cached_department_metrics(departments=depts)
    attr_df = get_cached_attrition_analysis(departments=depts, sources=sources, job_levels=job_levels)

    if attr_df.empty:
        st.warning("No attrition records found matching the active filter criteria.")
        return

    total_exits = attr_df["departures"].sum()
    avg_exit_tenure = round(attr_df["avg_tenure_months"].mean(), 1)
    avg_pre_exit_eng = round(attr_df["avg_engagement_before_exit"].dropna().mean(), 2)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Total Departures", f"{int(total_exits):,}", "Recorded employee exits")
    with c2:
        render_metric_card("Average Exit Tenure", f"{avg_exit_tenure} mo", "Average lifespan at company")
    with c3:
        render_metric_card("Pre-Exit Engagement", f"{avg_pre_exit_eng} / 5.0", "Prior survey sentiment")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Departure Timing Risk Segmentation")
        seg_summary = attr_df.groupby("attrition_risk_segment")["departures"].sum().reset_index()
        fig_seg = px.pie(
            seg_summary,
            names="attrition_risk_segment",
            values="departures",
            hole=0.45,
            color_discrete_sequence=["#F43F5E", "#FB923C", "#FBBF24", "#94A3B8"],
        )
        fig_seg.update_traces(textposition='inside', textinfo='percent+label')
        fig_seg.update_layout(height=340, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_seg, use_container_width=True)

    with col2:
        st.subheader("Exits by Department & Sourcing Channel")
        dept_exit = attr_df.groupby(["department_name", "recruiting_source"])["departures"].sum().reset_index()
        fig_dept_exit = px.bar(
            dept_exit,
            x="department_name",
            y="departures",
            color="recruiting_source",
            title="Departures by Department & Sourcing Origin",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_dept_exit.update_layout(xaxis_title="", height=340)
        st.plotly_chart(fig_dept_exit, use_container_width=True)

    st.subheader("Turnover Risk Segments Table")
    st.dataframe(
        attr_df[[
            "department_name", "recruiting_source", "job_level", "attrition_type",
            "attrition_risk_segment", "departures", "avg_tenure_months", "avg_engagement_before_exit"
        ]].rename(columns={
            "department_name": "Department",
            "recruiting_source": "Source Origin",
            "job_level": "Job Level",
            "attrition_type": "Exit Type",
            "attrition_risk_segment": "Risk Segment",
            "departures": "Exits",
            "avg_tenure_months": "Avg Tenure (Mo)",
            "avg_engagement_before_exit": "Pre-Exit Engagement (1–5)",
        }),
        use_container_width=True,
        hide_index=True,
    )
