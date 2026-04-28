#!/usr/bin/env bash
set -euo pipefail

fail=0
for h in "## What This Is" "## Key Metrics" "## What We Prove" "## What We Don't Claim" \
         "## Commercial Readiness" "## Tests and Verification" "## Proof Anchors" \
         "## Repo Shape" "## Quick Start" "## Upcoming Workstreams"; do
  if grep -qF "$h" README.md; then
    echo "OK:      $h"
  else
    echo "MISSING: $h"
    fail=1
  fi
done

if grep -qF "## Competitive Benchmarks" README.md; then
  echo "OK:      ## Competitive Benchmarks (optional, present)"
fi

test "$fail" -eq 0

verdict_line="$(grep -E '^\| Verdict \|' README.md || true)"
if [ -z "$verdict_line" ] || ! printf '%s\n' "$verdict_line" | grep -Eq '\| (STAGED|PASS|PARTIAL|BLOCKED|FAIL|INCONCLUSIVE) \|'; then
  echo "FAIL: Verdict not in enum"
  exit 1
fi

for forbidden in \
  "## Comp Benchmarks" "## Verified Claims" "## CI-Anchored Claims" \
  "## What We Do Not Claim" "## Not Claimed" "## What Is Not Claimed" \
  "## Bounded Verdict" "## Verification Surface" "## CI-Backed Checks" \
  "## Evidence On Disk" "## Proof Routes" "## Proof Anchors Used by CI" \
  "## Public Benchmark Snapshot" "## Performance Metrics" "## Current Metrics" \
  "## Validation Summary" "## Measured Performance" "## Quick Verify"; do
  if grep -qF "$forbidden" README.md; then
    echo "FAIL: forbidden rename present: $forbidden"
    exit 1
  fi
done

if grep -qF '"License :: Other/Proprietary License"' pyproject.toml && grep -qE '^license = ' pyproject.toml; then
  echo "FAIL: PEP 639 license expression + classifier conflict"
  exit 1
fi

anchor_file="$(mktemp)"
awk '
  /^## Proof Anchors$/ { in_section=1; next }
  /^## / && in_section { in_section=0 }
  in_section { print }
' README.md | grep -oE '`[^`]+`' | tr -d '`' | while read -r p; do
  if [ ! -e "$p" ]; then
    echo "MISSING ANCHOR: $p"
    echo "$p" >> "$anchor_file"
  fi
done
if [ -s "$anchor_file" ]; then
  rm -f "$anchor_file"
  exit 1
fi
rm -f "$anchor_file"

pii_user="prinivenpillay"
legacy_user="Zer0pa"
pii_name="Priniven"" Pillay"
if grep -RInE --exclude='LICENSE' --exclude='*.pyc' --exclude-dir='.git' --exclude-dir='.venv' "/Users/(${pii_user}|${legacy_user})|${pii_name}" . >/tmp/zpe-video-pii-scan.txt; then
  cat /tmp/zpe-video-pii-scan.txt
  rm -f /tmp/zpe-video-pii-scan.txt
  echo "FAIL: hardcoded local PII path present"
  exit 1
fi
rm -f /tmp/zpe-video-pii-scan.txt

echo "PASS: compliance audit clean"
