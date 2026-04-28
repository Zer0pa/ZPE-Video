<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

This public roadmap is a communication surface, not the full internal
`.gpd` execution ledger.

Its purpose is to show where the live repo sits in the scientific journey
and what is still open without pretending the lane has already closed
green.

<p>
  <img src=".github/assets/readme/section-bars/lane-status-snapshot.svg" alt="LANE STATUS SNAPSHOT" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Phase group</th>
      <th align="left">Current public reading</th>
      <th align="left">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>`08`</td><td>Comparator expansion vs AV1, VVC, and learned baselines: all three killed the universal-video-codec claim.</td><td><code>complete — killed</code></td></tr>
    <tr><td>`09` through `09.2`</td><td>Broad and semi-narrow video surfaces: bounded signal, no decisive wedge.</td><td><code>complete — bounded</code></td></tr>
    <tr><td>`09.3` through `09.3.2`</td><td>Narrow VIRAT facility-crossing work: real portal-local signal, weak consumer stability; retired.</td><td><code>complete — retired</code></td></tr>
    <tr><td>`09.4`</td><td>Repo public-surface hardening, docs/proofs routing, governance spine.</td><td><code>complete</code></td></tr>
    <tr><td>`09.4.1` through `09.4.1.1.1`</td><td>Ground-state wedge audit and pod-backed live archive-query benchmark on VIRAT: economics real, specificity not yet commercial.</td><td><code>complete — bounded_signal_only</code></td></tr>
    <tr><td>`09.4.1.1.2`</td><td>Fair-baseline archive-query falsification: raw struct+zlib strictly dominates on storage AND query latency with identical semantics. Archive-query wedge as ZPE-specific is falsified.</td><td><code>complete — killed</code></td></tr>
    <tr><td>`09.4.1.1.2.1`</td><td>Three parallel bounded wedge experiments: Candidate A (ROI sidecar) killed; Candidate B (video-LLM object memory) defended on cross-writer hash stability; Candidate C (state-layer enrichment) defended-with-caveat.</td><td><code>complete — B defended</code></td></tr>
    <tr><td>`v0.1.0`</td><td>Ship the Candidate B perception-receipt wedge as the public API. Full transparency bundle ships alongside.</td><td><code>shipping</code></td></tr>
    <tr><td>Next</td><td>Harden the perception-receipt surface against larger / messier benchmarks; identify 1-2 buyer partners; extend the receipt envelope only where evidence demands.</td><td><code>always-in-beta</code></td></tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/downstream-action-items.svg" alt="DOWNSTREAM ACTION ITEMS" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Track</th>
      <th align="left">Current next move</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Public repo</td><td>Keep docs aligned to shipped code and current transparency artifacts; update on every release.</td></tr>
    <tr><td>Wedge hardening</td><td>Extend the cross-writer hash test to a larger, messier VideoQA surface (LongVideoBench / NExT-QA spatial subsets); identify 1-2 buyer partners (C2PA, video-LLM infra, regulated chain-of-custody).</td></tr>
    <tr><td>Cadence</td><td>Ship minor releases when there is real new utility or a real new verdict to record. No milestone theatre.</td></tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

This roadmap does not mean:

- every prior research direction will be revived; retired or killed
  surfaces stay retired or killed
- the Compass-8 primitive-native substrate is an active product goal for
  this codec (it is historical research context; the product is the
  perception receipt)
- "always-in-beta" is an excuse to under-deliver; it means continuous
  improvement on a live, working package
