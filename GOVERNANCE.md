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

The current governing example is `09.3.2`: the portal-local state
machine produced a real improvement and still closed as
`retire_surface`.

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
    <tr><td><code>staging_only</code></td><td>The repo is a live staging and evidence surface, not a public release surface.</td></tr>
    <tr><td><code>bounded_signal_only</code></td><td>Real local signal exists, but it does not yet clear the governing acceptance gate.</td></tr>
    <tr><td><code>retire_surface</code></td><td>A bounded investigation was completed and the tested surface should not receive more tuning under the same contract.</td></tr>
    <tr><td><code>not_green</code></td><td>The authoritative gate remains red.</td></tr>
    <tr><td><code>mixed_snapshot</code></td><td>The proof set is historically valuable but not a clean current run-of-record.</td></tr>
    <tr><td><code>in_progress</code></td><td>The workstream is still being actively refined and should not be read as closed.</td></tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

The repo is allowed to claim:

- exact phase outcomes
- exact metrics from explicit artifacts
- exact file and proof routes
- exact current blockers

The repo is not allowed to claim:

- GO or release readiness without a current supporting artifact trail
- a commercial wedge where the governing science gate is still red
- generalized superiority from a narrow or retired surface
- proof freshness that the artifacts do not actually have

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
