# ZPE-Video — Lane Identity

**Lane:** ZPE-Video
**Domain:** AI video pipeline tooling — perception-receipt format
**Version:** 0.1.0 (always-in-beta)
**License:** SAL v7.0 (Sovereign Attribution License)
**Repo:** `Zer0pa/zpe-video`
**GPD retrofit date:** 2026-04-28

## What This Lane Is

ZPE-Video is the Zer0pa research lane that produced the **perception-receipt
wire format** for AI video pipelines. A perception receipt is a compact,
deterministic binary record of what a detector + tracker saw in a video. Its
defining property: under default settings, any two conforming writer
implementations produce **byte-identical output** on byte-identical input —
so the SHA-256 of a receipt is a stable cryptographic reference across
platforms and languages.

The v0.1.0 wedge is the cross-writer hash-stable AI-perception receipt.
All broader wedge claims were falsified through the 09.x phase series.

## What This Lane Is Not

- Not a claim about the Compass-8 / 8-primitive directional-encoding
  architecture. This codec does not use it. (See `docs/NOVELTY_CARD.md`.)
- Not a universal video-codec superiority claim (killed in Phase 08).
- Not an archive-query ZPE-specific claim (killed in Phase 09.4.1.1.2).

## Zer0pa 8 Primitives — Lane Position

The 8 primitives (determinism, finiteness, composability, verifiability,
extensibility, transparency, auditability, recoverability) are the Zer0pa
research primitives. For ZPE-Video specifically:

- **Determinism** is the load-bearing property (cross-writer bit-exactness).
- **Verifiability** is exercised by the cross-writer conformance test and
  per-frame CRC32.
- **Transparency** is exercised by the public falsification trail in
  `docs/TRANSPARENCY_JOURNEY.md`.
- The remaining primitives apply to future phases; they are not claimed as
  delivered for v0.1.0.

## Current Active Phase

`09.4.1.1.2.2` — receipt-core provenance benchmark and C2PA readiness.
Verdict: PASS (per authority packet in `proofs/manifests/CURRENT_AUTHORITY_PACKET.md`).

## Key Documents

| Document | Purpose |
|---|---|
| `docs/WEDGE.md` | One-page wedge claim and falsification table |
| `docs/WIRE_FORMAT.md` | Byte-level wire format specification |
| `docs/TRANSPARENCY_JOURNEY.md` | Full phase falsification trail |
| `proofs/manifests/CURRENT_AUTHORITY_PACKET.md` | Authority bundle for current phase |
| `.gpd/STATE.md` | Current operating state |
| `.gpd/ROADMAP.md` | Phase list with verdicts |
