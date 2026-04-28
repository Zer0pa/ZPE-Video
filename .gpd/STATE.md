# ZPE-Video — Operating State

**As of:** 2026-04-28
**Lane:** ZPE-Video
**Active phase:** `09.4.1.1.2.2` — receipt-core provenance benchmark and C2PA readiness
**Active phase verdict:** PASS

## Current Posture

| Coordinate | Value |
|---|---|
| Package version | `0.1.0` |
| Posture | `always-in-beta` |
| Commercial wedge | Cross-writer bit-exact AI-perception receipts |
| Sovereign gate | Red (not claimed closed; see `docs/WEDGE.md`) |
| Compass-8 substrate | Not used by this codec |

## Defended Wedge

**Cross-writer hash-stable perception receipt** (Phase 09.4.1.1.2.1 Candidate B).

Evidence:
- ZPE receipt hashes identically across two independent writer implementations
  under default settings
- Parquet pyarrow vs fastparquet hashes diverge under default settings
- 5-8x smaller and 15x faster cache-read than default-Parquet on bounded VideoQA subset
- Authority surface: `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`
- Transparency bundle: `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/`

## Killed Wedges (terminal)

| Wedge | Killed in | Reason |
|---|---|---|
| Universal video-codec superiority | Phase 08 | Lost to AV1, VVC, learned baselines on mAP@50 |
| Archive-query ZPE-specific | Phase 09.4.1.1.2 | Raw struct+zlib dominates on both storage and query latency |
| ROI / foveated sidecar | Phase 09.4.1.1.2.1-A | Lift is generic non-flat-QP, not packet-derived |

## Bounded / Retired Wedges

| Phase | Descriptive label | Canonical enum | Notes |
|---|---|---|---|
| 09-09 | `bounded_signal_only` | `INCONCLUSIVE` | Best >= 95% retention: 35.34% suppression (YOLOv8m) |
| 09.1 | `flat_lane_still_dominant` | `INCONCLUSIVE` | Bundle beats flat, loses to simpler temporal-only split |
| 09.2 | `bounded_signal_only` | `INCONCLUSIVE` | No layered policy reached >= 45% suppression |
| 09.3 | `bounded_signal_only` | `INCONCLUSIVE` | Two of four sparse VIRAT clips show no positive separation |
| 09.3.1 | `bounded_signal_only` | `INCONCLUSIVE` | Portal-local lift real (34.38% suppression) but LOOCV unstable |
| 09.3.2 | `retire_surface` | `SUSPENDED_BY_OWNER` | Sovereign gate still missed; event heterogeneity is root cause |

## Current Blockers

None blocking the v0.1.0 wedge surface.

Open decisions (non-blocking):
- PyPI publication (source-only install for now)
- `proofs/reference/2026-03-09_workspace_snapshot/` retention decision
- CI publish workflow secret audit (for future release cut)

## Next Move

Harden the cross-writer hash test against larger VideoQA surfaces
(LongVideoBench / NExT-QA spatial subsets); identify 1-2 buyer partners
(C2PA, video-LLM infra, regulated chain-of-custody).

## Tests and CI

| Surface | Count | Status |
|---|---|---|
| `tests/test_receipt.py` | 20 | Pass — CI covers Python 3.11/3.12/3.13 |
| `tests/test_manifest.py` | 7 | Pass |
| `tests/test_codec.py` | 2 | Pass |

Governing cross-writer conformance test:
`tests/test_receipt.py::test_cross_writer_independent_implementation_matches`
