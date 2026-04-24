# Open Questions — 2026-04-17

Questions surfaced by the reorientation pass that the repo agent cannot resolve alone.

## For the license agent

See [`NOVELTY_CARD.md`](NOVELTY_CARD.md) section "Open novelty questions for the license agent" — five items pinned there, each asking for the license agent's judgment on what belongs in the per-product novelty schedule versus what is disclosure-only. Summarized here for visibility:

1. Is "cross-writer byte-exactness under default settings" a method claim or a format-disclosure-plus-conformance-test claim?
2. Does the in-test independent-implementation pattern (test re-implements the spec, asserts byte-identity with the library) count as protectable discipline or is it standard hygiene?
3. Should the "overflow-is-an-error, not silent truncation" delta-encoding contract be called out separately or rolled into #1?
4. Is the "zero-runtime-dependency, <100-LOC-per-language re-implementability" product-property framed correctly (format-designed-for-implementability is novel, not implementability itself)?
5. Is "no timestamps, no writer metadata" as a spec-level prohibition a protectable discipline or a standard hygiene note?

## For the operator / repo owner

1. **PyPI publication.** The current install path is `pip install -e .[dev]` from a local checkout. The playbook-conforming README's Quick Start uses `git clone`. Publishing to PyPI would let the Quick Start become `pip install zpe-video`. The reorientation did not make that change because it is a release-cut decision, not a doc-alignment decision. Decision needed: publish v0.1.0 to PyPI, or keep source-only install through v0.1.x.

2. **CI secrets / tokens.** The new `.github/workflows/ci.yml` and `verify-package.yml` do not require secrets. The pre-existing `auto-add-to-project.yml` references `secrets.ADD_TO_PROJECT_PAT`. No action taken; flagging because any release pass that includes a publish workflow will want a separate secret audit.

3. **Historical `proofs/reference/2026-03-09_workspace_snapshot/` retention.** That directory holds ~3 MB of pre-0.1.0 evidence-custody artifacts, mostly dated March 2026. The reorientation framed it as historical; it was not deleted. If the repo owner wants the public tree slimmer, those can be moved to a release-notes archive or git-history-only. Decision needed: retain, archive to git-history, or remove outright (kill verdicts stay either way under `docs/transparency/`).

4. **Root README playbook — "Commit SHA" placeholder.** The `## Commercial Readiness` table has `Commit SHA | pre-commit (to be stamped on commit)`. The website generator may prefer an actual SHA. The reorientation pass does not stamp it because the stamp depends on which commit ships; a release workflow can substitute at release time via `git rev-parse HEAD`. Decision needed: leave placeholder for website generator to fill, or stamp on release with a post-commit `sed` step.

5. **`docs/transparency/` vs outer research tree synchronization.** The transparency bundle in this repo is a copy of `.gpd/phases/09.4.1.1.2*/` from the outer research tree. Two locations will drift over time as new phases run. Decision needed: document the outer tree as authoritative and this tree as a release-snapshot copy (currently the stance), or adopt a symlink / submodule relationship, or promote `docs/transparency/` to authoritative and stop writing into the outer tree for new phases.

None of these block the reorientation PR. They are captured so the next decision-owner does not have to re-discover them.
