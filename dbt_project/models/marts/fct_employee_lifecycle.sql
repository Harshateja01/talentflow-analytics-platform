{{ config(
    materialized='table',
    partition_by={
      "field": "hire_date",
      "data_type": "date",
      "granularity": "month"
    } if target.type == 'bigquery' else none,
    cluster_by=["department_id", "recruiting_source"] if target.type == 'bigquery' else none
) }}

with lifecycle as (
    select * from {{ ref('int_employee_lifecycle') }}
),

dept as (
    select department_id, department_name, department_lead from {{ ref('stg_departments') }}
),

cand as (
    select candidate_id, full_name, email from {{ ref('stg_candidates') }}
)

select
    l.employee_id,
    l.candidate_id,
    c.full_name as employee_name,
    c.email as employee_email,
    l.application_id,
    l.department_id,
    d.department_name,
    d.department_lead,
    l.job_title,
    l.job_level,
    l.location,
    l.hire_date,
    cast({{ date_trunc_month('l.hire_date') }} as date) as hire_month,
    l.employment_status,
    l.termination_date,
    cast({{ date_trunc_month('l.termination_date') }} as date) as termination_month,
    l.manager_id,
    l.performance_rating,
    l.is_active,
    l.is_attrition,
    l.tenure_days,
    round(l.tenure_days / 30.42, 1) as tenure_months,
    l.tenure_band,
    l.recruiting_source,
    l.application_date,
    l.time_to_hire_days,
    l.highest_education,
    l.years_of_experience,
    l.base_salary,
    l.bonus_pct,
    l.stock_units,
    l.avg_engagement_score,
    l.avg_satisfaction_score,
    l.avg_wlb_score,
    l.avg_career_growth_score,
    l.avg_manager_effectiveness_score,
    l.total_surveys_taken

from lifecycle l
left join dept d on l.department_id = d.department_id
left join cand c on l.candidate_id = c.candidate_id
