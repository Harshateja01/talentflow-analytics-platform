{{ config(materialized='view') }}

with emp as (
    select
        employee_id,
        candidate_id,
        application_id,
        department_id,
        job_title,
        job_level,
        location,
        hire_date,
        employment_status,
        termination_date,
        manager_id,
        performance_rating,
        is_active,
        is_attrition,
        tenure_days
    from {{ ref('stg_employees') }}
),

apps as (
    select
        application_id,
        recruiting_source,
        application_date
    from {{ ref('stg_applications') }}
),

cands as (
    select
        candidate_id,
        highest_education,
        years_of_experience
    from {{ ref('stg_candidates') }}
),

offers as (
    select
        application_id,
        base_salary,
        bonus_pct,
        stock_units
    from {{ ref('stg_offers') }}
),

surveys as (
    select
        employee_id,
        avg(engagement_score) as avg_engagement_score,
        avg(satisfaction_score) as avg_satisfaction_score,
        avg(work_life_balance_score) as avg_wlb_score,
        avg(career_growth_score) as avg_career_growth_score,
        avg(manager_effectiveness_score) as avg_manager_effectiveness_score,
        count(survey_id) as total_surveys_taken
    from {{ ref('stg_engagement_surveys') }}
    group by employee_id
)

select
    e.employee_id,
    e.candidate_id,
    e.application_id,
    e.department_id,
    e.job_title,
    e.job_level,
    e.location,
    e.hire_date,
    e.employment_status,
    e.termination_date,
    e.manager_id,
    e.performance_rating,
    e.is_active,
    e.is_attrition,
    e.tenure_days,
    
    -- Categorical Tenure Bands
    case 
        when e.tenure_days < 90 then '< 3 Months'
        when e.tenure_days < 180 then '3 - 6 Months'
        when e.tenure_days < 365 then '6 - 12 Months'
        when e.tenure_days < 730 then '1 - 2 Years'
        else '2+ Years'
    end as tenure_band,

    -- Sourcing origin
    coalesce(a.recruiting_source, 'Direct / Careers Site') as recruiting_source,
    a.application_date,
    case when a.application_date is not null then {{ datediff_days('e.hire_date', 'a.application_date') }} else null end as time_to_hire_days,

    -- Experience & Compensation
    c.highest_education,
    c.years_of_experience,
    o.base_salary,
    o.bonus_pct,
    o.stock_units,

    -- Engagement & Sentiment
    coalesce(s.avg_engagement_score, null) as avg_engagement_score,
    coalesce(s.avg_satisfaction_score, null) as avg_satisfaction_score,
    coalesce(s.avg_wlb_score, null) as avg_wlb_score,
    coalesce(s.avg_career_growth_score, null) as avg_career_growth_score,
    coalesce(s.avg_manager_effectiveness_score, null) as avg_manager_effectiveness_score,
    coalesce(s.total_surveys_taken, 0) as total_surveys_taken

from emp e
left join apps a on e.application_id = a.application_id
left join cands c on e.candidate_id = c.candidate_id
left join offers o on e.application_id = o.application_id
left join surveys s on e.employee_id = s.employee_id
