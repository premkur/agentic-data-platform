# Technology and guardrails

## Stack
Snowflake (compute and storage), dbt Core (transformations and tests), GitHub Actions (CI/CD).

## Environments
- RAW: AGENTIC_RAW.ECOM. READ ONLY for you. Never write or alter raw tables.
- DEV: AGENTIC_DEV via `--target dev`. This is the only target you may run.
- PROD: AGENTIC_PROD. Deployed ONLY by GitHub Actions after a PR is merged.
  Never run dbt with `--target prod`. Never edit `.github/workflows/cd.yml`.

## Conventions
- Staging models are views prefixed `stg_`. Marts are tables prefixed `fct_` or `dim_`.
- Use CTEs, lower_snake_case, explicit column lists (no `select *` in marts).
- Every model needs a description and column tests (unique/not_null on keys,
  relationships to parents, accepted_values for enums). Put them in a .yml next to the model.
- Business logic must follow the glossary in product.md. If the intent is ambiguous, list the
  ambiguity in requirements.md as an open question instead of guessing silently.
- Never commit secrets, key files, or data/*.csv.

## Commands
- `dbt build --target dev --select <model>+`
- `python scripts/policy_check.py`

## Workflow
One spec per intent. Work on branch `feat/<intent-id>-<slug>`. Open a PR; never push to main.
