{{ config(materialized='view') }}

with cohort_base as (
    select
        employee_id,
        department_id,
        recruiting_source,
        job_level,
        hire_date,
        cast({{ date_trunc_month('hire_date') }} as date) as cohort_month,
        tenure_days,
        is_active,
        is_attrition,
        case when tenure_days >= 90 then 1 else 0 end as retained_90_days,
        case when tenure_days >= 180 then 1 else 0 end as retained_180_days,
        case when tenure_days >= 365 then 1 else 0 end as retained_365_days
    from {{ ref('int_employee_lifecycle') }}
)

select
    cohort_month,
    department_id,
    recruiting_source,
    job_level,
    count(employee_id) as cohort_size,
    sum(is_active) as currently_active_count,
    sum(is_attrition) as total_attrition_count,
    sum(retained_90_days) as retained_90_days_count,
    sum(retained_180_days) as retained_180_days_count,
    sum(retained_365_days) as retained_365_days_count,
    round(sum(retained_90_days) * 100.0 / nullif(count(employee_id), 0), 1) as retention_rate_90d_pct,
    round(sum(retained_180_days) * 100.0 / nullif(count(employee_id), 0), 1) as retention_rate_180d_pct,
    round(sum(retained_365_days) * 100.0 / nullif(count(employee_id), 0), 1) as retention_rate_365d_pct
from cohort_base
group by 1, 2, 3, 4
