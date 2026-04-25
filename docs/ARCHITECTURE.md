# Architecture

This repo packages the current ZPE Video Wave-1 lane as a standalone private staging surface.

## Runtime Map

| Surface | Role |
|---|---|
| `src/zpe_video/codec.py` | encode/decode logic |
| `src/zpe_video/fixtures.py` | deterministic proxy data generation |
| `src/zpe_video/metrics.py` | metric helpers |
| `src/zpe_video/vision.py` | simple frame/sketch utilities |
| `src/zpe_video/pipeline.py` | gate execution and artifact generation |
| `scripts/execute_wave1.py` | runner entrypoint |
| `tests/test_codec.py` | lightweight codec smoke coverage |

## Artifact And Proof Surfaces

- Runtime-generated outputs currently land under `artifacts/2026-02-20_zpe_video_wave1/`.
- Curated staged evidence for this repo lives under `proofs/reference/2026-03-09_workspace_snapshot/`.
- Future clean reruns should be written under `proofs/reruns/` and then promoted deliberately into `proofs/reference/`.

## Authority Rule

Current runtime/artifact truth outranks dossier/live-status prose.
