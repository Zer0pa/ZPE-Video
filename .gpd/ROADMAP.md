# ZPE-Video — Phase Roadmap

**Lane:** ZPE-Video
**GPD retrofit date:** 2026-04-28

This roadmap is the canonical internal phase ledger. For the public-facing
version see `ROADMAP.md` at repo root.

## Phase Trail

| Phase | Title | Descriptive label | Canonical enum | Folder |
|---|---|---|---|---|
| 08 | Comparator expansion | killed | `FAIL` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09-09 | Architectural purification and contour primary recovery | `bounded_signal_only` | `INCONCLUSIVE` | [09-architectural-purification-and-contour-primary-recovery](PHASES/09-architectural-purification-and-contour-primary-recovery/) |
| 09.1 | Seedance-informed video subchannel factorization hypothesis | `flat_lane_still_dominant` | `INCONCLUSIVE` | [09.1-seedance-informed-video-subchannel-factorization-hypothesis](PHASES/09.1-seedance-informed-video-subchannel-factorization-hypothesis/) |
| 09.2 | Primitive-native layered control plane wedge | `bounded_signal_only` | `INCONCLUSIVE` | [09.2-primitive-native-layered-control-plane-wedge](PHASES/09.2-primitive-native-layered-control-plane-wedge/) |
| 09.3 | Narrow event-annotated surveillance wedge | `bounded_signal_only` | `INCONCLUSIVE` | [09.3-narrow-event-annotated-surveillance-wedge](PHASES/09.3-narrow-event-annotated-surveillance-wedge/) |
| 09.3.1 | Portal-anchored primitive event consumer on sparse facility crossing | `bounded_signal_only` | `INCONCLUSIVE` | [09.3.1-portal-anchored-primitive-event-consumer-on-sparse-facility-crossing](PHASES/09.3.1-portal-anchored-primitive-event-consumer-on-sparse-facility-crossing/) |
| 09.3.2 | Portal-local state machine | `retire_surface` | `SUSPENDED_BY_OWNER` | [09.3.2-portal-local-state-machine](PHASES/09.3.2-portal-local-state-machine/) |
| 09.4 | Repo public-surface hardening | complete | `PASS` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1–09.4.1.1.1 | Ground-state wedge audit + pod-backed archive-query benchmark | `bounded_signal_only` | `INCONCLUSIVE` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1.1.2 | Fair-baseline archive-query falsification | killed | `FAIL` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1.1.2.1-A | ROI / foveated sidecar | killed | `FAIL` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1.1.2.1-B | Cross-writer hash-stable receipt (Candidate B) | defended | `PASS` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1.1.2.1-C | State-layer enrichment (trajectory features) | defended-with-caveat | `PASS` | (pre-GPD; see `docs/TRANSPARENCY_JOURNEY.md`) |
| 09.4.1.1.2.2 | Receipt-core provenance benchmark and C2PA readiness | **ACTIVE** | `PASS` | `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/` |

## Verdict Enum Reference

- `PASS` — claim defended under falsification gate
- `FAIL` — claim falsified
- `INCONCLUSIVE` — tested, signal present but below gate; may be killed or bounded
- `UNTESTED` — not yet exercised
- `BLOCKED` — external dependency prevents execution
- `SUSPENDED_BY_OWNER` — owner decision to retire surface; no further execution planned
- `PAUSED_EXTERNAL` — waiting on external input
- `ACTIVE` — currently executing

## Notes on Descriptive Labels

The descriptive labels (`bounded_signal_only`, `flat_lane_still_dominant`,
`retire_surface`) are phase-specific shorthand from the authority packs. Each
is paired above with the canonical Zer0pa enum verdict that governs it.

- `bounded_signal_only` → `INCONCLUSIVE` (real signal present, below sovereign gate)
- `flat_lane_still_dominant` → `INCONCLUSIVE` (hypothesis tested, not confirmed)
- `retire_surface` → `SUSPENDED_BY_OWNER` (owner decision; not a test failure but a
  deliberate lane retirement after evidence of event heterogeneity as root cause)
