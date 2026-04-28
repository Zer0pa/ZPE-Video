# Contributing

This repo follows a falsification-first contribution standard.

## Working Rules

- Negative findings are valid contributions.
- Do not turn mixed evidence into a pass narrative.
- Do not hardcode machine-local paths.
- Keep changes scoped and evidence-backed.
- If a change touches runtime claims, proof handling, or gate logic, update the relevant docs and proof notes.

## Before Opening A PR

Run the cheap checks first:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m compileall src scripts
python -m unittest tests/test_codec.py -v
bash scripts/compliance_audit.sh
```

If you change path resolution or bootstrap behavior, include the exact before/after evidence in your PR.

## What We Want

- path portability fixes
- dependency-contract cleanup
- repo-structure hardening
- verification/doc corrections
- negative findings with clear evidence

## What We Do Not Want

- new broad claims without rerun evidence
- path hacks tied to one machine
- cosmetic churn that does not improve install/run/audit clarity
- silent weakening of failing or paused evidence

## Licensing

`LICENSE` is the legal source of truth for contributions and usage.
