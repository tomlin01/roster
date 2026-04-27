# Developer Report

## Round Metadata

- round: `round_008_runtime_invocation_guard`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/prompt.md`
- developer: `Codex`
- date: `2026-04-28`
- branch or worktree: current dirty worktree, no staging
- note: the first CLI developer thread was interrupted before it created the exchange artifacts; this report covers the reviewed and completed Prompt 8 patch.
- related artifacts:
  - `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/verification.md`
  - `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/reviewer_notes.md`

## Findings Addressed

- Added first-class approval evidence at `<workspace>/contexts/artifact_harness_runs/<packet-id>/approval_evidence.json`.
- Added `artifact-harness approval --path <workspace> --id <packet-id> --gate <gate-id> --decision approved|denied --approver <label> --json`.
- Added guarded `artifact-harness runtime-invoke --path <workspace> --id <packet-id> --adapter open-multi-agent --surface typescript-runTasks --dry-run --json`.
- `runtime-invoke` validates the existing packet run, manifest-derived paths, runtime readiness, approval evidence, requested adapter, and execution surface before writing `runtime_invocation_report.json`.
- `runtime-invoke` remains dry-run/export only: `execution_performed=false` for both pass and refusal paths.
- Approval-gated CLI invocation is refused; TypeScript `runTasks` is the enforceable surface for gated runs.
- Latest `denied` gate decision blocks invocation even if an earlier decision approved the same gate.
- Denied or withheld capabilities are filtered out of exposed capabilities in the invocation report.
- Missing packet runs, outside-target manifest packet paths, and config/path boundary failures return parseable JSON.
- Round 007 schema-check now recognizes `approval_evidence.json` and `runtime_invocation_report.json` as optional generated evidence.
- Runtime adapter policy and Artifact Harness workflow docs now state that adapters must not execute directly from Markdown mapping and must pass an invocation guard or equivalent CAP/readiness/approval check first.

## Changed Files

- `scripts/system_hub.py`
- `scripts/test_system_hub.py`
- `README.md`
- `AGENTS.md`
- `docs/RUNTIME_ARTIFACT_POLICY.md`
- `policy/system_hub.toml`
- `policy/ARTIFACT_HARNESS_SCHEMA_V0.md`
- `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
- `policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`
- `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/developer_report.md`
- `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/verification.md`
- `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/reviewer_notes.md`

## Generated Artifacts

- Temporary Prompt 8 smoke workspace under `/var/folders/.../codex-cns-r008-review-*`
  - created `approval_evidence.json` and `runtime_invocation_report.json`
  - removed after the smoke test
- `/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/runtime_invocation_report.json`
  - durable target-workspace invocation refusal evidence
  - produced by the required real workspace smoke
  - packet Markdown hashes remained unchanged in the follow-up hash check

No durable artifact-harness smoke packet runs were written under the `codex-cns` repo-local `contexts/` directory.

## Verification Commands

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: `system hub test harness checks passed`
- command: independent temp workspace Prompt 8 smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: initial refusal parsed, approval evidence parsed, passing dry-run wrote only invocation report, denied gate later blocked with `reason=approval_denied`
- command: Vis_Math Lecture1 `runtime-invoke --dry-run --json`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: structured refusal, acceptable for Prompt 8
  - output summary: `returncode=1`, `reason=runtime_readiness_blocking_findings`, `execution_performed=false`, invocation report exists
- command: Vis_Math Lecture1 repeated `runtime-invoke --dry-run --json` with packet Markdown hashes before/after
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: all five packet Markdown hashes unchanged
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: `missing=0 files_checked=93`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - result: passed
  - output summary: command returned empty

## Known Non-Goals

- did not start Prompt 9
- did not stage files
- did not invoke `open-multi-agent`
- did not spawn agents from `runtime-invoke`
- did not execute runtime tasks
- did not add a server, daemon, database, orchestration UI, or new dependency
- did not turn approval evidence, runtime readiness, or invocation reports into artifact acceptance
- did not make runtime adapters governance owners
- did not rewrite filled packet Markdown during approval recording, runtime-invoke, schema-check, or migrate

## Remaining Risks

- `runtime-invoke` is still a dry-run/export guard, not real runtime execution.
- Runtime readiness may be loaded from an existing report; future rounds may want freshness hashes tying readiness to the exact CAP/runtime mapping content.
- JSON command payloads remain lightweight implementation contracts, not standalone formal JSON Schema files.
- The Vis_Math smoke now has durable target-workspace invocation refusal evidence; this was expected by Prompt 8, but it is still local project state.
