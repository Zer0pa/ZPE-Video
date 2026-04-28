# ZPE-Video — Notation and Conventions

**Lane:** ZPE-Video
**GPD retrofit date:** 2026-04-28

## Hash Convention (Cross-Writer-Stable)

The ZPE-Video cross-writer hash convention is:

- `WIRE_MAGIC` = `ZPVID1` (6 bytes, ASCII)
- `WIRE_VERSION` = 1 (uint8)
- Hash function: `hashlib.sha256` over the complete encoded receipt bytes
- Canonical seed: `0` (uint32, opaque provenance tag)
- Delta encoding: signed 16-bit integers, sorted-canonical previous state as base
- Compression: `zlib.compress(..., level=9)` (fixed level for output stability)
- CRC: `zlib.crc32` per frame payload (mandatory, not optional)

Any two conforming writers on byte-identical input MUST produce the same
SHA-256 under these parameters. See `docs/WIRE_FORMAT.md` for the full
byte-level spec.

## Wire Format Reference

The authoritative byte-level specification lives at:
`docs/WIRE_FORMAT.md`

All phase SUMMARY and VERDICT documents that reference receipt formats must
cite this document. If a phase result depends on a specific wire version,
the version byte must be noted explicitly.

## SAL v7.0 License

This lane operates under the **Sovereign Attribution License v7.0** (SAL v7.0).
The full license text is at `LICENSE` (repo root). Key points for phase docs:

- External re-implementations of the wire format are permitted for conformance
  testing and interoperability.
- Commercial redistribution of the receipt format or derived products requires
  attribution and compliance with the SAL v7.0 terms.
- Phase evidence (summaries, verdict files, transparency bundles) may be cited
  with attribution.

## Zer0pa 8 Primitives

The 8 research primitives of Zer0pa are:

1. **Determinism** — given identical inputs, every invocation produces
   identical outputs.
2. **Finiteness** — the computation terminates in bounded space and time.
3. **Composability** — components can be freely combined without emergent
   behavior surprises.
4. **Verifiability** — claims are testable and falsifiable.
5. **Extensibility** — the format or system can be extended without breaking
   existing consumers.
6. **Transparency** — the research trail (successes, failures, killed wedges)
   is publicly documented.
7. **Auditability** — an external auditor can reproduce any verdict from the
   documented evidence.
8. **Recoverability** — if a component fails, the system can recover without
   data loss.

For ZPE-Video v0.1.0, primitives 1 (Determinism) and 4 (Verifiability) are
the load-bearing pair for the receipt wedge. Primitive 6 (Transparency) is
exercised by the public falsification trail.

## Phase Naming Convention

Phases use decimal notation: `09`, `09.1`, `09.3.2`, etc.
Sub-phases that run in parallel use letter suffixes: `09.4.1.1.2.1-A`, `-B`, `-C`.

GPD phase folders use full kebab-case expansion of the phase title:
`09.3.1-portal-anchored-primitive-event-consumer-on-sparse-facility-crossing/`

## Verdict Enum

The canonical Zer0pa verdict enum for phase-level claims:

| Enum | Meaning |
|---|---|
| `PASS` | Claim defended under falsification gate |
| `FAIL` | Claim falsified |
| `INCONCLUSIVE` | Tested; signal present but below gate; or result ambiguous |
| `UNTESTED` | Not yet exercised |
| `BLOCKED` | External dependency prevents execution |
| `SUSPENDED_BY_OWNER` | Owner decision to retire; no further execution planned |
| `PAUSED_EXTERNAL` | Waiting on external input |
| `ACTIVE` | Currently executing |

Descriptive labels (`bounded_signal_only`, `flat_lane_still_dominant`,
`retire_surface`) are phase-specific shorthand. Every descriptive label must
be paired with a canonical enum in the VERDICT.md file for that phase.

## Units and Measurement Conventions

- **Suppression**: fraction of detector invocations not executed, as a
  percentage. Sovereign gate is `>= 50%`.
- **Retention/Recall**: fraction of true-positive events preserved, as a
  percentage. Sovereign gate is `>= 95%`.
- **Bundle ratio**: factorized bundle size / flat lane size (dimensionless).
  Values < 1.0 mean the bundle is smaller.
- **LOOCV**: leave-one-clip-out cross-validation. Used to assess
  generalization across the VIRAT clip cohort.
- **MOT17Det**: the benchmark dataset used for the detector-routing phases
  (09-09 through 09.2).
- **VIRAT**: the surveillance dataset used for the narrow-surface phases
  (09.3 through 09.3.2).

## Path Sanitization Convention

No tracked file in this repo may contain hardcoded operator paths.

- Replace `<REPO_ROOT>/` for all repository-relative paths when an absolute
  path must be referenced in documentation.
- Replace `<OPERATOR_HOME>/` for any reference to the operator's home
  directory.
- The compliance script `scripts/compliance_audit.sh` enforces this check
  before every merge.

## Source Authority Hierarchy

When a narrative summary disagrees with a run-of-record JSON or phase
summary, trust:
1. Run-of-record JSON (highest authority)
2. Phase summary (`.gpd/PHASES/<phase>/SUMMARY.md`)
3. Explicit decision note
4. Narrative summary (lowest authority)

This hierarchy is stated in the original science-and-engineering packs and
is adopted as lane convention.
