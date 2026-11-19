{{ config(materialized='view') }}

with candidate_apps as (
    select
        c.candidate_id,
        c.full_name,
        c.email,
        c.location,
        c.highest_education,
        c.years_of_experience,
        count(a.application_id) as total_applications,
        count(distinct a.department_id) as distinct_departments_applied,
        min(a.application_date) as first_application_date,
        max(a.application_date) as latest_application_date,
        max(case when a.candidate_stage = 'Hired' then 1 else 0 end) as is_ever_hired
    from {{ ref('stg_candidates') }} c
    left join {{ ref('stg_applications') }} a on c.candidate_id = a.candidate_id
    group by 1, 2, 3, 4, 5, 6
)

select
    candidate_id,
    full_name,
    email,
    location,
    highest_education,
    years_of_experience,
    total_applications,
    distinct_departments_applied,
    first_application_date,
    latest_application_date,
    is_ever_hired
from candidate_apps
