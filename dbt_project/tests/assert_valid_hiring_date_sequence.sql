-- Singular test: Assert valid hiring date sequences across pipeline and lifecycle marts.
-- A test fails in dbt if this query returns any records.

with invalid_pipeline_dates as (
    select
        application_id,
        candidate_id,
        application_date,
        hire_date,
        'Hire date is earlier than application date' as failure_reason
    from {{ ref('fct_recruiting_pipeline') }}
    where hire_date is not null
      and hire_date < application_date
),

invalid_lifecycle_dates as (
    select
        application_id,
        candidate_id,
        hire_date as application_date,
        termination_date as hire_date,
        'Termination date is earlier than hire date' as failure_reason
    from {{ ref('fct_employee_lifecycle') }}
    where termination_date is not null
      and termination_date < hire_date
)

select * from invalid_pipeline_dates
union all
select * from invalid_lifecycle_dates
