<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

Current receipt-core proof surface:

- <code>proofs/manifests/CURRENT_AUTHORITY_PACKET.md</code>
- <code>proofs/manifests/current_authority_packet.json</code>

Historical (pre-0.1.0) proof surface:

- <code>proofs/reference/2026-03-09_workspace_snapshot/</code>

Historical proof reading:

- provenance: copied from the outer workspace on <code>2026-03-09</code>
- status: dated evidence-custody snapshot from pre-0.1.0 research phases
- cleanliness: mixed (<code>resource_inventory.json</code> reflects a later partial probe)

**Current v0.1.0 evidence route:** [`../docs/transparency/`](../docs/transparency/)
— reproducible bundle (harnesses, plans, summaries, machine-readable
result JSON) backing every claim in [`../docs/WEDGE.md`](../docs/WEDGE.md).
The current authority-bundle hash is regenerated with
`python scripts/authority_bundle.py` from the repository root.

<p>
  <img src="../.github/assets/readme/section-bars/engineering-references.svg" alt="ENGINEERING REFERENCES" width="100%">
</p>

Key files:

- `proofs/reference/2026-03-09_workspace_snapshot/README.md`
- `proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md`
- `proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json`
- `proofs/reference/2026-03-09_workspace_snapshot/quality_gate_scorecard.json`
- `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`
- `proofs/manifests/current_authority_packet.json`

<p>
  <img src="../.github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

What is still missing:

- public Zenodo DOI minting
- live PyPI release with PEP 740 attestation
- live release SBOM artifact

Those belong to the first tagged release after this hardening pass.
