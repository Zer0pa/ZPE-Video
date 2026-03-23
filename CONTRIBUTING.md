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
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
python3 -m compileall src scripts
pytest tests/test_codec.py
python3 - <<'PY'
import sys
sys.path.insert(0, "src")
from zpe_video import Wave1Pipeline
print(Wave1Pipeline)
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
- Repo cleanup is not a scientific pass.
- If the governing metric remains red, the repo must still say so.

`LICENSE` is the legal source of truth for contributions and usage.
