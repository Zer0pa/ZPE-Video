# Phase 09.4.1.1.2.2 Plan - Receipt-Core Provenance Benchmark

## Question

Can the defended Candidate B receipt wedge be extended into a C2PA-style
receipt-core proof without changing the receipt bytes, hiding commodity
baselines, or claiming Phase 10 / primitive-native closure?

## In Scope

- Cross-writer byte identity between the library writer and an independent
  from-spec writer.
- External manifest binding by receipt SHA-256 and byte length.
- Default Parquet writer comparison when optional dependencies are present.
- Deterministic controls: canonical JSON, compressed canonical JSON, raw
  struct plus zlib.
- Empty and dense limiting cases.

## Out Of Scope

- Phase 10 execution.
- Red Magic runtime validation.
- Compass-8 primitive-native closure.
- Pixel compression, VMS replacement, or buyer-visible VideoLLM latency wins.

## Acceptance Gate

Pass only if:

- every ZPE library receipt byte-matches the independent receipt writer
- every manifest verifies against the exact receipt blob and content id
- baseline outputs are disclosed with availability and byte/hash fields
- tuned controls are not narrated as receipt-grade when they lack schema,
  versioning, or per-frame CRC
- `sovereign_gate_status` remains `red` in `summary.json`

## Kill Conditions

- any independent writer hash mismatch
- manifest binding requires mutable or writer-specific receipt bytes
- a commodity baseline is silently omitted or presented without scope
- storage-only results are treated as the authority metric
- any Phase 10 or primitive-native closure claim enters pass language

## Execution Command

```bash
python scripts/receipt_core_benchmark.py
```

## Outputs

- `summary.json`
- `baseline_table.csv`
- `manifest_binding.json`
