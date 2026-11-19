{{ config(materialized='table') }}

with attrition_base as (
    select
        employee_id,
        candidate_id,
        employee_name,
        department_id,
        department_name,
        job_title,
        job_level,
        location,
        hire_date,
        termination_date,
        termination_month,
        employment_status as attrition_type,
        tenure_days,
        tenure_months,
        tenure_band,
        recruiting_source,
        performance_rating,
        base_salary,
        avg_engagement_score,
        avg_satisfaction_score,
        avg_wlb_score,
        avg_career_growth_score,
        avg_manager_effectiveness_score
    from {{ ref('fct_employee_lifecycle') }}
    where is_attrition = 1 and termination_date is not null
)

select
    employee_id,
    candidate_id,
    employee_name,
    department_id,
    department_name,
    job_title,
    job_level,
    location,
    hire_date,
    termination_date,
    termination_month,
    attrition_type,
    tenure_days,
    tenure_months,
    tenure_band,
    recruiting_source,
    performance_rating,
    base_salary,
    avg_engagement_score,
    avg_satisfaction_score,
    avg_wlb_score,
    avg_career_growth_score,
    avg_manager_effectiveness_score,
    case
        when tenure_days <= 90 then 'Early Departure (<= 90d)'
        when tenure_days <= 180 then 'Mid-Term Departure (91 - 180d)'
        when tenure_days <= 365 then 'First-Year Departure (181 - 365d)'
        else 'Tenured Departure (> 1yr)'
    end as attrition_risk_segment
from attrition_base
