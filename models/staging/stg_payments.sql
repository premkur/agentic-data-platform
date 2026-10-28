-- Amounts are always positive; direction is determined by status (captured / refunded).
select
    payment_id,
    order_id,
    payment_ts,
    amount,
    lower(method) as method,
    lower(status) as status
from {{ source('ecom', 'payments') }}
