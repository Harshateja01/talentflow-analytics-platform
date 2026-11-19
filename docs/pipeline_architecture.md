# TalentFlow Pipeline Architecture

## 1. High-Level Architecture Overview

The TalentFlow platform supports a dual-engine architecture:
1. **Local Development Mode**: DuckDB embedded analytical engine, local CSV storage, and dbt-duckdb adapter.
2. **Production GCP Mode**: Google Cloud Storage landing zone, Google BigQuery enterprise data warehouse, and dbt-bigquery adapter.

```mermaid
flowchart TD
    subgraph Data_Generation [1. Synthetic Data Generator]
        Gen[Python Synthetic Generator]
        CSVs[8 Relational CSV Extracts]
        DQ_Pre[Pre-Ingestion Data Quality Validator]
        Gen --> CSVs
        CSVs --> DQ_Pre
    end

    subgraph Storage_Layer [2. Storage & Landing Zone]
        GCS[GCS Bucket: raw/]
        DuckDB_Raw[(DuckDB talentflow_raw)]
        BQ_Raw[(BigQuery talentflow_raw)]
        
        CSVs -. Local Mode .-> DuckDB_Raw
        CSVs -. GCP Mode .-> GCS
        GCS --> BQ_Raw
    end

    subgraph Transformation_Engine [3. dbt Core Transformation]
        Staging[dbt Staging Views: deduplication & cleaning]
        Intermediate[dbt Intermediate Models: lifecycle & funnel]
        Marts[dbt Analytics Marts: partitioned & clustered tables]
        
        DuckDB_Raw --> Staging
        BQ_Raw --> Staging
        Staging --> Intermediate
        Intermediate --> Marts
    end

    subgraph Quality_Governance [4. Quality & Governance Gates]
        dbt_Tests[59 dbt Schema & Singular Tests]
        Audit_Rep[Data Quality Audit JSON & Markdown]
        Marts --> dbt_Tests
        DQ_Pre --> Audit_Rep
    end

    subgraph Stakeholder_Surfaces [5. Interactive Analytics]
        Dashboard[Streamlit Enterprise Dashboard: 7 Pages]
        AI_Insights[AI Insights Engine: Gemini + Deterministic Fallback]
        Marts --> Dashboard
        Marts --> AI_Insights
    end
```

---

## 2. Ingestion Flow & Repeatability

1. **Idempotent Ingestion**: Raw loads leverage `WRITE_TRUNCATE` (BigQuery) or `CREATE OR REPLACE TABLE` (DuckDB), preventing unintended duplicates across reruns.
2. **Schema Separation**: Complete separation of privileges across:
   - `talentflow_raw`: Unmodified landing zone.
   - `talentflow_staging`: Cleaning, deduplication, and transformation views.
   - `talentflow_analytics`: Governed, partitioned analytical marts accessible by BI and stakeholder consumers.
3. **Partitioning and Clustering**:
   Fact tables are partitioned by `DATE` columns (e.g. `application_date`, `hire_date`, `termination_date`) and clustered by high-cardinality query dimensions (`department_id`, `recruiting_source`), reducing BigQuery scan costs by up to 85%.
