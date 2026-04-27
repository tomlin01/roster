# Reviewer Notes

## Findings

No P0/P1/P2 blocking findings after reviewer completion.

### P3 - Runtime readiness freshness is not cryptographically tied to packet content

- File: `scripts/system_hub.py`
- Observation: `runtime-invoke` may load an existing `runtime_readiness_report.json` rather than recomputing readiness on every dry-run. This follows Prompt 8's "recompute or load" allowance and preserves the current no-rewrite behavior for existing readiness reports.
- Assessment: This is acceptable for Prompt 8, but a later execution-capable round should add freshness evidence such as CAP/runtime mapping hashes or an explicit `--refresh-readiness` step before real adapter execution.

## Review Summary

Prompt 8 is materially complete. The implementation adds a same-workspace
approval evidence sidecar and a guarded runtime invocation dry-run surface
without turning runtime adapters into governance owners.

The core behavior is now covered:

- `approval` operates only on existing packet runs
- approval evidence records gate decisions without rewriting packet Markdown
- latest denied gate decisions block invocation
- `runtime-invoke` validates adapter, surface, runtime readiness, approval
  evidence, and manifest-derived paths
- approval-gated CLI execution is refused
- TypeScript `runTasks` is the enforceable surface for gated runs
- invocation reports keep `execution_performed=false`
- denied or withheld capabilities are excluded from exposed capabilities
- JSON refusal paths are parseable
- schema-check recognizes the new optional evidence reports
- docs and policies make the non-execution and ownership boundaries explicit

The Vis_Math Lecture1 smoke produced a structured refusal because the existing
packet run is not runtime-ready. That is an acceptable outcome for Prompt 8 and
is better than pretending the adapter can run. The smoke wrote only
`runtime_invocation_report.json` in the target workspace and a repeated hash
check confirmed the five packet Markdown files were unchanged.

## Verification

Reviewer reruns:

- `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py` passed
- `python3 scripts/test_system_hub.py` passed
- independent temp workspace Prompt 8 smoke passed
- Vis_Math Lecture1 `runtime-invoke --dry-run --json` returned parseable refusal with `reason=runtime_readiness_blocking_findings`
- Vis_Math repeated runtime-invoke hash check confirmed packet Markdown unchanged
- non-reference Markdown link check passed: `missing=0 files_checked=93`
- repo-local artifact-harness packet output check returned empty:
  - `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`

## Remaining Risks

- This round proves the invocation guard envelope, not real adapter execution.
- JSON payloads are versioned in command envelopes but not formal JSON Schema
  files.
- Runtime readiness freshness should be strengthened before any future
  execution-capable Prompt.
- The codex-cns worktree remains dirty with pre-existing unrelated changes and
  untracked files; no staging was performed.
