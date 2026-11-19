"""Page 3: Recruiting Source Analysis."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.analytics.queries import AnalyticsQueries
from talentflow.analytics.kpis import KPIService
from talentflow.dashboards.components import render_metric_card, COLORS

def render():
    st.markdown('<span class="badge-header">Channel Economics & Sourcing Strategy</span>', unsafe_allow_html=True)
    st.title("Recruiting Source Performance & ROI")
    st.markdown("Evaluates which acquisition channels deliver top performers, high conversion rates, and sustainable cost per hire.")

    queries = AnalyticsQueries()
    source_df = queries.get_source_performance()

    if source_df.empty:
        st.warning("No recruiting source data available.")
        return

    source_enriched = KPIService.calculate_source_roi(source_df)

    # Highlighted Cards
    top_vol = source_df.sort_values(by="total_hires", ascending=False).iloc[0]
    top_conv = source_df.sort_values(by="app_to_hire_conversion_pct", ascending=False).iloc[0]
    best_ret = source_df.sort_values(by="employee_churn_rate_pct", ascending=True).iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Highest Volume Channel", f"{top_vol['source_name']}", f"{int(top_vol['total_hires']):,} hires ({int(top_vol['total_applications']):,} applications)")
    with c2:
        render_metric_card("Highest Conversion Rate", f"{top_conv['source_name']}", f"{top_conv['app_to_hire_conversion_pct']}% application-to-hire rate")
    with c3:
        render_metric_card("Lowest Employee Churn", f"{best_ret['source_name']}", f"{best_ret['employee_churn_rate_pct']}% historic churn rate")

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
            marker_color=COLORS["primary"],
        ))
        fig_vol.update_layout(barmode="group", xaxis_tickangle=-25, height=360, margin=dict(t=20, b=40))
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        st.subheader("Conversion Efficiency & Offer Acceptance")
        fig_conv = px.scatter(
            source_df,
            x="app_to_hire_conversion_pct",
            y="offer_acceptance_rate_pct",
            size="total_hires",
            color="source_name",
            hover_name="source_name",
            title="App-to-Hire Conversion vs. Offer Acceptance Rate",
            labels={
                "app_to_hire_conversion_pct": "App-to-Hire Conversion %",
                "offer_acceptance_rate_pct": "Offer Acceptance %",
            },
        )
        fig_conv.update_layout(height=360, showlegend=False)
        st.plotly_chart(fig_conv, use_container_width=True)

    # Secondary Row: Time to hire by source & Cost
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Average Days to Hire by Channel")
        fig_tth = px.bar(
            source_df.sort_values(by="avg_time_to_hire_days"),
            x="avg_time_to_hire_days",
            y="source_name",
            orientation="h",
            color="avg_time_to_hire_days",
            color_continuous_scale="Teal",
            text_auto=True,
        )
        fig_tth.update_layout(showlegend=False, yaxis_title="", xaxis_title="Days to Hire", height=320)
        st.plotly_chart(fig_tth, use_container_width=True)

    with col4:
        st.subheader("Candidate Experience Rating (1-5)")
        fig_exp = px.bar(
            source_df.sort_values(by="avg_candidate_experience_rating", ascending=False),
            x="source_name",
            y="avg_candidate_experience_rating",
            color="avg_candidate_experience_rating",
            color_continuous_scale="Blues",
            text_auto=True,
        )
        fig_exp.update_layout(showlegend=False, xaxis_title="", yaxis_title="Feedback Score", height=320, xaxis_tickangle=-25)
        st.plotly_chart(fig_exp, use_container_width=True)

    # Detailed Table
    st.subheader("Complete Sourcing Channel Scorecard")
    st.dataframe(
        source_df[[
            "source_name", "source_channel", "cost_per_posting", "total_applications",
            "total_hires", "app_to_hire_conversion_pct", "offer_acceptance_rate_pct",
            "avg_time_to_hire_days", "employee_churn_rate_pct", "avg_employee_tenure_months"
        ]].rename(columns={
            "source_name": "Recruiting Source",
            "source_channel": "Channel Type",
            "cost_per_posting": "Cost/Post ($)",
            "total_applications": "Applications",
            "total_hires": "Hires",
            "app_to_hire_conversion_pct": "Conversion %",
            "offer_acceptance_rate_pct": "Offer Accept %",
            "avg_time_to_hire_days": "Avg Time-to-Hire (d)",
            "employee_churn_rate_pct": "Churn %",
            "avg_employee_tenure_months": "Avg Tenure (Mo)",
        }),
        use_container_width=True,
        hide_index=True,
    )
