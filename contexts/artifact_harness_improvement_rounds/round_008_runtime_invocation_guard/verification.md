# Verification Evidence

## Round Metadata

- round: `round_008_runtime_invocation_guard`
- prompt file: `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/prompt.md`
- developer report: `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/developer_report.md`
- reviewer notes: `contexts/artifact_harness_improvement_rounds/round_008_runtime_invocation_guard/reviewer_notes.md`
- date: `2026-04-28`

## Reported Verification

The CLI developer thread was interrupted before it created a standalone
verification file. The patch it left behind included regression tests for:

- approval evidence creation without packet Markdown rewrites
- latest deny overriding prior approval
- readiness-blocked runtime invocation refusal
- missing approval evidence refusal
- approval-gated CLI refusal
- TypeScript `runTasks` dry-run invocation report
- denied or withheld capability filtering
- outside-target manifest packet path refusal
- missing packet run refusal
- dry-run idempotence limited to `runtime_invocation_report.json`

## Reviewer Rerun Verification

Commands actually rerun after reviewing and completing the patch.

- command: `python3 -m py_compile scripts/system_hub.py scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command exited `0`
- command: `python3 scripts/test_system_hub.py`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `system hub test harness checks passed`
- command: independent temp workspace Prompt 8 smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: create succeeded; missing readiness/approval path refused with parseable JSON; approval evidence parsed; runtime-check made the packet ready; `runtime-invoke --dry-run --json` passed with `execution_performed=false`; denied gate then blocked with `reason=approval_denied`; packet Markdown sentinel stayed intact
- command: Vis_Math Lecture1 runtime-invoke smoke
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed as structured refusal
  - evidence path or output summary: `returncode=1`, `reason=runtime_readiness_blocking_findings`, `execution_performed=false`, `runtime_invocation_report_path=/Users/tom/Documents/PHD/Vis_Math/Slides/Lecture1/contexts/artifact_harness_runs/vis-math-lecture1-team-smoke/runtime_invocation_report.json`
- command: Vis_Math Lecture1 repeated runtime-invoke with packet Markdown hash check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `runtime_invocation_report_exists=true`, all five packet Markdown hashes unchanged
- command: non-reference Markdown link check
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: `missing=0 files_checked=93`
- command: `find contexts -maxdepth 3 \( -path '*artifact_harness_runs*' -o -name 'artifact_harness_registry.json' \) -print`
  - cwd: `/Users/tom/Documents/PHD/codex-cns`
  - rerun result: passed
  - evidence path or output summary: command returned empty

## Artifact Inspection

- artifact: `approval_evidence.json`
  - expected state: same-workspace evidence sidecar under the packet run
  - observed state: created and parsed in temp smoke; not created in the Vis_Math smoke because the smoke intentionally tested refusal
  - reviewer note: evidence records gate decisions only and does not modify packet Markdown
- artifact: `runtime_invocation_report.json`
  - expected state: same-workspace dry-run/refusal envelope under the packet run
  - observed state: created in temp smoke and in the Vis_Math target workspace
  - reviewer note: `execution_performed=false` in all observed cases
- artifact: `policy/ARTIFACT_HARNESS_SCHEMA_V0.md`
  - expected state: lists new optional evidence reports
  - observed state: `approval_evidence.json` and `runtime_invocation_report.json` are documented as optional generated evidence
- artifact: `policy/ARTIFACT_HARNESS_WORKFLOW_V0.md`
  - expected state: states approval evidence and runtime invocation guard ownership boundaries
  - observed state: updated with command examples, output locations, and non-execution boundaries
- artifact: `policy/MULTI_AGENT_RUNTIME_ADAPTERS_V0.md`
  - expected state: forbids direct adapter execution from Markdown mapping alone
  - observed state: states adapter-backed runs must pass invocation guard or equivalent CAP/readiness/approval checks

## Not Run / Unable To Run

- command or check: Prompt 9
  - reason not run: explicitly out of scope for Prompt 8
  - residual risk: future UX/runtime work remains separate
- command or check: `open-multi-agent` execution
  - reason not run: explicitly forbidden by Prompt 8
  - residual risk: this round proves only the guarded dry-run/export envelope, not adapter execution behavior
- command or check: formal JSON Schema validation
  - reason not run: no new dependency or formal schema engine was requested
  - residual risk: JSON shapes are covered by implementation tests and policy docs, not a separate validator

## Verification Summary

- Syntax checks and the full system hub test suite passed.
- Approval evidence and runtime invocation reports are produced as same-folder evidence sidecars.
- Refusal paths return parseable JSON.
- Approval-gated CLI invocation is blocked.
- Latest denied gate decisions block invocation.
- Denied or withheld capabilities are not exposed in the dry-run envelope.
- Real Vis_Math smoke produced structured refusal evidence without executing any adapter or changing packet Markdown.
- No repo-local artifact-harness smoke packet output remains under `codex-cns/contexts/`.
