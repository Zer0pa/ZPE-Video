<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/license-and-ip.svg" alt="LICENSE AND IP" width="100%">
</p>

`LICENSE` is the legal source of truth for this repo.

This document is an operational boundary summary only.

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

- This repo ships the `zpe-video` Python package at v0.1.0 under SAL v6.2 (see `LICENSE`).
- The historical proof subset under `proofs/reference/2026-03-09_workspace_snapshot/` is dated pre-0.1.0 evidence custody; live v0.1.0 evidence is under `docs/transparency/`.
- Raw datasets (VIRAT, LongVideoBench, MLVU, etc.) are not bundled. Each has its own upstream license; harnesses in `docs/transparency/*/harness.py` point at public sources.
- Third-party comparators (Parquet via pyarrow / fastparquet, ffmpeg via libx265, YOLOv8m via ultralytics, DINOv2 / SigLIP / Qwen2.5 via transformers) retain their own licenses. See their respective upstream projects.

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

- Current claim posture: v0.1.0 ships one defended commercial wedge (cross-writer-stable perception receipt; see `WEDGE.md`).
- The repo does not claim primitive-native Compass-8 substrate closure; that historical research thesis was tested and is preserved as such.
- The repo does not claim fitness for any specific regulated deployment; downstream integration audits are the responsibility of the integrator.

<p>
  <img src="../.github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

- Datasets referenced by the pipeline remain external to the repo.
- Optional comparator stacks are not fully vendored here.
- Any future public release must re-check the dependency, proof, and license boundary on the exact release commit.
