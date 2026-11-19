{{ config(materialized='view') }}

with ranked_surveys as (
    select
        survey_id,
        employee_id,
        cast(survey_date as date) as survey_date,
        cast(engagement_score as numeric) as engagement_score,
        cast(satisfaction_score as numeric) as satisfaction_score,
        cast(work_life_balance_score as numeric) as work_life_balance_score,
        cast(career_growth_score as numeric) as career_growth_score,
        cast(manager_effectiveness_score as numeric) as manager_effectiveness_score,
        row_number() over (
            partition by survey_id 
            order by survey_date desc
        ) as row_num
    from {{ source('talentflow_raw', 'engagement_surveys') }}
)

select
    survey_id,
    employee_id,
    survey_date,
    engagement_score,
    satisfaction_score,
    work_life_balance_score,
    career_growth_score,
    manager_effectiveness_score,
    round(
        (engagement_score + satisfaction_score + work_life_balance_score + career_growth_score + manager_effectiveness_score) / 5.0, 
        2
    ) as overall_sentiment_score
from ranked_surveys
where row_num = 1
