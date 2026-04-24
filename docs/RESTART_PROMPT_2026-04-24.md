# ZPE-Video Restart Prompt - 2026-04-24

You are restarting the ZPE-Video lane after local Mac deletion. Do not rely on
any pre-existing local files. The authorities are GitHub and Hugging Face only.

## Lane

- Lane: ZPE-Video
- GitHub repo: `https://github.com/Zer0pa/ZPE-Video`
- Current recovery PR: `https://github.com/Zer0pa/ZPE-Video/pull/2`
- Recovery branch: `reorientation/2026-04-17`
- Recovery branch before this prompt correction: `bd5415e76aa9abd3081c21297c1cba224ae34fb1`
- Current custody commits:
  - `f833bd8` - `custody: harden video receipt core`
  - `cad0b29` - `fix: make receipt benchmark proof deterministic`
  - `bd5415e` - `custody: add video restart prompt`

## Clone And Restore

```bash
mkdir -p /Users/Zer0pa/ZPE
cd /Users/Zer0pa/ZPE
git clone https://github.com/Zer0pa/ZPE-Video.git "ZPE Video"
cd "ZPE Video"
git checkout reorientation/2026-04-17
git pull --ff-only origin reorientation/2026-04-17
```

If PR #2 has already merged, use `main` instead and verify that the receipt-core
custody commits above, this restart prompt, and the authority packet are present.

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

Use the existing private Zer0pa org Hugging Face repos. The repo IDs are
case-sensitive. Do not use lowercase `zpe-video-*` repo IDs for this lane.

Artifact/dataset custody:

- HF dataset: `Zer0pa/ZPE-Video-artifacts`
- URL: `https://huggingface.co/datasets/Zer0pa/ZPE-Video-artifacts`
- Contains:
  - `local/` analysis packets, receipt-adjacent reports, and small archives.
  - `runpod/` evidence bundles, including `zpe_video_lab`, `zpe_video_phase03`,
    `CompressAI-Vision`, cycle-8 budget images, UVG frames, VIRAT annotations,
    and RunPod reports.
  - `zpe_video_lab_worktree/` excluding `.git`, caches, and bytecode.
  - `restart_prompts/ZPE-Video_RESTART_PROMPT_2026-04-24.md`.

Model/checkpoint custody:

- HF model repo: `Zer0pa/ZPE-Video-models`
- URL: `https://huggingface.co/Zer0pa/ZPE-Video-models`
- Contains RT-DETR weights, YOLO weights, graph model checkpoints, and cycle-8
  checkpoint artifacts under `runpod/zpe_video_lab/...`.

Verified live HF paths on 2026-04-24:

- `runpod/zpe_video_lab/data/cycle8_zpe_budgets/b1000/images/train/000000013774_b1000.png`
- `runpod/zpe_video_lab/data/cycle8_zpe_budgets/b8000/images/train/000000425925_b8000.png`
- `runpod/zpe_video_lab/data/uvg_beauty/frames_480p/frame_0005.png`
- `local/strokegat_cycle4_sync.tar.gz`
- `local/database.xml`
- `runpod/zpe_video_lab/reports/h_c2_stroke_gat_results.json`
- `runpod/zpe_video_lab/python/rtdetr-l.pt`
- `runpod/zpe_video_lab/reports/cycle8_track_a_runs/domain_adapt_mixed/weights/best.pt`

Restore HF artifacts only when needed:

```bash
hf auth whoami
hf download Zer0pa/ZPE-Video-artifacts --type dataset --local-dir hf_zpe_video_artifacts
hf download Zer0pa/ZPE-Video-models --type model --local-dir hf_zpe_video_models
```

Do not pull the multi-GB artifact repo unless the next task explicitly needs old
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
