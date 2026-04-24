<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Low-cost sanity for the v0.1.0 perception-receipt surface:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip uv
uv sync --extra dev --extra benchmark
uv run python -m compileall src scripts
uv run pytest tests -v
uv run python examples/02_cross_writer.py   # expect: "cross-writer wedge: VERIFIED"
uv run python scripts/receipt_core_benchmark.py
uv run python scripts/authority_bundle.py
uv run python scripts/authority_bundle.py --check
uv run python - <<'PY'
import zpe_video
print("version:", zpe_video.__version__)
print("public:", sorted(zpe_video.__all__))
PY
```

Expected: all tests pass, example prints `cross-writer wedge: VERIFIED`,
receipt-core benchmark prints `{"verdict": "pass", ...}`, and the import
surface matches the pinned `__all__` set.

<p>
  <img src="../.github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

This does not cover:

- reruns of historical research phases (those are under
  `.gpd/phases/` in the outer research tree with their own harnesses)
- dataset-backed end-to-end reruns (VIRAT, LongVideoBench); those are
  documented per-harness under `docs/transparency/`
- downstream integration tests (C2PA pipeline, regulated chain-of-custody,
  video-LLM memory adapter); those are integrator-owned

<p>
  <img src="../.github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

Current verification truth:

- v0.1.0 package installs and imports with zero optional extras
- 20 perception-receipt tests pin round-trip fidelity, cross-writer
  bit-exactness, CRC32 integrity, and error paths
- manifest tests pin C2PA-style hash binding without mutating receipt bytes
- 2 legacy codec tests remain green for backward-compat sanity
- authority-bundle generation records a deterministic SHA-256 over the
  current receipt-core proof surface
- CI matrix covers Python 3.11, 3.12, 3.13
