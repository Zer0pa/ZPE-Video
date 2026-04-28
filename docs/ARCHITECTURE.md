# Architecture

ZPE Video packages a standalone video-structure encoding product. It is scoped to the Video lane and does not claim directional-primitive profile architecture or portfolio-wide platform architecture.

## Runtime Map

| Surface | Role |
|---|---|
| `src/zpe_video/codec.py` | `.zpvid` encode/decode logic |
| `src/zpe_video/fixtures.py` | deterministic proxy data generation |
| `src/zpe_video/metrics.py` | metric helpers |
| `src/zpe_video/vision.py` | frame/sketch utilities |
| `src/zpe_video/pipeline.py` | gate execution and artifact generation |
| `scripts/execute_wave1.py` | runner entrypoint |
| `tests/test_codec.py` | deterministic codec smoke coverage |

## Artifact And Proof Surfaces

- GitHub stores code, docs, tests, and lightweight proof metadata.
- Architect-Prime Hugging Face stores heavy Video artifacts, checkpoints, and scratch bucket content.
- Curated historical evidence in this repo lives under `proofs/reference/2026-03-09_workspace_snapshot/`.
- Future clean reruns should be written under `proofs/reruns/` and promoted deliberately into `proofs/reference/`.

## Authority Rule

Current runtime and proof artifacts outrank dossier or status prose. The current committed authority packet is historical and BLOCKED for commercial readiness because Gate A is FAIL and the snapshot is mixed.
