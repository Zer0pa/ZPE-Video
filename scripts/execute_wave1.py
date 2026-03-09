#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))

    from zpe_video import Wave1Pipeline

    parser = argparse.ArgumentParser(description="Run ZPE Video Wave-1 gates.")
    parser.add_argument(
        "--gate",
        default="ALL",
        choices=[
            "A",
            "B",
            "C",
            "D",
            "E",
            "M1",
            "M2",
            "M3",
            "M4",
            "ALL",
            "a",
            "b",
            "c",
            "d",
            "e",
            "m1",
            "m2",
            "m3",
            "m4",
            "all",
        ],
        help="Gate to execute.",
    )
    args = parser.parse_args()

    pipeline = Wave1Pipeline(repo_root=repo_root)
    result = pipeline.run(args.gate.upper())
    print(json.dumps({"gate_results": result}, indent=2, sort_keys=True))
    if args.gate.upper() == "ALL":
        return 0 if all(result.values()) else 1
    return 0 if result.get(args.gate.upper(), False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
