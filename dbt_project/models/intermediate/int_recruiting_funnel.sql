{{ config(materialized='view') }}

with app_base as (
    select
        application_id,
        candidate_id,
        department_id,
        recruiting_source,
        application_date,
        candidate_stage,
        current_status,
        rejection_reason
    from {{ ref('stg_applications') }}
),

interview_stages as (
    select
        application_id,
        max(case when interview_round = 'Screen' then 1 else 0 end) as reached_screen,
        min(case when interview_round = 'Screen' then interview_date else null end) as screen_date,
        max(case when interview_round = 'Technical' then 1 else 0 end) as reached_tech,
        min(case when interview_round = 'Technical' then interview_date else null end) as tech_date,
        max(case when interview_round like '%Onsite%' then 1 else 0 end) as reached_onsite,
        min(case when interview_round like '%Onsite%' then interview_date else null end) as onsite_date,
        avg(candidate_feedback_score) as avg_candidate_experience_score,
        avg(score) as avg_interview_score,
        sum(duration_minutes) as total_interview_duration_minutes
    from {{ ref('stg_interviews') }}
    group by application_id
),

offer_stage as (
    select
        application_id,
        offer_id,
        offer_date,
        offer_status,
        base_salary,
        is_accepted,
        days_to_respond
    from {{ ref('stg_offers') }}
),

emp_stage as (
    select
        application_id,
        employee_id,
        hire_date
    from {{ ref('stg_employees') }}
)

select
    a.application_id,
    a.candidate_id,
    a.department_id,
    a.recruiting_source,
    a.application_date,
    a.candidate_stage,
    a.current_status,
    a.rejection_reason,
    
    -- Funnel progression milestone flags (Binary indicators)
    1 as stage_applied,
    coalesce(i.reached_screen, 0) as stage_screen,
    coalesce(i.reached_tech, 0) as stage_tech,
    coalesce(i.reached_onsite, 0) as stage_onsite,
    case when o.offer_id is not null then 1 else 0 end as stage_offer,
    coalesce(o.is_accepted, 0) as stage_hired,

    -- Milestone dates
    i.screen_date,
    i.tech_date,
    i.onsite_date,
    o.offer_date,
    e.hire_date,

    -- Stage-by-stage cycle times (days)
    case when i.screen_date is not null then {{ datediff_days('i.screen_date', 'a.application_date') }} else null end as days_app_to_screen,
    case when i.tech_date is not null and i.screen_date is not null then {{ datediff_days('i.tech_date', 'i.screen_date') }} else null end as days_screen_to_tech,
    case when i.onsite_date is not null and i.tech_date is not null then {{ datediff_days('i.onsite_date', 'i.tech_date') }} else null end as days_tech_to_onsite,
    case when o.offer_date is not null and i.onsite_date is not null then {{ datediff_days('o.offer_date', 'i.onsite_date') }} else null end as days_onsite_to_offer,
    case when e.hire_date is not null then {{ datediff_days('e.hire_date', 'a.application_date') }} else null end as total_time_to_hire_days,

    -- Quality & evaluation metrics
    i.avg_candidate_experience_score,
    i.avg_interview_score,
    i.total_interview_duration_minutes,
    o.base_salary,
    o.days_to_respond as offer_decision_days

from app_base a
left join interview_stages i on a.application_id = i.application_id
left join offer_stage o on a.application_id = o.application_id
left join emp_stage e on a.application_id = e.application_id
