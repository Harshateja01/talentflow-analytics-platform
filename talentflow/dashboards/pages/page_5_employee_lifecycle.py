"""Page 5: Employee Lifecycle & Sourcing Impact Insights."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.analytics.queries import AnalyticsQueries
from talentflow.dashboards.components import render_metric_card, COLORS

def render():
    st.markdown('<span class="badge-header">Cross-Lifecycle Analytics: Recruitment to Retention</span>', unsafe_allow_html=True)
    st.title("Employee Lifecycle & Retention Cohorts")
    st.markdown("Connecting upstream recruiting source and candidate experience with downstream tenure, retention, and survey engagement.")

    queries = AnalyticsQueries()
    source_df = queries.get_source_performance()
    tenure_eng_df = queries.get_engagement_by_tenure()

    # Important Scientific / Analytics Methodology Banner
    st.info("""
    **Methodology & Governance Notice: Correlation vs. Causation**  
    The associations identified between recruiting sources, job levels, and employee retention reflect observed observational correlations within historical company cohorts. 
    *Example:* While employee referral cohorts demonstrate higher 1-year retention rates, this does not imply that sourcing channel alone causes employee longevity. Factors such as pre-existing network support, team fit, and compensation distribution contribute to these dynamics.
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1-Year Employee Retention (%) by Sourcing Channel")
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
            fig_ret.update_layout(showlegend=False, xaxis_title="", height=340, xaxis_tickangle=-25)
            st.plotly_chart(fig_ret, use_container_width=True)

    with col2:
        st.subheader("Average Employee Engagement by Sourcing Channel")
        if not source_df.empty:
            fig_src_eng = px.bar(
                source_df.sort_values(by="avg_employee_engagement", ascending=False),
                x="source_name",
                y="avg_employee_engagement",
                color="avg_employee_engagement",
                color_continuous_scale="Teal",
                text_auto=True,
                labels={"avg_employee_engagement": "Engagement Score (1-5)", "source_name": "Sourcing Channel"},
            )
            fig_src_eng.update_layout(showlegend=False, xaxis_title="", height=340, xaxis_tickangle=-25)
            st.plotly_chart(fig_src_eng, use_container_width=True)

    # Engagement by Tenure Band
    st.subheader("Workplace Engagement Dimensions Across Tenure Cohorts")
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
            height=420,
            margin=dict(t=30, b=30, l=40, r=40),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.dataframe(
            tenure_eng_df.rename(columns={
                "tenure_band": "Tenure Band",
                "sample_size": "Survey Sample Size",
                "avg_engagement": "Engagement",
                "avg_satisfaction": "Satisfaction",
                "avg_work_life_balance": "Work-Life Balance",
                "avg_career_growth": "Career Growth",
                "avg_manager_effectiveness": "Manager Effectiveness",
            }),
            use_container_width=True,
            hide_index=True,
        )
