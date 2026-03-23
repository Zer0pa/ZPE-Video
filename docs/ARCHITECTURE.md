<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="ARCHITECTURE AND THEORY" width="100%">
</p>

This repo packages the current ZPE Video lane as a standalone staging
surface.

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Surface</th>
      <th align="left">Role</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>src/zpe_video/codec.py</code></td><td>Encode/decode logic</td></tr>
    <tr><td><code>src/zpe_video/fixtures.py</code></td><td>Deterministic proxy data generation</td></tr>
    <tr><td><code>src/zpe_video/metrics.py</code></td><td>Metric helpers</td></tr>
    <tr><td><code>src/zpe_video/vision.py</code></td><td>Simple frame and sketch utilities</td></tr>
    <tr><td><code>src/zpe_video/pipeline.py</code></td><td>Gate execution and artifact generation</td></tr>
    <tr><td><code>scripts/execute_wave1.py</code></td><td>Runner entrypoint</td></tr>
    <tr><td><code>tests/test_codec.py</code></td><td>Lightweight codec smoke coverage</td></tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

- Runtime-generated outputs currently land under `artifacts/`.
- Curated staged evidence for this repo lives under
  `proofs/reference/2026-03-09_workspace_snapshot/`.
- Future clean reruns should be written under `proofs/reruns/` and then
  promoted deliberately into `proofs/reference/`.

<p>
  <img src="../.github/assets/readme/section-bars/dispatch-precedence.svg" alt="DISPATCH PRECEDENCE" width="100%">
</p>

Gate A no longer hardcodes machine-local absolute paths.

Optional input documents resolve in this order:

1. `ZPE_VIDEO_NET_NEW_PACK_MD`
2. `ZPE_VIDEO_NET_NEW_PACK_PDF`
3. `ZPE_VIDEO_GAP_CLOSURE_MD`
4. repo-relative files under `docs/inputs/`

If those files are absent, Gate A should fail honestly instead of
silently assuming someone else's machine layout.

Current runtime and artifact truth outrank stale dossier prose.
