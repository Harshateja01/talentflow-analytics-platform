"""Module 4: Workforce Analytics."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_department_metrics,
    get_cached_workforce_demographics,
)
from talentflow.dashboards.components import render_metric_card, render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    job_levels = filters.get("job_levels")

    st.markdown('<span class="badge-header">Headcount Planning & Org Demographics</span>', unsafe_allow_html=True)
    st.title("Workforce Analytics")
    st.markdown("Monitor organizational composition, geographic footprint, career ladder distribution, and department scale.")

    render_active_filter_bar(filters)

    queries = get_shared_analytics_queries()
    dept_df = get_cached_department_metrics(departments=depts)
    demo_df = get_cached_workforce_demographics(departments=depts, job_levels=job_levels)

    if dept_df.empty:
        st.warning("No workforce metrics found matching the selected criteria.")
        return

    total_active = dept_df["active_headcount"].sum()
    total_attr = dept_df["total_attrition"].sum()
    overall_attr_rate = round(total_attr * 100.0 / (total_active + total_attr), 1) if (total_active + total_attr) > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Active Workforce", f"{int(total_active):,}", "Active employee headcount")
    with c2:
        render_metric_card("Overall Turnover Rate", f"{overall_attr_rate}%", f"{int(total_attr):,} historic exits")
    with c3:
        render_metric_card("Primary Department", f"{dept_df.iloc[0]['department_name']}", f"{int(dept_df.iloc[0]['active_headcount'])} active employees")
    with c4:
        render_metric_card("Average Tenure", f"{round(dept_df['avg_tenure_months'].mean(), 1)} mo", "Across active workforce")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Headcount by Geographic Hub")
        if not demo_df.empty:
            loc_summary = demo_df.groupby("location")["active_count"].sum().reset_index()
            fig_loc = px.pie(
                loc_summary,
                names="location",
                values="active_count",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_loc.update_traces(textposition='inside', textinfo='percent+label')
            fig_loc.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_loc, use_container_width=True)

    with col2:
        st.subheader("Headcount by Career Ladder Level")
        if not demo_df.empty:
            level_summary = demo_df.groupby("job_level")["active_count"].sum().reset_index()
            fig_level = px.bar(
                level_summary,
                x="job_level",
                y="active_count",
                color="job_level",
                text_auto=True,
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig_level.update_layout(showlegend=False, xaxis_title="", yaxis_title="Active Headcount", height=350, xaxis_tickangle=-25)
            st.plotly_chart(fig_level, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Active Workforce by Department")
        fig_dept_active = px.bar(
            dept_df,
            x="department_name",
            y="active_headcount",
            color="active_headcount",
            color_continuous_scale="Teal",
            text_auto=True,
        )
        fig_dept_active.update_layout(showlegend=False, xaxis_title="", height=320)
        st.plotly_chart(fig_dept_active, use_container_width=True)

    with col4:
        st.subheader("Tenure Band Distribution")
        if not demo_df.empty:
            tenure_summary = demo_df.groupby("tenure_band")["active_count"].sum().reset_index()
            band_order = ["< 3 Months", "3 - 6 Months", "6 - 12 Months", "1 - 2 Years", "2+ Years"]
            tenure_summary["order"] = tenure_summary["tenure_band"].map(lambda x: band_order.index(x) if x in band_order else 99)
            tenure_summary = tenure_summary.sort_values(by="order")

            fig_tenure = px.bar(
                tenure_summary,
                x="tenure_band",
                y="active_count",
                color="tenure_band",
                text_auto=True,
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            fig_tenure.update_layout(showlegend=False, xaxis_title="", yaxis_title="Active Employees", height=320)
            st.plotly_chart(fig_tenure, use_container_width=True)
