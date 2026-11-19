{{ config(materialized='table') }}

with interviews as (
    select
        i.interview_id,
        i.application_id,
        i.interview_round,
        i.interview_date,
        i.interviewer_id,
        i.interview_result,
        i.score,
        i.candidate_feedback_score,
        i.duration_minutes,
        a.department_id,
        d.department_name,
        a.recruiting_source,
        a.candidate_stage,
        a.current_status
    from {{ ref('stg_interviews') }} i
    join {{ ref('stg_applications') }} a on i.application_id = a.application_id
    left join {{ ref('stg_departments') }} d on a.department_id = d.department_id
)

select
    interview_id,
    application_id,
    department_id,
    department_name,
    recruiting_source,
    interview_round,
    interview_date,
    interviewer_id,
    interview_result,
    score,
    candidate_feedback_score,
    duration_minutes,
    candidate_stage,
    current_status,
    case 
        when candidate_feedback_score >= 4 then 'Positive'
        when candidate_feedback_score = 3 then 'Neutral'
        else 'Negative'
    end as experience_sentiment
from interviews
