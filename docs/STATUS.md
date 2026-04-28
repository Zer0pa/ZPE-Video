<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

Current state (2026-04-24):

- Package version: <code>0.1.0</code>
- Posture: <code>always-in-beta</code> (useful now, improving continuously)
- Selected commercial wedge: perception-receipt format for AI video pipelines
- Compass-8 / 8-primitive architecture: <code>not used by this codec</code> (see <a href="_reorientation/2026-04-17/NOVELTY_CARD.md"><code>NOVELTY_CARD.md</code></a>)
- Most recent research phase: <code>09.4.1.1.2.2 = receipt-core provenance benchmark and C2PA readiness</code>

<p>
  <img src="../.github/assets/readme/section-bars/lane-status-snapshot.svg" alt="LANE STATUS SNAPSHOT" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Coordinate</th>
      <th align="left">Current value</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Public wedge claim</td><td>Cross-writer bit-exact AI-perception receipts (<a href="WEDGE.md">WEDGE.md</a>)</td></tr>
    <tr><td>Public wedge evidence</td><td>Phase 09.4.1.1.2.1 Candidate B — defend, plus Phase 09.4.1.1.2.2 receipt-core provenance benchmark (<a href="transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/">transparency bundle</a>)</td></tr>
    <tr><td>Archive-query wedge</td><td>killed on fair commercial baseline (Phase 09.4.1.1.2)</td></tr>
    <tr><td>ROI / foveated sidecar wedge</td><td>killed; lift is non-flat-QP property, not packet-derived (Phase 09.4.1.1.2.1-A)</td></tr>
    <tr><td>Universal video-codec superiority claim</td><td>killed on comparator expansion (Phase 08)</td></tr>
    <tr><td>State-layer enrichment (trajectory features)</td><td>defended as engineering insight, not as ZPE-specific wedge (Phase 09.4.1.1.2.1-C)</td></tr>
    <tr><td>Compass-8 primitive-native substrate thesis</td><td>historical; tested and not closed as a product goal for this codec (see <a href="TRANSPARENCY_JOURNEY.md"><code>TRANSPARENCY_JOURNEY.md</code></a>)</td></tr>
    <tr><td>Public test surface</td><td><code>tests/test_receipt.py</code> (20) + <code>tests/test_manifest.py</code> (7) + <code>tests/test_codec.py</code> (2); all pass on Python 3.11 locally, CI covers 3.11/3.12/3.13</td></tr>
    <tr><td>Package install</td><td><code>uv sync --extra dev</code> from source; no upstream deps for the core receipt surface</td></tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

This repo can establish:

- The exact byte format of the perception receipt (see [`WIRE_FORMAT.md`](WIRE_FORMAT.md))
- Cross-writer bit-exactness under default settings, pinned by
  [`tests/test_receipt.py::test_cross_writer_independent_implementation_matches`](../tests/test_receipt.py)
- Storage and cache-read economics vs default-Parquet on a bounded
  VideoQA subset (see
  [`transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json`](transparency/phase9_4_1_1_2_1_candidate_b_video_llm_object_memory/summary.json))
- The full falsification journey behind the selected wedge
  (see [`TRANSPARENCY_JOURNEY.md`](TRANSPARENCY_JOURNEY.md))
- C2PA-style external manifest binding without mutating receipt bytes
  (see [`../src/zpe_video/manifest.py`](../src/zpe_video/manifest.py))
- Deterministic authority-bundle hashing for the current receipt-core
  proof surface (see [`../proofs/manifests/CURRENT_AUTHORITY_PACKET.md`](../proofs/manifests/CURRENT_AUTHORITY_PACKET.md))

This repo does not establish:

- Universal video-codec superiority
- Buyer-visible end-to-end speedup (LLM generation dominates; receipt
  speed is a storage/memory property)
- That Parquet cannot be tuned to match (it can under non-default
  patterns; the wedge is specifically about default settings)
- The Compass-8 / 8-primitive architecture (this codec does not use it;
  see [`_reorientation/2026-04-17/NOVELTY_CARD.md`](_reorientation/2026-04-17/NOVELTY_CARD.md))
- Sovereign primitive-native closure or Phase 10 readiness
