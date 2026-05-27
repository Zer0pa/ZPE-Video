# ZPE-Video

> Product-page mirror for `/encoding/ZPE-Video/`.
> Live public repo: [Zer0pa/ZPE-Video](https://github.com/Zer0pa/ZPE-Video).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
git clone https://github.com/Zer0pa/ZPE-Video.git
python -m pip install --upgrade pip uv
uv run pytest tests -v
uv run python examples/02_cross_writer.py   # expected: "cross-writer wedge: VERIFIED"
```

## Product Page Mirror

**Product-page title:** ZPE-Video · A perception receipt for AI video · Zer0pa

**Product-page description:** ZPE-Video · perception-receipt package for AI video pipelines · cross-writer SHA-stable on receipt cases · SHA-256 manifest binding · PyPI zpe-video 0.1.0 · not video compression

### Hero Translation

> 00 · ZPE-VIDEO · PERCEPTION RECEIPTDEVELOPER-READY · RECEIPT CORE OPEN See what AI really saw in video. A byte-identical perception receipt for AI video pipelines · ZPE-Video · PyPI zpe-video v0.1.0 · github.com/Zer0pa/ZPE-Video AI systems decide what gets flagged in video, who gets identified, what a generation model is trained on — and until now, no one outside the pipeline could check what the detector was actually shown. ZPE-Video is the record that closes that gap. Two independent Python writers, built from the same spec, produce a byte-identical perception receipt for the same frames. What the AI saw becomes a re-derivable record. This is not a video codec.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-Video/ |
| Live public repository | https://github.com/Zer0pa/ZPE-Video |
| Repo identity used here | ZPE-Video |
| Website display identity | ZPE-Video |
| Verdict | STAGED |
| Posture | private_initial_crafting_perception_receipts_schema_active |
| Headline metric | Lane in initial crafting; perception-receipts data shape established and the cleanest 10-zone fit per PRD §9.4 gate-page selection. |
| Honest blocker | Repo PRIVATE during initial crafting; full proof anchors will surface on visibility flip. Phase 1 perception-receipts schema is the active surface. |
| Mechanics asset from product page |  |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| CROSS_WRITER_HASH_STABLE | TRUE | vs default-Parquet FALSE |
| STORAGE_VS_DEFAULT_PARQUET | 0.18× | vs default-Parquet 1.00× |
| CACHE_READ_VS_DEFAULT_PARQUET | 0.067× | vs default-Parquet 1.00× |
| RECEIPT_MANIFEST_BINDING | TRUE | C2PA-style hash reference; receipt bytes unchanged |

## Proof Anchors

| Path | State |
| --- | --- |
| docs/WEDGE.md | VERIFIED |
| docs/WIRE_FORMAT.md | VERIFIED |
| docs/TRANSPARENCY_JOURNEY.md | VERIFIED |
| docs/QUICKSTART.md | VERIFIED |
| docs/ARCHITECTURE.md | VERIFIED |
| docs/STATUS.md | VERIFIED |

## What We Prove

- Bit-exact cross-writer output under default settings — pinned by tests/test_receipt.py::test_cross_writer_independent_implementation_matches, which hand-rolls an independent from-spec encoder and asserts byte-identical output.
- Per-frame CRC32 integrity on every decode; any corruption raises ReceiptCorrupted — pinned by tests/test_receipt.py::test_crc_mismatch_raises.
- Deterministic hash: receipt_hash(blob) = SHA-256 of the encoded bytes, stable across conforming writers — pinned by tests/test_receipt.py::test_receipt_hash_is_stable.
- Round-trip fidelity: decode_receipt(encode_receipt(r)) recovers the same frame content up to canonical sort order — pinned by tests/test_receipt.py::test_round_trip_small.
- Zero runtime dependencies for the core zpe_video.receipt module — confirmed by installing the built wheel into a clean venv with no extras and running the import surface check (.github/workflows/verify-package.yml).
- Full wire-format specification in docs/WIRE_FORMAT.md sufficient for third-party re-implementation.
- Full falsification history preserved alongside the defended wedge — every kill verdict is recorded in docs/TRANSPARENCY_JOURNEY.md and docs/transparency/.

## What We Do Not Claim

- We do not claim universal video-codec superiority. Falsified at Phase 08 against AV1, VVC, and learned baselines on both detector families; record preserved.
- We do not claim the archive-query-on-box-state surface is a ZPE-specific wedge. Falsified at Phase 09.4.1.1.2 against a 60-line raw-struct+zlib baseline; raw-struct+zlib strictly dominates ZPE on both storage and query latency for that workload.
- We do not claim the ROI/foveated-sidecar produces a packet-specific lift. Killed at Phase 09.4.1.1.2.1-A when a spatially-uninformed mean-importance control lane produced the identical +7.93% matched-bitrate mAP@50 lift.
- We do not claim Parquet cannot be configured to match. The wedge is specifically about default settings; Parquet tuned with enforced encoding and sorting can close the gap.
- We do not claim buyer-visible end-to-end latency win in video-LLM pipelines. LLM generation dominates ~97% of end-to-end time; the receipt's speed advantage is a storage/memory property.
- We do not claim the Compass-8 / 8-primitive directional-encoding architecture. This codec does not use it. The Compass-8 substrate is a research thesis that was tested in pre-0.1.0 phases and did not produce a defended product closure; the v0.1.0 product is the perception receipt, which stands on its own.

## Blockers / Failures

> Repo PRIVATE during initial crafting; full proof anchors will surface on visibility flip. Phase 1 perception-receipts schema is the active surface.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
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

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | docs/WEDGE.md |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Active Engineering | Promote the Phase 09.4.1.1.2.2 receipt-core provenance benchmark to a CI-anchored, repo-generated reproducibility surface. |
| Active Engineering | Maintain byte-identical output between the library writer and the independent from-spec writer; extend coverage to the full WIRE_FORMAT.md surface. |
| Research-Deferred — Investigation Underway | Define the C2PA manifest-binding shape that references a perception receipt by hash without embedding receipt bytes in the credential. |
| Operations / External Dependency | Promote CURRENT_AUTHORITY_PACKET.md to a tagged release-cut authority packet via authority_bundle.py and compliance audit. |

## Related Repos

- ZPE-Neuro — neural-recording spike-sorting and breadth adjudication.
- ZPE-Prosody — speech prosody and rhythm analysis.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-VIDEO · PERCEPTION RECEIPTDEVELOPER-READY · RECEIPT CORE OPEN See what AI really saw in video. A byte-identical perception receipt for AI video pipelines · ZPE-Video · PyPI zpe-video v0.1.0 · github.com/Zer0pa/ZPE-Video AI systems decide what gets flagged in video, who gets identified, what a generation model is trained on — and until now, no one outside the pipeline could check what the detector was actually shown. ZPE-Video is the record that closes that gap. Two independent Python writers, built from the same spec, produce a byte-identical perception receipt for the same frames. What the AI saw becomes a re-derivable record. This is not a video codec.

### Bento Cell 2

> 01 · THE GAPNO RECEIPT An AI processes video — but no one can check what it was actually shown.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS AI video market'33 · $42.3B Content detection / provenance'30 · $39.7B AI image + video generator'30 · $60.8B Video analyticsest. $12.4B AI content authenticationest. $3.1B Adjacent AI-video and provenance markets · hypothesis only; no adoption, compliance, or legal-sufficiency claim.

### Bento Cell 4

> 03 · VALUE $39.7B Content provenance is growing; ZPE-Video is a bounded Python receipt layer beneath that infrastructure, not a replacement for it.

### Bento Cell 5

> 04 · INSIGHT What AI saw in the video can now be checked.

### Bento Cell 6

> 05.1 · CURRENT TECHNO RECEIPT FORMAT Perception traces from AI video pipelines scatter across Parquet, JSON, pickle, and MCAP containers. There is no portable record format and no second writer that can independently rebuild the same bytes from the spec.

### Bento Cell 7

> 05.2 · OUR TECHBYTE-IDENTICAL RECEIPT zpe-video v0.1.0 ships a zero-dependency Python library with a documented wire format, per-frame CRC32, stable receipt hashes, and SHA-256 manifest binding. Two independent writers — one built from the spec by hand — produce byte-identical output across 3 receipt-core cases. The record is re-derivable, not just inspectable.

### Bento Cell 8

> 05.3 · BENCHMARKS3 RECEIPT-CORE CASES Cross-writer SHA3cases stable Manifest bind3cases verified Receipt corePASSnot sovereign PyPIv0.1.0connected Writer ASHA= Writer BSHA= ParquetMISS Benchmark: 961B vs Parquet 5,386B · 0.302ms vs 4.500ms · receipt scope only.

### Bento Cell 9

> 06 · MEASUREMENTRECEIPT VALIDATION Receipt evidence lives in bytes, hash, CRC, and manifest.

### Bento Cell 10

> 06.1 · COMPARATIVE RECEIPT VALIDATIONCROSS-WRITER SHA STABILITY Writer ASHA= Writer BSHA= Parquetnot stable Raw structnot receipt Two writers produce the same bytes on 3 receipt-core cases · manifest binding holds · Parquet and raw-struct comparators shown for reference · wider corpus coverage open. Source: proofs/artifacts/

### Bento Cell 11

> 07 · KEY METRICSPHASE 09.4 PROVENANCE

### Bento Cell 12

> 07.1 · CROSS-WRITER SHA 3CASES STABLE Two independent Python writers · byte-identical output

### Bento Cell 13

> 07.2 · MANIFEST BIND 3CASES VERIFIED SHA-256 receipt → manifest binding verified

### Bento Cell 14

> 07.3 · RECEIPT CORE PASS Receipt scope only · not full-video replay

### Bento Cell 15

> 07.4 · RELEASE v0.1.0 PyPI zpe-video · released 2026-05-04

### Bento Cell 16

> 07.5 · COMPRESSION NO No video-frame compression claim.

### Bento Cell 17

> 08 · DETERMINISMBYTE-EXACT RECEIPT Two independent Python writers, one byte-identical receipt.

### Bento Cell 18

> 08.1 · WHAT DETERMINISTIC MEANSRECEIPT SCOPE Deterministic means the same detector and tracker input plus the same wire-format spec produce a byte-identical perception receipt from two independent Python writers, with SHA-256 manifest binding verified on the same three receipt-core cases. Cross-writer SHA-stable measures the receipt only — it is not deterministic computer vision, deterministic LLM output, a legal evidence chain, full-video replay, or a competitor to AV1 or VVC. The scope is the record, and the scope is named.

### Bento Cell 19

> 08.2 · HONEST BLOCKER Honest Blocker · The receipt carries detector and tracker state — boxes, track IDs, timestamps, CRCs, manifest binding. It does not reconstruct pixels, appearance, or audio. Cross-runtime replay is open, C2PA integration is not in scope yet, and the PyPI v0.1.0 README still carries stale private-repo and video-codec wording.

### Bento Cell 20

> 09 WHAT THE MODEL SAW, ON THE RECORD.

### Bento Cell 21

> 09.1 · THE AMBITION The ambition is not to compete with video codecs. It is to make the question "what was this AI actually shown?" answerable by anyone who can run Python. When that record exists at intake, AI video systems stop being black boxes that decide on inputs no one else can inspect.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW Working today: byte-identical perception records, two independent Python writers, manifest-bound on three receipt-core cases.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN Still open: cross-runtime replay, C2PA integration, sovereign closure, and the v0.1.0 PyPI README cleanup.

### Bento Cell 24

> 09.4 · MODERATION · NEAR-TERM (12–24 MO) Moderation teams gain a re-derivable record A trust-and-safety lead reviewing a content-removal appeal can ask the pipeline what frames the detector actually saw, and a second engineer can rebuild the writer and confirm the same bytes. Disputes stop hinging on the platform's word alone.

### Bento Cell 25

> 09.5 · STORAGE · NEAR-TERM (12–24 MO) Detection logs shrink without losing the record A surveillance archive owner storing months of detector output keeps the same boxes, tracks, and timestamps at roughly a fifth of the storage footprint of default Parquet. The infrastructure bill drops without changing what the auditor can re-read later.

### Bento Cell 26

> 09.6 · PROVENANCE · MID-TERM (24–48 MO) Provenance standards get a perception layer Content-authentication standards like C2PA describe what was made; this describes what was seen on the way in. As both layers connect, a published video can be traced back to the exact detector inputs the producing pipeline acknowledged, not just the rendered output.

### Bento Cell 27

> 09.7 · INTEGRITY · MID-TERM (24–48 MO) Silent corruption stops reaching the model A video-LLM inference pipeline that accepts a corrupted detector record today produces a quietly wrong answer. With per-frame CRC checked on decode, corruption surfaces as a raised error at the gate, so a downstream operator notices before the bad inference reaches a user.

### Bento Cell 28

> 09.8 · GOVERNANCE · PARADIGM (48 MO+) AI video input becomes legally answerable Regulators, insurers, and courts asking what an AI was shown today get a shrug. When pipelines carry byte-identical perception records at intake, the question becomes answerable on demand, and AI-video liability shifts from speculation about model intent to inspection of recorded input.

</details>

---

Source mapping: product route `/encoding/ZPE-Video/` -> live public repo `Zer0pa/ZPE-Video`. README generated from product-page authority plus retained install/dev commands only.
