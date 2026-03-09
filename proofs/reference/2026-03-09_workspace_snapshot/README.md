# 2026-03-09 Workspace Snapshot

This folder is a curated subset copied from:

- `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/`

Copy date:

- `2026-03-09`

## Why This Exists

The repo needed a proof surface for private staging without copying the full outer-workspace artifact warehouse.

## Important Warning

This is not a clean run-of-record.

The source workspace bundle became mixed after a later resource-only probe refreshed `resource_inventory.json`. That means:

- `handoff_manifest.json`, `claim_status_delta.md`, and `quality_gate_scorecard.json` still reflect the earlier full rerun
- `resource_inventory.json` reflects a later partial dependency probe

Use this folder as custody evidence, not as the final authority for release decisions.

