---
name: Bug Report
about: Something is broken in the repo, package, script, proof route, or docs
labels: bug
assignees: ''
---

<p>
  <img src="../assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../assets/readme/section-bars/bug-report.svg" alt="BUG REPORT" width="100%">
</p>

**Describe the bug**

A clear description of what is broken and what you expected instead.

**Component**

- [ ] `zpe_video` package
- [ ] Script or harness
- [ ] Proof surface or artifact route
- [ ] Documentation or repo structure
- [ ] GitHub template or workflow

**To reproduce**

Exact commands and inputs to reproduce the issue.

**Expected output**

What should have happened.

**Actual output**

What actually happened. Include full error output.

**Verification check**

- [ ] `python3 -m compileall src scripts` still passes
- [ ] `pytest tests/test_codec.py` still passes
- [ ] `from zpe_video import Wave1Pipeline` still imports cleanly
- [ ] I attached the failing output or artifact path

**Environment**

- Python version:
- OS:
- Install method:
- Relevant dependency versions:

**Evidence**

If this touches behaviour, attach or link before/after metrics, logs, or
a minimal reproducible artifact.
