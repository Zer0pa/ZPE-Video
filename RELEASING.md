<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

This repo is evidence-gated and non-release until the actual gate is met.

No public release action should happen from the current state.

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

All of the following must be true before any public release or visibility
change:

1. The exact commit has a current operator greenlight.
2. Active path portability defects are closed.
3. The dependency contract is stable and documented.
4. A clean rerun is executed from the repo itself.
5. The proof index is updated with clean repo-generated evidence.
6. Blind-clone verification succeeds.
7. Security validation succeeds on the exact release commit.

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

Current release state is below gate because:

- the governing science gate is still red
- the staged proof snapshot is mixed
- a fresh repo-local run-of-record does not yet exist
- blind-clone verification has not been run

If evidence conflicts, the repo stays non-release.
