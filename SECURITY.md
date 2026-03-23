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

There is no supported public release line yet.

Current security reading:

- this repo is `staging_only`
- the security contact is live
- release-grade security validation is still deferred

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

This phase did not run a fresh repo-local secret scan. Any future public
release decision must include a clean security validation pass on the
exact release commit.
