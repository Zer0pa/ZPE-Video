# ZPE Video

ZPE Video is the private Python package surface for the Video lane.

This repository is not a public release. It does not claim a commercial
readiness verdict, a current `GO`, or sovereign primitive-native closure.

## Current State

- Repo posture: private staging package.
- Tested package surface: deterministic codec encode/decode smoke coverage in
  `tests/test_codec.py`.
- Staged proof surface: historical custody snapshot indexed by
  `proofs/PROOF_INDEX.md`.
- Release posture: blocked until fresh clean-clone verification and
  repo-generated proof artifacts exist.

## What This Repo Contains

- `src/zpe_video/`: package code.
- `scripts/`: local runner and measurement utilities.
- `tests/`: lightweight codec smoke coverage.
- `docs/`: architecture, verification, legal boundary, and FAQ docs.
- `proofs/reference/2026-03-09_workspace_snapshot/`: curated historical
  evidence subset.

## What This Repo Does Not Claim

- It does not claim current `GO`.
- It does not claim public-release readiness.
- It does not claim a clean run-of-record generated inside this repo.
- It does not ship the raw datasets or the full mutable workspace artifact tree.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
python3 -m compileall src scripts
python3 -m unittest tests/test_codec.py -v
```

Current runner entrypoint:

```bash
python3 scripts/execute_wave1.py --gate B
```

Current measurement entrypoints:

```bash
python3 scripts/measure_am_c01.py --help
python3 scripts/measure_am_c01_ladder.py --help
```

Do not read a local smoke pass as release truth. Clean-clone inspection and
repo-generated proof artifacts are still required before any release claim.

## Verification And Boundaries

- Audit path: [AUDITOR_PLAYBOOK.md](AUDITOR_PLAYBOOK.md)
- Current limits: [PUBLIC_AUDIT_LIMITS.md](PUBLIC_AUDIT_LIMITS.md)
- Architecture map: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Verification notes: [docs/VERIFICATION.md](docs/VERIFICATION.md)
- Legal boundary: [docs/LEGAL_BOUNDARIES.md](docs/LEGAL_BOUNDARIES.md)
- Contribution rules: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security policy: [SECURITY.md](SECURITY.md)
- Support routing: [SUPPORT.md](SUPPORT.md)

## Operator Notes

- The repo uses IMC-style structure where it helps: front door, docs index, proof index, audit path, legal boundary, and private-first release gating.
- The repo does not copy IMC-specific runtime claims, Rust/Triton surfaces, or family-contract documents that do not belong to the Video lane.
