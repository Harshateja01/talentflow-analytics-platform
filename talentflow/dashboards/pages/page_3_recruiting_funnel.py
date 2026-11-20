"""Module 3: Recruiting Funnel Intelligence."""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_recruiting_funnel_summary,
    get_cached_stage_duration_breakdown,
)
from talentflow.analytics.kpis import KPIService
from talentflow.dashboards.components import create_plotly_funnel, render_metric_card, render_active_filter_bar, COLORS

def render(filters: Optional[Dict[str, Any]] = None):
    filters = filters or {}
    depts = filters.get("departments")
    sources = filters.get("sources")

    st.markdown('<span class="badge-header">Recruiting Operations & Pipeline Velocity</span>', unsafe_allow_html=True)
    st.title("Recruiting Funnel Intelligence")
    st.markdown("Full-funnel stage progression tracking, conversion drop-off points, stage transition cycle times, and bottleneck diagnostics.")

    render_active_filter_bar(filters)

    queries = get_shared_analytics_queries()
    funnel_summary_df = get_cached_recruiting_funnel_summary(departments=depts, sources=sources)
    stage_duration_df = get_cached_stage_duration_breakdown(departments=depts, sources=sources)

    if funnel_summary_df.empty or funnel_summary_df.iloc[0].get("applied", 0) == 0:
        st.warning("No recruiting funnel records available for the current filter scope.")
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

    # Main Funnel Diagram + Bottleneck Diagnostic
    col_chart, col_callout = st.columns([7, 5])
    with col_chart:
        st.subheader("End-to-End Candidate Progression")
        fig_funnel = create_plotly_funnel(funnel_steps)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_callout:
        st.subheader("Automated Bottleneck Detection")
        dropoffs = [s for s in funnel_steps if s["stage"] != "Applied"]
        worst_stage = max(dropoffs, key=lambda x: x["stage_dropoff_pct"])
        
        st.error(f"""
        **Primary Funnel Bottleneck: {worst_stage['stage']}**  
        - **Drop-off Rate:** **{worst_stage['stage_dropoff_pct']}%** of candidates do not advance through this hurdle.
        - **Passed Pool:** {worst_stage['candidates']:,} candidates successfully cleared this phase.
        """)
        
        st.info("""
        **Data-Driven Operational Diagnostics:**
        1. **Assessment Alignment**: Audit whether screening or technical rubrics reject qualified candidates due to overly restrictive criteria.
        2. **Scheduling Latency**: Review calendar gaps between interview stages; prolonged delays directly correlate with increased candidate drop-out.
        3. **Offer Parity**: Compare declining offers with competing market benchmarks.
        """)

    st.markdown("---")

    # Stage Durations and Latencies
    st.subheader("Average Stage Transition Cycle Times (Days by Department)")
    if not stage_duration_df.empty:
        fig_duration = px.bar(
            stage_duration_df,
            x="department_name",
            y=["avg_app_to_screen_days", "avg_screen_to_tech_days", "avg_tech_to_onsite_days", "avg_onsite_to_offer_days"],
            title="Recruitment Stage Latency Breakdown (Days)",
            labels={"value": "Days Spent in Stage", "variable": "Hiring Stage"},
            barmode="stack",
            color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["warning"], COLORS["success"]],
        )
        fig_duration.update_layout(xaxis_title="", height=350)
        st.plotly_chart(fig_duration, use_container_width=True)

        st.dataframe(stage_duration_df, use_container_width=True, hide_index=True)
