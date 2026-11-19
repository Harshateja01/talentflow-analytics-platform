"""Page 2: Recruiting Funnel Analytics."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.analytics.queries import AnalyticsQueries
from talentflow.analytics.kpis import KPIService
from talentflow.dashboards.components import create_plotly_funnel, render_metric_card, COLORS

def render():
    st.markdown('<span class="badge-header">Recruiting Operations & Pipeline Health</span>', unsafe_allow_html=True)
    st.title("Recruiting Funnel & Conversion Analytics")
    st.markdown("Detailed breakdown of candidate progression, conversion hurdles, stage latencies, and drop-off bottlenecks.")

    queries = AnalyticsQueries()
    funnel_summary_df = queries.get_recruiting_funnel_summary()
    stage_duration_df = queries.get_stage_duration_breakdown()

    if funnel_summary_df.empty:
        st.warning("No funnel records available. Please run the data pipeline.")
        return

    funnel_steps = KPIService.calculate_funnel_dropoff(funnel_summary_df)

    # Funnel Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("App to Screen", f"{funnel_steps[1]['stage_conversion_pct']}%", f"{funnel_steps[1]['candidates']:,} candidates passed")
    with c2:
        render_metric_card("Screen to Tech", f"{funnel_steps[2]['stage_conversion_pct']}%", f"{funnel_steps[2]['candidates']:,} candidates passed")
    with c3:
        render_metric_card("Tech to Onsite", f"{funnel_steps[3]['stage_conversion_pct']}%", f"{funnel_steps[3]['candidates']:,} candidates passed")
    with c4:
        render_metric_card("Offer to Hire", f"{funnel_steps[5]['stage_conversion_pct']}%", f"{funnel_steps[5]['candidates']:,} signed hires")

    # Main Funnel Diagram + Bottleneck Callout
    col_chart, col_callout = st.columns([7, 5])
    with col_chart:
        st.subheader("Candidate Progression Funnel")
        fig_funnel = create_plotly_funnel(funnel_steps)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_callout:
        st.subheader("Identified Funnel Bottlenecks")
        # Identify greatest dropoff stage
        dropoffs = [s for s in funnel_steps if s["stage"] != "Applied"]
        worst_stage = max(dropoffs, key=lambda x: x["stage_dropoff_pct"])
        
        st.error(f"""
        **Highest Drop-off Stage: {worst_stage['stage']}**  
        - **Drop-off Rate:** **{worst_stage['stage_dropoff_pct']}%** of candidates drop out at this transition.
        - **Remaining Pool:** Only {worst_stage['candidates']:,} candidates successfully passed.
        """)
        
        st.info("""
        **Operational Diagnostic Checklist:**
        1. **Screen Calibration:** Validate that initial resume screen filters are not discarding high-potential candidates prematurely.
        2. **Technical Exercise Friction:** Monitor whether take-home exercises or live coding evaluations show unreasonable abandonment.
        3. **Onsite Scheduling Delay:** Eliminate delays between rounds to capture top candidates before competing offers arrive.
        """)

    st.markdown("---")

    # Stage Durations and Latencies
    st.subheader("Average Stage Transition Cycle Times (Days by Department)")
    if not stage_duration_df.empty:
        fig_duration = px.bar(
            stage_duration_df,
            x="department_name",
            y=["avg_app_to_screen_days", "avg_screen_to_tech_days", "avg_tech_to_onsite_days", "avg_onsite_to_offer_days"],
            title="Recruitment Stage Duration Breakdown (Days)",
            labels={"value": "Days Spent in Stage", "variable": "Hiring Stage"},
            barmode="stack",
            color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["warning"], COLORS["success"]],
        )
        fig_duration.update_layout(xaxis_title="", height=360)
        st.plotly_chart(fig_duration, use_container_width=True)

        st.dataframe(stage_duration_df, use_container_width=True, hide_index=True)
