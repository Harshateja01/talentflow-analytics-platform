{{ config(materialized='table') }}

with pipeline as (
    select
        application_month,
        department_id,
        department_name,
        recruiting_source,
        count(application_id) as total_applications,
        sum(stage_screen) as total_screens,
        sum(stage_tech) as total_tech_interviews,
        sum(stage_onsite) as total_onsites,
        sum(stage_offer) as total_offers_extended,
        sum(stage_hired) as total_hires,
        avg(total_time_to_hire_days) as avg_time_to_hire_days,
        avg(avg_candidate_experience_score) as avg_candidate_experience,
        avg(base_salary) as avg_offer_salary
    from {{ ref('fct_recruiting_pipeline') }}
    group by 1, 2, 3, 4
)

select
    application_month,
    department_id,
    department_name,
    recruiting_source,
    total_applications,
    total_screens,
    total_tech_interviews,
    total_onsites,
    total_offers_extended,
    total_hires,
    
    -- Conversion rates between adjacent stages
    round(total_screens * 100.0 / nullif(total_applications, 0), 1) as app_to_screen_rate_pct,
    round(total_tech_interviews * 100.0 / nullif(total_screens, 0), 1) as screen_to_tech_rate_pct,
    round(total_onsites * 100.0 / nullif(total_tech_interviews, 0), 1) as tech_to_onsite_rate_pct,
    round(total_offers_extended * 100.0 / nullif(total_onsites, 0), 1) as onsite_to_offer_rate_pct,
    round(total_hires * 100.0 / nullif(total_offers_extended, 0), 1) as offer_acceptance_rate_pct,
    round(total_hires * 100.0 / nullif(total_applications, 0), 2) as overall_funnel_efficiency_pct,

    round(avg_time_to_hire_days, 1) as avg_time_to_hire_days,
    round(avg_candidate_experience, 2) as avg_candidate_experience,
    round(avg_offer_salary, 0) as avg_offer_salary
from pipeline
