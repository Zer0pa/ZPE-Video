# Auditor Playbook

This is the shortest honest audit path for ZPE Video.

It verifies structure and current known state. It does not establish commercial readiness.

## What You Can Verify Quickly

- the repo installs as a Python package
- the package imports cleanly
- the lightweight code surface compiles
- the deterministic codec smoke test passes
- the historical proof snapshot is present
- the current known verdict remains BLOCKED by Gate A

## Shortest Audit Path

1. Create a local environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

2. Run low-cost sanity:

```bash
python -m compileall src scripts
python -m unittest tests/test_codec.py -v
bash scripts/compliance_audit.sh
```

3. Inspect the proof snapshot:

- `proofs/PROOF_INDEX.md`
- `proofs/reference/2026-03-09_workspace_snapshot/README.md`
- `proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md`
- `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json`
- `proofs/reference/2026-03-09_workspace_snapshot/quality_gate_scorecard.json`

4. Read the current limits before making claims:

- `PUBLIC_AUDIT_LIMITS.md`
- `docs/VERIFICATION.md`
- `docs/LEGAL_BOUNDARIES.md`

## Current Expected Truth

- Current full workspace snapshot verdict is `NO-GO`.
- Commercial readiness is BLOCKED in the README parser enum.
- The proof subset is historical workspace evidence, not a clean rerun generated from this repo.
- Heavy artifacts and checkpoints live on Architect-Prime Hugging Face storage.

## What Is Open

- clean-clone verification
- dataset-backed benchmark replay
- Gate A evidence replacement
- commercial-safe generative decoder closure

