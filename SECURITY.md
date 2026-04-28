<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE Video Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/reporting-a-vulnerability.svg" alt="REPORTING A VULNERABILITY" width="100%">
</p>

Do not open a public issue for a security vulnerability.

Report security issues privately to:

- `architects@zer0pa.ai`

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

What counts as a security issue:

- committed secrets or tokens
- supply-chain or dependency compromise
- arbitrary code execution or privilege escalation paths
- unsafe workflow or bootstrap behaviour that can expose credentials or
  local files

What does not count:

- normal correctness failures
- falsification findings
- performance shortfalls
- stale proof claims

Those belong in the normal repo workflow.

<p>
  <img src=".github/assets/readme/section-bars/supported-versions.svg" alt="SUPPORTED VERSIONS" width="100%">
</p>

Supported versions: the currently-installable `zpe-video` package on
the main branch (package version `0.1.0`). The always-in-beta cadence
means the next minor release may ship at any time; security fixes target
the main branch and the latest tagged release.

Current security posture:

- the security contact is live
- the public code surface (`src/zpe_video/receipt.py`, tests,
  docs-facing examples) is zero-dependency pure stdlib for the core
  receipt module; optional extras (`producer`, `research`) pull in
  numpy / torch / ultralytics and inherit their upstream security
  surfaces
- repo-local secret scans are run before each signed release tag

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

If you find a vulnerability, email `architects@zer0pa.ai`. Do not open a
public issue for a security report, and do not file a CVE before we
respond. We will acknowledge within five business days.
