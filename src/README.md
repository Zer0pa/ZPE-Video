<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This directory contains the live Python package surface for ZPE Video
at v0.1.0.

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Module</th>
      <th align="left">Role</th>
      <th align="left">Surface</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>zpe_video/receipt.py</code></td><td>Perception-receipt encoder, decoder, hash, verify — the v0.1.0 public API</td><td>Public (stable within v0.x)</td></tr>
    <tr><td><code>zpe_video/models.py</code></td><td>Legacy Box / SequenceData dataclasses used by the Wave-1 pipeline</td><td>Internal</td></tr>
    <tr><td><code>zpe_video/codec.py</code></td><td>Legacy delta-encoded codec; predecessor to the receipt module</td><td>Internal</td></tr>
    <tr><td><code>zpe_video/detector.py</code></td><td>Repo-local detector utilities used by Wave-1 measurement harnesses</td><td>Internal</td></tr>
    <tr><td><code>zpe_video/fixtures.py</code></td><td>Deterministic proxy fixtures for Wave-1 benchmarks</td><td>Internal</td></tr>
    <tr><td><code>zpe_video/metrics.py</code></td><td>Metric helpers (ap_proxy, lpips_proxy)</td><td>Internal (historical)</td></tr>
    <tr><td><code>zpe_video/pipeline.py</code></td><td>Wave-1 gate runner (<code>Wave1Pipeline</code>); kept importable for backward compat</td><td>Internal (historical)</td></tr>
    <tr><td><code>zpe_video/vision.py</code></td><td>Frame and sketch utilities for the legacy pipeline</td><td>Internal</td></tr>
    <tr><td><code>zpe_video/constants.py</code></td><td>Claim thresholds and gate seeds for the Wave-1 pipeline</td><td>Internal (historical)</td></tr>
  </tbody>
</table>

The public API surface is what `zpe_video.__all__` exports: the
perception-receipt types and functions from `receipt.py`, plus
`Wave1Pipeline` for historical compat. All other modules are internal
implementation details and may change without notice.
