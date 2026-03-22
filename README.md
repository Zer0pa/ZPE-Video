# ZPE Video

ZPE Video is the Wave-1 video lane workspace extracted into a standalone private staging repo.

This repo is not a public release and it is not currently a green proof state.

## Current State

Snapshot date: `2026-03-22`

- Repo posture: private staging and science handoff mirror
- Latest Phase `09-09` verdict on the defended temporal surface: `bounded_signal_only`
- Latest Phase `09.1` run-of-record verdict: `flat_lane_still_dominant`
- Latest Phase `09.2` verdict on the defended layered-control-plane surface: `bounded_signal_only`
- Current inner-repo coherence check: `zpe_video.pipeline` imports cleanly and `tests/test_codec.py` passes (`2` tests)
- Active blocker class: the subordinate wedge gate is still red on the defended `MOT17Det` two-detector surface (`>= 50%` suppression with `>= 95%` retained utility)
- Current science handoff pack: `docs/inputs/2026-03-22_science_engineering_pack/`

If you need the current proof surface, start with `docs/inputs/2026-03-22_science_engineering_pack/` and `proofs/PROOF_INDEX.md`, not the older dossier/live-status claims.

## What This Repo Contains

- `src/zpe_video/`: the current Python package surface
- `scripts/execute_wave1.py`: the current lane runner
- `src/zpe_video/detector.py`: the repo-local detector surface used by the AM-C01 measurement utilities
- `scripts/measure_am_c01.py`: deterministic VisDrone-to-detector measurement harness
- `scripts/measure_am_c01_ladder.py`: sparse-representation ladder probe for AM-C01 style analysis
- `tests/`: lightweight codec smoke coverage
- `docs/`: repo front door, architecture, legal, verification, and FAQ docs
- `docs/inputs/2026-03-22_science_engineering_pack/`: compact scenario pack for the science engineering team
- `proofs/reference/2026-03-09_workspace_snapshot/`: curated evidence subset copied from the outer workspace

## What This Repo Does Not Claim

- It does not claim current `GO`.
- It does not claim public-release readiness.
- It does not claim a clean run-of-record inside this repo yet.
- It does not ship the raw datasets or the full mutable workspace artifact tree.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
python3 -m compileall src scripts
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
from zpe_video import Wave1Pipeline
print(Wave1Pipeline)
PY
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

Do not read a local gate pass as release truth. Phase 5 verification and clean-clone inspection are still deferred.

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
