<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/questions.svg" alt="QUESTIONS" width="100%">
</p>

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Question</th>
      <th align="left">Answer</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>What is this package?</td><td>A perception-receipt format for AI video pipelines. See <a href="WEDGE.md"><code>WEDGE.md</code></a>.</td></tr>
    <tr><td>What version is shipping?</td><td>v0.1.0. Posture is always-in-beta (useful now, improving continuously).</td></tr>
    <tr><td>What is the load-bearing claim?</td><td>Cross-writer bit-exactness under default settings: the same input produces the same bytes from every conforming writer in any language. Pinned by <a href="../tests/test_receipt.py"><code>tests/test_receipt.py::test_cross_writer_independent_implementation_matches</code></a>.</td></tr>
    <tr><td>What does ZPE Video not claim?</td><td>Universal video-codec superiority, archive-query wedge on box state, ROI/foveated-sidecar wedge, primitive-native Compass-8 substrate closure. Each has a recorded kill verdict in <a href="TRANSPARENCY_JOURNEY.md"><code>TRANSPARENCY_JOURNEY.md</code></a>.</td></tr>
    <tr><td>Does this codec use the 8-primitive / Compass-8 architecture?</td><td>No. See <a href="_reorientation/2026-04-17/NOVELTY_CARD.md"><code>docs/_reorientation/2026-04-17/NOVELTY_CARD.md</code></a>. The format uses delta-encoded per-frame box + track-id state with zlib compression and per-frame CRC32.</td></tr>
    <tr><td>Why is there a historical proof snapshot under <code>proofs/reference/2026-03-09_workspace_snapshot/</code>?</td><td>Evidence custody for the pre-0.1.0 research phases. Historical. The live v0.1.0 evidence is under <a href="transparency/"><code>docs/transparency/</code></a>.</td></tr>
    <tr><td>Why are large datasets not bundled?</td><td>They are too large and have their own license terms. Harness scripts under <a href="transparency/"><code>docs/transparency/</code></a> point at public sources (VIRAT Kitware Release 2, LongVideoBench, etc.).</td></tr>
    <tr><td>Is there a PyPI release?</td><td>Install from source today: <code>pip install -e .[dev]</code>. A PyPI publication may follow once packaging metadata and a signed release workflow are finalized.</td></tr>
  </tbody>
</table>
