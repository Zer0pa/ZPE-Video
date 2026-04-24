# Canonicalization Notes

Date: `2026-03-22`

## What Was Cleaned Up In The Inner Repo

- Restored tracked compatibility files that had been deleted while new measurement code still depended on them.
- Kept the new detector surface and AM-C01 measurement scripts instead of discarding them.
- Refreshed the repo front door so the current bounded state is visible from `README.md`.
- Added this GitHub-tracked handoff pack so the current scenario is not trapped only in the outer workspace.

## Why The Compatibility Restore Was Necessary

Before cleanup, the inner repo had become half-refactored:

- new measurement scripts imported package modules that had been deleted from the tracked repo
- `zpe_video.pipeline` no longer imported cleanly
- the only tracked test surface had been removed

That is not acceptable for a canonical handoff repo. The cleanup restored coherence first, then preserved the newer measurement additions.

## Current Canonicalization Risk

The biggest remaining risk is not code breakage. It is split truth:

- GitHub now has the code and the handoff pack
- the freshest `.gpd` phase history and run-of-record JSON still live outside the inner repo

If you want one fully canonical surface later, the next cleanup step should be to mirror the authoritative phase summaries and JSON extracts into a tracked inner-repo evidence area on every material phase close.

## Recommended Rule Going Forward

- inner repo: code, tracked handoff docs, compact evidence mirrors
- outer workspace: active mutable lab history
- run-of-record JSON wins when prose drifts
