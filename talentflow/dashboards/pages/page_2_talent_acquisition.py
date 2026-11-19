"""Module 2: Talent Acquisition Analytics."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.analytics.queries import AnalyticsQueries
from talentflow.analytics.kpis import KPIService
from talentflow.dashboards.components import render_metric_card, render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    sources = filters.get("sources")

    st.markdown('<span class="badge-header">Channel Economics & Sourcing Strategy</span>', unsafe_allow_html=True)
    st.title("Talent Acquisition Analytics")
    st.markdown("Assess channel efficiency, candidate acquisition costs, offer close rates, and sourcing pipeline quality.")

    render_active_filter_bar(filters)

    queries = AnalyticsQueries()
    source_df = queries.get_source_performance(departments=depts, sources=sources)

    if source_df.empty:
        st.warning("No recruiting source data available for the active filters.")
        return

    source_enriched = KPIService.calculate_source_roi(source_df)

    # Highlight Cards
    top_vol = source_df.sort_values(by="total_hires", ascending=False).iloc[0]
    top_conv = source_df.sort_values(by="app_to_hire_conversion_pct", ascending=False).iloc[0]
    best_churn = source_df.sort_values(by="employee_churn_rate_pct", ascending=True).iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card(
            "Top Volume Channel",
            f"{top_vol['source_name']}",
            f"{int(top_vol['total_hires']):,} hires ({int(top_vol['total_applications']):,} applications)"
        )
    with c2:
        render_metric_card(
            "Top Conversion Channel",
            f"{top_conv['source_name']}",
            f"{top_conv['app_to_hire_conversion_pct']}% application-to-hire rate"
        )
    with c3:
        render_metric_card(
            "Lowest Turnover Source",
            f"{best_churn['source_name']}",
            f"{best_churn['employee_churn_rate_pct']}% historic churn rate"
        )

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Applications vs. Hires by Source")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=source_df["source_name"],
            y=source_df["total_applications"],
            name="Applications",
            marker_color="#CBD5E1",
        ))
        fig_vol.add_trace(go.Bar(
            x=source_df["source_name"],
            y=source_df["total_hires"],
            name="Hires",
            marker_color=COLORS["secondary"],
        ))
        fig_vol.update_layout(
            barmode="group",
            xaxis_tickangle=-25,
            height=350,
            margin=dict(t=20, b=40, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        st.subheader("Conversion Efficiency Matrix")
        fig_conv = px.scatter(
            source_df,
            x="app_to_hire_conversion_pct",
            y="offer_acceptance_rate_pct",
            size="total_hires",
            color="source_name",
            hover_name="source_name",
            title="App-to-Hire Conversion % vs. Offer Acceptance %",
            labels={
                "app_to_hire_conversion_pct": "App-to-Hire Conversion %",
                "offer_acceptance_rate_pct": "Offer Acceptance %",
            },
        )
        fig_conv.update_layout(height=350, showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
        st.plotly_chart(fig_conv, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Hiring Cycle Days by Channel")
        fig_tth = px.bar(
            source_df.sort_values(by="avg_time_to_hire_days"),
            x="avg_time_to_hire_days",
            y="source_name",
            orientation="h",
            color="avg_time_to_hire_days",
            color_continuous_scale="Blues",
            text_auto=True,
        )
        fig_tth.update_layout(showlegend=False, yaxis_title="", xaxis_title="Average Days to Hire", height=320)
        st.plotly_chart(fig_tth, use_container_width=True)

    with col4:
        st.subheader("Candidate Experience Rating (1–5)")
        fig_exp = px.bar(
            source_df.sort_values(by="avg_candidate_experience_rating", ascending=False),
            x="source_name",
            y="avg_candidate_experience_rating",
            color="avg_candidate_experience_rating",
            color_continuous_scale="Teal",
            text_auto=True,
        )
        fig_exp.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average Rating", height=320, xaxis_tickangle=-25)
        st.plotly_chart(fig_exp, use_container_width=True)

    # Detailed Table
    st.subheader("Comprehensive Sourcing Channel Scorecard")
    st.dataframe(
        source_enriched[[
            "source_name", "source_channel", "cost_per_posting", "total_applications",
            "total_hires", "app_to_hire_conversion_pct", "offer_acceptance_rate_pct",
            "avg_time_to_hire_days", "retention_rate_pct", "employee_churn_rate_pct",
            "avg_employee_tenure_months"
        ]].rename(columns={
            "source_name": "Recruiting Channel",
            "source_channel": "Channel Classification",
            "cost_per_posting": "Unit Cost ($)",
            "total_applications": "Applications",
            "total_hires": "Hires",
            "app_to_hire_conversion_pct": "App-to-Hire %",
            "offer_acceptance_rate_pct": "Offer Accept %",
            "avg_time_to_hire_days": "Avg Time to Hire (d)",
            "retention_rate_pct": "1-Yr Retention %",
            "employee_churn_rate_pct": "Turnover %",
            "avg_employee_tenure_months": "Avg Tenure (Mo)",
        }),
        use_container_width=True,
        hide_index=True,
    )
