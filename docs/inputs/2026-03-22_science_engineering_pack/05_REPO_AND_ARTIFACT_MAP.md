# Repo And Artifact Map

Date: `2026-03-22`

## GitHub-Tracked Inner Repo Surface

Core package:

- `src/zpe_video/codec.py`
- `src/zpe_video/models.py`
- `src/zpe_video/vision.py`
- `src/zpe_video/metrics.py`
- `src/zpe_video/pipeline.py`
- `src/zpe_video/detector.py`

Key scripts:

- `scripts/execute_wave1.py`
- `scripts/measure_am_c01.py`
- `scripts/measure_am_c01_ladder.py`

Minimal test surface:

- `tests/test_codec.py`

Science handoff pack:

- `docs/inputs/2026-03-22_science_engineering_pack/`

## Outer Workspace Authority Surface

These files remain outside the inner GitHub repo and are the current research authority sources:

- `/Users/Zer0pa/ZPE/ZPE Video/.gpd/phases/09-architectural-purification-and-contour-primary-recovery/09-09-SUMMARY.md`
- `/Users/Zer0pa/ZPE/ZPE Video/artifacts/phases/09-architectural-purification-and-contour-primary-recovery/temporal-scoring-frontier-decision.md`
- `/Users/Zer0pa/ZPE/ZPE Video/zpe_video_lab/reports/phase9_temporal_scoring_frontier/summary.json`
- `/Users/Zer0pa/ZPE/ZPE Video/.gpd/phases/09.1-seedance-informed-video-subchannel-factorization-hypothesis/09.1-01-SUMMARY.md`
- `/Users/Zer0pa/ZPE/ZPE Video/artifacts/phases/09.1-seedance-informed-video-subchannel-factorization-hypothesis/subchannel-factorization-decision.md`
- `/Users/Zer0pa/ZPE/ZPE Video/zpe_video_lab/reports/phase9_1_video_subchannel_factorization/summary.json`
- `/Users/Zer0pa/ZPE/ZPE Video/.gpd/phases/09.2-primitive-native-layered-control-plane-wedge/09.2-01-SUMMARY.md`
- `/Users/Zer0pa/ZPE/ZPE Video/artifacts/phases/09.2-primitive-native-layered-control-plane-wedge/layered-wedge-decision.md`
- `/Users/Zer0pa/ZPE/ZPE Video/zpe_video_lab/reports/phase9_2_primitive_layered_wedge/summary.json`

## What The Team Should Actually Open First

- This pack for a compact read
- `phase9_temporal_scoring_frontier/summary.json` for the defended temporal reference
- `phase9_1_video_subchannel_factorization/summary.json` for the Seedance-informed bounded result
- `phase9_2_primitive_layered_wedge/summary.json` for the layered-control-plane bounded result

## Why The Map Matters

The handoff problem is not only scientific. It is also topological: code and GitHub history live in the inner repo, while the freshest experiment history still lives one level up in the outer workspace.
