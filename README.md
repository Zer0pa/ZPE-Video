# ZPE Video

## What This Is

ZPE Video is an independent video-structure encoding product for compact frame, sketch, motion, and detector-oriented video state. It is a Video lane codec surface, not a directional-primitive profile product, not a platform component, and not a generative video model.

The strongest historical proxy result currently committed here is `134.575x` compression against an H.265 proxy baseline, anchored at `proofs/reference/2026-03-09_workspace_snapshot/video_compression_benchmark.json`. That number is useful as a research signal, but it is not commercial closure: the same authority packet marks Gate A `FAIL` and overall workspace status `NO-GO` because proxy-only evidence cannot close the P0 compression claim.

The current repo is useful now for code inspection, package installation, deterministic codec smoke checks, and evidence custody. The open blocker is authority quality: fresh clean-clone reruns and repo-generated proof artifacts must replace the mixed historical workspace snapshot before any commercial-readiness pass is asserted.

| Field | Value |
|-------|-------|
| Architecture | VIDEO_STRUCTURE_STREAM |
| Encoding | VIDEO_ZPVID_V1 |

## Key Metrics

| Metric | Value | Baseline |
|---|---:|---|
| PROXY_COMPRESSION | 134.575x | H265_PROXY |
| CLAIM_PASS_COUNT | 5/8 | CLAIMS |
| DETERMINISM_REPLAY | 5/5 | HASHES |
| GATE_PASS_COUNT | 4/5 | GATES |

> Source: `proofs/reference/2026-03-09_workspace_snapshot/video_compression_benchmark.json`, `proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md`, `proofs/reference/2026-03-09_workspace_snapshot/determinism_replay_results.json`, and `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json`.

## What We Prove

- The package exposes an installable Python codec surface under `src/zpe_video/`, with deterministic encode/decode smoke coverage in `tests/test_codec.py`.
- The historical workspace snapshot records 5 PASS claims, 2 FAIL claims, and 1 PAUSED_EXTERNAL claim in `proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md`.
- The historical replay artifact records 5 identical hashes from 5 deterministic runs in `proofs/reference/2026-03-09_workspace_snapshot/determinism_replay_results.json`.
- The historical authority packet records Gates B, C, D, and E as PASS while Gate A remains FAIL in `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json`.
- The repo separates GitHub code/proof metadata from heavy video artifacts and checkpoints, which are preserved in Architect-Prime Hugging Face storage rather than committed into this repository.

## What We Don't Claim

- We do not claim commercial readiness.
- We do not claim a current `GO` verdict.
- We do not claim sovereign primitive-native closure.
- We do not claim directional-primitive profile architecture or portfolio-wide platform architecture for Video.
- We do not claim that proxy compression, proxy detection, or local smoke checks are enough to close the Video lane's authority gate.
- We do not claim that the commercial-safe generative decoder path is closed; the historical snapshot records VID-C006 as PAUSED_EXTERNAL.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Commit SHA | 9f9d2aab6980 |
| Source | `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json` |

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | `python -m unittest tests/test_codec.py -v` | PASS |
| V_02 | `python -m compileall src scripts` | PASS |
| V_03 | Historical Gate A authority check | FAIL |
| V_04 | Historical deterministic replay hash check | PASS |

## Proof Anchors

| Path | State |
|---|---|
| `proofs/PROOF_INDEX.md` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/README.md` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/quality_gate_scorecard.json` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/determinism_replay_results.json` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/video_compression_benchmark.json` | VERIFIED |
| `proofs/reference/2026-03-09_workspace_snapshot/video_generative_eval.json` | VERIFIED |

## Repo Shape

| Field | Value |
|---|---|
| Product | ZPE Video |
| Package | `zpe-video` / `zpe_video` |
| Proof Anchors | 8 |
| Modality Lanes | 1 |
| Authority Source | `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json` |
| Heavy Artifact Home | `Architect-Prime/zpe-video-artifacts` and `Architect-Prime/zpe-video-models` on Hugging Face |

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall src scripts
python -m unittest tests/test_codec.py -v
python scripts/execute_wave1.py --gate B
```

## Upcoming Workstreams

This section captures the active lane priorities - what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Clean-clone authority rerun** - Active Engineering. Execute the package from a fresh clone, write repo-generated proof artifacts under `proofs/reruns/`, and promote only after the rerun resolves the mixed historical snapshot boundary.
- **Gate A evidence replacement** - Research-Deferred - Investigation Underway. Replace proxy-only compression closure with a dataset-backed benchmark design that can decide VID-C001 without relying on proxy promotion.
- **Commercial-safe generative decoder closure** - Operations / External Dependency. Validate a commercial-safe decoder path before any VID-C006 pass claim can replace the current PAUSED_EXTERNAL state.
- **Heavy artifact retrieval playbook** - Active Engineering. Document exact Hugging Face recovery commands for `Architect-Prime/zpe-video-artifacts`, `Architect-Prime/zpe-video-models`, and `Architect-Prime/zeropa-org-ZPE-Video-scratch` without moving bulk bytes back into Git.
