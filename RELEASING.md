<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

This repo follows the always-in-beta cadence: ship when there is real
utility, improve continuously. v0.1.0 is shipping on the basis of the
perception-receipt wedge (see [`docs/WEDGE.md`](docs/WEDGE.md)), and
subsequent releases follow the same evidence discipline.

Tagged releases are cut by the maintainer from the main branch. The
procedure below applies to any cut after v0.1.0.

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

All of the following must be true for a tagged release:

1. The exact commit has maintainer approval.
2. `uv run pytest tests -v` passes on Python 3.11, 3.12, 3.13.
3. `uv run python examples/02_cross_writer.py` prints `cross-writer wedge: VERIFIED`.
4. `uv build` produces a clean wheel and sdist.
5. The wheel installs into a fresh venv and `import zpe_video` succeeds
   with zero optional extras.
6. `CHANGELOG.md` has an entry for this version.
7. `CITATION.cff` and `pyproject.toml` versions match the tag.
8. Repo-local secret scan passes on the release commit.
9. Any new claim in the README or in `docs/WEDGE.md` is backed by a
   plan + summary + machine-readable artifact in
   [`docs/transparency/`](docs/transparency/).
10. `uv run python scripts/authority_bundle.py --check` confirms the
    current authority packet is not stale.
11. The tag-triggered `publish.yml` workflow emits GitHub artifact
    attestations for `dist/*` and publishes through PyPI Trusted
    Publishing; the tag-triggered `sbom.yml` workflow emits a CycloneDX
    SBOM artifact.

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

What a release ships:

- one pip-installable wheel + sdist
- PyPI Trusted Publishing provenance with PEP 740 attestations
- GitHub artifact attestations for the wheel and sdist
- a CycloneDX SBOM artifact from the release workflow
- no breaking changes to `src/zpe_video/receipt.py` public API or to
  the wire format without a major-version bump
- the full transparency bundle for any new research phase that
  contributed a claim

What a release does not ship:

- broadened product claims without new transparency artifacts
- performance numbers without the harness that produced them
- features marked "coming soon" — always-in-beta means live, not promised
