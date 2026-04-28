# Reproducibility

## Scope

This document covers the repo-local reproducibility surface. Heavy artifacts, historical datasets, and model checkpoints are stored on Hugging Face under Architect-Prime rather than committed to Git.

## Fresh Clone Check

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall src scripts
python -m unittest tests/test_codec.py -v
```

## Evidence Check

```bash
test -e proofs/reference/2026-03-09_workspace_snapshot/handoff_manifest.json
test -e proofs/reference/2026-03-09_workspace_snapshot/claim_status_delta.md
test -e proofs/reference/2026-03-09_workspace_snapshot/determinism_replay_results.json
```

## Heavy Artifact Recovery

Use the Architect-Prime Hugging Face repos when a reviewer needs the heavy Video corpus:

```bash
hf download Architect-Prime/zpe-video-artifacts --repo-type dataset
hf download Architect-Prime/zpe-video-models
hf buckets ls hf://buckets/Architect-Prime/zeropa-org-ZPE-Video-scratch -R
```

Do not restore the full heavy corpus into the Git repository. Keep GitHub as code and lightweight proof metadata; keep heavy bytes on Hugging Face.

## Current Authority Boundary

The committed March 2026 proof snapshot is historical custody evidence. A clean rerun must write new artifacts under `proofs/reruns/` before any commercial-readiness pass is asserted.

