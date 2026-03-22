# Local Continuation On Mac

## Current State

The latest narrow-surface experiment already ran locally on the Mac.

Local prerequisites that are present:

- outer workspace at `/Users/Zer0pa/ZPE/ZPE Video`
- local VIRAT surface under `datasets/VIRAT/kitware_release2`
- arm64 lab runtime at `zpe_video_lab/.venv-arm64`
- arm64 `libzpe_stroke.dylib` matching that runtime

## Current Local Entrypoint

```bash
cd "/Users/Zer0pa/ZPE/ZPE Video"
./zpe_video_lab/.venv-arm64/bin/python zpe_video_lab/python/phase9_3_narrow_surveillance_wedge.py
```

## What Can Continue Locally Without Pod

- rerunning `09.3`
- adjusting the narrow VIRAT cohort rule
- changing the evaluator logic on the current sparse facility surface
- updating docs, summaries, and handoff packs

## What Local Work Still Depends On

- the outer workspace, not just the GitHub mirror
- the local datasets already staged on the Mac
- the local arm64 lab build

If those remain intact, the pod is not required for immediate continuation on the current `09.3` lane.
