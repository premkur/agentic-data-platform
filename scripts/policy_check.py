#!/usr/bin/env python3
"""Deterministic guardrails that run in CI regardless of who (human or agent) wrote the code.

1. No PII columns (email, full_name) in models/marts.
2. Every model has a description and at least one column-level test.
"""
import pathlib
import re
import sys

import yaml

PII = re.compile(r"\b(email|full_name)\b", re.I)
errors = []

for sql in pathlib.Path("models/marts").glob("**/*.sql"):
    if PII.search(sql.read_text()):
        errors.append(f"{sql}: PII column referenced in a mart")

documented = {}
for yml in pathlib.Path("models").glob("**/*.yml"):
    for m in (yaml.safe_load(yml.read_text()) or {}).get("models", []):
        documented[m["name"]] = m

for sql in pathlib.Path("models").glob("**/*.sql"):
    m = documented.get(sql.stem)
    if not m or not m.get("description"):
        errors.append(f"{sql}: model missing a description in a .yml file")
    elif not any(c.get("data_tests") or c.get("tests") for c in m.get("columns", [])):
        errors.append(f"{sql}: model has no column tests")

if errors:
    print("POLICY CHECK FAILED"); [print(" -", e) for e in errors]; sys.exit(1)
print("Policy check passed")
