# TalentFlow Data Models & Dimensional Architecture

TalentFlow organizes transformations into three distinct layers following Kimball dimensional modeling and dbt best practices:

```
[Raw Sources] ──> [Staging Views] ──> [Intermediate Models] ──> [Analytical Marts]
```

---

## 1. Staging Layer (`talentflow_staging`)

Staging models are 1:1 view representations of raw tables that perform type casting, column renaming, whitespace cleaning, and deduplication.

- **`stg_candidates`**: Deduplicates raw candidates using `ROW_NUMBER() OVER (PARTITION BY candidate_id ORDER BY created_at DESC)` and validates email formats.
- **`stg_applications`**: Standardizes non-standard department strings (`'Eng'`, `'ENGINEERING'`, `'Sales '`, `'CS'`) into canonical department keys (`DEP-001`, `DEP-003`, etc.).
- **`stg_interviews`**: Casts ratings to integer scales and cleans round nomenclature.
- **`stg_offers`**: Derives response turnaround latencies and normalizes missing decline rationales.
- **`stg_employees`**: Calculates employee tenure in days, active status indicators, and attrition indicators.
- **`stg_engagement_surveys`**: Computes an aggregate overall sentiment composite across 5 survey dimensions.
- **`stg_departments` & `stg_recruiting_sources`**: Clean dimensional lookups.

---

## 2. Intermediate Layer (`talentflow_staging`)

Intermediate models join and enrich domain models prior to mart materialization:

- **`int_candidate_application_history`**: Aggregates candidate cross-application history, tracking total lifetime requisitions applied for, multi-department submissions, and eventual hire status.
- **`int_recruiting_funnel`**: Core recruiting progression engine. Generates binary stage milestone flags (`stage_applied`, `stage_screen`, `stage_tech`, `stage_onsite`, `stage_offer`, `stage_hired`) and computes cycle times between adjacent stages.
- **`int_employee_lifecycle`**: Bridges original talent acquisition records (sourcing channel, time to hire, offer details) with ongoing employee records (tenure bands, current performance rating, and engagement survey feedback).
- **`int_employee_retention`**: Aggregates hire cohorts by month, department, and sourcing channel, computing milestone survival metrics at 90 days, 180 days, and 365 days.

---

## 3. Analytical Marts Layer (`talentflow_analytics`)

Marts are materialized as high-performance physical tables with BigQuery partitioning and clustering:

| Mart Name | Granularity | Partition Key | Clustering Keys | Purpose |
|---|---|---|---|---|
| `fct_recruiting_pipeline` | 1 row per Application | `application_date` (Month) | `department_id`, `recruiting_source` | Full recruiting conversion and funnel drop-off analytics |
| `fct_employee_lifecycle` | 1 row per Employee | `hire_date` (Month) | `department_id`, `recruiting_source` | Comprehensive workforce tenure, performance, and engagement |
| `fct_employee_attrition` | 1 row per Churned Employee | `termination_date` (Month) | `department_id`, `recruiting_source` | Exit drivers, early-departure risk analysis |
| `fct_candidate_experience` | 1 row per Interview Round | `interview_date` (Month) | `department_id`, `interview_round` | Interviewer rating and feedback score distributions |
| `dim_department` | 1 row per Department | None (Dimension) | `department_id` | Enriched department metrics, active headcount, and tenure |
| `dim_recruiting_source` | 1 row per Source Channel | None (Dimension) | `source_id` | Sourcing efficiency, conversion rates, and turnover |
| `mart_recruiting_kpis` | 1 row per Month x Dept x Source | `application_month` (Month) | `department_id`, `recruiting_source` | Pre-aggregated recruiting KPI scorecard |
| `mart_workforce_kpis` | 1 row per Month x Dept | `reporting_month` (Month) | `department_id` | Monthly headcount inflow, outflow, and net workforce delta |
