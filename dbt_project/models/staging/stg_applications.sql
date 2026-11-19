{{ config(materialized='view') }}

with ranked_applications as (
    select
        application_id,
        candidate_id,
        job_id,
        -- Standardize dirty or inconsistent department values
        case 
            when department_id is null or trim(department_id) in ('', 'Unknown') then 'DEP-001'
            when lower(trim(department_id)) in ('eng', 'engineering') then 'DEP-001'
            when lower(trim(department_id)) in ('product', 'prod') then 'DEP-002'
            when lower(trim(department_id)) in ('sales', 'sales ') then 'DEP-003'
            when lower(trim(department_id)) in ('marketing', 'mktg') then 'DEP-004'
            when lower(trim(department_id)) in ('cs', 'customer success') then 'DEP-005'
            when lower(trim(department_id)) in ('g&a', 'ga') then 'DEP-006'
            when lower(trim(department_id)) in ('hr', 'people', 'hr dept') then 'DEP-007'
            when lower(trim(department_id)) in ('finance', 'fin') then 'DEP-008'
            when department_id in ('DEP-001', 'DEP-002', 'DEP-003', 'DEP-004', 'DEP-005', 'DEP-006', 'DEP-007', 'DEP-008') then department_id
            else 'DEP-001'
        end as department_id,
        coalesce(trim(recruiting_source), 'Direct / Careers Site') as recruiting_source,
        cast(application_date as date) as application_date,
        trim(candidate_stage) as candidate_stage,
        trim(current_status) as current_status,
        cast(rejection_reason as varchar) as rejection_reason,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at,
        row_number() over (
            partition by application_id 
            order by updated_at desc
        ) as row_num
    from {{ source('talentflow_raw', 'applications') }}
)

select
    application_id,
    candidate_id,
    job_id,
    department_id,
    recruiting_source,
    application_date,
    candidate_stage,
    current_status,
    rejection_reason,
    created_at,
    updated_at
from ranked_applications
where row_num = 1
