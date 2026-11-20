{{ config(materialized='view') }}

with ranked_employees as (
    select
        employee_id,
        candidate_id,
        application_id,
        trim(department_id) as department_id,
        trim(job_title) as job_title,
        trim(job_level) as job_level,
        trim(location) as location,
        cast(hire_date as date) as hire_date,
        trim(employment_status) as employment_status,
        cast(termination_date as date) as termination_date,
        cast(manager_id as {{ dbt.type_string() }}) as manager_id,
        cast(performance_rating as integer) as performance_rating,
        row_number() over (
            partition by employee_id 
            order by hire_date desc
        ) as row_num
    from {{ source('talentflow_raw', 'employees') }}
)

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
    case when employment_status = 'Active' then 1 else 0 end as is_active,
    case when employment_status in ('Terminated', 'Resigned') then 1 else 0 end as is_attrition,
    case 
        when termination_date is not null 
        then {{ datediff_days('termination_date', 'hire_date') }}
        else {{ datediff_days("cast('2025-12-31' as date)", 'hire_date') }}
    end as tenure_days
from ranked_employees
where row_num = 1
