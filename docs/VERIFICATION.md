# Verification

This phase allows only minimal sanity.

## Allowed Low-Cost Checks

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 -m compileall src scripts
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
from zpe_video import Wave1Pipeline
print(Wave1Pipeline)
PY
```

Optional lightweight local smoke:

```bash
python3 -m unittest tests/test_codec.py
```

## What This Does Not Cover

- full gate reruns
- benchmark campaigns
- clean-clone verification
- dataset-backed replay
- public release checks

## Current Verification Truth

- The staged repo structure can be checked now.
- The staged proof subset can be inspected now.
- Clean rerun authority must be deferred to Phase 4.5 and Phase 5.

