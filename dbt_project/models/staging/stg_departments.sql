{{ config(materialized='view') }}

select
    trim(department_id) as department_id,
    trim(department_name) as department_name,
    trim(department_lead) as department_lead,
    trim(cost_center) as cost_center
from {{ source('talentflow_raw', 'departments') }}
