{{ config(materialized='view') }}

with ranked_interviews as (
    select
        interview_id,
        application_id,
        trim(interview_round) as interview_round,
        cast(interview_date as date) as interview_date,
        trim(interviewer_id) as interviewer_id,
        trim(interview_result) as interview_result,
        cast(score as integer) as score,
        cast(candidate_feedback_score as integer) as candidate_feedback_score,
        cast(duration_minutes as integer) as duration_minutes,
        row_number() over (
            partition by interview_id 
            order by interview_date desc
        ) as row_num
    from {{ source('talentflow_raw', 'interviews') }}
)

select
    interview_id,
    application_id,
    interview_round,
    interview_date,
    interviewer_id,
    interview_result,
    score,
    candidate_feedback_score,
    duration_minutes
from ranked_interviews
where row_num = 1
