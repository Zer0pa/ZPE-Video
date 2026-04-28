# Phase 09.4.1.1.2.2 Summary - Receipt-Core Provenance Benchmark

## Verdict

`pass` for the bounded commercial receipt-core proof.

## What Passed

- ZPE library writer and independent from-spec writer produced identical
  receipt bytes and SHA-256 on all benchmark cases.
- C2PA-style manifest binding verified on all benchmark cases.
- Default Parquet baselines were generated for pyarrow and fastparquet in
  the local execution environment.
- Canonical JSON, compressed canonical JSON, and raw struct plus zlib
  controls were disclosed rather than hidden.

## What Did Not Pass

No sovereign gate passed here. This benchmark does not execute Phase 10,
does not qualify Red Magic runtime, and does not prove Compass-8
primitive-native closure.

## Key Machine Results

See `summary.json`:

- `zpe_receipt_cross_writer_stable_all_cases: true`
- `manifest_binding_verified_all_cases: true`
- `parquet_pair_available_all_cases: true`
- `parquet_default_cross_writer_stable_all_cases: false`
- `tuned_controls_close_storage_gap: true`
- `sovereign_gate_status: red`

The tuned control result is not promoted into a kill because the control
is not receipt-grade: it lacks the receipt envelope, versioned schema, and
per-frame CRC authority surface.

## Evidence Files

- `summary.json`
- `baseline_table.csv`
- `manifest_binding.json`

## Non-Claims

- No Phase 10 execution.
- No Red Magic runtime validation.
- No primitive-native closure.
- No universal compression superiority.
- No claim that Parquet cannot be configured for deterministic output.
