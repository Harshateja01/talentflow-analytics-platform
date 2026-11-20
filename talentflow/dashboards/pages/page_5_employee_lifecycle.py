"""Module 5: Employee Lifecycle Analytics."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_source_performance,
    get_cached_engagement_by_tenure,
)
from talentflow.dashboards.components import render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    sources = filters.get("sources")

    st.markdown('<span class="badge-header">Employee Journey & Experience</span>', unsafe_allow_html=True)
    st.title("Employee Lifecycle Analytics")
    st.markdown("Connect upstream recruitment attributes with downstream employee tenure, compensation trajectory, and workplace engagement sentiment.")

    render_active_filter_bar(filters)

    queries = get_shared_analytics_queries()
    source_df = get_cached_source_performance(departments=depts, sources=sources)
    tenure_eng_df = get_cached_engagement_by_tenure(departments=depts)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1-Year Employee Retention (%) by Acquisition Channel")
        if not source_df.empty:
            source_df["retention_pct"] = 100.0 - source_df["employee_churn_rate_pct"]
            fig_ret = px.bar(
                source_df.sort_values(by="retention_pct", ascending=False),
                x="source_name",
                y="retention_pct",
                color="retention_pct",
                color_continuous_scale="Viridis",
                text_auto=True,
                labels={"retention_pct": "Retention Rate (%)", "source_name": "Sourcing Channel"},
            )
            fig_ret.update_layout(showlegend=False, xaxis_title="", height=330, xaxis_tickangle=-25)
            st.plotly_chart(fig_ret, use_container_width=True)

    with col2:
        st.subheader("Workplace Engagement Score by Acquisition Channel")
        if not source_df.empty:
            fig_src_eng = px.bar(
                source_df.sort_values(by="avg_employee_engagement", ascending=False),
                x="source_name",
                y="avg_employee_engagement",
                color="avg_employee_engagement",
                color_continuous_scale="Teal",
                text_auto=True,
                labels={"avg_employee_engagement": "Engagement Rating (1–5)", "source_name": "Sourcing Channel"},
            )
            fig_src_eng.update_layout(showlegend=False, xaxis_title="", height=330, xaxis_tickangle=-25)
            st.plotly_chart(fig_src_eng, use_container_width=True)

    # Multi-dimensional Engagement by Tenure Band
    st.subheader("Survey Sentiment Profile Across Employee Tenure Bands")
    if not tenure_eng_df.empty:
        fig_radar = go.Figure()
        
        dimensions = [
            ("avg_engagement", "Overall Engagement"),
            ("avg_satisfaction", "Job Satisfaction"),
            ("avg_work_life_balance", "Work-Life Balance"),
            ("avg_career_growth", "Career Growth"),
            ("avg_manager_effectiveness", "Manager Effectiveness"),
        ]

        for _, row in tenure_eng_df.iterrows():
            vals = [row[dim[0]] for dim in dimensions]
            vals.append(vals[0])  # close the loop
            categories = [dim[1] for dim in dimensions]
            categories.append(categories[0])
            
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=categories,
                name=row["tenure_band"],
                mode="lines+markers",
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1.5, 5.0])),
            height=400,
            margin=dict(t=20, b=20, l=40, r=40),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.dataframe(
            tenure_eng_df.rename(columns={
                "tenure_band": "Tenure Cohort",
                "sample_size": "Survey Respondents",
                "avg_engagement": "Overall Engagement",
                "avg_satisfaction": "Job Satisfaction",
                "avg_work_life_balance": "Work-Life Balance",
                "avg_career_growth": "Career Growth",
                "avg_manager_effectiveness": "Manager Effectiveness",
            }),
            use_container_width=True,
            hide_index=True,
        )
