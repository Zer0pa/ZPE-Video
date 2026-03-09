# Auditor Playbook

This is the shortest honest audit path for the private ZPE Video staging repo.

It verifies structure and current known state. It does not establish release readiness.

## What You Can Verify Quickly

- the repo installs as a Python package
- the package imports cleanly
- the lightweight code surface compiles
- the staged proof snapshot is present
- the current known verdict is still `NO-GO`

## Shortest Audit Path

1. Create a local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

2. Run near-zero-cost sanity:

```bash
python3 -m compileall src scripts
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
from zpe_video import Wave1Pipeline
print(Wave1Pipeline)
PY
```

3. Inspect the staged proof snapshot:

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

- Current repo state is private staging.
- Current full workspace snapshot verdict is `NO-GO`.
- The staged proof subset is historical/current-workspace evidence, not a clean rerun generated from this repo.
- A later resource-only probe touched `resource_inventory.json`, so the copied snapshot is mixed and cannot be promoted as a clean run-of-record.

## What Is Explicitly Deferred

- broad reruns
- clean-clone verification
- benchmark/performance campaigns
- public release posture

Those belong to Phase 4.5 and Phase 5, not this staging phase.

