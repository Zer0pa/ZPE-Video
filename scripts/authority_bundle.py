"""Emit the deterministic ZPE Video authority-bundle manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import TypedDict

AUTHORITY_PROFILE = "zpe-video.authority-bundle.v1"
PREDICATE_TYPE = "https://zer0pa.ai/predicates/zpe-video-receipt/v1"
PHASE_ID = "09.4.1.1.2.2"

AUTHORITY_PATHS = (
    "README.md",
    "pyproject.toml",
    "CITATION.cff",
    "docs/WEDGE.md",
    "docs/WIRE_FORMAT.md",
    "docs/VERIFICATION.md",
    "docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/summary.json",
    "docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/manifest_binding.json",
    "docs/transparency/phase09_4_1_1_2_2_receipt_core_provenance_benchmark/baseline_table.csv",
    "src/zpe_video/receipt.py",
    "src/zpe_video/manifest.py",
    "tests/test_receipt.py",
    "tests/test_manifest.py",
)


class AuthorityFile(TypedDict):
    path: str
    size: int
    sha256: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_authority_packet(repo_root: Path) -> dict[str, object]:
    files: list[AuthorityFile] = []
    missing: list[str] = []

    for relative_path in AUTHORITY_PATHS:
        path = repo_root / relative_path
        if not path.is_file():
            missing.append(relative_path)
            continue
        data = path.read_bytes()
        files.append(
            {
                "path": relative_path,
                "size": len(data),
                "sha256": _sha256(data),
            }
        )

    if missing:
        formatted = ", ".join(missing)
        raise FileNotFoundError(f"authority bundle inputs missing: {formatted}")

    bundle_subject = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "profile": AUTHORITY_PROFILE,
        "phase_id": PHASE_ID,
        "predicate_type": PREDICATE_TYPE,
        "sovereign_gate_status": "red",
        "commercial_receipt_core_verdict": "PASS",
        "bundle_sha256": _sha256(bundle_subject),
        "files": files,
    }


def render_json(packet: dict[str, object]) -> bytes:
    return json.dumps(packet, sort_keys=True, indent=2).encode("utf-8") + b"\n"


def render_markdown(packet: dict[str, object]) -> str:
    files = packet["files"]
    if not isinstance(files, list):
        raise TypeError("packet files must be a list")
    file_rows = "\n".join(
        f"| `{entry['path']}` | `{entry['sha256']}` | {entry['size']} |" for entry in files
    )
    return "\n".join(
        [
            "# ZPE Video Current Authority Packet",
            "",
            f"- Profile: `{packet['profile']}`",
            f"- Phase: `{packet['phase_id']}`",
            f"- Predicate type: `{packet['predicate_type']}`",
            f"- Commercial receipt-core verdict: `{packet['commercial_receipt_core_verdict']}`",
            f"- Sovereign gate status: `{packet['sovereign_gate_status']}`",
            f"- Bundle SHA-256: `{packet['bundle_sha256']}`",
            "",
            "The bundle hash covers the canonical sorted list of authority files below. It is",
            "a repo-local receipt-chain anchor; it does not claim Phase 10 closure.",
            "",
            "| Path | SHA-256 | Bytes |",
            "|---|---:|---:|",
            file_rows,
            "",
        ]
    )


def write_packet(repo_root: Path) -> tuple[Path, Path]:
    packet = build_authority_packet(repo_root)
    manifest_dir = repo_root / "proofs" / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    json_path = manifest_dir / "current_authority_packet.json"
    md_path = manifest_dir / "CURRENT_AUTHORITY_PACKET.md"

    json_path.write_bytes(render_json(packet))
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if generated files differ from the current checked-in files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    if args.check:
        packet = build_authority_packet(repo_root)
        json_path = repo_root / "proofs" / "manifests" / "current_authority_packet.json"
        md_path = repo_root / "proofs" / "manifests" / "CURRENT_AUTHORITY_PACKET.md"
        if json_path.read_bytes() != render_json(packet):
            raise SystemExit("authority packet JSON is stale")
        if md_path.read_text(encoding="utf-8") != render_markdown(packet):
            raise SystemExit("authority packet Markdown is stale")
        print("authority packet is current")
        return 0

    expected_json, expected_md = write_packet(repo_root)

    print(f"wrote {expected_json.relative_to(repo_root)}")
    print(f"wrote {expected_md.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
