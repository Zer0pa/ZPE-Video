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

## Gate A Input Resolution

Gate A no longer hardcodes machine-local absolute paths.

It now resolves optional input documents in this order:

1. `ZPE_VIDEO_NET_NEW_PACK_MD`
2. `ZPE_VIDEO_NET_NEW_PACK_PDF`
3. `ZPE_VIDEO_GAP_CLOSURE_MD`
4. repo-relative files under `docs/inputs/`

If those files are absent, Gate A should fail honestly instead of silently assuming someone else's machine layout.

## Authority Rule

Current runtime/artifact truth outranks dossier/live-status prose.

