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
    <tr><td><code>README.md</code> and root governance docs</td><td>Public front door and project policy</td><td>Truthful status language only; no release posture inflation</td></tr>
    <tr><td><code>.github/</code></td><td>Issue/PR intake and shared README assets</td><td>Matches the IMC public-shell discipline layer</td></tr>
    <tr><td><code>src/</code>, <code>scripts/</code>, <code>tests/</code></td><td>Live Python code substrate</td><td>Intentionally kept Python-native; no forced `v0.0/` mimicry</td></tr>
    <tr><td><code>docs/</code></td><td>Status, support, repo-shape, verification, and historical-input routing</td><td>Stable public docs only</td></tr>
    <tr><td><code>proofs/</code></td><td>Proof routing, reference snapshot, rerun targets, log targets</td><td>Historical proof custody remains explicit</td></tr>
    <tr><td><code>artifacts/</code></td><td>Secondary runtime output area</td><td>Not treated as the primary public proof surface</td></tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/no-change-guarantees.svg" alt="NO CHANGE GUARANTEES" width="100%">
</p>

This repo does not guarantee:

- stable public APIs
- frozen release layout
- a permanent proof hierarchy

What is frozen instead is the evidence rule: the public surface must not
overclaim what the artifacts can support.
