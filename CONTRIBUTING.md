<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/before-you-start.svg" alt="BEFORE YOU START" width="100%">
</p>

This repo follows a falsification-first contribution standard.

Working rules:

- Negative findings are valid contributions.
- Do not turn mixed evidence into a pass narrative.
- Do not hardcode machine-local paths.
- Keep changes scoped and evidence-backed.
- If a change touches status claims, proof routing, or gate logic, update
  the relevant docs and artifact references.

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Run the low-cost checks first:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
python3 -m compileall src scripts
python3 -m pytest tests -v
python3 examples/02_cross_writer.py   # expect: "cross-writer wedge: VERIFIED"
python3 - <<'PY'
import zpe_video
print("version:", zpe_video.__version__)
print("public:", sorted(zpe_video.__all__))
PY
```

If your change affects behaviour, attach the exact artifact path, metric
delta, or proof note in the PR. If it does not, say why evidence is not
required.

<p>
  <img src=".github/assets/readme/section-bars/what-we-accept.svg" alt="WHAT WE ACCEPT" width="100%">
</p>

- Path portability fixes
- Dependency-contract cleanup
- Repo-structure hardening
- Documentation corrections
- Proof-route corrections
- Negative findings with exact evidence

<p>
  <img src=".github/assets/readme/section-bars/what-we-do-not-accept.svg" alt="WHAT WE DO NOT ACCEPT" width="100%">
</p>

- New broad claims without rerun evidence
- Path hacks tied to one machine
- Cosmetic churn that does not improve install, run, or audit clarity
- Silent weakening of failing or retired evidence

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

- Repo cleanup is valuable.
- Repo cleanup is not a research pass.
- Claims in docs must match the current code, tests, and artifacts — if
  a kill verdict is recorded in [`docs/transparency/`](docs/transparency/),
  the README and docs must not quietly reframe it as a win.
- This codec does not use Compass-8 / 8-primitive directional encoding.
  Do not add framing that claims it does (see
  [`docs/_reorientation/2026-04-17/NOVELTY_CARD.md`](docs/_reorientation/2026-04-17/NOVELTY_CARD.md)).

`LICENSE` is the legal source of truth for contributions and usage.
