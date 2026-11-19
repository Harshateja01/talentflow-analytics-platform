{{ config(materialized='table') }}

with dept_base as (
    select
        department_id,
        department_name,
        department_lead,
        cost_center
    from {{ ref('stg_departments') }}
),

emp_stats as (
    select
        department_id,
        count(employee_id) as total_historic_hires,
        sum(is_active) as active_headcount,
        sum(is_attrition) as total_attrition,
        round(avg(tenure_days) / 30.42, 1) as avg_tenure_months,
        round(avg(performance_rating), 2) as avg_performance_rating,
        round(avg(avg_engagement_score), 2) as avg_department_engagement
    from {{ ref('int_employee_lifecycle') }}
    group by department_id
)

select
    d.department_id,
    d.department_name,
    d.department_lead,
    d.cost_center,
    coalesce(e.total_historic_hires, 0) as total_historic_hires,
    coalesce(e.active_headcount, 0) as active_headcount,
    coalesce(e.total_attrition, 0) as total_attrition,
    round(coalesce(e.total_attrition, 0) * 100.0 / nullif(e.total_historic_hires, 0), 1) as historic_attrition_rate_pct,
    coalesce(e.avg_tenure_months, 0) as avg_tenure_months,
    coalesce(e.avg_performance_rating, 0) as avg_performance_rating,
    coalesce(e.avg_department_engagement, 0) as avg_department_engagement
from dept_base d
left join emp_stats e on d.department_id = e.department_id
