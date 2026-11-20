"""Module 1: Executive Overview Dashboard."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_executive_kpis,
    get_cached_monthly_hiring_trends,
    get_cached_department_metrics,
)
from talentflow.dashboards.components import render_metric_card, render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    sources = filters.get("sources")

    st.markdown('<span class="badge-header">Executive Leadership & Strategy</span>', unsafe_allow_html=True)
    st.title("Executive Overview")
    st.markdown("High-level executive scorecard connecting recruitment velocity with workforce composition and organizational stability.")

    render_active_filter_bar(filters)

    queries = get_shared_analytics_queries()
    kpis = get_cached_executive_kpis(departments=depts, sources=sources)

    if not kpis:
        st.warning("No warehouse data found matching the selected criteria. Adjust your filters or run the data pipeline.")
        return

    # Top KPI Metrics Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_metric_card("Total Applications", f"{int(kpis.get('total_applications', 0)):,}", "All channels")
    with c2:
        render_metric_card("Total Hires", f"{int(kpis.get('total_hires', 0)):,}", "Signed offers")
    with c3:
        render_metric_card("Avg Time to Hire", f"{kpis.get('avg_time_to_hire_days', 0)}d", "App to hire date")
    with c4:
        render_metric_card("Offer Acceptance", f"{kpis.get('offer_acceptance_rate_pct', 0)}%", f"Of {int(kpis.get('total_offers', 0)):,} offers")
    with c5:
        render_metric_card("Active Headcount", f"{int(kpis.get('active_headcount', 0)):,}", "Current workforce")
    with c6:
        render_metric_card("Attrition Rate", f"{kpis.get('attrition_rate_pct', 0)}%", f"{int(kpis.get('total_attrition', 0)):,} total exits")

    st.markdown("---")

    # Trend Visualizations
    col_left, col_right = st.columns([7, 5])
    monthly_df = get_cached_monthly_hiring_trends(departments=depts, sources=sources)

    with col_left:
        st.subheader("Monthly Application & Hiring Velocity")
        if not monthly_df.empty:
            fig_trends = go.Figure()
            fig_trends.add_trace(go.Bar(
                x=monthly_df["application_month"],
                y=monthly_df["applications"],
                name="Applications Inflow",
                marker_color="#CBD5E1",
                yaxis="y",
            ))
            fig_trends.add_trace(go.Scatter(
                x=monthly_df["application_month"],
                y=monthly_df["hires"],
                name="Completed Hires",
                line=dict(color=COLORS["secondary"], width=3),
                mode="lines+markers",
                yaxis="y2",
            ))
            fig_trends.update_layout(
                yaxis=dict(title="Applications", showgrid=True),
                yaxis2=dict(title="Hires", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_trends, use_container_width=True)

    with col_right:
        st.subheader("Hiring Cycle Latency Trend (Days)")
        if not monthly_df.empty:
            fig_cycle = px.line(
                monthly_df,
                x="application_month",
                y="avg_time_to_hire_days",
                markers=True,
                line_shape="spline",
                color_discrete_sequence=[COLORS["accent"]],
            )
            fig_cycle.update_layout(
                yaxis_title="Average Days",
                xaxis_title="",
                margin=dict(l=20, r=20, t=30, b=20),
                height=360,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_cycle, use_container_width=True)

    # Department Scorecard
    st.subheader("Department Workforce Health Scorecard")
    dept_df = get_cached_department_metrics(departments=depts)
    if not dept_df.empty:
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            fig_headcount = px.bar(
                dept_df,
                x="department_name",
                y="active_headcount",
                title="Active Headcount by Department",
                color="department_name",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_headcount.update_layout(showlegend=False, xaxis_title="", height=300)
            st.plotly_chart(fig_headcount, use_container_width=True)

        with c_chart2:
            fig_attr = px.bar(
                dept_df,
                x="department_name",
                y="historic_attrition_rate_pct",
                title="Annualized Attrition Rate (%) by Department",
                color="historic_attrition_rate_pct",
                color_continuous_scale="Reds",
                text_auto=True,
            )
            fig_attr.update_layout(showlegend=False, xaxis_title="", height=300)
            st.plotly_chart(fig_attr, use_container_width=True)

        st.dataframe(
            dept_df[[
                "department_name", "department_lead", "cost_center", "active_headcount",
                "total_historic_hires", "total_attrition", "historic_attrition_rate_pct",
                "avg_tenure_months", "avg_department_engagement"
            ]].rename(columns={
                "department_name": "Department",
                "department_lead": "Executive Lead",
                "cost_center": "Cost Center",
                "active_headcount": "Active Headcount",
                "total_historic_hires": "Total Hires",
                "total_attrition": "Attrition Exits",
                "historic_attrition_rate_pct": "Attrition %",
                "avg_tenure_months": "Avg Tenure (Mo)",
                "avg_department_engagement": "Avg Engagement (1-5)",
            }),
            use_container_width=True,
            hide_index=True,
        )
