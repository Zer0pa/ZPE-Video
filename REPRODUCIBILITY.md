# Reproducibility

ZPE Video's current reproducibility surface is the perception-receipt core:
the same detector/tracker box state must produce byte-identical receipt bytes
across independent conforming writers.

## Canonical Inputs

The authority bundle is generated from this fixed file list:

- `README.md`
- `pyproject.toml`
- `CITATION.cff`
- `docs/WEDGE.md`
- `docs/WIRE_FORMAT.md`
- `docs/VERIFICATION.md`
- `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json`
- `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/manifest_binding.json`
- `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/baseline_table.csv`
- `src/zpe_video/receipt.py`
- `src/zpe_video/manifest.py`
- `tests/test_receipt.py`
- `tests/test_manifest.py`

## Golden-Bundle Hash

The current bundle hash is recorded in
`proofs/manifests/CURRENT_AUTHORITY_PACKET.md`. Wave 3's portfolio
`receipt-bundle.yml` workflow can later publish the same authority surface as an
external in-toto/Sigstore receipt. Until then, the repo-local generated packet is
the lane authority bundle for this commercial receipt-core pass.

## Verification Command

```bash
uv sync --extra dev --extra benchmark
uv run python scripts/receipt_core_benchmark.py
uv run python scripts/authority_bundle.py
uv run python scripts/authority_bundle.py --check
uv run pytest tests -v
```

The authority bundle lands in `proofs/manifests/`:

- `proofs/manifests/current_authority_packet.json`
- `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`

The bundle hash is a deterministic hash over the sorted authority-file
records. It is a receipt-chain anchor for this commercial receipt-core surface.
It is not a sovereign primitive-native closure claim and does not unblock Phase
10.

## Supported Runtimes

- Python 3.11, 3.12, and 3.13 for the package and CI matrix.
- macOS and Linux for the stdlib-only core receipt surface.
- Optional producer/research extras require their own OpenCV/Torch-compatible
  Python environment.

## External Provenance

On a release tag, `.github/workflows/publish.yml` builds the source
distribution and wheel, emits GitHub artifact attestations for `dist/*`, and
publishes with PyPI Trusted Publishing. The PyPI action version is pinned to a
release at or above `v1.11.0`, where PEP 740 attestations are on by default for
Trusted Publishing.

`.github/workflows/sbom.yml` emits a CycloneDX SBOM artifact for release
review. Hugging Face storage is reserved for large validation corpora, benchmark
packs, model weights, and large proof bundles; the current receipt-core
artifacts are small repository proof files and do not require HF upload.
