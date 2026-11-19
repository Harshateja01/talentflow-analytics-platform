{{ config(materialized='table') }}

with source_base as (
    select
        source_id,
        source_name,
        source_channel,
        cost_per_posting
    from {{ ref('stg_recruiting_sources') }}
),

pipeline_metrics as (
    select
        recruiting_source,
        count(application_id) as total_applications,
        sum(stage_offer) as total_offers_extended,
        sum(stage_hired) as total_hires,
        round(avg(total_time_to_hire_days), 1) as avg_time_to_hire_days,
        round(avg(avg_candidate_experience_score), 2) as avg_candidate_experience_rating
    from {{ ref('int_recruiting_funnel') }}
    group by recruiting_source
),

lifecycle_metrics as (
    select
        recruiting_source,
        count(employee_id) as employees_hired,
        sum(is_attrition) as employees_churned,
        round(avg(tenure_days) / 30.42, 1) as avg_employee_tenure_months,
        round(avg(avg_engagement_score), 2) as avg_employee_engagement
    from {{ ref('int_employee_lifecycle') }}
    group by recruiting_source
)

select
    s.source_id,
    s.source_name,
    s.source_channel,
    s.cost_per_posting,
    coalesce(p.total_applications, 0) as total_applications,
    coalesce(p.total_offers_extended, 0) as total_offers_extended,
    coalesce(p.total_hires, 0) as total_hires,
    round(coalesce(p.total_hires, 0) * 100.0 / nullif(p.total_applications, 0), 2) as app_to_hire_conversion_pct,
    round(coalesce(p.total_hires, 0) * 100.0 / nullif(p.total_offers_extended, 0), 1) as offer_acceptance_rate_pct,
    coalesce(p.avg_time_to_hire_days, 0) as avg_time_to_hire_days,
    coalesce(p.avg_candidate_experience_rating, 0) as avg_candidate_experience_rating,
    coalesce(l.employees_churned, 0) as employees_churned,
    round(coalesce(l.employees_churned, 0) * 100.0 / nullif(l.employees_hired, 0), 1) as employee_churn_rate_pct,
    coalesce(l.avg_employee_tenure_months, 0) as avg_employee_tenure_months,
    coalesce(l.avg_employee_engagement, 0) as avg_employee_engagement
from source_base s
left join pipeline_metrics p on s.source_name = p.recruiting_source
left join lifecycle_metrics l on s.source_name = l.recruiting_source
