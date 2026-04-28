# Reorientation Fix Log — 2026-04-17

Reorientation pass applying the ETHOS (operator-private artifact at `<OPERATOR_WORKSPACE>/Status_Packets/2026-04-17_Orchestrator-Working-Docs/ETHOS.md`) and UNIVERSAL_BRIEF to every in-scope doc in `zpe-video`. Scope is wider than a light touch on a few files because this repo was landing v0.1.0 in the same sequence — the perception-receipt surface was newly written and the legacy doc shell had pre-0.1.0 "staging_only / 09.3.2 = retire_surface" framing throughout. All changes below are content-level; no code was modified.

## Drift

- [`CITATION.cff`] — version `0.0.0` → `0.1.0`; date `2026-03-23` → `2026-04-17`; license `LicenseRef-Zer0pa-SAL-5.1` → `LicenseRef-Zer0pa-SAL-6.2`; abstract rewritten to describe the v0.1.0 perception-receipt product (prior abstract referenced `09.3.2` sparse VIRAT facility-crossing as "latest staged truth"); keywords refreshed (added C2PA, chain-of-custody, video-LLM, object-memory, cross-writer-hash-stability; removed "primitive state machine").
- [`ROADMAP.md`] — phase snapshot table was missing Phase 08, 09.4.1, 09.4.1.1, 09.4.1.1.1, 09.4.1.1.2, 09.4.1.1.2.1, and the v0.1.0 wedge selection. Added eight rows; verdicts aligned to the transparency-bundle results (Phase 08 killed, Phase 09.4.1.1.2 killed archive-query, Phase 09.4.1.1.2.1-A killed ROI sidecar, Phase 09.4.1.1.2.1-B defended video-LLM memory, etc.). Downstream-action-items table rewritten from "release blocked" framing to always-in-beta continuous-improvement framing.
- [`docs/PUBLIC_AUDIT_SNAPSHOT_STAMP.md`] — stamp table: stamp date `2026-03-23` → `2026-04-17`; removed `Current staged truth: 09.3.2 = retire_surface` and `Current repo-hardening phase: 09.4 = complete`; added `Package version: 0.1.0`, `Posture: always-in-beta`, `Defended commercial wedge`, `Commercial wedge route`, `Transparency bundle route`, `Wire format spec` rows.
- [`docs/FAQ.md`] — "What is the latest scientific verdict?" `09.3.2 = retire_surface` → reframed; rebuilt the entire Q/A table for v0.1.0 ("What is this package?", "What version is shipping?", "What is the load-bearing claim?", "What does ZPE Video not claim?", "Does this codec use Compass-8?", "Why is there a historical proof snapshot?", "Why are datasets not bundled?", "Is there a PyPI release?"); removed stale "Gate A inputs" machine-local questions.
- [`docs/VERIFICATION.md`] — verification block listed only `pytest tests/test_codec.py` (2 tests) and a `Wave1Pipeline` import check. Replaced with full `pytest tests -v` (22 tests) + `examples/02_cross_writer.py` cross-writer VERIFIED smoke + public-`__all__` inspection; OUT-OF-SCOPE and SUMMARY sections rewritten to match.
- [`docs/REPO_SHAPE.md`] — purpose table was dated pre-0.1.0 (mentioned "IMC public-shell discipline layer", "historical-input routing"); updated to list the receipt module, 22-test suite, examples/, docs/transparency/, CI matrix, and the proofs/ dir as "pre-0.1.0 historical" explicitly. NO CHANGE GUARANTEES rewritten from abstract "evidence rule" to concrete v0.1.0 stability guarantees (public `zpe_video.receipt` API, wire format).
- [`docs/README.md`] (nav index) — engineering-references table was missing `WEDGE.md`, `WIRE_FORMAT.md`, `QUICKSTART.md`, `TRANSPARENCY_JOURNEY.md`, `transparency/`, `_reorientation/`. Added all seven.
- [`docs/inputs/README.md`] — "current priority route: status-notes/2026-03-23_phase09_3_2_retire_surface/" → reframed as historical pre-0.1.0 with pointers to current authority (`WEDGE.md`, `STATUS.md`, `TRANSPARENCY_JOURNEY.md`, `transparency/`).
- [`proofs/PROOF_INDEX.md`] — "current staged truth route: 09.3.2 = retire_surface" → reframed as historical pre-0.1.0 snapshot with pointer to live v0.1.0 evidence bundle at `docs/transparency/`.
- [`proofs/README.md`] — "This directory is the proof-routing surface for ZPE Video" → reframed to say this is historical pre-0.1.0; live v0.1.0 evidence is at `docs/transparency/`.
- [`src/README.md`] — module table missing `receipt.py`; added it as the primary public API surface with explicit "public/internal" column; dated modules (`pipeline.py`, `constants.py`, `metrics.py`) labeled "Internal (historical)"; removed "live staging package, not a frozen public API contract" line.
- [`CHANGELOG.md`] — trailing `This repository is still staging_only` bullet removed from the Historical (pre-0.1.0) section; replaced with a pointer-to-`docs/STATUS.md` note that pre-0.1.0 used the staging_only label and v0.1.0 retires that framing.

## Clarity

- [`PUBLIC_AUDIT_LIMITS.md`] — first sentence "This repo is a live staging snapshot. Its current value is evidence custody, public legibility, and truthful routeing, not a claim of release-ready performance" was hedge-heavy; replaced with a concrete one-sentence scope statement plus cross-references to `docs/WEDGE.md` and `docs/transparency/`.
- [`AUDITOR_PLAYBOOK.md`] — first section rewritten: "shortest honest audit path for the live ZPE Video repo" with `staging_only` framing → "shortest honest audit path for the zpe-video repo" with concrete v0.1.0 sanity steps and link to `docs/transparency/`. "Explicitly deferred" list (broad reruns, clean-clone verification, benchmark campaigns, public release posture) rewritten to "What this playbook does not establish on its own" (fitness for specific downstream workflows, independent clean-clone runs).
- [`docs/TRANSPARENCY_JOURNEY.md`] — reframed "We started with an ambitious thesis: a primitive-native Compass-8 video substrate" to explicitly call it research-phase framing, not a product claim; reframed "The sovereign Compass-8 primitive-native acceptance gate remains red" as "tested and not closed as a product goal for this codec"; reframed "Claim the Compass-8 substrate is 'almost there'. It is not. Sovereign gate stays red" as "it is a research thesis that was tested and not closed; v0.1.0 ships a different product."

## Consistency

- [`CITATION.cff`] vs [`pyproject.toml`] vs [`README.md`] — CITATION said version 0.0.0, SAL-5.1, date 2026-03-23; pyproject said 0.1.0; README said 0.1.0. Aligned all three to `0.1.0` / `SAL-6.2` / `2026-04-17`.
- [`docs/VERIFICATION.md`] vs [`AUDITOR_PLAYBOOK.md`] vs [`CONTRIBUTING.md`] — all three had the same stale verification block (`pytest tests/test_codec.py` only, `Wave1Pipeline` import). Aligned all three to the v0.1.0 block (`pytest tests -v`, `examples/02_cross_writer.py`, `zpe_video.__version__` / `__all__`).
- [`GOVERNANCE.md`] — "mode semantics" table listed `staging_only`, `bounded_signal_only`, `retire_surface`, `not_green`, `mixed_snapshot`, `in_progress`. `staging_only`, `not_green`, and `in_progress` contradicted the v0.1.0 posture established in `docs/STATUS.md`; replaced with `always-in-beta`, `defend`, `kill`, `bounded_signal_only`, `retire_surface`, `mixed_snapshot` — the verdict-style labels actually used by the plan/summary contracts in `docs/transparency/`.

## Framing

- [`README.md`] — Repo Shape row "Sovereign Research Gate | RED" → replaced with "Compass-8 / 8-primitive architecture | NOT USED by this codec" + pointer to the NOVELTY_CARD. This retires the portfolio-level sovereign-gate framing per ETHOS: "The earlier narrative of 'eight primitives as the substrate for everything under ZPE' is retired. Each product speaks for itself."
- [`README.md`] — "What We Don't Claim" bullet "We do not claim primitive-native Compass-8 substrate closure. The sovereign research gate remains red." → rewritten to state that Compass-8 is a research thesis and this codec does not use it, with pointer to NOVELTY_CARD.
- [`docs/STATUS.md`] — header row "Sovereign Compass-8 primitive-native acceptance gate: red" → "Compass-8 / 8-primitive architecture: not used by this codec" with pointer to NOVELTY_CARD. "Sovereign Compass-8 primitive-native substrate / not closed; gate remains red" row → "Compass-8 primitive-native substrate thesis / historical; tested and not closed as a product goal for this codec".
- [`docs/WEDGE.md`] — "Not a closure of the Compass-8 primitive-native acceptance gate. That gate remains red." → rewritten to state the codec does not use Compass-8 and the substrate was a research thesis. Added a killed-wedges row "Compass-8 / 8-primitive substrate as the product / Retired / pre-0.1.0 framing" with pointer to NOVELTY_CARD.
- [`GOVERNANCE.md`] — "The current governing example is 09.3.2: the portal-local state machine produced a real improvement and still closed as retire_surface" → replaced with current wedge-discovery examples (Phase 08 killed, 09.4.1.1.2 killed, 09.4.1.1.2.1-A killed, Candidate B defended on cross-writer hash stability). The disallowed-claims list now explicitly includes "primitive-native or Compass-8 product-architecture framing for this codec".

## Beta posture

- [`SECURITY.md`] — "There is no supported public release line yet. ... this repo is staging_only, ... release-grade security validation is still deferred" → rewritten to name v0.1.0 as the supported version on main, describe the always-in-beta cadence, note that core receipt is zero-dep pure stdlib (reduced attack surface), and commit to five-business-day acknowledgement on security reports.
- [`PUBLIC_AUDIT_LIMITS.md`] — "staged_only" framing replaced; "What this repo can establish today" / "What this repo cannot establish today" rewritten for v0.1.0 reality. Added explicit non-claims: no fitness-for-specific-deployment, no tuned-Parquet-always-diverges claim, no primitive-native closure.
- [`RELEASING.md`] — "This repo is evidence-gated and non-release until the actual gate is met. No public release action should happen from the current state." → rewritten to the always-in-beta cadence, with a concrete 9-item release checklist, and clear "what a release ships vs does not ship" framing.
- [`CHANGELOG.md`] — trailing `This repository is still staging_only` bullet removed; replaced with explicit "pre-0.1.0 used staging_only; v0.1.0 retires that framing" note.
- [`AUDITOR_PLAYBOOK.md`] — "It verifies structure and current known state. It does not establish release readiness" → "It verifies structure and current shipping state of the v0.1.0 perception-receipt surface. It does not by itself establish fitness for a particular downstream application." The "Explicitly deferred" list was pre-0.1.0 pessimism; removed.
- [`docs/LEGAL_BOUNDARIES.md`] — "This repo is a staging repo, not a public release" / "The repo does not currently claim GO" / "The repo does not currently claim public commercialization readiness" → rewritten to name v0.1.0, clarify the defended wedge is the receipt, and note that specific-deployment fitness is the integrator's responsibility.

## Primitive scope

- [`docs/_reorientation/2026-04-17/NOVELTY_CARD.md`] — new file; explicitly answers the Compass-8 question with NO and cites the three modules (`receipt.py`, `pipeline.py`, `codec.py`) that don't implement it. Documents the four novel contributions with `path:line` citations into `src/zpe_video/receipt.py` and `tests/test_receipt.py`.
- [`CONTRIBUTING.md`] — added an explicit "This codec does not use Compass-8 / 8-primitive directional encoding. Do not add framing that claims it does" line in the scope-discipline section, with pointer to NOVELTY_CARD.
- [`GOVERNANCE.md`] — added to the forbidden-claim list: "'primitive-native' or 'Compass-8' product-architecture framing for this codec" with pointer to NOVELTY_CARD.

## Honest limits

- [`README.md`] — the "What We Don't Claim" section already enumerated the five honest non-claims (universal codec, archive-query-as-ZPE, ROI sidecar, Parquet-cannot-be-tuned, user-visible speedup); kept intact and added the Compass-8 non-claim. The kill verdicts are surfaced in the "Competitive Benchmarks" row-that-we-lose-on (raw struct + zlib is smaller; explicitly disclosed) and in the Proof Anchors + Competitive Benchmarks sources.
- [`docs/WEDGE.md`] — killed-wedges table kept in full including Phase 08 AV1/VVC/learned losses, Phase 09.4.1.1.2 archive-query kill, Phase 09.4.1.1.2.1-A ROI-sidecar kill. Added the Compass-8 substrate retirement row. None of these are buried in footnotes.
- [`docs/transparency/`] — full kill-verdict PLAN + SUMMARY + harness + result-JSON preserved for Phase 09.4.1.1.2 (archive-query falsification) and Phase 09.4.1.1.2.1-A (ROI sidecar kill). Not summarized; verbatim.

## Not in scope (explicitly untouched)

- Code under `src/zpe_video/*.py` — the receipt module was newly written for v0.1.0; the legacy modules (`codec.py`, `pipeline.py`, etc.) were not modified.
- Tests under `tests/` — not modified. The 22-test suite still passes.
- The SAL v6.2 license text at `LICENSE` — per UNIVERSAL_BRIEF, the license pass is separate.
- Proof-artifact JSON values (numbers, hashes, SHAs) in `proofs/reference/*` or `docs/transparency/*/summary.json` — those are data, not narrative.
- The `.github/assets/` masthead GIF and section-bar SVGs — those are visual assets, not narrative.
- Historical verbatim-preserved `docs/transparency/*/PLAN.md` and `SUMMARY.md` files — these are preserved as they were written at the time of each phase; they are the evidence ledger, not forward-looking narrative. Any reframing belongs in `docs/TRANSPARENCY_JOURNEY.md` (the current-voice narrative), not in the historical records.
- The outer research tree under `.gpd/phases/` — the reorientation pass scope is this repo (`zpe-video/`), not the outer workspace.

## Summary

Fixes by category: drift 11 · clarity 3 · consistency 3 · framing 5 · beta posture 6 · primitive scope 3 · honest limits 3. Total distinct files touched: 18. No test files or code modules modified; 22-test suite still passes.
