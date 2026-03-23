<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

This is the shortest honest audit path for the live ZPE Video repo.

It verifies structure and current known state. It does not establish
release readiness.

What you can verify quickly:

- the repo installs as a Python package
- the package imports cleanly
- the lightweight code surface compiles
- the staged proof snapshot is present
- the current staged truth is still `09.3.2 = retire_surface`

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

1. Create a local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

2. Run low-cost sanity:

```bash
python3 -m compileall src scripts
pytest tests/test_codec.py
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
from zpe_video import Wave1Pipeline
print(Wave1Pipeline)
PY
```

3. Inspect the current authority routes:

- `docs/STATUS.md`
- `proofs/PROOF_INDEX.md`
- `docs/inputs/status-notes/2026-03-23_phase09_3_2_retire_surface/`
- `proofs/reference/2026-03-09_workspace_snapshot/`

4. Read the limits before making claims:

- `PUBLIC_AUDIT_LIMITS.md`
- `docs/VERIFICATION.md`
- `docs/LEGAL_BOUNDARIES.md`

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

Current expected truth:

- repo state is `staging_only`
- sparse VIRAT facility-crossing surface is `retire_surface`
- the proof subset is historical evidence custody, not a clean repo rerun
- the proof snapshot is mixed because `resource_inventory.json` was touched later

Explicitly deferred:

- broad reruns
- clean-clone verification
- benchmark campaigns
- public release posture
