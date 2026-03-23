# Local Continuation And Pod Shutdown

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
./zpe_video_lab/.venv-arm64/bin/python zpe_video_lab/python/phase9_3_1_portal_anchored_event_consumer.py
```

## What Can Continue Locally Without Pod

- rerunning `09.3.1`
- adjusting portal-local rule logic
- testing tighter facility-crossing micro-surfaces on the same VIRAT lane
- updating docs, summaries, and handoff packs

## Safe Pod Shutdown Read

For immediate continuation of the current `09.3.1` lane:

- pod is **not required**

The pod can be shut down if the Mac keeps:

- `datasets/VIRAT/kitware_release2/`
- `zpe_video_lab/.venv-arm64/`
- `zpe_video_lab/reports/phase9_3_1_portal_anchored_event_consumer/summary.json`
- `.gpd/`

## What Still Depends On Local Reality

- the outer workspace, not just the GitHub mirror
- the local VIRAT files already staged on the Mac
- the local arm64 lab build

If those remain intact, shutting down the pod does not block immediate continuation.
