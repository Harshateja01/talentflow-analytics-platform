"""Page 6: Data Quality Monitoring & Pipeline Governance."""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

from talentflow.config import config
from talentflow.dashboards.components import render_metric_card

def render():
    st.markdown('<span class="badge-header">Data Governance & Warehouse Reliability</span>', unsafe_allow_html=True)
    st.title("Data Quality & Governance Monitoring")
    st.markdown("Real-time audit dashboard monitoring schema constraints, controlled anomaly tests, and referential integrity.")

    report_path = config.reports_dir / "data_quality_report.json"
    
    if not report_path.exists():
        st.warning("No data quality report found. Please run the pipeline to generate quality audit metrics.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Top KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Assertions", f"{summary['total_checks']}", "Pre-ingestion + schema tests")
    with c2:
        render_metric_card("Passed Checks", f"{summary['passed_checks']}", "Verified clean constraints")
    with c3:
        render_metric_card("Failed Checks", f"{summary['failed_checks']}", "Controlled anomaly scenarios")
    with c4:
        render_metric_card("Overall Pass Rate", f"{summary['pass_rate_pct']}%", "Healthy threshold > 80%")

    st.markdown("---")

    # Controlled Data Quality Scenarios Explanation
    st.subheader("Controlled Anomaly Injection & Detection")
    st.markdown("""
    In accordance with production testing best practices, the pipeline injects **controlled data quality scenarios** into synthetic raw extracts to verify that validation gates, dbt cleaning models, and monitoring alerts function correctly.
    """)

    failed_details = summary.get("failed_checks_detail", [])
    if failed_details:
        st.error(f"Detected {len(failed_details)} controlled quality anomalies in raw ingest:")
        fail_df = pd.DataFrame(failed_details)
        st.dataframe(
            fail_df[[
                "dataset", "check_name", "check_type", "failed_records", "failure_percentage", "details"
            ]].rename(columns={
                "dataset": "Raw Dataset",
                "check_name": "Quality Rule",
                "check_type": "Rule Type",
                "failed_records": "Failed Records",
                "failure_percentage": "Failure %",
                "details": "Remediation & Finding",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("All data quality checks passed with 100% compliance.")

    st.markdown("---")

    # Tests by Category
    col_chart, col_gov = st.columns([6, 6])
    with col_chart:
        st.subheader("Validation Rules by Category")
        type_df = pd.DataFrame([
            {"Category": k.replace("_", " ").title(), "Checks Count": v}
            for k, v in summary["checks_by_type"].items()
        ])
        fig_cat = px.bar(
            type_df,
            x="Category",
            y="Checks Count",
            color="Category",
            text_auto=True,
        )
        fig_cat.update_layout(showlegend=False, height=320, xaxis_title="")
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_gov:
        st.subheader("Security & Least-Privilege IAM Controls")
        st.markdown("""
        **Production HR Data Protection Architecture:**
        - **Data Masking:** PII (candidate personal emails, phone numbers) masked using BigQuery Policy Tags.
        - **Column-Level Security:** Strict RBAC permissions on compensation fields (`base_salary`, `bonus_pct`, `stock_units`).
        - **Authorized Views:** Analysts query `talentflow_analytics` marts without direct access to raw PII landing zones.
        - **Synthetic Guarantee:** 100% synthetic data generated for this platform. No personal or confidential HR data is present.
        """)
