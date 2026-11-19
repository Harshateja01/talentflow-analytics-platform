"""Page 7: AI-Powered Insights."""

import streamlit as st
import pandas as pd

from talentflow.config import config
from talentflow.ai_insights.engine import AIInsightsEngine
from talentflow.ai_insights.prompts import SUPPORTED_QUESTIONS

def render():
    st.markdown('<span class="badge-header">Executive Assistant & Natural Language Analytics</span>', unsafe_allow_html=True)
    st.title("AI-Powered Talent Analytics Insights")
    st.markdown("Ask complex talent acquisition, conversion, and workforce retention questions powered by curated analytical queries and AI summarization.")

    engine = AIInsightsEngine()

    # Engine status banner
    if engine.has_gemini:
        st.success("🤖 **Gemini 2.5 API Connected:** Summaries are synthesized using Google Gemini with approved metrics tables.")
    else:
        st.info("💡 **Deterministic Analytics Engine Active (Safe Fallback):** Predefined rule-based analysis based on verified warehouse tables.")

    st.markdown("---")

    # Question Selection
    st.subheader("Select an Analytical Question")
    question_options = {k: v["label"] for k, v in SUPPORTED_QUESTIONS.items()}
    
    selected_key = st.selectbox(
        "Choose an analytical query:",
        options=list(question_options.keys()),
        format_func=lambda k: f"{question_options[k]} — {SUPPORTED_QUESTIONS[k]['description']}",
    )

    if st.button("Generate Strategic Analysis", type="primary"):
        with st.spinner("Analyzing warehouse data and generating executive brief..."):
            result = engine.analyze_question(selected_key)
            
            st.markdown(f"**Synthesized using:** `{result['engine']}`")
            st.markdown(result["summary"])
            
            st.markdown("---")
            with st.expander("🔍 View Underlying Curated Data Table", expanded=False):
                st.dataframe(result["data"], use_container_width=True)

    # Pre-canned Quick Inquiry Buttons
    st.markdown("#### Quick Analytical Inquiries")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚨 Funnel Bottlenecks"):
            res = engine.analyze_question("funnel_bottlenecks")
            st.markdown(res["summary"])
    with col2:
        if st.button("📈 High Conversion Sources"):
            res = engine.analyze_question("highest_conversion_sources")
            st.markdown(res["summary"])
    with col3:
        if st.button("🏢 Department Turnover"):
            res = engine.analyze_question("high_attrition_departments")
            st.markdown(res["summary"])
