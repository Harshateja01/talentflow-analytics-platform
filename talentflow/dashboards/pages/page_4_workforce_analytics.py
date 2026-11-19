"""Page 4: Workforce Analytics."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.analytics.queries import AnalyticsQueries
from talentflow.dashboards.components import render_metric_card, COLORS

def render():
    st.markdown('<span class="badge-header">Workforce Composition & Headcount Planning</span>', unsafe_allow_html=True)
    st.title("Workforce Demographics & Retention Analytics")
    st.markdown("Deep dive into organizational structure, geographic distribution, tenure bands, and department attrition.")

    queries = AnalyticsQueries()
    dept_df = queries.get_department_metrics()
    demo_df = queries.get_workforce_demographics()
    attr_df = queries.get_attrition_analysis()

    if dept_df.empty:
        st.warning("No workforce metrics found.")
        return

    total_active = dept_df["active_headcount"].sum()
    total_attr = dept_df["total_attrition"].sum()
    overall_attr_rate = round(total_attr * 100.0 / (total_active + total_attr), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Active Workforce", f"{int(total_active):,}", "Full-time employees")
    with c2:
        render_metric_card("Overall Attrition Rate", f"{overall_attr_rate}%", f"{int(total_attr):,} historic exits")
    with c3:
        render_metric_card("Largest Org Unit", f"{dept_df.iloc[0]['department_name']}", f"{int(dept_df.iloc[0]['active_headcount'])} employees")
    with c4:
        render_metric_card("Average Tenure", f"{round(dept_df['avg_tenure_months'].mean(), 1)} mo", "Across all departments")

    st.markdown("---")

    # Headcount Distributions
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
            fig_loc.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_loc, use_container_width=True)

    with col2:
        st.subheader("Tenure Band Distribution")
        if not demo_df.empty:
            tenure_summary = demo_df.groupby("tenure_band")["active_count"].sum().reset_index()
            # Order tenure bands logically
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
            fig_tenure.update_layout(showlegend=False, xaxis_title="", yaxis_title="Active Employees", height=360)
            st.plotly_chart(fig_tenure, use_container_width=True)

    # Department Retention & Attrition Breakdown
    st.subheader("Department Turnover Breakdown")
    col3, col4 = st.columns(2)
    with col3:
        fig_attr_bars = px.bar(
            dept_df,
            x="department_name",
            y=["active_headcount", "total_attrition"],
            title="Active vs. Departed Employees by Department",
            barmode="stack",
            color_discrete_map={"active_headcount": COLORS["primary"], "total_attrition": COLORS["danger"]},
            labels={"value": "Headcount", "variable": "Status"},
        )
        fig_attr_bars.update_layout(xaxis_title="", height=360)
        st.plotly_chart(fig_attr_bars, use_container_width=True)

    with col4:
        st.subheader("Attrition Risk Segments")
        if not attr_df.empty:
            seg_summary = attr_df.groupby("attrition_risk_segment")["departures"].sum().reset_index()
            fig_seg = px.pie(
                seg_summary,
                names="attrition_risk_segment",
                values="departures",
                hole=0.4,
                color_discrete_sequence=["#FF7675", "#FAB1A0", "#FFEAA7", "#DFE6E9"],
            )
            fig_seg.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_seg, use_container_width=True)
