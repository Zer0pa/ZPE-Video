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

ZPE Video is a compact, deterministic binary format for recording what a detector and tracker saw in a video. The format's one unique structural property is **cross-writer bit-exactness under default settings**: given identical per-frame box state, every conforming writer — in any language — emits the same bytes, so the SHA-256 of a receipt is a stable cryptographic reference to "what the model saw." The core library is pure stdlib; the wire format is implementable in under 100 lines of any language with `struct` / `zlib` / `crc32` primitives. Full research history, including every falsified broader claim, ships in [`docs/transparency/`](docs/transparency/).

| Field | Value |
|-------|-------|
| Architecture | VIDEO_RECEIPT_STREAM |
| Encoding | VIDEO_PERCEPTION_RECEIPT_V1 |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| CROSS_WRITER_HASH_STABLE | TRUE | vs default-Parquet FALSE |
| STORAGE_VS_DEFAULT_PARQUET | 0.18× | vs default-Parquet 1.00× |
| CACHE_READ_VS_DEFAULT_PARQUET | 0.067× | vs default-Parquet 1.00× |
| RECEIPT_MANIFEST_BINDING | TRUE | C2PA-style hash reference; receipt bytes unchanged |

> Source: [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`](docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json) and [`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json)

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

## What We Prove

- Bit-exact cross-writer output under default settings — pinned by [`tests/test_receipt.py::test_cross_writer_independent_implementation_matches`](tests/test_receipt.py), which hand-rolls an independent from-spec encoder and asserts byte-identical output.
- Per-frame CRC32 integrity on every decode; any corruption raises `ReceiptCorrupted` — pinned by [`tests/test_receipt.py::test_crc_mismatch_raises`](tests/test_receipt.py).
- Deterministic hash: `receipt_hash(blob)` = SHA-256 of the encoded bytes, stable across conforming writers — pinned by [`tests/test_receipt.py::test_receipt_hash_is_stable`](tests/test_receipt.py).
- Round-trip fidelity: `decode_receipt(encode_receipt(r))` recovers the same frame content up to canonical sort order — pinned by [`tests/test_receipt.py::test_round_trip_small`](tests/test_receipt.py).
- Zero runtime dependencies for the core `zpe_video.receipt` module — confirmed by installing the built wheel into a clean venv with no extras and running the import surface check ([`.github/workflows/verify-package.yml`](.github/workflows/verify-package.yml)).
- Full wire-format specification in [`docs/WIRE_FORMAT.md`](docs/WIRE_FORMAT.md) sufficient for third-party re-implementation.
- Full falsification history preserved alongside the defended wedge — every kill verdict is recorded in [`docs/TRANSPARENCY_JOURNEY.md`](docs/TRANSPARENCY_JOURNEY.md) and [`docs/transparency/`](docs/transparency/).

## What We Don't Claim

- We do not claim universal video-codec superiority. Falsified at Phase 08 against AV1, VVC, and learned baselines on both detector families; record preserved.
- We do not claim the archive-query-on-box-state surface is a ZPE-specific wedge. Falsified at Phase 09.4.1.1.2 against a 60-line raw-struct+zlib baseline; raw-struct+zlib strictly dominates ZPE on both storage and query latency for that workload.
- We do not claim the ROI/foveated-sidecar produces a packet-specific lift. Killed at Phase 09.4.1.1.2.1-A when a spatially-uninformed mean-importance control lane produced the identical +7.93% matched-bitrate mAP@50 lift.
- We do not claim Parquet cannot be configured to match. The wedge is specifically about **default settings**; Parquet tuned with enforced encoding and sorting can close the gap.
- We do not claim buyer-visible end-to-end latency win in video-LLM pipelines. LLM generation dominates ~97% of end-to-end time; the receipt's speed advantage is a storage/memory property.
- We do not claim the Compass-8 / 8-primitive directional-encoding architecture. This codec does not use it. The Compass-8 substrate is a research thesis that was tested in pre-0.1.0 phases and did not produce a defended product closure; the v0.1.0 product is the perception receipt, which stands on its own.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | STAGED |
| Commit SHA | d68a3da2ab8e |
| Confidence | 100% |
| Source | [`proofs/manifests/CURRENT_AUTHORITY_PACKET.md`](proofs/manifests/CURRENT_AUTHORITY_PACKET.md) |

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | Round-trip fidelity (small / empty / single-empty-frame) | PASS |
| V_02 | Same input yields byte-identical bytes | PASS |
| V_03 | Reordered input yields byte-identical bytes | PASS |
| V_04 | Independent from-spec encoder matches byte-for-byte | PASS |
| V_05 | `receipt_hash` stable across encodings | PASS |
| V_06 | CRC32 mismatch raises `ReceiptCorrupted` | PASS |
| V_07 | Bad magic / unsupported version / truncation / trailing bytes rejected | PASS |
| V_08 | `verify_receipt` hash + peer-blob match | PASS |
| V_09 | File write + read round-trip | PASS |
| V_10 | Frame-count mismatch / 255-box cap / signed-16 delta overflow raise | PASS |
| V_11 | Seed changes bytes but not decoded content | PASS |
| V_12 | Legacy codec smoke (`tests/test_codec.py`) | PASS |

> Source: run `uv run pytest tests -v`. All 29 tests pass on Python 3.11 locally; CI runs Python 3.11, 3.12, 3.13.

Receipt-core execution checks:

```bash
python scripts/receipt_core_benchmark.py
```

Expected: `verdict` is `pass`; generated artifacts land under
[`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/).
This benchmark verifies receipt cross-writer byte identity, C2PA-style
manifest binding, baseline disclosure, and explicit non-claims. It does
not execute Phase 10 or prove primitive-native closure.

## Proof Anchors

| Path | State |
|------|-------|
| [`docs/WEDGE.md`](docs/WEDGE.md) | VERIFIED |
| [`docs/WIRE_FORMAT.md`](docs/WIRE_FORMAT.md) | VERIFIED |
| [`docs/TRANSPARENCY_JOURNEY.md`](docs/TRANSPARENCY_JOURNEY.md) | VERIFIED |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | VERIFIED |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | VERIFIED |
| [`docs/STATUS.md`](docs/STATUS.md) | VERIFIED |
| [`docs/transparency/README.md`](docs/transparency/README.md) | VERIFIED |
| [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`](docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json) | VERIFIED |
| [`docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json`](docs/transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/cross_writer_hashes.json) | VERIFIED |
| [`docs/transparency/phase9_4_1_1_2_fair_baseline/summary.json`](docs/transparency/phase9_4_1_1_2_fair_baseline/summary.json) | VERIFIED |
| [`docs/transparency/research_ledger/VERDICT-SYNTHESIS.md`](docs/transparency/research_ledger/VERDICT-SYNTHESIS.md) | VERIFIED |
| [`docs/transparency/research_ledger/ranked_hypothesis_ladder.md`](docs/transparency/research_ledger/ranked_hypothesis_ladder.md) | VERIFIED |
| [`docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json`](docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json) | VERIFIED |
| [`proofs/manifests/CURRENT_AUTHORITY_PACKET.md`](proofs/manifests/CURRENT_AUTHORITY_PACKET.md) | VERIFIED |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | VERIFIED |
| [`src/zpe_video/receipt.py`](src/zpe_video/receipt.py) | VERIFIED |
| [`src/zpe_video/manifest.py`](src/zpe_video/manifest.py) | VERIFIED |
| [`tests/test_receipt.py`](tests/test_receipt.py) | VERIFIED |
| [`tests/test_manifest.py`](tests/test_manifest.py) | VERIFIED |
| [`CHANGELOG.md`](CHANGELOG.md) | VERIFIED |

## Repo Shape

| Field | Value |
|-------|-------|
| Package Name | `zpe-video` |
| Package Version | `0.1.0` |
| Python Compat | 3.11 / 3.12 / 3.13 |
| Core Runtime Deps | 0 (stdlib only) |
| Proof Anchors | 20 |
| Modality Lanes | 1 (video perception receipts) |
| Test Suite | 29 tests, all PASS |
| Authority Source | [`docs/WEDGE.md`](docs/WEDGE.md) |
| Wire Format Spec | [`docs/WIRE_FORMAT.md`](docs/WIRE_FORMAT.md) |
| Compass-8 / 8-primitive architecture | NOT USED by this codec (see [`docs/_reorientation/2026-04-17/NOVELTY_CARD.md`](docs/_reorientation/2026-04-17/NOVELTY_CARD.md)) |

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
