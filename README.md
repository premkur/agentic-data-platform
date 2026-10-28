# Agentic SDLC mini-prototype (Snowflake + dbt + Kiro + GitHub)

Goal: experience the loop **Intent -> Spec -> Plan -> Design -> Build -> Test -> Deploy -> Feedback**
on a small data platform, with humans approving at the right gates.

| Stage    | Where it lives                                  | Who acts                         |
|----------|--------------------------------------------------|----------------------------------|
| Intent   | `intents/NNN-*.md` or a GitHub issue (template)  | Human                            |
| Spec     | `.kiro/specs/<name>/requirements.md`             | Kiro drafts, human approves      |
| Design   | `.kiro/specs/<name>/design.md`                   | Kiro drafts, human approves      |
| Plan     | `.kiro/specs/<name>/tasks.md`                    | Kiro drafts, human approves      |
| Build    | dbt models/tests on branch `feat/...`            | Kiro executes tasks              |
| Test     | `dbt build --target dev`, then CI on the PR      | Kiro locally, GitHub Actions     |
| Deploy   | merge -> `cd.yml` -> AGENTIC_PROD                | GitHub Actions + human approval  |
| Feedback | `monitor.yml` opens an `intent` issue on failure | Automation -> human -> new intent|

Guardrails (read `.kiro/steering/*` and `scripts/policy_check.py`): least-privilege Snowflake roles,
agent limited to the DEV target, PII policy check in CI, PR-only changes, cost monitor on the warehouse.

## Setup (once)
1. Snowflake trial account; note your account identifier as `orgname-accountname`.
2. Key pair (Git Bash / WSL / macOS / Linux):
   ```
   mkdir -p ~/.snowflake
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out ~/.snowflake/agentic_key.p8 -nocrypt
   openssl rsa -in ~/.snowflake/agentic_key.p8 -pubout -out ~/.snowflake/agentic_key.pub
   ```
3. Paste the public key body into `scripts/setup_snowflake.sql` and run it in Snowsight as ACCOUNTADMIN.
4. Local env:
   ```
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt snowflake-connector-python
   export SNOWFLAKE_ACCOUNT=<orgname-accountname>
   export SNOWFLAKE_PRIVATE_KEY_PATH=~/.snowflake/agentic_key.p8
   export DBT_PROFILES_DIR=.
   ```
5. Data: `python scripts/generate_data.py && python scripts/load_data.py`
6. Verify: `dbt debug && dbt seed && dbt build` (dev target)
7. GitHub: push this repo, add secrets `SNOWFLAKE_ACCOUNT` and `SNOWFLAKE_PRIVATE_KEY`
   (full contents of the .p8 file), create environment `production`, protect `main` (require PR + passing CI).

## Run the loop
1. Open this folder in Kiro. Give it Intent 001 and start a spec.
2. Review and approve requirements, design, tasks. Let Kiro execute tasks.
3. Open a PR, watch CI, merge, watch CD.
4. Break it on purpose: `python scripts/generate_data.py --drift && python scripts/load_data.py`,
   then run the Monitor workflow manually. Take the issue it opens back to Kiro as Intent 002.

