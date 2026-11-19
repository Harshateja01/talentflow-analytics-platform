{{ config(materialized='view') }}

with ranked_offers as (
    select
        offer_id,
        application_id,
        cast(offer_date as date) as offer_date,
        trim(offer_status) as offer_status,
        cast(base_salary as numeric) as base_salary,
        cast(bonus_pct as numeric) as bonus_pct,
        cast(stock_units as integer) as stock_units,
        cast(offer_response_date as date) as offer_response_date,
        coalesce(trim(cast(decline_reason as varchar)), 'Not Applicable') as decline_reason,
        row_number() over (
            partition by offer_id 
            order by offer_date desc
        ) as row_num
    from {{ source('talentflow_raw', 'offers') }}
)

select
    offer_id,
    application_id,
    offer_date,
    offer_status,
    base_salary,
    bonus_pct,
    stock_units,
    offer_response_date,
    decline_reason,
    case 
        when offer_status = 'Accepted' then 1 
        else 0 
    end as is_accepted,
    case
        when offer_response_date is not null 
        then {{ datediff_days('offer_response_date', 'offer_date') }}
        else null
    end as days_to_respond
from ranked_offers
where row_num = 1
