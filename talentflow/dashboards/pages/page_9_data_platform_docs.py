"""Module 9: Data Platform & Model Documentation."""

from typing import Dict, Any, Optional
import streamlit as st
from talentflow.dashboards.cache import get_shared_analytics_queries

def render(filters: Optional[Dict[str, Any]] = None):
    queries = get_shared_analytics_queries()
    st.markdown('<span class="badge-header">Analytics Engineering & Architecture</span>', unsafe_allow_html=True)
    st.title("Data Platform & Model Documentation")
    st.markdown("Interactive platform architecture guide, Kimball dimensional models, data dictionary, and pipeline execution standards.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏗️ Architecture & Lineage",
        "📖 Data Dictionary",
        "📐 Dimensional Modeling",
        "🚀 Execution & Runbook",
    ])

    with tab1:
        st.subheader("Cloud-Native Architecture Overview")
        st.markdown("""
        TalentFlow Analytics implements a dual-engine data architecture that supports both local development and cloud production deployment:
        """)
        
        st.markdown("""
        ```mermaid
        flowchart TD
            subgraph Raw_Sources [Raw Data Ingestion]
                CSV[8 Synthetic CSV Datasets]
                Val[Python Pre-Ingestion Validator]
                CSV --> Val
            end

            subgraph Storage [Landing & Warehouse]
                Local_DB[(DuckDB talentflow_raw)]
                Cloud_Storage[Google Cloud Storage]
                BQ[(BigQuery talentflow_raw)]
                CSV -. Local .-> Local_DB
                CSV -. GCP .-> Cloud_Storage --> BQ
            end

            subgraph dbt_Transformations [dbt Transformation Layers]
                Stg[8 Staging Views: Deduplication & Typing]
                Int[4 Intermediate Models: Funnel & Lifecycle]
                Marts[8 Analytical Marts: Partitioned & Clustered]
                Local_DB --> Stg
                BQ --> Stg
                Stg --> Int --> Marts
            end

            subgraph Consumption [Analytics Consumption]
                Dash[Streamlit Enterprise Dashboard]
                AI[AI Insights Engine: Gemini 2.5]
                Marts --> Dash
                Marts --> AI
            end
        ```
        """)

    with tab2:
        st.subheader("Data Dictionary (Key Entities)")
        st.markdown("""
        | Table Name | Layer | Primary Key | Description |
        |---|---|---|---|
        | `candidates` | Raw / Staging | `candidate_id` | Candidate directory, contact details, and experience. |
        | `applications` | Raw / Staging | `application_id` | Requisition submissions linking candidates, sources, and departments. |
        | `interviews` | Raw / Staging | `interview_id` | Interview round outcomes, interviewer ratings, and candidate feedback. |
        | `offers` | Raw / Staging | `offer_id` | Extended compensation packages, acceptance statuses, and decline reasons. |
        | `employees` | Raw / Staging | `employee_id` | Active and departed workforce records, tenure, and performance. |
        | `engagement_surveys` | Raw / Staging | `survey_id` | Employee sentiment across 5 survey dimensions. |
        | `departments` | Dimension | `department_id` | Business departments, leads, and cost centers. |
        | `recruiting_sources` | Dimension | `source_id` | Sourcing acquisition channels and posting costs. |
        """)

    with tab3:
        st.subheader("dbt Model Hierarchy & Kimball Design")
        st.markdown("""
        ### Staging Views (`talentflow_staging`)
        - `stg_candidates`: Cleans candidate names, deduplicates records via window functions, formats timestamps.
        - `stg_applications`: Standardizes inconsistent department casing (`'Eng'`, `'Sales '`, `'CS'`) into valid keys.
        - `stg_interviews`: Normalizes rating scales and round titles.
        - `stg_offers`: Derives decision turnaround days and fills missing decline reasons.
        - `stg_employees`: Calculates tenure in days and months, active indicator, and attrition flags.
        - `stg_engagement_surveys`: Computes aggregate sentiment score across survey pillars.

        ### Intermediate Models (`talentflow_staging`)
        - `int_candidate_application_history`: Candidate cross-requisition application frequency and hire flags.
        - `int_recruiting_funnel`: Binary milestone progression flags (`stage_applied`, `stage_screen`, `stage_tech`, `stage_onsite`, `stage_offer`, `stage_hired`) and stage duration cycle times.
        - `int_employee_lifecycle`: Connects initial recruitment origin with ongoing workforce tenure, compensation, and survey feedback.
        - `int_employee_retention`: Cohort analysis aggregating 90d, 180d, and 365d retention rates by hire cohort month.

        ### Analytical Marts (`talentflow_analytics`)
        - `fct_recruiting_pipeline`: Partitioned by `application_date`, clustered by `department_id`, `recruiting_source`.
        - `fct_employee_lifecycle`: Partitioned by `hire_date`, clustered by `department_id`, `recruiting_source`.
        - `fct_employee_attrition`: Turnover risk segmentation and exit indicators.
        - `fct_candidate_experience`: Interview feedback scores and duration metrics.
        - `dim_department`: Department dimension with current headcount and historic turnover.
        - `dim_recruiting_source`: Channel effectiveness and cost-per-hire economics.
        - `mart_recruiting_kpis`: Pre-aggregated monthly recruiting performance metrics.
        - `mart_workforce_kpis`: Pre-aggregated monthly net workforce headcount changes.
        """)

    with tab4:
        st.subheader("Pipeline Execution & Local Runbook")
        st.markdown("""
        ### 1. Local Pipeline Execution (DuckDB Engine)
        ```bash
        # Execute the end-to-end 10-step pipeline
        python -m talentflow.pipeline --mode local
        ```
        *Duration: ~22 seconds. Ingests ~20k records, builds 20 dbt models, and runs 59 dbt tests.*

        ### 2. Launch Streamlit Platform
        ```bash
        streamlit run talentflow/dashboards/app.py
        ```

        ### 3. Run Automated Pytest Suite
        ```bash
        pytest -v
        ```

        ### 4. Cloud GCP Execution
        ```bash
        # Requires configured GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS in .env
        python -m talentflow.pipeline --mode gcp
        ```
        """)
