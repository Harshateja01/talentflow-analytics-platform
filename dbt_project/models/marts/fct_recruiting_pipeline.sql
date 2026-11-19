{{ config(
    materialized='table',
    partition_by={
      "field": "application_date",
      "data_type": "date",
      "granularity": "month"
    } if target.type == 'bigquery' else none,
    cluster_by=["department_id", "recruiting_source"] if target.type == 'bigquery' else none
) }}

with funnel as (
    select * from {{ ref('int_recruiting_funnel') }}
),

dept as (
    select department_id, department_name from {{ ref('stg_departments') }}
),

cand as (
    select
        candidate_id,
        full_name,
        email,
        location,
        highest_education,
        years_of_experience
    from {{ ref('stg_candidates') }}
)

select
    f.application_id,
    f.candidate_id,
    c.full_name as candidate_name,
    c.email as candidate_email,
    c.location as candidate_location,
    c.highest_education,
    c.years_of_experience,
    f.department_id,
    d.department_name,
    f.recruiting_source,
    f.application_date,
    cast({{ date_trunc_month('f.application_date') }} as date) as application_month,
    f.candidate_stage,
    f.current_status,
    f.rejection_reason,
    
    -- Funnel Binary Progression Flags
    f.stage_applied,
    f.stage_screen,
    f.stage_tech,
    f.stage_onsite,
    f.stage_offer,
    f.stage_hired,

    -- Milestone Dates
    f.screen_date,
    f.tech_date,
    f.onsite_date,
    f.offer_date,
    f.hire_date,

    -- Cycle Times
    f.days_app_to_screen,
    f.days_screen_to_tech,
    f.days_tech_to_onsite,
    f.days_onsite_to_offer,
    f.total_time_to_hire_days,

    -- Evaluation & Economics
    f.avg_candidate_experience_score,
    f.avg_interview_score,
    f.total_interview_duration_minutes,
    f.base_salary,
    f.offer_decision_days

from funnel f
left join dept d on f.department_id = d.department_id
left join cand c on f.candidate_id = c.candidate_id
