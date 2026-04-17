<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This document defines the public governance boundary for evidence
handling, status language, and claim discipline in ZPE Video.

Canonical anchors:

- Repository: `https://github.com/Zer0pa/ZPE-Video`
- Contact: `architects@zer0pa.ai`

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

Governance baseline:

- Technical claims must be evidence-backed.
- Runtime artifacts, proof artifacts, and explicit phase decisions outrank prose if they conflict.
- Contradictions are retained and logged rather than rewritten away.
- Negative results are first-class artifacts.
- A local or narrow improvement does not count as a repo-level win if the governing gate remains red.

Concrete examples: Phase 08 closed as `comparator_gate_failed` against
AV1/VVC/learned baselines; Phase 09.4.1.1.2 closed as
`zpe_packet_beaten_by_commodity_format` on fair-baseline archive query;
Phase 09.4.1.1.2.1-A closed as `kill` when the mean-importance control
matched the ROI lane. Every kill verdict is preserved in full under
[`docs/transparency/`](docs/transparency/) alongside the single defended
wedge (Candidate B, perception-receipt cross-writer hash stability).

<p>
  <img src=".github/assets/readme/section-bars/mode-semantics.svg" alt="MODE SEMANTICS" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Token</th>
      <th align="left">Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>always-in-beta</code></td><td>The repo ships products when they have utility. What installs today works; what installs next month may be materially better. Cadence is continuous, not milestoned. Not an apology, not an excuse.</td></tr>
    <tr><td><code>defend</code></td><td>A claim passed the plan-contract acceptance test with explicit kill criteria and independent-method verification.</td></tr>
    <tr><td><code>kill</code></td><td>A claim failed its plan-contract kill criterion. Recorded verbatim; not softened.</td></tr>
    <tr><td><code>bounded_signal_only</code></td><td>A phase produced real local signal but did not clear its own acceptance gate. Neither defend nor kill; recorded as-is.</td></tr>
    <tr><td><code>retire_surface</code></td><td>A bounded investigation was completed and the tested surface should not receive more tuning under the same contract.</td></tr>
    <tr><td><code>mixed_snapshot</code></td><td>A proof set is historically valuable but not a clean current run-of-record.</td></tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

The repo is allowed to claim:

- exact phase outcomes with citation to PLAN + SUMMARY + machine-readable result
- exact metrics from explicit artifacts (a file path, not a rewritten number)
- exact file and proof routes (every path in a claim must resolve via `ls`)
- exact current blockers
- one narrow defended commercial wedge (perception receipts; see
  [`docs/WEDGE.md`](docs/WEDGE.md)) with cited evidence

The repo is not allowed to claim:

- broad product superiority from a narrow defended surface
- generalized superiority from a retired or killed surface
- proof freshness that the artifacts do not actually have
- "primitive-native" or "Compass-8" product-architecture framing for this
  codec; this codec does not use Compass-8 directional encoding (see
  [`docs/_reorientation/2026-04-17/NOVELTY_CARD.md`](docs/_reorientation/2026-04-17/NOVELTY_CARD.md))

<p>
  <img src=".github/assets/readme/section-bars/escalation-path.svg" alt="ESCALATION PATH" width="100%">
</p>

Use these routes for governance disputes:

- Claim/evidence dispute: open a GitHub issue with the Evidence Dispute template
- Policy or scope concern: open a GitHub issue and cite the exact file and sentence at issue
- Security or conduct escalation: `architects@zer0pa.ai`

If a public-facing document and a run artifact disagree, the run artifact
and explicit phase decision are the source of truth until the conflict is
resolved.
