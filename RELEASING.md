# Releasing

This repo is private-first and evidence-gated.

No public release action should happen from this state.

## Release Gate

All of the following must be true before any public release or visibility change:

1. The exact commit has a current inspector greenlight.
2. Active path portability defects are closed.
3. The dependency contract is stable and documented.
4. A clean rerun is executed from the repo itself.
5. The proof index is updated with clean repo-generated evidence.
6. Blind-clone verification succeeds.
7. Explicit operator approval is captured for the exact commit.

## Current Status

Current status is below release gate because:

- proof state is still `NO-GO`
- the staged proof snapshot is mixed
- blind-clone verification has not been run

## Release Rule

If evidence conflicts, the repo stays private.
