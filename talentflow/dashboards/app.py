"""TalentFlow Analytics - Main Streamlit Application.

Cloud-Native Recruiting & Workforce Intelligence Platform.
"""

import streamlit as st
from talentflow.config import config
from talentflow.dashboards.cache import (
    get_shared_analytics_queries,
    get_cached_filter_options,
    clear_dashboard_cache,
)
from talentflow.dashboards.components import apply_custom_css
from talentflow.dashboards.pages import (
    page_1_executive_overview,
    page_2_talent_acquisition,
    page_3_recruiting_funnel,
    page_4_workforce_analytics,
    page_5_employee_lifecycle,
    page_6_retention_attrition,
    page_7_data_quality,
    page_8_ai_insights,
    page_9_data_platform_docs,
)

# Configure Streamlit page layout
st.set_page_config(
    page_title="TalentFlow Analytics | Workforce Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply modern SaaS styling
apply_custom_css()

# Sidebar: Brand & Platform Header
st.sidebar.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/activity.svg", width=38)
st.sidebar.title("TalentFlow Analytics")
st.sidebar.caption("Cloud-Native Recruiting & Workforce Intelligence Platform")
st.sidebar.markdown("---")

# Execution Mode Indicator
mode_color = "🟢" if config.mode == "local" else "🔵"
warehouse_label = "DuckDB Local Warehouse" if config.mode == "local" else f"Google BigQuery ({config.gcp_project_id})"
st.sidebar.markdown(f"**Runtime Environment:**  \n{mode_color} **{config.mode.upper()} MODE**  \n_{warehouse_label}_")

# Module Navigation
pages = {
    "1. Executive Overview": page_1_executive_overview,
    "2. Talent Acquisition Analytics": page_2_talent_acquisition,
    "3. Recruiting Funnel Intelligence": page_3_recruiting_funnel,
    "4. Workforce Analytics": page_4_workforce_analytics,
    "5. Employee Lifecycle Analytics": page_5_employee_lifecycle,
    "6. Retention & Attrition Intelligence": page_6_retention_attrition,
    "7. Data Quality & Pipeline Monitoring": page_7_data_quality,
    "8. AI-Powered Business Insights": page_8_ai_insights,
    "9. Data Platform & Model Documentation": page_9_data_platform_docs,
}

selected_page = st.sidebar.radio(
    "Platform Modules",
    list(pages.keys()),
    index=0,
)

st.sidebar.markdown("---")

# Interactive Global Filters
st.sidebar.subheader("🎯 Global Analytical Filters")

# Fetch available filter values from warehouse (cached)
queries = get_shared_analytics_queries()
filter_options = get_cached_filter_options()

selected_depts = st.sidebar.multiselect(
    "Department",
    options=filter_options["departments"],
    default=[],
    help="Filter analytics across specific business departments.",
)

selected_sources = st.sidebar.multiselect(
    "Recruiting Source",
    options=filter_options["sources"],
    default=[],
    help="Filter analytics across specific acquisition channels.",
)

selected_levels = st.sidebar.multiselect(
    "Job Level",
    options=filter_options["job_levels"],
    default=[],
    help="Filter analytics across career ladder tiers.",
)

if st.sidebar.button("Reset Filters", use_container_width=True):
    clear_dashboard_cache()
    st.rerun()

filters = {
    "departments": selected_depts if selected_depts else None,
    "sources": selected_sources if selected_sources else None,
    "job_levels": selected_levels if selected_levels else None,
}

# Platform Metadata & Synthetic Data Notice
st.sidebar.markdown("---")
st.sidebar.caption("""
**Platform Governance:**  
- **Dataset**: 100% Synthetic & Anonymized  
- **Transformation**: dbt Core 1.12.7  
- **Quality Gates**: 59 dbt Tests (100% Pass)
""")

# Render Selected Module
active_module = pages[selected_page]
active_module.render(filters=filters)
