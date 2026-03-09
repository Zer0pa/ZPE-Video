from __future__ import annotations

from pathlib import Path

ARTIFACT_RELATIVE_ROOT = Path("artifacts/2026-02-20_zpe_video_wave1")
GLOBAL_SEED = 20260220
GATE_SEEDS = {
    "A": 20260221,
    "B": 20260222,
    "C": 20260223,
    "D": 20260224,
    "E": 20260225,
    "M1": 20260226,
    "M2": 20260227,
    "M3": 20260228,
    "M4": 20260229,
}

CLAIM_THRESHOLDS = {
    "VID-C001": 50.0,  # compression ratio vs h265
    "VID-C002": 0.90,  # zpe_map / h265_map
    "VID-C003": 28.0,  # sketch psnr
    "VID-C004": 0.60,  # zpe_mv_bitrate / h265_mv_bitrate
    "VID-C005": 33.0,  # ms/frame
    "VID-C006": 0.25,  # lpips
    "VID-C007": 5.0,  # edge mse percent
    "VID-C008": 50.0,  # machine mode ms
}

CLAIM_EVIDENCE_FILES = {
    "VID-C001": "video_compression_benchmark.json",
    "VID-C002": "video_detection_eval.json",
    "VID-C003": "video_sketch_quality.json",
    "VID-C004": "video_mv_bitrate_eval.json",
    "VID-C005": "video_latency_benchmark.json",
    "VID-C006": "video_generative_eval.json",
    "VID-C007": "video_edge_roundtrip_eval.json",
    "VID-C008": "video_machine_mode_latency.json",
}

MANDATORY_FILES = [
    "handoff_manifest.json",
    "before_after_metrics.json",
    "falsification_results.md",
    "claim_status_delta.md",
    "command_log.txt",
    "video_compression_benchmark.json",
    "video_detection_eval.json",
    "video_sketch_quality.json",
    "video_mv_bitrate_eval.json",
    "video_latency_benchmark.json",
    "video_generative_eval.json",
    "video_edge_roundtrip_eval.json",
    "video_machine_mode_latency.json",
    "determinism_replay_results.json",
    "regression_results.txt",
    "quality_gate_scorecard.json",
    "innovation_delta_report.md",
    "integration_readiness_contract.json",
    "residual_risk_register.md",
    "commercialization_risk_register.md",
    "internet_evidence_log.md",
    "concept_open_questions_resolution.md",
    "concept_resource_traceability.json",
    "max_resource_lock.json",
    "max_resource_validation_log.md",
    "max_claim_resource_map.json",
    "impracticality_decisions.json",
    "external_baseline_comparison_table.csv",
    "net_new_gap_closure_matrix.json",
    "runpod_readiness_manifest.json",
    "runpod_exec_plan.md",
    "runpod_dataset_stage_manifest.json",
    "runpod_pinned_deps_lock.txt",
    "runpod_expected_artifact_manifest.json",
]

RESOURCE_DEPENDENCIES = {
    "VID-C001": ["ffmpeg_h265", "virat_dataset"],
    "VID-C002": ["ffmpeg_h265", "visdrone_dataset", "compressai_vision"],
    "VID-C003": ["uvg_dataset"],
    "VID-C004": ["hevc_ctc_dataset"],
    "VID-C005": [],
    "VID-C006": ["xiph_derf", "lpips_package", "commercial_decoder_stack"],
    "VID-C007": [],
    "VID-C008": [],
}

CORE_P0_CLAIMS = ["VID-C001", "VID-C002", "VID-C006"]
