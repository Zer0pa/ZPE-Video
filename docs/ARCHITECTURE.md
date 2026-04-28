<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="ARCHITECTURE AND THEORY" width="100%">
</p>

This repo packages two surfaces:

1. **Public surface (v0.1.0+): the perception-receipt library.** This is
   the commercial wedge. Zero-dependency core, pure stdlib, cross-writer
   bit-exact under default settings. See [`WEDGE.md`](WEDGE.md) for
   rationale and [`WIRE_FORMAT.md`](WIRE_FORMAT.md) for the spec.
2. **Internal research surface (subordinate): Wave-1 gate pipeline.**
   This is the historical research harness used to produce the
   falsification ledger. Not a product. Kept for reproducibility.

## Public surface — `zpe_video`

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Module</th>
      <th align="left">Role</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>src/zpe_video/receipt.py</code></td><td>Perception-receipt encode / decode / hash / verify. Zero deps.</td></tr>
    <tr><td><code>src/zpe_video/__init__.py</code></td><td>Public API surface; exports <code>PerceptionReceipt</code>, <code>Box</code>, and the functional helpers.</td></tr>
    <tr><td><code>tests/test_receipt.py</code></td><td>20 tests pinning round-trip, cross-writer bit-exactness, CRC integrity, and error behavior.</td></tr>
  </tbody>
</table>

### Public API (stable)

```python
from zpe_video import (
    Box,                     # dataclass: per-frame tracked detection
    PerceptionReceipt,       # dataclass: collection of per-frame Box lists
    encode_receipt,          # (receipt) -> bytes
    decode_receipt,          # (bytes) -> PerceptionReceipt
    receipt_hash,            # (bytes) -> str (sha256 hex)
    verify_receipt,          # (bytes, *, expected_hash=..., expected_peer_blob=...)
    read_receipt,            # (path) -> PerceptionReceipt
    write_receipt,           # (receipt, path) -> int (bytes written)
    WIRE_MAGIC,
    WIRE_VERSION,
    CrossWriterMismatch,
    ReceiptCorrupted,
)
```

No upstream runtime dependency. All types are pure Python dataclasses /
byte operations / stdlib hashlib + zlib + struct.

## Internal research surface — `zpe_video` (historical)

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Module</th>
      <th align="left">Role</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>src/zpe_video/codec.py</code></td><td>Legacy encode/decode (delta-encoded box stream; predecessor to the receipt module).</td></tr>
    <tr><td><code>src/zpe_video/fixtures.py</code></td><td>Deterministic proxy data generation for Wave-1 benchmarks.</td></tr>
    <tr><td><code>src/zpe_video/metrics.py</code></td><td>Metric helpers (ap_proxy, lpips_proxy) — historical; see kill verdicts.</td></tr>
    <tr><td><code>src/zpe_video/vision.py</code></td><td>Simple frame and sketch utilities.</td></tr>
    <tr><td><code>src/zpe_video/detector.py</code></td><td>Detector interface for the legacy pipeline.</td></tr>
    <tr><td><code>src/zpe_video/pipeline.py</code></td><td><code>Wave1Pipeline</code> — gate A/B/C/D/E runner; historical.</td></tr>
    <tr><td><code>scripts/execute_wave1.py</code></td><td>Runner entrypoint for the historical gate stack.</td></tr>
  </tbody>
</table>

The Wave-1 pipeline is subordinate to the receipt surface. It is kept
because the falsification ledger in
[`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md) references it, and
we do not delete the evidence behind our verdicts.

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

- Canonical research artifacts (PLAN.md, SUMMARY.md, BENCHMARK-REPORT.md
  per phase) live in the outer repository at `.gpd/phases/`.
- Full falsification and defend verdicts from the wedge-discovery phase
  are mirrored into this repo at [`docs/transparency/`](transparency/).
- Any claim in [`WEDGE.md`](WEDGE.md) is backed by a referenced
  transparency artifact. If the reference is missing, the claim is not
  defended.

<p>
  <img src="../.github/assets/readme/section-bars/dispatch-precedence.svg" alt="DISPATCH PRECEDENCE" width="100%">
</p>

Precedence rule for anyone reading this repo:

1. Byte-level behavior defined in [`WIRE_FORMAT.md`](WIRE_FORMAT.md) and
   pinned by `tests/test_receipt.py` is the highest authority.
2. [`WEDGE.md`](WEDGE.md) states what is commercially claimed.
3. [`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md) records what was
   tried and what was killed on evidence.
4. `docs/STATUS.md` and the outer `.gpd/STATE.md` record current
   position in the research program.
5. The root-level `README.md` is a front door; authoritative detail lives
   in the docs linked above.

Current runtime and test truth outrank any prose description, including
this document.
