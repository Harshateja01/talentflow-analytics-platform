{{ config(materialized='view') }}

select
    trim(source_id) as source_id,
    trim(source_name) as source_name,
    trim(source_channel) as source_channel,
    cast(cost_per_posting as numeric) as cost_per_posting
from {{ source('talentflow_raw', 'recruiting_sources') }}
