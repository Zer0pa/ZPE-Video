# Residual Risk Register

1. RISK-001: Dataset parity is partial (subset ingestion for VisDrone/UVG/VIRAT/HEVC assets).
- Impact: external validity is improved but still below full-corpus production confidence.
- Mitigation: complete full-corpus ingestion and rerun full benchmark matrix.

2. RISK-002: Comparator stack remains partially constrained by local environment coupling.
- Impact: full parity with external benchmark leaderboards remains limited.
- Mitigation: execute full comparator stack in dedicated GPU environment and publish parity table.

3. RISK-003: SPADE/vid2vid commercial-safe decoder path unresolved.
- Impact: generative claim C006 remains PAUSED_EXTERNAL.
- Mitigation: continue decoder-alternative exhaustion and rerun C006 closure tests.
- Evidence: `/Users/zer0pa-build/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/internet_evidence_log.md`.

4. RISK-004: Remaining proxy-derived paths still exist outside primary claim evidence.
- Impact: auxiliary robustness comparisons may underrepresent field variance.
- Mitigation: replace residual proxies with real-corpus stress slices.
