# ZPE-Video Restart Prompt - 2026-04-24

You are restarting the ZPE-Video lane after local Mac deletion. Do not rely on
any pre-existing local files. The authorities are GitHub and Hugging Face only.

## Lane

- Lane: ZPE-Video
- GitHub repo: `https://github.com/Zer0pa/ZPE-Video`
- Current recovery PR: `https://github.com/Zer0pa/ZPE-Video/pull/2`
- Recovery branch: `reorientation/2026-04-17`
- Current recovery commit: `cad0b2994dfb26bd7c659c4a053a49ebc3dbe03c`
- Current custody commits:
  - `f833bd8` - `custody: harden video receipt core`
  - `cad0b29` - `fix: make receipt benchmark proof deterministic`

## Clone And Restore

```bash
mkdir -p /Users/Zer0pa/ZPE
cd /Users/Zer0pa/ZPE
git clone https://github.com/Zer0pa/ZPE-Video.git "ZPE Video"
cd "ZPE Video"
git checkout reorientation/2026-04-17
git pull --ff-only origin reorientation/2026-04-17
```

If PR #2 has already merged, use `main` instead and verify that commit
`cad0b2994dfb26bd7c659c4a053a49ebc3dbe03c` or its merge equivalent is present.

## Verify Repo Recovery

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip uv
uv sync --extra dev --extra benchmark
uv run pytest tests -v
uv run python scripts/receipt_core_benchmark.py
uv run python scripts/authority_bundle.py --check
uv build
```

Expected:

- 29 tests pass.
- `scripts/receipt_core_benchmark.py` returns `"verdict": "pass"`.
- `scripts/authority_bundle.py --check` returns `authority packet is current`.
- GitHub PR #2 checks are green.

## Current Truth Boundary

- Commercial receipt-core verdict: PASS.
- Sovereign primitive-native gate: red.
- Phase 10 remains blocked unless separately verified.
- Do not equate the nested `zpe-video` receipt wedge with sovereign
  primitive-native closure.
- Do not claim Red Magic runtime qualification from this lane state.

## GitHub Authority Surface

The GitHub PR contains all code, docs, workflows, reproducibility metadata, and
small proof files needed to resume:

- `src/zpe_video/manifest.py`
- `scripts/receipt_core_benchmark.py`
- `scripts/authority_bundle.py`
- `tests/test_manifest.py`
- `docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/`
- `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`
- `proofs/manifests/current_authority_packet.json`
- `REPRODUCIBILITY.md`
- `.zenodo.json`
- `uv.lock`

## Hugging Face Custody Surface

Zer0pa org HF writes failed during emergency custody with `403 Forbidden`.
The emergency fallback is private Hugging Face storage under the authenticated
`Architect-Prime` account. Migrate these repos to the Zer0pa org when org-write
auth is repaired.

Artifact/dataset custody:

- HF dataset: `Architect-Prime/zpe-video-artifacts`
- URL: `https://huggingface.co/datasets/Architect-Prime/zpe-video-artifacts`
- Contains:
  - `.custody_staging/artifacts` upload at repo root, including `runpod/` and
    `local/` evidence bundles.
  - `custody_staging/scratch/`
  - `zpe_video_lab_worktree/` excluding `.git`, caches, and bytecode.

Model/checkpoint custody:

- HF model repo: `Architect-Prime/zpe-video-models`
- URL: `https://huggingface.co/Architect-Prime/zpe-video-models`
- Contains `.custody_staging/models`, including RT-DETR weights and cycle-8
  checkpoint artifacts.

Restore HF artifacts only when needed:

```bash
hf auth whoami
hf download Architect-Prime/zpe-video-artifacts --type dataset --local-dir hf_zpe_video_artifacts
hf download Architect-Prime/zpe-video-models --type model --local-dir hf_zpe_video_models
```

Do not pull the 11+ GB artifact repo unless the next task explicitly needs old
RunPod/local research bundles.

## Disk Hygiene After Restart

The active repo should be small. Regenerable local bloat can be deleted:

- `.venv/`
- `dist/`
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`
- `src/zpe_video.egg-info/`

Do not delete newly generated evidence until it is either committed to GitHub or
uploaded to HF.

## Immediate Next Action

Resume from GitHub PR #2. If the user asks for release/merge readiness, inspect
the PR checks first. If the user asks for large historical evidence, restore the
specific HF subset instead of downloading everything.

