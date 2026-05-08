<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

# ZPE Video

Perception receipts for AI video pipelines. Cross-writer bit-exact under default settings. Zero runtime dependencies.

- Package: `zpe-video` v0.1.0
- Python: 3.11 / 3.12 / 3.13
- Repository: `https://github.com/Zer0pa/ZPE-Video`
- Contact: `architects@zer0pa.ai`

---

## What This Is

Perception-receipt video codec. Staged v0.1.0 receipt surface with explicit non-claims for C2PA and end-to-end latency.

## Codec Mechanics

| Field | Value |
| ------- | ------- |
| Architecture | VIDEO_RECEIPT_STREAM |
| Encoding | VIDEO_PERCEPTION_RECEIPT_V1 |
| Mechanics Asset | Not assigned |

## Key Metrics

| Metric | Value | Baseline |
| -------- | ------- | ---------- |
| CROSS_WRITER_HASH_STABLE | TRUE | vs default-Parquet FALSE |
| STORAGE_VS_DEFAULT_PARQUET | 0.18× | vs default-Parquet 1.00× |
| CACHE_READ_VS_DEFAULT_PARQUET | 0.067× | vs default-Parquet 1.00× |
| RECEIPT_MANIFEST_BINDING | TRUE | C2PA-style hash reference; receipt bytes unchanged |

> Source: [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`](docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json) and [`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json)

## Repo Identity

| Field | Value |
| ------- | ------- |
| Identifier | ZPE-Video |
| Repository | https://github.com/Zer0pa/ZPE-Video |
| Section | encoding |
| Visibility | PUBLIC |
| Architecture | VIDEO_RECEIPT_STREAM |
| Encoding | VIDEO_PERCEPTION_RECEIPT_V1 |
| Commit SHA | 73bc7de3 |
| License | SAL-7.1 |
| Authority Source | docs/WEDGE.md |

## Readiness

| Field | Value |
| ------- | ------- |
| Verdict | STAGED |
| Checks | 12/12 |
| Anchors | 6 display anchors |
| Commit | 73bc7de3 |
| Authority | docs/WEDGE.md |

### Honest Blocker

Cross-writer evidence is Python-to-Python only — multi-language portability is not proven. C2PA closure and end-to-end latency remain explicit non-claims. Not a universal video codec; falsified at Phase 08 against AV1, VVC, and learned baselines.

## What We Prove

- Bit-exact cross-writer output under default settings — pinned by tests/test_receipt.py::test_cross_writer_independent_implementation_matches, which hand-rolls an independent from-spec encoder and asserts byte-identical output.
- Per-frame CRC32 integrity on every decode; any corruption raises ReceiptCorrupted — pinned by tests/test_receipt.py::test_crc_mismatch_raises.
- Deterministic hash: receipt_hash(blob) = SHA-256 of the encoded bytes, stable across conforming writers — pinned by tests/test_receipt.py::test_receipt_hash_is_stable.
- Round-trip fidelity: decode_receipt(encode_receipt(r)) recovers the same frame content up to canonical sort order — pinned by tests/test_receipt.py::test_round_trip_small.
- Zero runtime dependencies for the core zpe_video.receipt module — confirmed by installing the built wheel into a clean venv with no extras and running the import surface check (.github/workflows/verify-package.yml).
- Full wire-format specification in docs/WIRE_FORMAT.md sufficient for third-party re-implementation.
- Full falsification history preserved alongside the defended wedge — every kill verdict is recorded in docs/TRANSPARENCY_JOURNEY.md and docs/transparency/.

## What We Don't Claim

- We do not claim universal video-codec superiority. Falsified at Phase 08 against AV1, VVC, and learned baselines on both detector families; record preserved.
- We do not claim the archive-query-on-box-state surface is a ZPE-specific wedge. Falsified at Phase 09.4.1.1.2 against a 60-line raw-struct+zlib baseline; raw-struct+zlib strictly dominates ZPE on both storage and query latency for that workload.
- We do not claim the ROI/foveated-sidecar produces a packet-specific lift. Killed at Phase 09.4.1.1.2.1-A when a spatially-uninformed mean-importance control lane produced the identical +7.93% matched-bitrate mAP@50 lift.
- We do not claim Parquet cannot be configured to match. The wedge is specifically about default settings; Parquet tuned with enforced encoding and sorting can close the gap.
- We do not claim buyer-visible end-to-end latency win in video-LLM pipelines. LLM generation dominates ~97% of end-to-end time; the receipt's speed advantage is a storage/memory property.
- We do not claim the Compass-8 / 8-primitive directional-encoding architecture. This codec does not use it. The Compass-8 substrate is a research thesis that was tested in pre-0.1.0 phases and did not produce a defended product closure; the v0.1.0 product is the perception receipt, which stands on its own.

## Verification Status

| Code | Check | Verdict |
| ------ | ------- | --------- |
| V_01 | Round-trip fidelity (small / empty / single-empty-frame) | PASS |
| V_02 | Same input yields byte-identical bytes | PASS |
| V_03 | Reordered input yields byte-identical bytes | PASS |
| V_04 | Independent from-spec encoder matches byte-for-byte | PASS |
| V_05 | receipt_hash stable across encodings | PASS |
| V_06 | CRC32 mismatch raises ReceiptCorrupted | PASS |
| V_07 | Bad magic / unsupported version / truncation / trailing bytes rejected | PASS |
| V_08 | verify_receipt hash + peer-blob match | PASS |
| V_09 | File write + read round-trip | PASS |
| V_10 | Frame-count mismatch / 255-box cap / signed-16 delta overflow raise | PASS |
| V_11 | Seed changes bytes but not decoded content | PASS |
| V_12 | Legacy codec smoke (tests/test_codec.py) | PASS |

## Proof Anchors

| Path | State |
| ------ | ------- |
| `docs/WEDGE.md` | VERIFIED |
| `docs/WIRE_FORMAT.md` | VERIFIED |
| `docs/TRANSPARENCY_JOURNEY.md` | VERIFIED |
| `docs/QUICKSTART.md` | VERIFIED |
| `docs/ARCHITECTURE.md` | VERIFIED |
| `docs/STATUS.md` | VERIFIED |

## Repo Shape

| Field | Value |
| ------- | ------- |
| Proof Anchors | 6 display anchors |
| Modality Lanes | 1 |
| Architecture | VIDEO_RECEIPT_STREAM |
| Encoding | VIDEO_PERCEPTION_RECEIPT_V1 |
| Verification | 12/12 checks |
| Authority Source | docs/WEDGE.md |

## Competitive Benchmarks

| Format | Cross-Writer Hash (default) | Per-Frame CRC32 | Storage / video | Notes |
|--------|-----------------------------|-----------------|-----------------|-------|
| **ZPE-Video** | **TRUE (byte-identical)** | **YES** | **~1.1 KB** | Zero runtime deps, schema-enforced |
| Parquet (pyarrow, defaults) | FALSE | NO | ~5.4 KB | Diverges vs fastparquet on same input |
| Parquet (fastparquet, defaults) | FALSE | NO | ~5.0 KB | Diverges vs pyarrow on same input |
| JSON + gzip | Stable if key-sorted | NO | ~2.4 KB | No framing, larger, tool-dependent |
| raw struct + zlib | Stable | NO | ~0.3 KB | No CRC, no schema, no versioning |

> Source: [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json`](docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json) and [`docs/transparency/phase9_4_1_1_2_fair_baseline/summary.json`](docs/transparency/phase9_4_1_1_2_fair_baseline/summary.json)

Raw struct + zlib is smaller in raw bytes but has no per-frame CRC32, no schema, no versioning — unsuitable as a receipt. ZPE is the smallest format that is also cross-writer stable under defaults AND carries integrity.

## Quick Start

```bash
git clone https://github.com/Zer0pa/ZPE-Video.git
cd ZPE-Video
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip uv
uv sync --extra dev
uv run pytest tests -v
uv run python examples/02_cross_writer.py   # expected: "cross-writer wedge: VERIFIED"
```

Expected: 29/29 tests pass; the cross-writer example prints `cross-writer wedge: VERIFIED` with byte-identical output from the library and an independent from-spec encoder.

---

## Ecosystem

ZPE Video is one lane in a broader family of ZPE repositories. Each lane follows the same evidence-first discipline: narrow wedges, preserved kill verdicts, cross-writer or cross-implementation determinism where it's the load-bearing product property.

- [`ZPE-Neuro`](https://github.com/Zer0pa/ZPE-Neuro) — neural-recording spike-sorting and breadth adjudication.
- [`ZPE-Prosody`](https://github.com/Zer0pa/ZPE-Prosody) — speech prosody and rhythm analysis.

Common conventions: stdlib-heavy cores, deterministic binary artifacts, explicit non-claims, and falsification ledgers shipped alongside defended wedges.

## Who This Is For

- **Platform teams building AI perception pipelines** who need an auditable "what was seen" record that survives platform migration without re-running the detector.
- **Regulated video workflows** (police body-worn cameras, insurance fraud, legal discovery) that need to disclose track state without disclosing pixels.
- **C2PA implementers** who want a tiny, stable, binary artifact to reference by hash from a Content Credentials manifest.
- **Video-LLM / VideoRAG infrastructure** needing integrity-guaranteed, cross-platform object-memory caches.
- **ML teams** redistributing detection output as training data across languages and toolchains.

Not for teams that need full-fidelity video compression, perceptual video quality, or a VMS replacement. See [`docs/WEDGE.md`](docs/WEDGE.md) for the full buyer-shape list and non-claims.

## Upcoming Workstreams

Active lane priorities under the `0.1.0` perception-receipt wedge. Cadence is continuous, not milestoned. Open items, falsification routes, and decision criteria live in [`docs/_reorientation/2026-04-17/OPEN_QUESTIONS.md`](docs/_reorientation/2026-04-17/OPEN_QUESTIONS.md) and the synthesis docs under [`docs/transparency/research_ledger/`](docs/transparency/research_ledger/).

- **Receipt-core provenance benchmark adoption** — Active. Promote the Phase `09.4.1.1.2.2` receipt-core provenance benchmark from internal transparency bundle to a CI-anchored, repo-generated reproducibility surface. See [`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/).
- **Cross-writer-stable hash defense** — Active. Maintain byte-identical output between the library writer and the independent from-spec writer in [`examples/02_cross_writer.py`](examples/02_cross_writer.py); extend coverage to the full `WIRE_FORMAT.md` surface.
- **C2PA Content Credentials binding** — Research-Deferred. Define the manifest-binding shape that lets a C2PA producer reference a perception receipt by hash without embedding receipt bytes in the credential. See [`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/manifest_binding.json`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/manifest_binding.json).
- **Authority-packet promotion** — Operations. Move `proofs/manifests/CURRENT_AUTHORITY_PACKET.md` from staged state to a release-cut authority packet bound to a tagged version; gate via [`scripts/authority_bundle.py`](scripts/authority_bundle.py) and [`scripts/compliance_audit.sh`](scripts/compliance_audit.sh).

---
