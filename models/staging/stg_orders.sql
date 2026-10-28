-- Raw can contain several versions of an order (CDC-style); keep the latest.
select
    order_id,
    customer_id,
    order_ts,
    lower(status) as status,
    currency,
    updated_at
from {{ source('ecom', 'orders') }}
qualify row_number() over (partition by order_id order by updated_at desc) = 1
