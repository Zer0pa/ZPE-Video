<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

This directory holds the proof-custody surface for ZPE Video. Historical
pre-0.1.0 evidence remains in `reference/`; the current receipt-core
authority packet is generated under `manifests/`.

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Area</th>
      <th align="left">What it is</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>PROOF_INDEX.md</code></td><td>Index and limits for the historical <code>reference/</code> snapshot</td></tr>
    <tr><td><code>manifests/CURRENT_AUTHORITY_PACKET.md</code></td><td>Current deterministic receipt-core authority bundle</td></tr>
    <tr><td><code>manifests/current_authority_packet.json</code></td><td>Machine-readable authority bundle with per-file SHA-256 values</td></tr>
    <tr><td><code>reference/2026-03-09_workspace_snapshot/</code></td><td>Dated evidence-custody snapshot from pre-0.1.0 research phases</td></tr>
    <tr><td><code>logs/</code></td><td>Optional target location for future repo-owned run logs</td></tr>
    <tr><td><code>reruns/</code></td><td>Optional target location for future clean reruns</td></tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/what-this-directory-is-not.svg" alt="WHAT THIS DIRECTORY IS NOT" width="100%">
</p>

**Current v0.1.0 evidence is not here.** See
[`../docs/transparency/`](../docs/transparency/) for the experiment
bundle and [`manifests/CURRENT_AUTHORITY_PACKET.md`](manifests/CURRENT_AUTHORITY_PACKET.md)
for the current receipt-core bundle hash that backs the live README claim in
[`../docs/WEDGE.md`](../docs/WEDGE.md), including the harnesses,
plans, summaries, and machine-readable result JSON for every kill and
defend verdict from the wedge-discovery phase.
