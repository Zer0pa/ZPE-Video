<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

All notable changes to ZPE Video are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow `MAJOR.MINOR.PATCH`. The package version in
`pyproject.toml` is the authoritative version record.

---

<p>
  <img src=".github/assets/readme/section-bars/unreleased.svg" alt="[UNRELEASED]" width="100%">
</p>

Nothing outstanding after the v0.1.0 wedge selection. Follow-up work is
recorded in the per-phase ledger under `.gpd/phases/` and the updated
[`docs/STATUS.md`](docs/STATUS.md).

## 0.1.0 — 2026-04-17

### The version that selects the commercial wedge

After a long research journey (see
[`docs/TRANSPARENCY_JOURNEY.md`](docs/TRANSPARENCY_JOURNEY.md)), one
narrow commercial wedge survived every falsification attempt: the ZPE
packet as a cross-writer bit-exact perception-receipt format for AI
video pipelines. v0.1.0 promotes that surface to a stable public API,
ships the supporting docs and tests, and preserves the full research
evidence alongside the chosen wedge.

### Added

- **Public perception-receipt API** at `zpe_video.receipt`:
  `PerceptionReceipt`, `Box`, `encode_receipt`, `decode_receipt`,
  `receipt_hash`, `verify_receipt`, `read_receipt`, `write_receipt`,
  plus error types `ReceiptCorrupted` and `CrossWriterMismatch`, and
  constants `WIRE_MAGIC` / `WIRE_VERSION`. Zero upstream runtime
  dependency (stdlib `struct` / `zlib` / `hashlib` only).
- **`tests/test_receipt.py`** — 20 tests covering round-trip fidelity,
  cross-writer bit-exactness against an independent from-spec encoder,
  frame-level CRC32 integrity, error paths (bad magic, wrong version,
  truncated header, trailing bytes, CRC mismatch), the `verify_receipt`
  helpers, I/O helpers, and the 255-box / signed-16-delta limits.
- **`docs/WEDGE.md`** — commercial-wedge rationale with the explicit
  list of buyer shapes (C2PA perception credentials, regulated
  chain-of-custody, video-LLM object-memory caches, cross-platform
  training-data provenance).
- **`docs/TRANSPARENCY_JOURNEY.md`** — phase-by-phase verdict ledger
  from Phase 1 through Phase 09.4.1.1.2.1, including every kill verdict
  and defend verdict.
- **`docs/WIRE_FORMAT.md`** — byte-level spec for third-party
  re-implementation.
- **`docs/QUICKSTART.md`** — five-minute onboarding with three
  runnable examples.
- **`docs/transparency/`** — reproducible snapshot of the research
  evidence: PLAN, SUMMARY, `summary.json`, harnesses, and the research
  ledger (VERDICT-SYNTHESIS, ranked_hypothesis_ladder, takeover
  assessment) for Phases 09.4.1.1.2 and 09.4.1.1.2.1.
- **`examples/`** — three stdlib-only runnable examples
  (`01_round_trip`, `02_cross_writer`, `03_file_round_trip`).
- **`Makefile`** — `install`, `test`, `lint`, `format`, `build`,
  `verify-package`, `clean` targets.
- **`.github/workflows/ci.yml`** — CI on Python 3.11 / 3.12 / 3.13
  matrix; runs the full test suite and ruff lint.
- **`.github/workflows/verify-package.yml`** — wheel build + import
  surface check; pins the public `__all__` symbol set; independently
  runs the cross-writer wedge test.
- **Optional install extras** in `pyproject.toml`:
  `dev` (pytest, ruff), `producer` (numpy + opencv + ultralytics +
  torch for ingesting raw video), `research` (Wave-1 pipeline deps),
  `all`.

### Changed

- **Package version** `0.0.0` -> `0.1.0`.
- **`src/zpe_video/__init__.py`** now exports the perception-receipt
  surface as the primary public API. `Wave1Pipeline` remains importable
  for backward compatibility with the legacy research harness.
- **`pyproject.toml`** — full `[project]` metadata (classifiers,
  keywords, URLs), strict `requires-python = ">=3.11,<3.14"`, and the
  new optional extras.
- **`docs/ARCHITECTURE.md`** — reorganized around the public
  perception-receipt surface with the Wave-1 research pipeline moved
  below as subordinate.
- **`docs/STATUS.md`** — refreshed for the 2026-04-17 wedge-selection
  posture. Sovereign-gate status stays `red`.

### Kept as evidence, not removed

The kill verdicts (Phase 08 universal-codec failure, Phase 09.4.1.1.2
archive-query falsification, Phase 09.4.1.1.2.1-A ROI-sidecar kill) are
preserved in full — both in the outer research tree and in
`docs/transparency/`. They are the reason the defend verdict is
trustworthy.

### Historical (pre-0.1.0)

- Repo hardening and public-surface discipline (Phase 09.4). Root
  governance spine (CITATION, CODE_OF_CONDUCT, GOVERNANCE, ROADMAP,
  SECURITY, SUPPORT, CONTRIBUTING), public docs shell, and
  proof-routing surface were added.
- Pre-0.1.0 posture used "staging_only" labels throughout the doc set.
  v0.1.0 retires that framing in favor of the always-in-beta public
  posture: useful now, improving continuously. See
  [`docs/STATUS.md`](docs/STATUS.md).
