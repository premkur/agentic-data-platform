# Repository structure

- `intents/`            business intents (the "why"); one file per intent, numbered
- `.kiro/specs/`        Kiro specs per intent: requirements.md, design.md, tasks.md
- `.kiro/steering/`     persistent context and guardrails for the agent
- `models/staging/`     1:1 cleaned views over RAW sources
- `models/marts/`       business-facing tables (no PII)
- `seeds/`              small reference data (country aliases, country-to-region map)
- `macros/`             dbt macros (schema naming, CI cleanup)
- `scripts/`            data generator, loader, policy check
- `.github/workflows/`  ci.yml (PR), cd.yml (merge to main), monitor.yml (feedback loop)
