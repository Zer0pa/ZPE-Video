# Phase 09.4.1.1.2.1 Verdict Synthesis

Date: 2026-04-17
Operator directive (2026-04-16): run all three candidates in parallel with
no pre-selection; let signal emerge from evidence.

## Wave-1 verdicts (verbatim)

### Candidate A — ROI/foveated guidance sidecar

**Verdict:** `kill`

**Measured:**
- Matched-bitrate mAP@50 relative gain (ROI lane): `+7.93%` over flat H.265
- Matched-bitrate mAP@50 relative gain (mean-importance control lane): `+7.93%`
- `roi_vs_mean_ratio`: `1.00`
- `roi_exceeds_2x_control`: `False`

**Rationale:** Non-flat QP allocation lifts mAP@50 over a flat H.265
baseline, but a spatially-uninformed mean-importance control lane produces
the identical lift. The packet carries no unique bitrate-allocation value
in the libx265 temporal-zone control regime. The lift is a generic
non-flat-QP property, not a packet-derived ROI property.

**Scope disclosure:** Run at 2-QP sweep × 1 encode repeat × 1 detector
repeat × 48 frames/clip after a full-scope run projected >8 hours
wall-clock. The structural finding `roi_vs_mean_ratio = 1.0` is
scope-invariant.

**Sovereign gate:** red, untouched.

### Candidate B — Video-LLM object-memory sidecar

**Verdict:** `defend`

**Measured:**
- Cross-writer hash stability (ZPE repo vs independent reference
  implementation): `True`
- Cross-writer hash stability (Parquet pyarrow vs Parquet fastparquet):
  `False`
- Storage: ZPE 961-2,970 B vs Parquet 5,044-25,242 B (4.5x-8.5x smaller)
- Cache-read latency: ZPE 0.30 ms vs Parquet 4.50 ms (15x faster)
- End-to-end latency: 2,087-2,194 ms (LLM-generation-dominated, ~97%)
- Answer accuracy parity across `none`, `parquet`, `zpe_packet`: 0.40 / 0.40 / 0.40 (max delta 0 pp)

**Rationale:** ZPE packet achieves the alt-defend branch of the plan
contract: matches Parquet on end-to-end latency at matched answer
accuracy AND uniquely produces bit-exact cross-writer hashes under
default settings. Also meets the cache-read-latency and storage
sub-branches.

**Scope disclosure:** Bounded deterministic VideoQA spatial subset (4
synthetic videos derived from the Phase 09.4.1.1.2 proxy plus
synthetic YOLOv8-shaped detector output; Qwen2.5-0.5B-Instruct LLM
with greedy decoding; N=11 cache-path latency, N=1 greedy generation).

**Sovereign gate:** red, untouched. Cross-writer hash stability is a
schema-level property, not a substrate-level property.

### Candidate C — Primitive-semantic enrichment

**Verdict:** `defend` (with small-sample caveat)

**Measured (LogReg + LightGBM agreement, stratified 5-fold CV,
3-seed robustness):**
- Joint (appearance + trajectory) classifier: precision=1.00,
  recall=1.00
- Trajectory-only classifier: precision=1.00, recall=1.00
- Appearance-only (LightGBM): precision=1.00, recall=1.00
- Appearance-only (LogReg): precision=1.00, recall=0.75 (fails
  recall >= 0.9)
- Shuffled-features control: near base rate as required
- Saturated-features control: reproduces naive-operator 0.138

**Rationale:** Richer per-track state (trajectory features alone, plus
frozen DINOv2-small appearance features) lifts operator precision from
0.138 (Phase 09.4.1.1.2 naive operator on same noisy proxy) to 1.00 at
recall=1.00. Classifier-family agreement and control ablations pass.

**Scope disclosure:** N=29 tracks (4 real facility-crossings + 25 ghost
tracks); `nan_fold_count=1` on the winning configurations (one CV fold
had 0 positives in test). Small-sample caveat: 1.00/1.00 should be read
as "separation is clean on the available sample" rather than a
statistically-powered benchmark.

**Sovereign gate:** red, untouched. The state-layer is the lever, NOT
ZPE as the carrier. Any sparse-metadata format can carry the same
features.

## Cross-verdict attribution

| Finding | Candidate | ZPE-specific? | State-layer? | Schema-level? | Substrate-level? |
| ------- | --------- | ------------- | ------------ | ------------- | ---------------- |
| Non-flat QP lifts matched-bitrate mAP | A (kill) | No | No | No | No |
| Cross-writer hash stability under defaults | B (defend) | Yes (vs default-Parquet) | No | Yes | No |
| Storage 5-8x smaller than default-Parquet | B (defend) | Mostly | No | Partial | No |
| Trajectory features lift precision | C (defend) | No | Yes | No | No |
| Appearance features help (LightGBM only) | C (defend) | No | Yes | No | No |

Only Candidate B has a ZPE-specific-at-the-schema-level property. None of
the three is at the substrate level. The Compass-8 primitive-native
sovereign gate remains red.

## What the operator selected

Per 2026-04-17 direction: Option 1 — pursue Candidate B (perception-receipt
wedge) as the commercial direction, executed with radical transparency
(ship the full research journey, including the kill verdicts and the
sovereign-gate-red status, alongside the commercial pick).

## What is explicitly NOT claimed

- Compass-8 primitive-native closure
- ROI/foveated-sidecar wedge (killed)
- Archive-query box-state wedge (killed in Phase 09.4.1.1.2)
- Universal video compression superiority (killed in Phase 8)
- A Parquet-will-never-be-stable claim (Parquet may be configurable to
  enforce deterministic output; the defend is specifically about DEFAULT
  settings)
- An LLM-latency-win claim (LLM generation dominates end-to-end latency)
- A statistically-powered Candidate-C lift (N=4 positives, small-sample)

## What IS claimed

The ZPE packet format uniquely produces bit-exact output across
independent writer implementations under default settings, which is a
documented deficiency of default-Parquet and default-JSON formats. A
buyer who specifically needs auditable, hash-stable "what the model saw"
receipts — e.g., C2PA AI-perception credentials, regulated chain-of-
custody, cross-platform LLM-memory caches with integrity requirements —
has a real structural reason to prefer the ZPE format over commodity
alternatives.

This is a narrow but defensible commercial wedge, subordinate to the
still-red sovereign Compass-8 primitive-native gate.
