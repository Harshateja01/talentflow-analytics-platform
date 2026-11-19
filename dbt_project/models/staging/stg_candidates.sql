{{ config(materialized='view') }}

with ranked_candidates as (
    select
        candidate_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        concat(trim(first_name), ' ', trim(last_name)) as full_name,
        lower(trim(email)) as email,
        coalesce(trim(phone), 'Unknown') as phone,
        trim(location) as location,
        trim(highest_education) as highest_education,
        cast(years_of_experience as integer) as years_of_experience,
        cast(created_at as timestamp) as created_at,
        row_number() over (
            partition by candidate_id 
            order by created_at desc
        ) as row_num
    from {{ source('talentflow_raw', 'candidates') }}
)

select
    candidate_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    location,
    highest_education,
    years_of_experience,
    created_at
from ranked_candidates
where row_num = 1
