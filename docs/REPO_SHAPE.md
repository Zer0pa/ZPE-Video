<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

This document defines the intended public organization of the live
`zpe-video` repo.

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Area</th>
      <th align="left">Purpose</th>
      <th align="left">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>README.md</code> and root governance docs</td><td>Public front door and project policy</td><td>Structured to the Repo README Playbook; the website product-page generator parses <code>##</code> headings as exact strings</td></tr>
    <tr><td><code>.github/</code></td><td>Issue/PR intake, CI workflows, shared README assets</td><td>CI matrix on Python 3.11 / 3.12 / 3.13; verify-package workflow pins the public <code>__all__</code></td></tr>
    <tr><td><code>src/zpe_video/</code></td><td>Live Python package — perception-receipt surface is the primary API</td><td>Core receipt module is zero-dependency (stdlib only); legacy <code>Wave1Pipeline</code> stays importable for backward compat</td></tr>
    <tr><td><code>tests/</code></td><td>Public test surface</td><td>22 tests: 20 receipt + 2 legacy codec. All pass.</td></tr>
    <tr><td><code>examples/</code></td><td>Runnable minimal examples</td><td>Stdlib-only; cover round-trip, cross-writer wedge proof, file I/O</td></tr>
    <tr><td><code>docs/</code></td><td>Commercial wedge rationale, wire-format spec, quickstart, architecture, transparency bundle</td><td>Every claim in <code>WEDGE.md</code> is backed by a file under <code>transparency/</code></td></tr>
    <tr><td><code>docs/transparency/</code></td><td>Reproducible snapshot of the research evidence behind each claim</td><td>5 phase artifacts + research ledger; harnesses, plans, summaries, machine-readable result JSON</td></tr>
    <tr><td><code>proofs/</code></td><td>Pre-0.1.0 historical proof-custody snapshot and route surface</td><td>Dated historical evidence from research phases; live v0.1.0 evidence is under <code>docs/transparency/</code></td></tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/no-change-guarantees.svg" alt="NO CHANGE GUARANTEES" width="100%">
</p>

Stability guarantees at v0.1.0:

- the public `zpe_video.receipt` API surface (`PerceptionReceipt`, `Box`,
  the eight functional helpers, the two error types) will not break
  without a major-version bump
- the wire format defined in `WIRE_FORMAT.md` will not change without a
  `WIRE_VERSION` bump
- the evidence rule is permanent: every forward-looking claim must point
  at a file that resolves
