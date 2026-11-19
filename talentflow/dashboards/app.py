"""Main Streamlit Application for TalentFlow Analytics Platform."""

import streamlit as st
from talentflow.config import config
from talentflow.dashboards.components import apply_custom_css
from talentflow.dashboards.pages import (
    page_1_executive_overview,
    page_2_recruiting_funnel,
    page_3_recruiting_source,
    page_4_workforce_analytics,
    page_5_employee_lifecycle,
    page_6_data_quality,
    page_7_ai_insights,
)

# Configure Streamlit page layout
st.set_page_config(
    page_title="TalentFlow Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply corporate enterprise CSS
apply_custom_css()

# Sidebar Navigation and Configuration
st.sidebar.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/activity.svg", width=42)
st.sidebar.title("TalentFlow")
st.sidebar.caption("Recruiting & Employee Lifecycle Platform")
st.sidebar.markdown("---")

# Execution Mode Indicator
mode_color = "🟢" if config.mode == "local" else "🔵"
st.sidebar.markdown(f"**Runtime Environment:**  \n{mode_color} **{config.mode.upper()} MODE** ({'DuckDB Warehouse' if config.mode == 'local' else 'BigQuery + GCS'})")

pages = {
    "1. Executive Overview": page_1_executive_overview,
    "2. Recruiting Funnel": page_2_recruiting_funnel,
    "3. Recruiting Sources": page_3_recruiting_source,
    "4. Workforce Analytics": page_4_workforce_analytics,
    "5. Employee Lifecycle": page_5_employee_lifecycle,
    "6. Data Quality & Audit": page_6_data_quality,
    "7. AI-Powered Insights": page_7_ai_insights,
}

selected_page = st.sidebar.radio(
    "Navigation",
    list(pages.keys()),
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Platform Metadata")
st.sidebar.text(f"Version: 1.0.0")
st.sidebar.text(f"Warehouse: {'DuckDB' if config.mode == 'local' else 'BigQuery'}")
st.sidebar.text(f"Engine: dbt Core 1.12.7")

# Footer in sidebar
st.sidebar.markdown("---")
st.sidebar.caption("Portfolio Analytics Engineering Project\nHR Analytics – Elastic Architecture")

# Render active page
page_module = pages[selected_page]
page_module.render()
