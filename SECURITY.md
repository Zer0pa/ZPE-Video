# Security Policy

Do not open a public issue for a security vulnerability.

Report security issues privately to:

- `architects@zer0pa.ai`

## What Counts As A Security Issue

- committed secrets or tokens
- supply-chain or dependency compromise
- arbitrary code execution or privilege escalation paths
- unsafe workflow/bootstrap behavior that can expose credentials or local files

## What Does Not Count

- normal correctness failures
- falsification findings
- performance shortfalls
- stale proof claims

Those are engineering issues and should be handled through the normal repo workflow.

## Current Security Caveat

This staging phase did not run a fresh repo-local secret scan. Phase 5 verification must cover that before any public release decision.

