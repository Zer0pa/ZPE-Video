# 2026-03-09 Workspace Snapshot

This folder is a curated subset copied from:

- `/Users/zer0pa-build/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/`

Copy date:

- `2026-03-09`

## Why This Exists

The repo needed a proof surface for custody review without copying the full outer-workspace artifact warehouse.

## Important Warning

This is not a clean run-of-record.

The source workspace bundle became mixed after a later resource-only probe refreshed `resource_inventory_unparseable_snapshot.txt`. That means:

- `handoff_manifest.json`, `claim_status_delta.md`, and `quality_gate_scorecard.json` still reflect the earlier full rerun
- `resource_inventory_unparseable_snapshot.txt` reflects a later partial dependency probe and is retained as custody text, not machine-readable authority

Use this folder as custody evidence, not as the final authority for release decisions.

## Sanitization Note

Machine-local paths in this committed copy use the `/Users/zer0pa-build/` alias required by the repo playbook. Historical SHA values embedded inside `handoff_manifest.json` are retained as source-bundle custody references and are not presented as checksums of this path-sanitized committed copy.
