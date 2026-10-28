with src as (
    select * from {{ source('ecom', 'customers') }}
),

cleaned as (
    select
        customer_id,
        lower(trim(email))      as email,
        trim(full_name)         as full_name,
        upper(trim(country))    as country_raw,
        signup_date,
        marketing_opt_in
    from src
)

select
    c.customer_id,
    c.email,
    c.full_name,
    coalesce(a.country_code, 'UNKNOWN') as country_code,
    c.signup_date,
    c.marketing_opt_in
from cleaned c
left join {{ ref('country_aliases') }} a
    on c.country_raw = upper(a.alias)
