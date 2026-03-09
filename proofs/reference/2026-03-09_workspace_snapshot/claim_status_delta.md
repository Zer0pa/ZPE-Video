# Claim Status Delta

| Claim ID | Pre-status | Post-status | Metric | Threshold | Evidence | Notes |
|---|---|---|---|---|---|---|
| VID-C001 | UNTESTED | FAIL | 134.575028 | 50.0 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_compression_benchmark.json` | P0 claim cannot be PASS from proxy-only evidence (E-G2). |
| VID-C002 | UNTESTED | FAIL | 1.000000 | 0.9 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_detection_eval.json` | Missing or substituted dependencies for closure: compressai_vision |
| VID-C003 | UNTESTED | PASS | 99.000000 | 28.0 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_sketch_quality.json` | Threshold satisfied with required dependencies available. |
| VID-C004 | UNTESTED | PASS | 0.404310 | 0.6 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_mv_bitrate_eval.json` | Threshold satisfied with required dependencies available. |
| VID-C005 | UNTESTED | PASS | 0.015219 | 33.0 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_latency_benchmark.json` | Threshold satisfied with required dependencies available. |
| VID-C006 | UNTESTED | PAUSED_EXTERNAL | 0.049342 | 0.25 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_generative_eval.json` | Only NC/restricted generative path documented (SPADE/vid2vid), no commercial-safe open decoder validated in-lane for LPIPS-based generative closure. |
| VID-C007 | UNTESTED | PASS | 0.000000 | 5.0 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_edge_roundtrip_eval.json` | Threshold satisfied with required dependencies available. |
| VID-C008 | UNTESTED | PASS | 0.030285 | 50.0 | `/Users/Zer0pa/ZPE/ZPE Video/artifacts/2026-02-20_zpe_video_wave1/video_machine_mode_latency.json` | Threshold satisfied with required dependencies available. |
