# Product and business context

Project: "Agentic Shop", a fictional online retailer used to prototype an agentic SDLC
on a Snowflake data platform. Stakeholders: Finance and Marketing analysts.

## Business glossary (source of truth)
- Gross revenue: sum of `captured` payment amounts.
- Refunds: sum of `refunded` payment amounts (stored as positive numbers).
- Net revenue: gross revenue minus refunds. Orders with status `cancelled` never count as revenue.
- Revenue is attributed to the order date (UTC date of `order_ts`), not the payment date.
- All amounts are USD.

## Data classification
- PII: `email`, `full_name`. PII may exist in staging but must NEVER appear in `models/marts`.
