<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This document records the honest limits of what a reader can establish
from this repo alone. It is a complement to the shipping v0.1.0
perception-receipt surface documented in [`docs/WEDGE.md`](docs/WEDGE.md),
not a substitute for it.

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

What this repo can establish today:

- the exact byte-level wire format of the perception receipt (see
  [`docs/WIRE_FORMAT.md`](docs/WIRE_FORMAT.md))
- cross-writer bit-exactness of the format under default settings,
  pinned by [`tests/test_receipt.py`](tests/test_receipt.py) against an
  independent from-spec re-implementation in the test file
- the current v0.1.0 package, script, and test surfaces
- the full research transparency bundle, including every kill verdict
  (see [`docs/transparency/`](docs/transparency/))
- the documentation boundary between the shipping wedge and the
  retired or falsified claims

What this repo does not establish today:

- fitness for a specific downstream integration (C2PA pipeline,
  chain-of-custody workflow, video-LLM memory adapter, etc.) — those
  are downstream integration evaluations that the ZPE Video team has
  not yet performed with specific partners
- comparative benchmarks against every possible alternative format
  under every possible tuning (the comparisons in
  [`docs/WEDGE.md`](docs/WEDGE.md) are specifically about default
  settings)
- primitive-native Compass-8 substrate closure — that is a historical
  research thesis, not a product claim for this codec

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Limit</th>
      <th align="left">Current state</th>
      <th align="left">Why it matters</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Current shipping posture</td><td><code>always-in-beta</code> at v0.1.0</td><td>Useful now, improving continuously; not a hedge</td></tr>
    <tr><td>Historical proof snapshot</td><td><code>proofs/reference/2026-03-09_workspace_snapshot/</code></td><td>Dated evidence-custody snapshot from pre-0.1.0 research phases, not a current rerun</td></tr>
    <tr><td>Dataset custody</td><td>Raw datasets are not included</td><td>Independent reruns of phase experiments require separate dataset acquisition (VIRAT Kitware Release 2, LongVideoBench, etc.)</td></tr>
    <tr><td>Scope of defended wedge</td><td>Cross-writer hash stability under default settings</td><td>Parquet tuned with non-default enforcement may close the gap; see <code>docs/WEDGE.md</code> for the explicit scope</td></tr>
    <tr><td>Buyer-visible latency</td><td>Receipt speed is a storage/memory property</td><td>In video-LLM pipelines LLM generation dominates end-to-end latency; no end-to-end speedup claimed</td></tr>
    <tr><td>Sovereign research thesis</td><td>Compass-8 primitive-native substrate: tested, not closed</td><td>Historical research context only; not a v0.1.0 product claim</td></tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

Honest reading rules:

- Treat `proofs/reference/2026-03-09_workspace_snapshot/` as a dated historical snapshot from pre-0.1.0 research phases.
- Treat `docs/transparency/` as the live falsification + defend ledger for the v0.1.0 wedge selection.
- Treat any local pass on your own machine as local evidence, not as a release verdict for other environments.
- Treat `LICENSE` as the legal source of truth.
