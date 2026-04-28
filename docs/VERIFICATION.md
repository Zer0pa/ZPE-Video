# Verification

## Low-Cost Checks

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m compileall src scripts
python -m unittest tests/test_codec.py -v
bash scripts/compliance_audit.sh
```

## What These Checks Cover

- package installation from the clone root
- deterministic codec smoke behavior
- parser-safe README shape
- proof-anchor path existence
- basic Python syntax compilation

## What These Checks Do Not Cover

- full gate reruns
- benchmark campaigns
- dataset-backed replay
- blind external reproduction
- commercial-readiness closure

## Current Verification Truth

The repo can be inspected, installed, and smoke-tested. Commercial authority remains BLOCKED until clean reruns generate fresh proof artifacts under `proofs/reruns/` and replace the mixed historical authority surface.

