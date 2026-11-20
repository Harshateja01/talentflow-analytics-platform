{{ config(materialized='table') }}

with hires as (
    select
        hire_month as reporting_month,
        department_id,
        count(employee_id) as new_hires_count
    from {{ ref('fct_employee_lifecycle') }}
    group by 1, 2
),

exits as (
    select
        termination_month as reporting_month,
        department_id,
        count(employee_id) as terminations_count
    from {{ ref('fct_employee_lifecycle') }}
    where is_attrition = 1 and termination_month is not null
    group by 1, 2
),

months_and_depts as (
    select reporting_month, department_id from hires
    union distinct
    select reporting_month, department_id from exits
),

dept as (
    select department_id, department_name, department_lead from {{ ref('stg_departments') }}
)

select
    m.reporting_month,
    m.department_id,
    d.department_name,
    d.department_lead,
    coalesce(h.new_hires_count, 0) as new_hires_count,
    coalesce(e.terminations_count, 0) as terminations_count,
    coalesce(h.new_hires_count, 0) - coalesce(e.terminations_count, 0) as net_headcount_change
from months_and_depts m
left join dept d on m.department_id = d.department_id
left join hires h on m.reporting_month = h.reporting_month and m.department_id = h.department_id
left join exits e on m.reporting_month = e.reporting_month and m.department_id = e.department_id
where m.reporting_month is not null
order by m.reporting_month desc, m.department_id
